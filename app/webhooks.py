import json
import logging
import os

from pathlib import Path

from flask import Blueprint, request

import constants
from lib import utils

logger = logging.getLogger(__name__)
bp = Blueprint("webhooks", __name__, url_prefix="/webhooks")

MEDIA_TYPE_VIDEO = "Video"
EVENT_LIBRARY_NEW_MEDIA_ADDED = "library.new"
EVENT_SYSTEM_WEBHOOK_TEST = "system.webhooktest"

EVENTS_SUPPORTED = (
    EVENT_LIBRARY_NEW_MEDIA_ADDED,
)


@bp.route("/", methods=("POST",))
def index():
    try:
        # parse webhook data
        post_data = request.form.getlist('data')[0]
        json_data = json.loads(post_data)
    except Exception as e:
        logger.exception("oh no")
        return {"success": False}, 500

    event = json_data["Event"]
    item = json_data.get("Item", {})

    if event == EVENT_SYSTEM_WEBHOOK_TEST:
        logger.info("Webhook test received.")
        return {
            "success": True,
            "message": "Received webhook test.",
        }
    if event == EVENT_LIBRARY_NEW_MEDIA_ADDED:
        return _handle_library_new(item)
    else:
        return {
            "success": False,
            "message": f"The provided event '{event}' is not supported.",
        }, 400


def _handle_library_new(item):
    """ Handle Emby webhook "library.new". """
    # TODO: a better way to handle actions..handle multiple actions?

    if item["MediaType"] == MEDIA_TYPE_VIDEO:
        return __handle_subtitle_generation(item)
    else:
        # TODO: a better message, not doing anything could be a bug
        return {
            "success": True,
            "message": "Nothing to do, done!",
        }


def __handle_subtitle_generation(item):
    """ Handle generating subtitles for video file. """
    # name = item["Name"]
    filename = item["FileName"]
    filepath = item["Path"]  # abs path to file
    filepath_obj = Path(filepath)
    filepath_sub = filepath_obj.with_suffix(f"{constants.SUB_PREFIX}-en.srt")
    media_type = item["MediaType"]

    # check media type
    if media_type != MEDIA_TYPE_VIDEO:
        return {
            "success": False,
            "message": f"Cannot generate subtitles for media type '{media_type}'."
        }, 400

    # check if video file exists
    if not filepath_obj.exists():
        return {
            "success": False,
            "message": f"Cannot generate subtitle, video file does not exist at '{filepath}'."
        }

    # check if sub already exists
    if filepath_sub.exists():
        return {
            "success": False,
            "message": f"Cannot generate subtitle, subtitle file does not exist at '{filepath}'."
        }

    # extract audio from video file
    try:
        filepath_audio = utils.extract_audio(filepath)
    except Exception as e:
        logger.exception(f"Extraction error for '{filepath}'.")
        return {
            "success": False,
            "message": f"Failed to extract audio from: '{filepath}'",
        }, 500

    # run whisper, transcribe audio
    try:
        result = utils.transcribe(filepath_audio, constants.WHISPER_MODEL)
    except Exception as e:
        logger.exception(f"Transcription error for audio file: '{filepath_audio}'")
        return {
            "success": False,
            "message": f"Failed to transcribe audio from: '{filepath_audio}'",
        }, 500

    # write srt file
    try:
        utils.transcription_to_srt(result, str(filepath_sub))
    except Exception as e:
        logger.exception(f"Error writing SRT file to '{filepath_sub}'")
        return {
            "success": False,
            "message": f"Failed to write SRT to: '{filepath_sub}'",
        }, 500

    # clean up
    try:
        os.remove(filepath_audio)
        logger.debug("Removed tmp audio file.")
    except:
        logger.exception(f"Failed to remove tmp audio file: '{filepath_audio}'. Continuing..")

    # TODO: async processing and return?
    return {
        "success": True,
        "messages": f"Successfully processed subtitle generation for '{filename}'.",
    }
