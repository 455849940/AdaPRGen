#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <upcont> <pattern> <checkpoint> <save_steps> <prompt_pattern> <data_file> <gpu_seq> <port>"
  exit 1
fi

UPCONT=$1
PATTERN=$2 
CHECKPOINT=$3
SAVE_STEPS=$4
PROMPT_PATTERN=$5
DATA_FILE=$6
gpu_seq=$7
PORT=$8
batch_size=$9
Version=${10}
use_predict_crp=${11}
CRPdata_path=${12}

if [ -z "$UPCONT" ] || [ -z "$PATTERN" ] || [ -z "$CHECKPOINT" ] || [ -z "$SAVE_STEPS" ] || [ -z "$PROMPT_PATTERN" ] || [ -z "$DATA_FILE" ] || [ -z "$gpu_seq" ] || [ -z "$PORT" ]; then
  echo "Missing one or more required parameters."
  echo "Usage: $0 <upcont> <pattern> <checkpoint> <save_steps> <prompt_pattern> <data_file> <gpu_seq> <port> <batch_size>"
  exit 1
fi

IFS=',' read -ra GPU_ARRAY <<< "$gpu_seq"
gpu_count=${#GPU_ARRAY[@]}

export NCCL_P2P_DISABLE=1
export CUDA_LAUNCH_BLOCKING=1
export TORCH_USE_CUDA_DSA=1
export NCCL_BLOCKING_WAIT=1

while [ $CHECKPOINT -le $UPCONT ]
do
  echo "Running eval for checkpoint $CHECKPOINT"
  CUDA_VISIBLE_DEVICES=$gpu_seq torchrun --master_port=$PORT --nproc_per_node=$gpu_count -m LoraTrainer.eval_Multi \
      --do_eval True \
      --debug_mode False \
      --use_peft True \
      --prompt_pattern "$PROMPT_PATTERN" \
      --eval_pattern "$PATTERN" \
      --output_dir "./output_dir/DpoWeight/$Version/checkpoint-$CHECKPOINT/" \
      --data_path "./repairDataset/RepairData-PythonLevel/$DATA_FILE/" \
      --predict_filePath "./predict_dir/DpoWeight/$Version-GEN/$PATTERN-checkpoint-$CHECKPOINT.json" \
      --per_device_eval_batch_size $batch_size\
      --use_predict_crp "$use_predict_crp" \
      --CRPdata_path "$CRPdata_path"
  

  if [ $? -ne 0 ]; then
    echo "Error running eval for checkpoint $CHECKPOINT. Exiting."
    exit 1
  fi

  CHECKPOINT=$((CHECKPOINT + SAVE_STEPS))
done

echo "All evaluations completed."
