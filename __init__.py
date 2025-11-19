# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import os
import sys
import subprocess
import threading
from pathlib import Path
from concurrent.futures import Future
from dataclasses import dataclass
from typing import List, cast

from anki.lang import compatMap
from anki.sound import AVTag, TTSTag
from aqt import mw
from aqt.utils import showInfo, qconnect
from aqt.qt import QAction
from aqt.sound import OnDoneCallback, av_player
from aqt.tts import TTSProcessPlayer, TTSVoice

sys.path.append(os.path.join(os.path.dirname(__file__), "vendor"))

from gtts import gTTS, gTTSError
from gtts.lang import tts_langs

# --- Configuration Handling ---
CONFIG = mw.addonManager.getConfig(__name__)

def get_config():
    """Returns the current configuration."""
    return mw.addonManager.getConfig(__name__)

def write_config(new_config):
    """Writes the new configuration."""
    mw.addonManager.writeConfig(__name__, new_config)

# --- Piper TTS Integration ---
def run_piper_tts(text: str, lang: str, output_path: str) -> bool:
    """
    Calls piper_tts.py to generate an audio file.
    Uses atomic write (temp file -> rename) to prevent corrupted cache.
    """
    conf = get_config()
    python_exe = conf.get("piper_python_path")
    script_path = conf.get("piper_script_path")
    
    temp_output_path = f"{output_path}.temp"

    if not all([python_exe, script_path]):
        print("Piper TTS: Python executable or script path not configured.")
        return False
        
    if not Path(python_exe).exists() or not Path(script_path).exists():
        print(f"Piper TTS: Path does not exist. Python: '{python_exe}', Script: '{script_path}'")
        return False

    if "_" in lang:
        lang_code = lang.split("_")[0]
    else:
        lang_code = lang

    command = [
        python_exe,
        script_path,
        "--lang", lang_code,
        "--text", text,
        "--output-file", temp_output_path
    ]

    try:
        creation_flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            creationflags=creation_flags
        )
        if process.returncode == 0 and os.path.exists(temp_output_path) and os.path.getsize(temp_output_path) > 0:
            # Atomic rename to ensure valid cache
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except OSError:
                    pass
            os.rename(temp_output_path, output_path)
            print(f"Piper TTS successfully generated: {output_path}")
            return True
        else:
            print(f"Piper TTS Error: {process.stderr}")
            if os.path.exists(temp_output_path):
                os.remove(temp_output_path)
            return False
    except Exception as e:
        print(f"Failed to run Piper TTS process: {e}")
        if os.path.exists(temp_output_path):
            try:
                os.remove(temp_output_path)
            except:
                pass
        return False

# --- gTTS Wrapper with Timeout ---
def run_gtts_with_timeout(text: str, lang: str, slow: bool, output_path: str) -> bool:
    """
    Runs gTTS in a separate thread with a configurable timeout.
    Uses atomic write (save to .temp -> rename) to prevent partial files 
    from being treated as valid cache in future runs.
    """
    conf = get_config()
    timeout = conf.get("gtts_timeout_sec", 5)
    result_container = {}
    
    temp_output_path = f"{output_path}.temp"

    def gtts_save_job():
        try:
            tts = gTTS(text=text, lang=lang, lang_check=False, slow=slow)
            tts.save(temp_output_path)
            result_container['success'] = True
        except Exception as e:
            result_container['error'] = e

    try:
        thread = threading.Thread(target=gtts_save_job)
        thread.start()
        thread.join(timeout=timeout)

        if thread.is_alive():
            print(f"gTTS timed out after {timeout} seconds.")
            # We cannot kill the thread, but we ensure we don't rename the temp file here.
            # If the thread eventually finishes, it will leave a .temp file, which is harmless
            # because we only check for the existence of the final .mp3 file.
            return False
        
        if 'error' in result_container:
            if os.path.exists(temp_output_path):
                try:
                    os.remove(temp_output_path)
                except:
                    pass
            raise result_container['error']
        
        # Success: Rename temp to final
        if os.path.exists(temp_output_path) and os.path.getsize(temp_output_path) > 0:
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except OSError:
                    pass
            os.rename(temp_output_path, output_path)
            return True
        
        return False

    except gTTSError as e:
        print(f"gTTS API Error: {e}")
        return False
    except Exception as e:
        print(f"gTTS general error: {e}")
        return False

@dataclass
class GTTSVoice(TTSVoice):
    gtts_lang: str

class GTTSPlayer(TTSProcessPlayer):
    def get_available_voices(self) -> List[TTSVoice]:
        voices = []
        for code, name in tts_langs().items():
            if "-" in code:
                head, tail = code.split("-")
                std_code = f"{head}_{tail.upper()}"
            else:
                std_code = compatMap.get(code)
                if not std_code:
                    continue
            
            if std_code == "en_US":
                std_code = "en_GB"

            voices.append(GTTSVoice(name="gTTS", lang=std_code, gtts_lang=code))
        return voices  # type: ignore

    def _play(self, tag: AVTag) -> None:
        assert isinstance(tag, TTSTag)
        match = self.voice_for_tag(tag)
        assert match
        voice = cast(GTTSVoice, match.voice)

        if not tag.field_text.strip():
            return

        conf = get_config()
        engine = conf.get("tts_engine", "gTTS")
        piper_cache_enabled = conf.get("piper_cache_enabled", False)
        
        base_filename = self.temp_file_for_tag_and_voice(tag, match.voice)
        
        gtts_cache_file = f"{base_filename}.mp3"
        piper_cache_file = f"{base_filename}.wav"

        self._tmpfile = None

        def try_gtts():
            # Check if valid cache exists (must be > 0 bytes)
            if os.path.exists(gtts_cache_file):
                if os.path.getsize(gtts_cache_file) > 0:
                    self._tmpfile = gtts_cache_file
                    return True
                else:
                    # Clean up corrupted 0-byte file
                    try:
                        os.remove(gtts_cache_file)
                    except OSError:
                        pass
            
            slow = tag.speed < 1
            if run_gtts_with_timeout(tag.field_text, voice.gtts_lang, slow, gtts_cache_file):
                self._tmpfile = gtts_cache_file
                return True
            return False
        
        def try_piper():
            # 1. Check Piper cache if enabled (must be > 0 bytes)
            if piper_cache_enabled and os.path.exists(piper_cache_file):
                if os.path.getsize(piper_cache_file) > 0:
                    print(f"Using existing Piper cache: {piper_cache_file}")
                    self._tmpfile = piper_cache_file
                    return True
                else:
                    try:
                        os.remove(piper_cache_file)
                    except OSError:
                        pass

            # 2. Generate if not found
            if run_piper_tts(tag.field_text, voice.lang, piper_cache_file):
                self._tmpfile = piper_cache_file
                return True
            return False

        if engine == "Piper":
            if not try_piper():
                print("Piper failed. No fallback configured.")
        else: # Default to gTTS with Piper fallback
            if not try_gtts():
                print("gTTS failed or timed out, falling back to Piper...")
                if not try_piper():
                    print("Fallback to Piper also failed.")
    
    def _on_done(self, ret: Future, cb: OnDoneCallback) -> None:
        if not hasattr(self, "_tmpfile") or not self._tmpfile:
            cb()
            return
        
        ret.result()
        av_player.insert_file(self._tmpfile)
        cb()

    def stop(self):
        pass

av_player.players.append(GTTSPlayer(mw.taskman))

# --- UI Menu for Switching Engine ---
def switch_tts_engine():
    conf = get_config()
    current_engine = conf.get("tts_engine", "gTTS")
    new_engine = "Piper" if current_engine == "gTTS" else "gTTS"
    conf["tts_engine"] = new_engine
    write_config(conf)
    action.setText(f"TTS Engine: {new_engine}")
    showInfo(f"TTS engine switched to: {new_engine}")

def setup_menu():
    global action
    action = QAction(mw)
    mw.form.menuTools.addAction(action)
    conf = get_config()
    engine = conf.get("tts_engine", "gTTS")
    action.setText(f"TTS Engine: {engine}")
    qconnect(action.triggered, switch_tts_engine)

setup_menu()