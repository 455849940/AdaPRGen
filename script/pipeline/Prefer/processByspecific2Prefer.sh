#!/bin/bash

PATTERN="train"
DATA_FILE="PreferDataset_First"
gpu_seq=0,1,2,5,6
PORT=36000
batch_size=4
PROMPT_PATTERN="fixbycrflp"
SECOND_PROMPT_PATTERN="fixbycrflp2"
SECOND_CHECKPOINT=12000
predict_filePath="predict_dir/loraWeight/trace_CRFLP_PerferData/Prefer2SecondFixResult.json"
IFS=',' read -ra GPU_ARRAY <<< "$gpu_seq"
gpu_count=${#GPU_ARRAY[@]}

export NCCL_P2P_DISABLE=1
export CUDA_LAUNCH_BLOCKING=1
export TORCH_USE_CUDA_DSA=1
export NCCL_BLOCKING_WAIT=1

echo "Running test"
CUDA_VISIBLE_DEVICES=$gpu_seq torchrun --master_port=$PORT --nproc_per_node=$gpu_count -m LoraTrainer.eval_Multi \
    --do_eval True \
    --debug_mode False \
    --use_peft True \
    --prompt_pattern "$PROMPT_PATTERN" \
    --eval_pattern "$PATTERN" \
    --output_dir "./output_dir/DirectFixCodeLlama/" \
    --data_path "./repairDataset/RepairData-PythonLevel/$DATA_FILE/" \
    --predict_filePath "$predict_filePath" \
    --per_device_eval_batch_size $batch_size \
    --half True
      
echo "All evaluations completed."
