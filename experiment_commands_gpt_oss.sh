# Shift ciphers - encode + decode

python run_openai_locally.py --tasks rot13enc,rot13dec,rot12enc,rot12dec --conditions highprob,mediumprob,lowprob,adversarial --max_tokens 200  --model gpt-oss-20b

# Reversal task 

python run_openai_locally.py --tasks revenc,revdec --conditions highprob,mediumprob,lowprob,adversarial --max_tokens 200 --model gpt-oss-20b

#Sorting a list / Keyboard cipher task

python run_openai_locally.py --tasks keyboardcot,keyboardcotreference,keyboardcotdetailed --conditions highprob --max_tokens 4000 --model gpt-oss-20b

# Pig Latin - encode + decode

python run_openai_locally.py --tasks pigenc_ay,pigdec_ay,pigenc_uv,pigdec_uv --conditions highprob,mediumprob,lowprob,adversarial --max_tokens 200 --model gpt-oss-20b

# Swapping task / article swapping task

python run_openai_locally.py --tasks zeroshot_swap_next_base,zeroshot_swap_prev_base --conditions highprob,mediumprob,lowprob --max_tokens 200 --model gpt-oss-20b

# Forming Acronym task

python run_openai_locally.py --tasks acronym1 --conditions 11  --max_tokens 100 --model gpt-oss-20b
python run_openai_locally.py --tasks acronym2 --conditions 11  --max_tokens 100 --model gpt-oss-20b

# Applying a linear function

python run_openai_locally.py --tasks conversion --conditions actual,actualinverse,actualprimed,actualprimedcontrol,fake,fakeinverse --max_tokens 100 --model gpt-oss-20b
python run_openai_locally.py --tasks conversion_ood --conditions actual,actualinverse,actualprimed,actualprimedcontrol,fake,fakeinverse --max_tokens 100 --model gpt-oss-20b