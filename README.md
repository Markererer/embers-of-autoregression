


# Preproducing Embers of Autoregression

**Authors:** Mark Assejev, Bent Joke Heinks, Dimitar Kochev, Gabriel Ionescu

This repository was used to reproduce the Embers of Autoregression in Reasoning LLMs paper.  
[Original repository](https://github.com/tommccoy1/embers-of-autoregression.git)

The commands given in the rest of this README show how to run the tests for Qwen3.8 27B. We also explain how to generate the figures with our results below.

# Shift ciphers

## Example generation
- High-probability sentences: Created by `example_generation_scripts/sentences_high_probability.py`. Then used the top 100 after manually filtering to remove ones that:
    - Mentioned violence, death, or sex
    - Included proper names  (except for very common ones, such as names of countries)
    - Had grammatical errors
    - Were not complete sentences
- Medium-probability sentences: Created by `example_generation_scripts/sentences_medium_probability.py`. This generates 20 candidates; we manually selected the first (i.e., highest-perplexity) candidate that was grammatically correct (even if semantically odd). For a few sentences, we had to re-run the script to generate additional candidates because none of the 20 that were generated were grammatical; in some cases, we combined parts of two candidates in order to produce a grammatical sentence.
- Low-probability sentences: Created by `example_generation_scripts/sentences_low_probability.py`.
- Adversarial sentences: Copied the high-probability sentences into a new file, and then manually edited each line to replace a single word with another word that was grammatical but unlikely in that context. The new word was selected to be one that had a Levenshtein edit distance of either 1 or 2 from the word being replaced (where each edit could be a single-letter insertion, deletion, or substitution).

## Stimulus generation
- Done with `stimulus_generation_scripts/stimulus_generator_rot_encode.py`, `stimulus_generation_scripts/stimulus_generator_rot_decode.py`, `stimulus_generation_scripts/stimulus_generator_rot_prompts.py`, `stimulus_example_generator/stimulus_generator_shift.py`, and `stimulus_generator_shift_prompts.py`.

## Model testing
- Run these commands:
```
# Rot-13
python run_openai_locally.py --tasks rot13enc,rot13dec,rot12enc,rot12dec --conditions highprob,mediumprob,lowprob,adversarial --max_tokens 200  --model gpt-oss-20b

python run_ollama_qwen3_27b.py --tasks rot13enc,rot13dec,rot12enc,rot12dec --conditions highprob,mediumprob,lowprob,adversarial  


```


# Reversal task

## Example generation
- This task uses the same examples as the rot-13 task.

## Stimulus generation
- Done with `stimulus_generator_reverse_encode.py` and `stimulus_generator_reverse_decode.py`

## Model testing
- Run these commands:
```
python run_openai_locally.py --tasks revenc,revdec --conditions highprob,mediumprob,lowprob,adversarial --max_tokens 200 --model gpt-oss-20b

python run_ollama_qwen3_27b.py --tasks revenc,revdec --conditions highprob,mediumprob,lowprob,adversarial 

```

# Swapping task

## Example generation
- This sentences were generated in a similar way as the sentences for rot-13, except with the added restriction that each sentence had to contain at least one article (a, an, or the). Further, they could not have an article as the first or last word (since that could create issues when attempting to swap the article the adjacent word - in such cases there would be no adjacent word for one of the possible swapping directions).
```
python swap_high_probability.py
python swap_low_probability.py
python swap_medium_probability.py
python swap_next_prev.py
```

## Stimulus generation
- Done with `stimulus_generator_swap.py`

## Model testing
- Run these commands:

```
python run_openai_locally.py --tasks zeroshot_swap_next_base,zeroshot_swap_prev_base --conditions highprob,mediumprob,lowprob --max_tokens 200 --model gpt-oss-20b

python run_ollama_qwen3_27b.py --tasks zeroshot_swap_next_base,zeroshot_swap_prev_base --conditions highprob,mediumprob,lowprob 

```


# Pig Latin and Boar Etruscan tasks

## Example generation
- High-probability sentences: Created by `example_generation_scripts/piglatin_high_probability.py`. The results were then manually filtered for the same criteria as the Rot-13 sentences, as well as the criteria specified below about initial consonant clusters; we then used the first 100 (i.e., 100 lowest perplexity) remaining examples.
- Medium-probability sentences: Created by `example_generation_scripts/piglatin_medium_probability.py`, using the same basic approach as the medium-probability sentences for rot-13.
- Adversarial sentences: Created in the same way as the rot-13 adversarial sentences.
- Low-probability sentences: Created by `example_generation_scripts/piglatin_low_probability.py`.
- Pig Latin is primarily a spoken game. Since English spelling often differs from pronuncation, this means that the Pig Latin treatment of many written words is ambiguous. E.g., should "union" become "unionay" or "unionyay"? Should "hour" become "houray" or "ourhay"? To check for such cases, we excluded words whose first written consonant cluster did not parallel their first spoken consonant cluster. In addition, for each word whose first vowel was [u], we checked the word's British pronunciation in the online Cambridge dictionary (https://dictionary.cambridge.org/) to see if it was pronounced with an unwritten /j/ (e.g., "new" is pronounced /nju/); if so, we excluded it. Checking for such words was done with the aid of the CMU pronouncing dictionary. To replicate this checking:
```
wget https://raw.githubusercontent.com/Alexir/CMUdict/master/cmudict-0.7b
mv cmudict-0.7b cmudict.txt
python piglatin_consonant_check.py
```

## Stimulus generation
- Done with `stimulus_generation_scripts/stimulus_generator_piglatin_encode.py` and `stimulus_generation_scripts/stimulus_generator_piglatin_decode.py`

## Model testing
- Run these commands:
```
python run_openai_locally.py --tasks pigenc_ay,pigdec_ay,pigenc_uv,pigdec_uv --conditions highprob,mediumprob,lowprob,adversarial --max_tokens 200 --model gpt-oss-20b

python run_ollama_qwen3_27b.py --tasks pigenc_ay,pigdec_ay,pigenc_uv,pigdec_uv --conditions highprob,mediumprob,lowprob,adversarial 

```


# Acronym task

## Example generation
- First, produce candidate word lists. This was done as follows:
```
# Download wikitext-103
wget https://s3.amazonaws.com/research.metamind.io/wikitext/wikitext-103-v1.zip
unzip wikitext-103-v1.zip

# Download CMU Pronouncing Dictionary
wget https://raw.githubusercontent.com/Alexir/CMUdict/master/cmudict-0.7b
mv cmudict-0.7b cmudict.txt

# Find all words that appear in the CMU Pronouncing Dictionary that are 2 tokens long 
# in uppercase (whether or not there is a space before them), and similarly for 
# lowercase; this produces one file for uppercase and one for lowercase, 
# both sorted by the probability assigned to them by GPT-2.
cd example_generation_scripts
python probability_cmu.py

# We then manually removed any words in the lists that included profanity
```

- Then, generate acronyms using `example_generation_scripts/acronym.py`. This controls for split points: that is, for a given line index, all generated acronym files will have at that index an output word that has the same split point as all other files do, and each input word will have the same split point as the input words at the same position in all other files. The split point is the index where the first subword token ends.
- To check that the inputs and outputs match, and that the break points are correctly controlled for, we ran `python acronym_check.py` in `example_generation_scripts/
- A note about the filenames: "1" means highest probability, "5" means lowest. Each file has a 2-digit tag indicating first the output probability then the input probability. E.g., `acronym1_51` means very low-probability outputs and very high-probability inputs.

## Stimulus generation
- Done with `stimulus_generation_scripts/stimulus_generator_acronym.py`

## Model testing
- Run these commands:
```
python run_openai_locally.py --tasks acronym1 --conditions 11  --max_tokens 100 --model gpt-oss-20b
python run_openai_locally.py --tasks acronym2 --conditions 11  --max_tokens 100 --model gpt-oss-20b

python run_ollama_qwen3_27b.py --tasks acronym1 --conditions 11 
python run_ollama_qwen3_27b.py --tasks acronym2 --conditions 11 
```

# Conversion task

## Names for conditions
This code repository uses names for the conditions that differ somewhat from how we discuss them in the paper. Here is a guide to the terms used in the codebase:
- The function (9/5)x+32 is referred to as `actual`, while (7/5)x+31 is referred to as `fake`.
- The default setting is to control the inputs across functions. When we instead control the outputs, it is referred to as `inverse`. In some files, this distinction is referred to as `fwd` (the default setting) vs.\ `rev` (the inverse setting).
- The case where the inputs are sampled uniformly from the integers 0 to 999 is referred to as `conversion`, while the case where the inputs are constrained to be greater than 500 and not divisible by 10 is referred to as `conversion_ood`.


## Example generation
- Done with `example_generation_scripts/celsius.py`. This generates two pairs:
    - `conversion_actual.txt` and `conversion_fake.txt` use the same inputs for the two task versions, but different outputs.
    - `conversion_actualinverse.txt` and `conversion_fakeinverse.txt` use the same outputs (after rounding) for the two task versions, but different inputs.
- And then we also ran `example_generation_scripts/celsius_ood.py`, which similarly generates two pairs but labeled `conversion_ood` instead of `conversion`.


## Stimulus generation
- Done with `stimulus_generation_scripts/stimulus_generator_conversion.py` and `stimulus_generation_scripts/stimulus_generator_conversion_ood.py`. This generates stimuli for the above pairs, as well as a `primed` and `primedcontrol` versions of `actual`, both of which are the same as `actual` but with either a mention of Fahrenheit and Celsius in the prompt (`primed`) or a neutral extra sentence in the prompt (`primedcontrol`).

## Model testing
- Run these commands:
```
python run_openai_locally.py --tasks conversion --conditions actual,actualinverse,actualprimed,actualprimedcontrol,fake,fakeinverse --max_tokens 100 --model gpt-oss-20b
python run_openai_locally.py --tasks conversion_ood --conditions actual,actualinverse,actualprimed,actualprimedcontrol,fake,fakeinverse --max_tokens 100 --model gpt-oss-20b

python run_ollama_qwen3_27b.py --tasks conversion --conditions actual,actualinverse,actualprimed,actualprimedcontrol,fake,fakeinverse 
python run_ollama_qwen3_27b.py --tasks conversion_ood --conditions actual,actualinverse,actualprimed,actualprimedcontrol,fake,fakeinverse
```


# Sorting tasks

## Example generation
- For sorting words: The length of the list had to be from 10 to 20 inclusive. There could not be any repeats. The words were selected randomly (without replacement) from the set of common words used for the counting task.
- For sorting numbers: The length of the list had to be from 10 to 20 inclusive. There could not be any repeats. The numbers were selected randomly (without replacement) from the set of integers from 1 to 10,000 inclusive.

```
python sort_words.py
python sort_numbers.py 
```

## Stimulus generation
- Done with `stimulus_generation_scripts/python stimulus_generator_sorting.py` and `stimulus_generation_scripts/stimulus_generator_sortingnumbers.py`

## Model testing
- Run these commands:
```
python run_openai_locally.py --tasks sorting --conditions fwd,rev,ascending,descending --max_tokens 200 --model gpt-oss-20b

python run_ollama_qwen3_27b.py --tasks sorting --conditions fwd,rev,ascending,descending
```

# Generating the graphs
For generating the graphs, the scripts graph.py and rare_vs_common_graph.py need to be ran. They take the data from the viz_data directory.

In order to run the files on any desired JSON file, the following lines in them must be modified, as they are hard-coded.

## graphs.py

To use this script, first modify the constants referring to the directory paths for saving and utilizing the files you want.
```
DATA_DIR = "viz_data/logs_ollama" #directory where the data to be used it
OUTPUT_DIR = "graphs" #directory where the graphs will be saved
OUT_NAME = "Qwen3.8-27B_graphs" #name of the graph generated
```
Additionally, there are a few optional parameters that were hard-coded as part of the limitations of reproducing the original research, used to accommodate our naming conventions. They can be deleted or reused depending on other naming conventions.
```
SUFFIX = "n=1.json" #optional addition to the path to accommodate name convention
COND = {"low": "lowprob", "medium": "mediumprob", "high": "highprob"} #optional addition to the path to accommodate name convention

#Construction of the file path to use for graphs
def levels(prefix):
    """Paths for the three probability levels of one task/variant and model."""
    return {lvl: os.path.join(DATA_DIR, f"{prefix}_{cond}_{SUFFIX}")
            for lvl, cond in COND.items()}
```
The graph computed by the script is a collage of different graphs, in order to show the performance across all different tasks that were tested. Each task is represented by a panel in the graph. Each panel must be manually added in the following way, subsequent panels repeating the pattern.
``` 
PANELS = [
    #This represents one graph / panel inside the graph collage
    dict(title="Shift cipher enc (rot-12)", logprob="rot", runs={
        "Qwen3.8-27B": levels("rot12enc", "Qwen3.8-27B"), #"Qwen3.8-27B": represents the name that will appear on the legend for what model is being plotted
    }),
    #This represents a second graph / panel inside the graph collage
    dict(title="Shift cipher dec (rot-12)", logprob="rot", runs={
        "Qwen3.8-27B": levels("rot12dec", "Qwen3.8-27B"),
    }),
]
```
There is another hard codded element into the previous code, which is the x axis of the panels. It represents the log probability of the tasks that were being tested, and the original work does not provide a computation method for them, so we hard coded them in a similar fashion. If needed, these should be changed to accommodate the graphs being generated. Ideally, they should not be hard coded like we did.
```
# x-axes for each task
STIMULUS_LOGPROB = {
    "rot":      {"low": -144.54, "medium": -86.25, "high": -58.38}, 
    "pig":      {"low": -132.26, "medium": -86.86, "high": -62.54},
    "reversal": {"low": -144.54, "medium": -86.25, "high": -58.38},
    "swap":     {"low": -161.4,  "medium": -101.7, "high": -68.4},
}
```
## rare_vs_common_graph.py

