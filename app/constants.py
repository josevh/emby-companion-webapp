from os import getenv

PORT = int(getenv("PORT", 8100))
WHISPER_MODEL = getenv("WHISPER_MODEL", "small.en")
SUB_PREFIX = getenv("SUB_PREFIX", ".aa")
WHISPER_LOGPROB_THRESHOLD = float(getenv("WHISPER_LOGPROB_THRESHOLD", "-0.9"))
WHISPER_NO_SPEECH_THRESHOLD = float(getenv("WHISPER_NO_SPEECH_THRESHOLD", "0.6"))
