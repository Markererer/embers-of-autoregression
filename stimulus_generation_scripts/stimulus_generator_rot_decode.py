
import jsonlines


# Functions for encoding in rot-12 or rot-13
alphabet = "abcdefghijklmnopqrstuvwxyz"
rot12 = {}
rot13 = {}
for index, char in enumerate(alphabet):
    rot12[char] = alphabet[(index+12)%26]
    rot13[char] = alphabet[(index+13)%26]

def rot12_encode(sequence):
    new_sequence = []
    for char in sequence:
        if not char.isalpha():
            new_sequence.append(char)
        elif char.isupper():
            new_sequence.append(rot12[char.lower()].upper())
        else:
            new_sequence.append(rot12[char])

    return "".join(new_sequence)

def rot13_encode(sequence):
    new_sequence = []
    for char in sequence:
        if not char.isalpha():
            new_sequence.append(char)
        elif char.isupper():
            new_sequence.append(rot13[char.lower()].upper())
        else:
            new_sequence.append(rot13[char])

    return "".join(new_sequence)


print(rot12_encode("stay"))
print(rot13_encode("stay"))

for fi_name, fo_name in [("../examples/sentences_high_probability.txt", "../stimuli/rot12dec_highprob.jsonl"), ("../examples/sentences_medium_probability.txt", "../stimuli/rot12dec_mediumprob.jsonl"), ("../examples/sentences_adversarial.txt", "../stimuli/rot12dec_adversarial.jsonl"), ("../examples/sentences_low_probability.txt", "../stimuli/rot12dec_lowprob.jsonl")]:
    
    fi = open(fi_name, "r")
    fo12 = open(fo_name, "w")
    jsl12 = jsonlines.Writer(fo12)
    fo13 = open(fo_name.replace("rot12", "rot13"), "w")
    jsl13 = jsonlines.Writer(fo13)

    count_encoded = 0
    for line in fi:
        example12 = {}
        example13 = {}

        # Task
        example12["task_name"] = "rot12"
        example13["task_name"] = "rot13"

        # Condition
        example_type = fo_name.split("_")[1].split(".")[0]
        example12["example_type"] = example_type
        example13["example_type"] = example_type


        sentence = line.strip()
        encoded12 = rot12_encode(sentence)
        encoded13 = rot13_encode(sentence)

        
        # Instruction
        example12["task_instruction"] = 'Rot-12 is a cipher in which each letter is shifted 12 positions forward in the alphabet. For example, here is a message written in rot-12 along with the original text that it was created from:\nRot-12 text: "Efmk tqdq!"\nOriginal text: "Stay here!"\n\nHere is another message in rot-12. Decode this message to produce the original text:\nRot-12 text: "%s"\nOriginal text:'
        example13["task_instruction"] = 'Rot-13 is a cipher in which each letter is shifted 13 positions forward in the alphabet. For example, here is a message written in rot-13 along with the original text that it was created from:\nRot-13 text: "Fgnl urer!"\nOriginal text: "Stay here!"\n\nHere is another message in rot-13. Decode this message to produce the original text:\nRot-13 text: "%s"\nOriginal text:'

        # Input
        example12["input"] = encoded12
        example13["input"] = encoded13

        # Combining the instruction and input (this is the string that should be given to the model)
        example12["instruction_plus_input"] = example12["task_instruction"] % example12["input"]
        example13["instruction_plus_input"] = example13["task_instruction"] % example13["input"]

        # The correct output
        example12["correct_output"] = sentence
        example13["correct_output"] = sentence


        jsl12.write(example12)
        jsl13.write(example13)
        

        count_encoded += 1
        if count_encoded == 100:
            break


    





