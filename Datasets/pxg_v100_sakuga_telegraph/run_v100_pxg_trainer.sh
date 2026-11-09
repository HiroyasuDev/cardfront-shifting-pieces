#!/usr/bin/env bash
# ==============================================================================
# PXG Engine — NVIDIA Tesla V100 (sm_70, FP16) Anime Telegraph & Cut-In Trainer
# ==============================================================================
set -euo pipefail

export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:128,garbage_collection_threshold:0.8"
export TORCH_CUDNN_V8_API_ENABLED=1

echo "[PXG-V100] Step 1/2: Synthesizing Pose-B Keyframes & 8-Frame Sakuga Strips..."
python3 Backend/pxg_v100_anime_telegraph_trainer.py

echo "[PXG-V100] Step 2/2: Launching PXG Spatio-Temporal Sakuga LoRA Trainer (FP16 Tensor Cores)..."
python3 Backend/train_v100_sakuga_lora.py --epochs 12 --lora-rank 32 --lora-alpha 64 --fp16
