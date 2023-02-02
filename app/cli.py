#! /usr/bin/env python3
"""
A command-line subtitle generator.
"""
import argparse
import json
import logging
import os
import sys

from pathlib import Path

import constants

from lib import utils

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def gen_subs(args):
    video_filepath = Path(args.filepath)

    if not video_filepath.exists():
        raise Exception(f"Video file does not exist: '{video_filepath}'.")

    srt_filepath = video_filepath.with_suffix(f"{constants.SUB_PREFIX}-en.srt")

    # TODO: prompt user with options: replace, create additional, exit.
    if srt_filepath.exists():
        raise Exception(f"Generated subtitle file exists: '{srt_filepath}'.")

    # extract audio
    try:
        logger.debug("Starting audio extraction")
        audio_filepath = utils.extract_audio(video_filepath)
        logger.debug("extraction done")
    except:
        logger.exception(f"Failed to extract audio from '{video_filepath}'.")
        exit(1)

    # transcribe audio
    try:
        logger.debug("Starting audio transcription")
        whisper_model = "small.en"  # TODO: arg
        result = utils.transcribe(audio_filepath, whisper_model)
        logger.debug("transcribe done")
        logger.debug(json.dumps(result))
    except:
        logger.exception(f"Failed to transcribe file '{audio_filepath}'.")
        exit(1)

    # generate sub file
    try:
        logger.debug("Starting subs generation.")
        utils.transcription_to_srt(result, srt_filepath)
        logger.debug("srt write done")
    except:
        logger.exception("Failed to write SRT file.")
        exit(1)

    # clean up
    try:
        os.remove(audio_filepath)
        logger.debug("Removed tmp audio file.")
    except:
        logger.exception(f"Failed to remove tmp audio file: '{audio_filepath}'. Continuing..")

    logger.debug("SCRIPT DONE OK")


def main(args):
    parser = argparse.ArgumentParser(
        prog="EmbyCompanionCLI",
        description="CLI counterpart tool for the Emby Companion Web App.",
    )

    commands = parser.add_subparsers(dest="commands", required=True)

    # command: gen-sub
    parser_sub_gen = commands.add_parser("gen-subs", help="Generate subtitles from video file.")
    parser_sub_gen.add_argument("filepath", type=str, help="The filepath for the video file we're generating subs for.")

    # parse args
    args = parser.parse_args()

    try:
        command = args.commands.replace("-", "_")
        del(args.commands) # type: ignore
        return globals()[command](args)
    except KeyboardInterrupt:
        print("Exited.")
        return 0
    except Exception as e:
        logger.exception("Encountered error.")
        return 1

if __name__ == "__main__":
    sys.exit(main(sys.argv))
