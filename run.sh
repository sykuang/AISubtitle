#!/bin/bash
if [[ ! -f $1 ]]; then
    echo "Usage: $0 <path_to_video>"
    exit 1
fi
# set -e
while getopts ":ha" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      a)
        hwaccel="-hwaccel auto"
        exit;;   
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done

SCRIPT_PATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
WHISPER_PATH=$SCRIPT_PATH/whisper.cpp
filename=$(basename "$1")
extension="${filename##*.}"
filename="${filename%.*}"
ffmpeg -i $1 $hwaccel -vn -ar 16000 -ac 1 -acodec pcm_s16le $filename.wav
$WHISPER_PATH/main -m $WHISPER_PATH/models/ggml-large-v2.bin -l ja -osrt --max-context 32 --entropy-thold 2.8 -f $filename.wav
python $SCRIPT_PATH/post_whisper.py $filename.srt
rm $filename.wav
rm $filename.srt