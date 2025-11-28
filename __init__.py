# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import os
import sys
import subprocess
import threading
import glob
import re
from pathlib import Path
from concurrent.futures import Future
from dataclasses import dataclass
from typing import List, cast, Optional

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

CONFIG = mw.addonManager.getConfig(__name__)

def get_config():
    return mw.addonManager.getConfig(__name__)

def write_config(new_config):
    mw.addonManager.writeConfig(__name__, new_config)

def sanitize_filename(text: str) -> str:
    text = re.sub(r'[<>:"/\\|?*]', '', text)
    return text.strip().lower()

def find_in_audio_dictionary(text: str, lang: str) -> Optional[str]:
    conf = get_config()
    if not conf.get("audio_dictionary_enabled", False):
        return None

    root_path = conf.get("audio_dictionary_path", "").strip()
    if not root_path or not os.path.exists(root_path):
        return None

    exclusions = conf.get("audio_dictionary_exclusions", [])
    lang_map = conf.get("audio_dictionary_lang_map", {})
    
    # 1. Determine standard short code (default behavior)
    default_short = lang.split('_')[0] if '_' in lang else lang
    
    # 2. Determine target folder name based on map configuration
    target_folder = default_short # Fallback default
    
    # Check for exact match (e.g. "en_GB" -> "British")
    if lang in lang_map:
        target_folder = lang_map[lang]
    # Check for short match (e.g. "en" -> "English")
    elif default_short in lang_map:
        target_folder = lang_map[default_short]
        
    clean_name = sanitize_filename(text)
    filename = f"{clean_name}.mp3"
    
    # Construct path using the resolved folder name
    search_pattern = os.path.join(root_path, target_folder, "*", filename)
    
    # Debug print to help user troubleshoot mapping
    # print(f"Audio Dictionary searching in: {search_pattern}") 

    candidates = glob.glob(search_pattern)
    
    if not candidates:
        return None

    for path in candidates:
        if exclusions and any(ex in path for ex in exclusions):
            continue
        
        if os.path.exists(path) and os.path.getsize(path) > 0:
            print(f"Audio Dictionary: Found match: {path}")
            return path

    return None

def run_piper_tts(text: str, lang: str, output_path: str) -> bool:
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

def run_gtts_with_timeout(text: str, lang: str, slow: bool, output_path: str) -> bool:
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
            return False
        
        if 'error' in result_container:
            if os.path.exists(temp_output_path):
                try:
                    os.remove(temp_output_path)
                except:
                    pass
            raise result_container['error']
        
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
        return voices

    def _play(self, tag: AVTag) -> None:
        assert isinstance(tag, TTSTag)
        match = self.voice_for_tag(tag)
        assert match
        voice = cast(GTTSVoice, match.voice)

        if not tag.field_text.strip():
            return

        conf = get_config()
        engine = conf.get("tts_engine", "gTTS")
        
        persistent_enabled = conf.get("persistent_cache_enabled", False)
        custom_path = conf.get("persistent_cache_path", "").strip()
        
        anki_temp_full_path = self.temp_file_for_tag_and_voice(tag, match.voice)
        
        if persistent_enabled:
            if custom_path:
                cache_dir = custom_path
            else:
                addon_dir = os.path.dirname(__file__)
                cache_dir = os.path.join(addon_dir, "user_cache")
            
            if not os.path.exists(cache_dir):
                try:
                    os.makedirs(cache_dir, exist_ok=True)
                except OSError as e:
                    print(f"Error creating cache dir: {e}. Falling back to temp.")
                    base_filename = anki_temp_full_path
                else:
                    filename_only = os.path.basename(anki_temp_full_path)
                    base_filename = os.path.join(cache_dir, filename_only)
            else:
                filename_only = os.path.basename(anki_temp_full_path)
                base_filename = os.path.join(cache_dir, filename_only)
        else:
            base_filename = anki_temp_full_path

        gtts_cache_file = f"{base_filename}.mp3"
        piper_cache_file = f"{base_filename}.wav"

        self._tmpfile = None

        # Priority 1: Local Audio Dictionary
        dict_file = find_in_audio_dictionary(tag.field_text, voice.gtts_lang)
        if dict_file:
            self._tmpfile = dict_file
            return

        # Priority 2 & 3: gTTS and Piper
        gtts_cache_enabled = conf.get("gtts_cache_enabled", True)
        piper_cache_enabled = conf.get("piper_cache_enabled", False)
        
        enable_gtts_logic = conf.get("gtts_enabled", True)
        enable_piper_logic = conf.get("piper_enabled", True)

        def try_gtts():
            if not enable_gtts_logic:
                return False

            if gtts_cache_enabled and os.path.exists(gtts_cache_file):
                if os.path.getsize(gtts_cache_file) > 0:
                    self._tmpfile = gtts_cache_file
                    return True
                else:
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
            if not enable_piper_logic:
                return False

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

            if run_piper_tts(tag.field_text, voice.lang, piper_cache_file):
                self._tmpfile = piper_cache_file
                return True
            return False

        if engine == "Piper":
            if not try_piper():
                print("Piper failed or disabled.")
        else:
            if not try_gtts():
                if enable_gtts_logic:
                    print("gTTS failed or timed out, falling back to Piper...")
                else:
                    print("gTTS disabled by config, skipping to Piper...")
                
                if not try_piper():
                    print("Fallback to Piper also failed or disabled.")
    
    def _on_done(self, ret: Future, cb: OnDoneCallback) -> None:
        if not hasattr(self, "_tmpfile") or not self._tmpfile:
            cb()
            return
        
        if ret:
            try:
                ret.result()
            except Exception as e:
                print(f"Error in future: {e}")

        av_player.insert_file(self._tmpfile)
        cb()

    def stop(self):
        pass

av_player.players.append(GTTSPlayer(mw.taskman))

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