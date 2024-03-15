#!/bin/bash
cd whisper.cpp
WHISPER_CUBLAS=1 make -j
bash ./models/download-ggml-model.sh large-v2
pip install srt