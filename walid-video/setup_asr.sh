#!/bin/bash
# Installs the speech-sync tool (sherpa-onnx + Whisper small, Arabic-capable). HuggingFace is blocked here, so models come from GitHub releases.
set -e
pip install -q sherpa-onnx
mkdir -p ~/asr && cd ~/asr
[ -d sherpa-onnx-whisper-small ] || { curl -sSL -o s.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-small.tar.bz2 && tar xjf s.tar.bz2 && rm s.tar.bz2; }
echo "ready: ~/asr/sherpa-onnx-whisper-small"
