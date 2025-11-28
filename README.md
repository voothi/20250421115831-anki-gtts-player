# gTTS Player with Piper Fallback & Smart Caching for Anki

An enhanced Anki add-on that provides Text-to-Speech (TTS) functionality with a seamless offline fallback, intelligent caching, and persistent storage.

[![Version](https://img.shields.io/badge/version-v1.48.2-blue)](https://github.com/voothi/20250421115831-anki-gtts-player) 
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![AnkiWeb](https://img.shields.io/badge/AnkiWeb-42281744-blue)](https://ankiweb.net/shared/info/42281744)
[![Anki](https://img.shields.io/badge/Anki-2.1%2B-lightgrey)](https://apps.ankiweb.net/)

> **Attribution & Source**
>
> This add-on is a modified fork of the official **gTTS Player** developed by Ankitects Pty Ltd.
>
> *   **Original Project**: [Source Code](https://github.com/ankitects/anki-addons/tree/main/code/gtts_player) | [AnkiWeb (391644525)](https://ankiweb.net/shared/info/391644525)
> *   **This Enhanced Version**: [Source Code](https://github.com/voothi/20250421115831-anki-gtts-player) | [AnkiWeb (42281744)](https://ankiweb.net/shared/info/42281744)
>
> Licensed under the **GNU AGPL, version 3 or later**.

This enhanced version uses a 3-tier system for audio playback: a local high-fidelity audio dictionary, Google's online TTS service, and a local Piper TTS engine for a complete offline fallback.

## Table of Contents

- [gTTS Player with Piper Fallback \& Smart Caching for Anki](#gtts-player-with-piper-fallback--smart-caching-for-anki)
  - [Table of Contents](#table-of-contents)
  - [Project Philosophy](#project-philosophy)
  - [Features](#features)
  - [How It Works](#how-it-works)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    - [Part 1: Install the Add-on](#part-1-install-the-add-on)
    - [Part 2: Set up the Piper TTS Backend (Optional but Recommended)](#part-2-set-up-the-piper-tts-backend-optional-but-recommended)
    - [Part 3: Finalize](#part-3-finalize)
  - [Configuration](#configuration)
    - [Full Configuration Example](#full-configuration-example)
    - [Configuration Keys](#configuration-keys)
  - [Usage in Templates](#usage-in-templates)
    - [Basic Syntax](#basic-syntax)
    - [Language Examples](#language-examples)
    - [Real-World Examples](#real-world-examples)
  - [Related Projects](#related-projects)
  - [Kardenwort Ecosystem](#kardenwort-ecosystem)
  - [License](#license)

---

## Project Philosophy

The primary goal of this enhancement is to create a self-sufficient study environment. Whether you are on the go with limited mobile data or wish to disconnect completely for a focused study session, this add-on ensures your audio cards work flawlessly. By leveraging a local TTS engine, it saves bandwidth, works entirely offline, and removes dependency on an active internet connection.

[Return to Top](#table-of-contents)

## Features

-   **3-Tier Audio Source Priority**:
    1.  **Local Audio Dictionary**: Plays high-quality, pre-recorded audio from your local collection (e.g., Forvo packs) for the most authentic pronunciation.
    2.  **gTTS (Online)**: If no local file is found, it uses Google's high-quality online TTS service.
    3.  **Piper TTS (Offline)**: If gTTS fails or is disabled, it falls back to a high-quality, local, and fully offline Piper TTS engine.
-   **Playback Cycling**: On repeated clicks, cycle through different voices:
    -   Hear various pronunciations from different authors in your Audio Dictionary.
    -   Alternate between `gTTS` and `Piper` to compare synthesized voices.
-   **Smart Caching & Persistent Storage**: Caches all generated audio to avoid repeated network requests (gTTS) or CPU usage (Piper). Files can be stored permanently across Anki sessions.
-   **Flexible Configuration**: Fine-tune every aspect, from enabling/disabling sources to mapping custom language folders and excluding specific speakers.
-   **On-the-Fly Engine Switching**: Instantly switch between `gTTS` and `Piper` as the primary TTS engine via the Anki `Tools` menu.
-   **Atomic Writes**: Prevents corrupted or zero-byte audio files if generation is interrupted.

[Return to Top](#table-of-contents)

## How It Works

The add-on intercepts Anki's default TTS requests and processes them with the following priority:

1.  **Check Audio Dictionary**: 
    -   It first searches for a matching `.mp3` file in your configured local audio dictionary path.
    -   If found, it plays immediately. On subsequent clicks, it can cycle through other available recordings for the same word.

2.  **Attempt Primary TTS (or Cycle)**:
    -   If no local audio is found, it proceeds to TTS.
    -   If `tts_cycle_enabled` is `true`, it alternates between gTTS and Piper on each click.
    -   Otherwise, it uses the default engine set in the config (`gTTS` or `Piper`).

3.  **Cross-Engine Failover**:
    -   If the selected TTS engine fails (e.g., gTTS timeout, Piper script error), it **automatically attempts the other engine** as a final fallback.
    -   Sound will only fail if both your local dictionary is empty for a term and both TTS engines are disabled or failing.

[Return to Top](#table-of-contents)

## Prerequisites

1.  **Anki**: The Anki desktop application.
2.  **Python 3**: A separate Python 3 installation is required to run the Piper TTS script.
3.  **Piper TTS Utility**: You must have the [Piper TTS Command-Line Utility](https://github.com/voothi/20241206010110-piper-tts) project downloaded and configured.

## Installation

### Part 1: Install the Add-on

Choose **one** of the following methods:

**Option A: Install via AnkiWeb (Recommended)**
1.  Open Anki.
2.  Go to **Tools** > **Add-ons** > **Get Add-ons...**
3.  Enter code: `42281744`
4.  Click **OK**.

**Option B: Manual Installation (Advanced)**
1.  Clone this repository or download the ZIP.
2.  Move the extracted folder into your Anki `addons21` directory.

### Part 2: Set up the Piper TTS Backend (Optional but Recommended)

For offline functionality, you **must** set up the external TTS engine:

1.  Download the [Piper TTS Command-Line Utility](https://github.com/voothi/20241206010110-piper-tts).
2.  **Crucial:** Follow the setup instructions in that repository (downloading voice models, configuring `config.ini`, etc.). 
3.  **Note:** If this utility is not configured correctly, Piper TTS will **not** work.

### Part 3: Finalize

1.  **Configure**: Go to **Tools -> Add-ons**, select this add-on, and click **Config** to set up your paths and preferences.
2.  **Restart**: Restart Anki to ensure all modules are loaded correctly.

## Configuration

> **Important:** Please configure this add-on via the Anki interface:
> **Tools -> Add-ons -> Select this add-on -> Config**.
>
> Anki manages user preferences using a separate `meta.json` file. Manually editing `config.json` in the file system is **not recommended**, as your changes may be ignored or overwritten by Anki's internal settings management.

> **Immediate Effect:** 
> **All** configuration changes (including paths, timeouts, and cache settings) apply **immediately** after clicking "OK" in the configuration window. You do not need to restart Anki for these changes to take effect, as the add-on re-reads the configuration before playing each audio file.

The default configuration (in `config.json`) looks like this:

```json
{
    "tts_engine": "gTTS",
    "persistent_cache_enabled": true,
    "persistent_cache_path": "",
    "audio_dictionary_enabled": true,
    "audio_dictionary_path": "D:/AudioDictionaries",
    "audio_dictionary_lang_map": {
        "de_DE": "German",
        "en_US": "English",
        "en_GB": "English"
    },
    "audio_dictionary_exclusions": [
        "BadSpeakerName"
    ],
    "audio_dictionary_cycle_enabled": true,
    "audio_dictionary_cycle_limit": 3,
    "tts_cycle_enabled": true,
    "gtts_enabled": true,
    "gtts_timeout_sec": 5,
    "gtts_cache_enabled": true,
    "piper_enabled": true,
    "piper_python_path": "C:/Python/Python312/python.exe",
    "piper_script_path": "D:/apps/piper-tts/piper_tts.py",
    "piper_cache_enabled": true
}
```

### Configuration Keys

| Key | Type | Description |
| :--- | :--- | :--- |
| **General Settings** | | |
| `tts_engine` | String | The default TTS engine: `"gTTS"` or `"Piper"`. Can also be toggled via the Tools menu. |
| `persistent_cache_enabled`| Boolean | (Optional, Default: `true`) If `true`, saves TTS files to a permanent folder. If `false`, uses Anki's temp folder (deleted on exit). |
| `persistent_cache_path` | String | (Optional, Default: `""`) A custom path for the cache. If empty, defaults to `user_cache` inside the add-on folder. |
| `tts_cycle_enabled` | Boolean | (Optional, Default: `false`) If `true`, repeated clicks on a TTS field will alternate between gTTS and Piper. |
| **Audio Dictionary Settings** | | |
| `audio_dictionary_enabled`| Boolean | (Optional, Default: `false`) Master switch to enable or disable the local audio dictionary feature. |
| `audio_dictionary_path` | String | (Optional, Default: `""`) **Required if enabled.** Absolute path to the root folder of your audio dictionary (e.g., `D:/Forvo`). |
| `audio_dictionary_lang_map`| Object | (Optional, Default: `{}`) Maps Anki language codes to your custom folder names (e.g., `"de_DE": "German"`). If omitted, it defaults to two-letter codes (e.g., `de`, `en`). |
| `audio_dictionary_exclusions`| Array | (Optional, Default: `[]`) A list of strings. If any string appears in an audio file's path, it will be skipped. Useful for blacklisting speakers. |
| `audio_dictionary_cycle_enabled`| Boolean | (Optional, Default: `false`) If `true`, repeated clicks will cycle through different recordings of the same word. |
| `audio_dictionary_cycle_limit`| Integer | (Optional, Default: `2`) The maximum number of recordings to cycle through for a single word. |
| **gTTS Engine Settings** | | |
| `gtts_enabled` | Boolean | (Optional, Default: `true`) Master switch to enable or disable the gTTS engine entirely. |
| `gtts_timeout_sec` | Integer | (Optional, Default: `5`) Seconds to wait for Google's API before failing over to Piper. |
| `gtts_cache_enabled` | Boolean | (Optional, Default: `true`) If `false`, forces a fresh download every time. <br>⚠️ **Warning:** Disabling this may lead to a temporary IP ban from Google. |
| **Piper TTS Engine Settings** | | |
| `piper_enabled` | Boolean | (Optional, Default: `true`) Master switch to enable or disable the Piper TTS engine entirely. |
| `piper_python_path` | String | (Optional, Default: `""`) **Required if enabled.** Full path to your Python executable (e.g., `C:/Python/python.exe`). |
| `piper_script_path` | String | (Optional, Default: `""`) **Required if enabled.** Full path to the `piper_tts.py` script. |
| `piper_cache_enabled` | Boolean | (Optional, Default: `true`) If `false`, regenerates audio every time (high CPU usage). |


[Return to Top](#table-of-contents)

## Usage in Templates

To enable audio on your cards, you need to add the standard Anki TTS tag to your Card Templates (Front or Back).

### Basic Syntax

Insert the following code into your template where you want the audio to play:

```anki
{{tts en_GB voices=gTTS:Front}}
```

*   **`en_GB`**: The language code. Change this to match your target language (e.g., `en_US`, `de_DE`, `ru_RU`, `uk_UA`).
*   **`voices=gTTS`**: **Important:** Do not change this parameter. This add-on specifically intercepts requests made to `gTTS` to enable the caching and offline fallback features.
*   **`Front`**: The name of the field you want to be read aloud.

### Language Examples

Below are examples of how to configure the tag for different languages, based on common usage patterns:

*   **English (UK):** `{{tts en_GB voices=gTTS:EnglishWord}}`
*   **English (US):** `{{tts en_US voices=gTTS:EnglishWord}}`
*   **German:** `{{tts de_DE voices=gTTS:GermanWord}}`
*   **Russian:** `{{tts ru_RU voices=gTTS:RussianhWord}}`
*   **Ukrainian:** `{{tts uk_UA voices=gTTS:UkrainianhWord}}`

### Real-World Examples

For a comprehensive collection of real-world templates demonstrating proper integration, please refer to the **Kardenwort Anki Templates** project.

> **[Kardenwort Anki Templates](https://github.com/kardenwort/20250913123501-kardenwort-anki-templates)**

This project provides extensive examples of how to structure cards and tag fields for various languages within a production-ready environment.

[Return to Top](#table-of-contents)

## Related Projects

-   [**Piper TTS Command-Line Utility**](https://github.com/voothi/20241206010110-piper-tts): The local TTS engine that this add-on depends on for its offline functionality.
-   [**No TTS Player for Anki**](https://github.com/voothi/20250902105308-anki-no-tts/): A companion add-on to temporarily or permanently silence all TTS fields (`{{tts...}}`) without needing to edit card templates.

[Return to Top](#table-of-contents)

## Kardenwort Ecosystem

This project is part of the **[Kardenwort](https://github.com/kardenwort)** environment, designed to create a focused and efficient learning ecosystem.

[Return to Top](#table-of-contents)

## License

[GNU AGPL v3](./LICENSE)

[Return to Top](#table-of-contents)