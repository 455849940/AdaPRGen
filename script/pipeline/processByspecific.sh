#!/bin/bash


PATTERN="test"
DATA_FILE="CRFLPDataset"
gpu_seq=0,1,2,3
PORT=55000
batch_size=1
PROMPT_PATTERN="fixbycrflp"
SECOND_PROMPT_PATTERN="fixbycrflp2"
SECOND_CHECKPOINT=12000
CRPdata_path="./predict_dir/Chatgpt/proposal_trace_gpt4o-0.7-v2prompt.json"
predict_filePath="./predict_dir/Chatgpt/proposal_trace_gpt4o-0.7-v2prompt_Fix2_12k_gen.json"
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
    --output_dir "./output_dir/loraWeight/$SECOND_PROMPT_PATTERN/checkpoint-$SECOND_CHECKPOINT/" \
    --data_path "./repairDataset/RepairData-PythonLevel/$DATA_FILE/" \
    --predict_filePath "$predict_filePath" \
    --per_device_eval_batch_size $batch_size \
    --CRPdata_path "$CRPdata_path"\
    --use_predict_crp True
      
echo "All evaluations completed."
