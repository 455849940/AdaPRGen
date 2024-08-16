#!/bin/bash

begin_iterations=2000
end_iterations=30000
PORT=61200
DEVPORT=$((PORT + 10))
gpu_seq=4,5,6,7
gpu_seq2eval=4,5,6,7
gpu_seq2test=4,5,6,7
PATTERN="dev" 
SAVE_STEPS=2000
eval_steps=6000
PROMPT_PATTERN="CRFLP"
SECOND_PROMPT_PATTERN="fixbycrflp"
second_checkpoint=8000
DATA_FILE="CRFLPDataset"
resume=False
num_train_epochs=10
train_batch_size=4
eval_batch_size=3
test_batch_size=1
newloss_pattern=False
debug_mode=False

IFS=',' read -ra GPU_ARRAY <<< "$gpu_seq"
gpu_count=${#GPU_ARRAY[@]}


echo ">>>start Train"
bash ./script/pipeline/part/train.sh "$gpu_seq" "$PROMPT_PATTERN" "$DATA_FILE" "$PORT" "$gpu_count" "$resume" "$num_train_epochs" "$newloss_pattern" "$debug_mode" "$eval_steps" "$train_batch_size"

file_path="./predict_dir/loraWeight/$PROMPT_PATTERN"

if [ -e "$file_path" ]; then
    echo "file $file_path exist"
else
    echo "catalogue $file_path not exist, create it"
    mkdir -p "$file_path"
fi

echo ">>>start Eval DEV to gengeration"
bash ./script/pipeline/part/recyle_eval.sh "$end_iterations" "$PATTERN" "$begin_iterations" "$SAVE_STEPS" "$PROMPT_PATTERN" "$DATA_FILE" "$gpu_seq2eval" "$DEVPORT" "$eval_batch_size"


file_path="./predict_dir/loraWeight/$PROMPT_PATTERN-GEN"
if [ -e "$file_path" ]; then
    echo "file $file_path exist"
else
    echo "catalogue $file_path not exist, create it"
    mkdir -p "$file_path"
fi

echo ">>>start eval dev to fix buggy code by fixModel"
bash ./script/pipeline/part/recyle_choseCRP.sh "$end_iterations" "$PATTERN" "$begin_iterations" "$SAVE_STEPS" "$PROMPT_PATTERN" "$DATA_FILE" "$gpu_seq2eval" "$DEVPORT" "$eval_batch_size" \
"$SECOND_PROMPT_PATTERN" "$second_checkpoint"


file_path="./predict_evalResult_dir/$PROMPT_PATTERN-GEN"

if [ -e "$file_path" ]; then
    echo "file $file_path exist"
else
    echo "catalogue $file_path not exist, create it"
    mkdir -p "$file_path"
fi
echo ">>>start Execution" 
bash ./script/pipeline/part/recyle_Execution.sh "$end_iterations" "$PATTERN" "$begin_iterations" "$SAVE_STEPS" "$PROMPT_PATTERN-GEN"


max_rate=0.0
best_iteration=0
echo ">>>start choose best dev rate value"

for ((i=begin_iterations; i<=end_iterations; i+=SAVE_STEPS)); do
    output=$(bash ./script/pipeline/part/Statistical_Execution_Results.sh "$PROMPT_PATTERN-GEN" "$PATTERN" "$i")
    echo "$output"
    avg_improve_rate=$(echo "$output" | grep 'avg_improve_rate = ' | awk '{print $3}')

    if [ -z "$avg_improve_rate" ]; then
        echo "Failed to extract rate for iteration $i"
        continue
    fi

    if (( $(echo "$avg_improve_rate > $max_rate" | bc -l) )); then
       max_rate=$avg_improve_rate
       best_iteration=$i
    fi
done


echo ">>>start Eval TEST to gengeration  $best_iteration"
bash ./script/pipeline/part/recyle_eval.sh "$best_iteration" "test" "$best_iteration" "$SAVE_STEPS" "$PROMPT_PATTERN" "$DATA_FILE" "$gpu_seq2test" "$DEVPORT" "$test_batch_size"
bash ./script/pipeline/part/recyle_choseCRP.sh "$best_iteration" "test" "$best_iteration" "$SAVE_STEPS" "$PROMPT_PATTERN" "$DATA_FILE" "$gpu_seq2test" "$DEVPORT" "$test_batch_size" \
"$SECOND_PROMPT_PATTERN" "$second_checkpoint"
echo ">>>start Execution For TESt" 
bash ./script/pipeline/part/recyle_Execution.sh "$best_iteration" "test" "$best_iteration" "$SAVE_STEPS" "$PROMPT_PATTERN-GEN"
echo ">>>start Statistic Execution Result For TEST"
bash ./script/pipeline/part/Statistical_Execution_Results.sh "$PROMPT_PATTERN-GEN" "test" "$best_iteration"