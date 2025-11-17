# gTTS Player with Piper Fallback for Anki

An enhanced Anki add-on that provides Text-to-Speech (TTS) functionality with a seamless offline fallback.

[![Version](https://img.shields.io/badge/version-v2.0--mod-blue)](https://github.com/voothi/20250421115831-anki-gtts-player) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This add-on modifies the standard gTTS player to be more resilient and versatile. It uses Google's Text-to-Speech service when online but automatically switches to a local, high-quality Piper TTS engine when an internet connection is unavailable or slow. This ensures your study flow is never interrupted.

## Table of Contents

- [gTTS Player with Piper Fallback for Anki](#gtts-player-with-piper-fallback-for-anki)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [How It Works](#how-it-works)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Related Projects](#related-projects)
  - [License](#license)

## Features

-   **Online Mode**: Utilizes Google's high-quality gTTS service for audio generation.
-   **Offline Fallback**: Seamlessly and automatically switches to a local Piper TTS engine if gTTS fails or times out.
-   **Configurable Timeout**: Prevents Anki from freezing by setting a custom timeout for web requests.
-   **On-the-Fly Engine Switching**: Use the `Tools` menu in Anki to switch between `gTTS` and `Piper` as the primary engine without restarting.
-   **No Template Changes Required**: Works with your existing card templates that use the standard `{{tts...}}` syntax.

[Back to Top](#table-of-contents)

## How It Works

The add-on intercepts Anki's default TTS requests. Based on its configuration, it decides which engine to use:

1.  **gTTS Mode (Default)**: It first attempts to generate audio via the gTTS API.
    -   If the request takes too long (exceeds `gtts_timeout_sec`), it fails.
    -   On any failure (timeout or network error), it automatically calls the `piper-tts.py` script as a fallback to generate the audio locally and instantly.
    -   Successfully fetched gTTS files are cached permanently as `.mp3`.

2.  **Piper Mode**: It directly calls the `piper-tts.py` script to generate audio locally. This mode is ideal for fully offline use or for preferring Piper's voices. Audio generated in this mode is not cached, ensuring instant generation every time.

The engine can be switched at any time via the `Tools -> TTS Engine` menu item in Anki's main window.

[Back to Top](#table-of-contents)

## Prerequisites

1.  **Anki**: The Anki desktop application must be running.
2.  **Python 3**: A separate Python 3 installation is required to run the Piper TTS script.
3.  **Piper TTS Utility**: You must have the [Piper TTS Command-Line Utility](https://github.com/voothi/20241206010110-piper-tts) project downloaded and configured, as this add-on calls it for offline generation.

## Installation

1.  **Install the Add-on**:
    -   Clone this repository into your Anki `addons21` folder.
    -   The folder name must be `391644525`.

2.  **Set up Piper TTS**:
    -   Follow the installation instructions in the [Piper TTS Utility repository](https://github.com/voothi/20241206010110-piper-tts). Make sure you can successfully generate audio from your command line with that script.

3.  **Configure the Add-on**:
    -   Open the add-on folder (`addons21/391644525`).
    -   Create a file named `config.json` and paste the configuration from the section below.
    -   **You must update the paths** in `config.json` to point to your Python executable and `piper_tts.py` script.

4.  **Restart Anki**.

[Back to Top](#table-of-contents)

## Configuration

Create a `config.json` file in the add-on's directory (`391644525`) with the following content.

| Key                   | Description                                                                    | Example Value                                                             |
| --------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------- |
| `tts_engine`          | The default TTS engine to use. Can be `gTTS` or `Piper`.                       | `"gTTS"`                                                                  |
| `gtts_timeout_sec`    | Seconds to wait for a response from Google before timing out and using Piper.  | `5`                                                                       |
| `piper_python_path`   | **(Required)** Full path to your Python 3 executable.                          | `"C:/Python/Python312/python.exe"`                                        |
| `piper_script_path`   | **(Required)** Full path to the `piper_tts.py` script from the related project.| `"U:/voothi/20241206010110-piper-tts/piper_tts.py"`                        |

[Back to Top](#table-of-contents)

## Related Projects

-   [**Piper TTS Command-Line Utility**](https://github.com/voothi/20241206010110-piper-tts): The local TTS engine that this add-on depends on for its offline functionality.
-   [**No TTS Player for Anki**](https://github.com/voothi/20250902105308-anki-no-tts/): For users who want to disable TTS instead of enhancing it. This provides a way to temporarily or permanently silence TTS playback.

[Back to Top](#table-of-contents)

## License

[MIT](./LICENSE)

[Back to Top](#table-of-contents)