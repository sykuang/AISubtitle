#!/bin/bash
set -e
if ! options=$(getopt -o h --long help,skip-whisper,skip-ffmpeg,audio-lang,srt-lang -n 'parse-options' -- "$@"); then
   # parse error
   exit 1
fi
set -- $options
while [ $# -gt 0 ]; do
   case $1 in
   -h | --help)
      echo "Usage: run.sh [options] <input_file>"
      echo "Options:"
      echo "  -h, --help: Show this help message"
      echo "  --skip-whisper: Skip whispering"
      echo "  --skip-ffmpeg: Skip ffmpeg"
      echo "  --audio-lang <lang>: Set audio language"
      echo "  --srt-lang <lang>: Set srt language"
      exit 0
      ;;
   --skip-whisper) skip_whisper=1 ;;
   --skip-ffmpeg) skip_ffmpeg=1 ;;
   --audio-lang)
      audio_lang=$2
      shift
      ;;
   --srt-lang)
      srt_lang=$2
      shift
      ;;
   --)
      shift
      break
      ;;
   *)
      echo "Internal error!"
      exit 1
      ;;
   esac
   shift
done
file="${1//\'/''}"
if [[ ! -f "$file" ]]; then
   echo "File not found: $file"
   exit 1
fi
if [[ $audio_lang ]]; then
   echo "Audio language: $audio_lang"
else
   echo "Audio language: auto"
   audio_lang="auto"
fi
if [[ $srt_lang ]]; then
   echo "SRT language: $srt_lang"
else
   echo "SRT language: Tranditional chinese"
   srt_lang="Tranditional chinese"
fi
filename=$(basename "$file")
extension="${filename##*.}"
filename="${filename%.*}"
SCRIPT_PATH=$(dirname $(realpath $0))
WHISPER_PATH="$SCRIPT_PATH/whisper.cpp"
if [[ ! $skip_ffmpeg ]]; then
   ffmpeg -y -i "$file" -vn -ar 16000 -ac 1 -acodec pcm_s16le "$filename.wav"
fi
if [[ ! $skip_whisper ]]; then
   $WHISPER_PATH/main -m "$WHISPER_PATH/models/ggml-large-v2.bin" -l "$audio_lang" -osrt --max-context 32 --entropy-thold 2.8 -f "$filename.wav"
fi
python "$SCRIPT_PATH/post_whisper.py" "$filename.wav.srt"

$SCRIPT_PATH/AzureOpenAI_srt_translator/main.py -b 20 -l "$srt_lang" -m gpt-35-turbo "$filename.wav_post.srt"
# Clean up
rm $filename.wav
rm $filename.wav.srt
rm $filename.wav_post.srt