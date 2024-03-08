#!/bin/bash
pip install ane_transformers
pip install openai-whisper
pip install coremltools
cd whisper.cpp
echo "Build with make"
WHISPER_COREML=1 make -j
echo "Downloading model"
bash ./models/download-ggml-model.sh large-v2
bash ./models/generate-coreml-model.sh large-v2