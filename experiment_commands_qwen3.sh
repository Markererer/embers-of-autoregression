# Shift ciphers - encode + decode

python run_ollama_qwen3_27b.py --tasks rot13enc,rot13dec,rot12enc,rot12dec --conditions highprob,mediumprob,lowprob,adversarial  

# Reversal task 

python run_ollama_qwen3_27b.py --tasks revenc,revdec --conditions highprob,mediumprob,lowprob,adversarial 

#Sorting a list / Keyboard cipher task

python run_ollama_qwen3_27b.py --tasks sorting --conditions fwd,rev,ascending,descending

# Pig Latin - encode + decode

python run_ollama_qwen3_27b.py --tasks pigenc_ay,pigdec_ay,pigenc_uv,pigdec_uv --conditions highprob,mediumprob,lowprob,adversarial 

# Swapping task / article swapping task

python run_ollama_qwen3_27b.py --tasks zeroshot_swap_next_base,zeroshot_swap_prev_base --conditions highprob,mediumprob,lowprob 

# Forming Acronym task

python run_ollama_qwen3_27b.py --tasks acronym1 --conditions 11 
python run_ollama_qwen3_27b.py --tasks acronym2 --conditions 11 

# Applying a linear function

python run_ollama_qwen3_27b.py --tasks conversion --conditions actual,actualinverse,actualprimed,actualprimedcontrol,fake,fakeinverse 
python run_ollama_qwen3_27b.py --tasks conversion_ood --conditions actual,actualinverse,actualprimed,actualprimedcontrol,fake,fakeinverse