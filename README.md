# Emby Companion Web App 📺

A companion web app for [Emby](https://emby.media) leveraging [webhooks](https://support.emby.media/support/solutions/articles/44001848859-webhooks).

Also includes a CLI!


## Features

- Subtitle Generation - Inspired by [McCloudS/subgen](https://github.com/McCloudS/subgen) for Plex.
  - Uses:
    - [openai/whisper](https://github.com/openai/whisper)
    - [kkroening/ffmpeg-python](https://github.com/kkroening/ffmpeg-python)
    - [cdown/srt](https://github.com/cdown/srt)
  - Emby webhook event trigger: `library.new`
  - ENV vars
    - `WHISPER_MODEL='small.en'` ([see](https://github.com/openai/whisper#available-models-and-languages))
    - `SUB_PREFIX='.ai'` to output `$FILENAME.$SUB_PREFIX-en.srt`
    - `WHISPER_LOGPROB_THRESHOLD='-0.9'` ([see](https://github.com/openai/whisper/blob/a6b36ede1f060860d5676a543176a6439d91eae6/whisper/transcribe.py#L54-L55))
    - `WHISPER_NO_SPEECH_THRESHOLD='0.6'` ([see](https://github.com/openai/whisper/blob/a6b36ede1f060860d5676a543176a6439d91eae6/whisper/transcribe.py#L57-L59))


## Usage (Docker)

1. Install the "Webhooks" plugin, see the Emby docs on installing plugins [here](https://support.emby.media/support/solutions/articles/44001159720-plugins).

2. Configure Emby to send webhook requests for events:
    1. Set the **Url** field to point to the host running this application, e.g.: 
        ```
        http://${host}:${port}/webhooks/
        ```
        The default port is `PORT=8100`.
    2. Select the **Events** you'd like to trigger requests, e.g.:
        ```
         library.new
        ```

3. Setup docker, ensure your media mount path matches the media paths that Emby recognizes. If emby accesses your media at `/media/`, setup docker to mount media with that same path. **THIS IS CRITICAL**.
    ```yaml
    volumes:
      - /my/local/media:/media
    ```

## Usage (cli)
You can run the generator via terminal:
```console
❯ ./app/cli.py --help
usage: EmbyCompanionCLI [-h] {gen-subs} ...

CLI counterpart tool for the Emby Companion Web App.

positional arguments:
  {gen-subs}
    gen-subs  Generate subtitles from video file.

optional arguments:
  -h, --help  show this help message and exit
```
