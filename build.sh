#!/bin/bash
set -e
if ! options=$(getopt -o h --long help,cuda,coreml -n 'parse-options' -- "$@"); then
    # parse error
    exit 1
fi
set -- $options
while [ $# -gt 0 ]; do
    case $1 in
    -h | --help)
        echo "Usage: build.sh [options]"
        echo "Options:"
        echo "  -h, --help: Show this help message"
        echo "  --cuda: Build with CUDA support"
        echo "  --coreml: Build with CoreML support"
        exit 0
        ;;
    --cuda) cuda=1 ;;
    --coreml) coreml=1 ;;
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
if [[ $coreml ]]; then
    echo "Building with CoreML support"
    pip install ane_transformers
    pip install openai-whisper
    pip install coremltools
    WHISPER_COREML=1
elif [[ $cuda ]]; then
    echo "Building with CUDA support"
    WHISPER_CUBLAS=1
else
    echo "Building with CPU support"
fi

cd whisper.cpp
WHISPER_COREML=$WHISPER_COREML WHISPER_CUBLAS=$WHISPER_CUBLAS make -j
bash ./models/download-ggml-model.sh large-v2
if [[ $coreml ]]; then
    bash ./models/generate-coreml-model.sh large-v2
fi
