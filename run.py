#!/usr/bin/env python3
import argparse
from pathlib import Path
import subprocess
from post_whisper import main as post_whisper


def parse_args():
    parser = argparse.ArgumentParser(
        description="This script is for running the AI Subtitle"
    )
    parser.add_argument("--skip-whisper", action="store_true", help="Skip whispering")
    parser.add_argument("--skip-ffmpeg", action="store_true", help="Skip ffmpeg")
    parser.add_argument("--audio-lang", type=str, help="Audio language", default="auto")
    parser.add_argument(
        "--srt-lang", type=str, help="SRT language", default="Tranditional chinese"
    )
    parser.add_argument(
        "--skip-clean", action="store_true", help="Do not clean the temp files"
    )
    parser.add_argument(
        "--skip-translate", action="store_true", help="Do not translate the srt"
    )
    parser.add_argument("--output", type=str, help="Output file")
    parser.add_argument("input", type=str, help="Input file")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()


    out_file = Path(args.input).stem + ".wav"
    out_srt = args.output if args.output else Path(args.input).stem + ".srt"
    if args.skip_ffmpeg == False:
        if Path(args.input).is_file() == False:
            print("Input file not found")
        return
        print("Running ffmpeg")
        # ffmpeg -y -i "$file" -vn -ar 16000 -ac 1 -acodec pcm_s16le "$filename.wav"
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                args.input,
                "-vn",
                "-ar",
                "16000",
                "-ac",
                "1",
                "-acodec",
                "pcm_s16le",
                out_file,
            ]
        )
    if args.skip_whisper == False:
        print("Running whisper")
        #    $WHISPER_PATH/main -m "$WHISPER_PATH/models/ggml-large-v2.bin" -l "$audio_lang" -osrt --max-context 32 --entropy-thold 30 -f "$filename.wav"
        whisper_path = Path(__file__).parent / "whisper.cpp" / "main"
        whisper_model = (
            Path(__file__).parent / "whisper.cpp" / "models" / "ggml-large-v2.bin"
        )
        subprocess.run(
            [
                whisper_path,
                "-m",
                whisper_model,
                "-l",
                args.audio_lang,
                "-osrt",
                "--max-context",
                "32",
                "--entropy-thold",
                "30",
                "-f",
                out_file,
            ]
        )
    post_whisper([out_file + ".srt"])
    if args.skip_translate == False:
        print("Running translate")
        from translator import Translator

        #    $SCRIPT_PATH/AzureOpenAI_srt_translator/main.py -b 20 -l "$srt_lang" -m gpt-35-turbo "$filename.wav_post.srt"
        tran = Translator(
            batchsize=20,
            lang=args.srt_lang,
        )
        tran.translate_srt(out_file + "_post.srt")
        tran.save(out_srt)
    if args.skip_clean == False:
        print("Cleaning temp files")
        #  rm $filename.wav
        #   rm $filename.wav.srt
        #   rm $filename.wav_post.srt
        from os import remove

        try:
            if out_file and out_file.is_file():
                remove(out_file)
            if (out_file + ".srt").is_file():
                remove(out_file + ".srt")
            if (out_file + "_post.srt").is_file():
                remove(out_file + "_post.srt")
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
