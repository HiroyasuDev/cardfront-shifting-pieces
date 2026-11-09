#!/usr/bin/env bash
# ==============================================================================
# PXG Engine — NVIDIA Tesla V100 (sm_70, FP16) Anime Telegraph & Cut-In Trainer
# ==============================================================================
set -euo pipefail

export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:128,garbage_collection_threshold:0.8"
export TORCH_CUDNN_V8_API_ENABLED=1

echo "[PXG-V100] Initializing Volta sm_70 FP16 Tensor Core Environment..."
python3 -c "
import torch
assert torch.cuda.is_available(), 'CUDA GPU required for V100 training'
props = torch.cuda.get_device_properties(0)
print(f'[PXG-V100] Detected GPU: {props.name} ({props.total_memory // (1024**2)} MB, sm_{props.major}{props.minor})')
torch.backends.cuda.enable_flash_sdp(False)
torch.backends.cuda.enable_mem_efficient_sdp(True)
torch.backends.cuda.enable_math_sdp(True)
"

echo "[PXG-V100] Dataset Manifest: Datasets/pxg_v100_sakuga_telegraph/v100_sakuga_manifest.json (53 600x800 assets)"
echo "[PXG-V100] Ready to launch Wan 2.1 FP16 Sakuga LoRA & ToonCrafter Keyframe Interpolation."
