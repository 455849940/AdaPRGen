export NCCL_P2P_DISABLE=1
export CUDA_LAUNCH_BLOCKING=1
export TORCH_USE_CUDA_DSA=1
CUDA_VISIBLE_DEVICES=4,5,6,7 torchrun --master_port=60000 --nproc_per_node 4 -m LoraTrainer.train \
    --do_train True \
    --do_eval True \
    --debug_mode False\
    --bf16 True \
    --prompt_pattern "trace_normal_base" \
    --output_dir "./output_dir/loraWeight/trace_normal_base/" \
    --resume True\
    --num_train_epochs 12 \
    --per_device_train_batch_size 4 \
    --per_device_eval_batch_size 4 \
    --save_steps 2000 \
    --eval_steps 40000 \
    --logging_steps 50 \
    --data_path "./repairDataset/RepairData-PythonLevel/traceDataset/" \
    --deepspeed configs/default_offload_opt_param-o.json \
    --save_safetensors False \
    --evaluation_strategy steps\
    --save_strategy steps \
    --remove_unused_columns False 
