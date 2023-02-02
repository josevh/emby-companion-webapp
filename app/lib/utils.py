import logging
import tempfile
from datetime import timedelta
from pathlib import Path

import ffmpeg
import srt
import whisper

import constants


logger = logging.getLogger(__name__)

def extract_audio(filepath):
    """
    see: https://kkroening.github.io/ffmpeg-python/#ffmpeg.overwrite_output

    emulating:
        ffmpeg
            # overwrite output file
            -y
            # input filename
            -i \"{filename}\"
            # audio: frequency, default 44100Hz
            -ar 16000
            # audio: channels, default 1
            -ac 1
            # codec audio
            -c:a pcm_s16le
            # output file
            \"{filename}.output.wav\"
    """
    filepath_obj = Path(filepath)
    # filepath_tmp_audio = str(filepath_obj.with_suffix(".tmp.wav"))
    filepath_tmp_audio = tempfile.NamedTemporaryFile().name

    ffmpeg_args = {
        "acodec": "pcm_s16le",
        "ar": "16000",
        "ac": "1",
        "format": "wav",
    }

    input = ffmpeg.input(filepath)
    out = ffmpeg.output(
        input.audio,
        filename=filepath_tmp_audio,
        **ffmpeg_args)
    out.run()

    return filepath_tmp_audio


def transcribe(filepath_audio, whisper_model):
    """
    see: https://github.com/openai/whisper/blob/main/whisper/transcribe.py#L19

    Returns
    -------
    A dictionary containing the resulting text ("text") and segment-level details ("segments"), and
    the spoken language ("language"), which is detected when `decode_options["language"]` is None.
    """
    """
    emulating:
        ./main
            -m models/ggml-{whisper_model}.bin
            -of \"{final_subname}\"
            -t {whisper_threads}
            -p {whisper_processors}
            -osrt
            # -osrt -su # if speedup
            -f \"{input_wav_file}\"
    """
    # TODO: support inputting language, parse from the webhook event data? from pathname?
    model = whisper.load_model(whisper_model)
    result = model.transcribe(
        filepath_audio,
        logprob_threshold=constants.WHISPER_LOGPROB_THRESHOLD,
        no_speech_threshold=constants.WHISPER_NO_SPEECH_THRESHOLD,
    )

    logger.debug(f"Transcribed '{filepath_audio}', result:")
    logger.debug(str(result))

    return result


def transcription_to_srt(transcription_result, srt_filepath):
    # TODO: check for segment["no_speech_prob"].. if it's high.. then
    #       there was likely no speech, skip it?
    sub_index = 1
    subs = []
    for segment in transcription_result["segments"]:
        subs.append(
            srt.Subtitle(
                index=sub_index,
                start=timedelta(seconds=segment["start"]),
                end=timedelta(seconds=segment["end"]),
                content=segment["text"]
            )
        )
        sub_index += 1

    subs_str = srt.compose(subs)

    with open(srt_filepath, "w") as sub_file:
        sub_file.write(subs_str)
