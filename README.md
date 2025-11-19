# gTTS Player with Piper Fallback & Smart Caching for Anki

An enhanced Anki add-on that provides Text-to-Speech (TTS) functionality with a seamless offline fallback, intelligent caching, and persistent storage.

[![Version](https://img.shields.io/badge/version-v1.46.14-blue)](https://github.com/voothi/20250421115831-anki-gtts-player) 
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

This enhanced version uses Google's Text-to-Speech service when online but automatically switches to a local, high-quality Piper TTS engine when an internet connection is unavailable or slow.

## Table of Contents

- [gTTS Player with Piper Fallback \& Smart Caching for Anki](#gtts-player-with-piper-fallback--smart-caching-for-anki)
  - [Table of Contents](#table-of-contents)
  - [Project Philosophy](#project-philosophy)
  - [Features](#features)
  - [How It Works](#how-it-works)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    - [Part 1: Install the Add-on](#part-1-install-the-add-on)
    - [Part 2: Set up the Piper TTS Backend (Mandatory)](#part-2-set-up-the-piper-tts-backend-mandatory)
    - [Part 3: Finalize](#part-3-finalize)
  - [Configuration](#configuration)
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

-   **Hybrid Online/Offline TTS**: Uses Google's high-quality gTTS service online and seamlessly falls back to the local Piper TTS engine when offline or when the connection is unstable.
-   **Smart Caching**: 
    -   **gTTS**: Caches downloaded MP3s to avoid repeated network requests.
    -   **Piper**: Caches generated WAV files to save CPU resources and battery life on subsequent plays.
-   **Persistent Storage**: Unlike the standard temporary cache which is deleted when Anki closes, this add-on can save audio files permanently in a dedicated folder. This significantly reduces bandwidth usage and generation time over long-term study.
-   **Atomic Writes**: Implements fail-safe file writing (generating to `.temp` first) to prevent corrupted or zero-byte audio files if the process is interrupted or the network fails.
-   **On-the-Fly Engine Switching**: Instantly switch between `gTTS` and `Piper` as the primary engine via the Anki `Tools` menu.
-   **Configurable Timeout**: Prevents Anki from freezing by setting a custom timeout for web requests before switching to the offline engine.

[Return to Top](#table-of-contents)

## How It Works

The add-on intercepts Anki's default TTS requests and processes them based on your configuration:

1.  **Check Cache**: 
    -   It first checks if a valid audio file already exists in the configured cache directory.
    -   If `persistent_cache_enabled` is active, files remain available across Anki restarts.
    -   If the file exists and caching is enabled for the current engine, it plays immediately (0 latency, 0 network usage, 0 CPU generation).

2.  **Primary Engine (Default: gTTS)**: 
    -   Attempts to fetch audio from Google.
    -   If successful, saves the file (atomically) and plays it.
    -   If the request times out (default 5s) or fails, it triggers the fallback.

3.  **Fallback / Secondary Engine (Piper)**: 
    -   Checks if a pre-generated Piper file exists in the cache. If yes, plays it immediately.
    -   If not, runs the local `piper_tts.py` script to generate the audio, saves it to the cache, and plays it.

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

### Part 2: Set up the Piper TTS Backend (Mandatory)

Regardless of how you installed the add-on in Part 1, you **must** set up the external TTS engine:

1.  Download the [Piper TTS Command-Line Utility](https://github.com/voothi/20241206010110-piper-tts).
2.  **Crucial:** Follow the setup instructions in that repository (downloading voice models, configuring `config.ini`, etc.). 
3.  **Note:** If this utility is not configured correctly, the Piper fallback will **not** work.

### Part 3: Finalize

1.  **Configure**: Create or update the configuration (see below) to point to your Python and Piper script paths.
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
    "gtts_timeout_sec": 5,
    "piper_python_path": "C:/Python/Python312/python.exe",
    "piper_script_path": "U:/voothi/20241206010110-piper-tts/piper_tts.py",
    "piper_cache_enabled": true,
    "gtts_cache_enabled": true,
    "persistent_cache_enabled": true,
    "persistent_cache_path": ""
}
```

### Configuration Keys

| Key | Type | Description |
| :--- | :--- | :--- |
| `tts_engine` | String | The default engine: `"gTTS"` or `"Piper"`. Can be toggled via the Tools menu. |
| `gtts_timeout_sec` | Integer | Seconds to wait for Google's API before switching to Piper. |
| `piper_python_path` | String | **Required.** Full path to your Python executable. |
| `piper_script_path` | String | **Required.** Full path to the `piper_tts.py` script. |
| `gtts_cache_enabled` | Boolean | **Recommended: true**. If `false`, forces a fresh download every time. <br>⚠️ **Warning:** Leaving this disabled during regular study may lead to a **temporary IP ban** from Google due to excessive requests. |
| `piper_cache_enabled` | Boolean | If `true`, uses existing WAV files. If `false`, regenerates audio every time (high CPU usage). |
| `persistent_cache_enabled` | Boolean | If `true`, saves files to a permanent folder. If `false`, uses Anki's temp folder (deleted on exit). |
| `persistent_cache_path` | String | Optional. A custom absolute path for the cache folder. If empty `""`, defaults to `user_cache` inside the add-on folder. |

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
