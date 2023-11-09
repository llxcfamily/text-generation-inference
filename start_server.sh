MODEL_PATH=models/vicuna-7b-v1.5/
CUDA_VISIBLE_DEVICES=0, text-generation-launcher --model-id ${MODEL_PATH} \
--sharded false \
--max-batch-prefill-tokens 2048 \
--dtype float16 -p 5000 > log.info 2>&1 &
