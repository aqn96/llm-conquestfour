#INSTALLS:
#pip install sentencepiece blobfile torch tensorflow
# can only use numpy 1.x.x
# can only use python 3.1 and below

import onnx
import onnxruntime as ort
from transformers import AutoTokenizer
import numpy as np
import torch
from torch.nn.functional import softmax


model_path = "./models/mistral-7b-Instruct-v0.2-kvc-AWQ-int4-onnx"
model_file = model_path + "/model.onnx"
model = onnx.load(model_file)

# template_string = """
# {% for message in messages %}
#     {% if message['role'] == 'user' %}
#         {{ bos_token + '[INST] ' + message['content'] + ' [/INST]' }}
#     {% elif message['role'] == 'system' %}
#         {{ '<<SYS>>\\n' + message['content'] + '\\n<</SYS>>\\n\\n' }}
#     {% elif message['role'] == 'assistant' %}
#         {{ ' '  + message['content'] + ' ' + eos_token }}
#     {% endif %}
# {% endfor %}
# """

template_string =""""
{% for message in messages %})
    {% if message['role'] == 'user' %}
        {{  message['content'] }}
    {% elif message['role'] == 'system' %}
        {{ bos_token + message['content']}}
    {% elif message['role'] == 'assistant' %}
        {{ ' '  + message['content'] + ' ' }}
    {% endif %}
{% endfor %}
"""

# messages = [
#     {"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"},
#     {"role": "user", "content": "Who are you?"},
# ]

messages = [
    {"role": "user", "content": "You are a pirate chatbot\n who responds in pirate speak!"},
]
# Function to apply top-p (nucleus) sampling (Was used for a different model, left here for reference)
def top_p_sampling(logits, top_p=0.9):

    #Sort the logits, and keep track of their original location with indices::
    sorted_logits, sorted_indices = torch.sort(logits, descending=True)

    #Use softmax to create a probability tensor
    cumulative_probs = torch.cumsum(torch.nn.functional.softmax(sorted_logits, dim=-1), dim=-1)

    #create a new tensor in same shape with true or false values to know what to remove:
    sorted_indices_to_remove = cumulative_probs > top_p

    #Keep the highest logit and place in beginning of tensor
    sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()

    #Set the highest logit boolean to false ensuring we keep it
    sorted_indices_to_remove[..., 0] = 0


    for batch_idx in range(sorted_indices.size(0)):
        logits[batch_idx, sorted_indices[batch_idx][sorted_indices_to_remove[batch_idx]]] = -float('Inf')
    return logits

#=========================================================================================
def main():
    #Number of tokens must be at least this (chunk size):
    window = 16
    max_gen_tokens = 80  # number of tokens we want to generate
    total_sequence = 512  # total sequence_length
    context = 1024

    tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=True)
    sess = ort.InferenceSession(model_file)

    #Format the input prompt:
    # tokenizer.chat_template = template_string
    # prompt = tokenizer.apply_chat_template(messages, tokenize=False)
    prompt = "You are a war general who always responds aggressively!"
    print(f"\nSending to model: {prompt}\n\n")


    input_tensor = tokenizer(prompt, return_tensors="pt")
    prompt_size = len(input_tensor['input_ids'][0])
    actual_input = input_tensor['input_ids']

    #Create padding for tokens if too small:
    if prompt_size < window:
        actual_input = np.concatenate((tokenizer.bos_token_id * np.ones([1, window - prompt_size], dtype='int64'),
                                       actual_input), axis=1)

    #Keep prompt within limit
    if prompt_size + max_gen_tokens > total_sequence:
        print("ERROR: Longer total sequence is needed!")
        return

    #Create an attention mask (String of 1s and 0s to know which part of the text to pay attention to)
    first_attention = np.concatenate(
        (np.zeros([1, total_sequence - window], dtype='int64'),np.ones((1, window), dtype='int64')), axis=1
        )

    #Set up parameters of our input:
    max_gen_tokens += prompt_size #we need to generate on top of parsing the prompt
    inputs_names =[node.name for node in model.graph.input]
    output_names =[node.name for node in model.graph.output]
    n_heads = 8 #gqa-heads of the kvc (number of inputs for this model)


    inputs_dict = {}
    inputs_dict['input_ids'] = actual_input[:, :window].reshape(1, window) #.numpy()
    inputs_dict['attention_mask'] = first_attention
    index_pos = sum(first_attention[0])

    inputs_dict['position_ids'] = np.concatenate(
        (np.zeros([1, total_sequence - index_pos], dtype='int64'),np.arange(index_pos, dtype='int64').reshape(1, index_pos)),
        axis=1
    )
    inputs_dict['tree_attention'] = (
        np.triu(-65504 * np.ones(total_sequence), k=1).astype('float16').reshape(1, 1, total_sequence,total_sequence))

    for name in inputs_names:
        if name == 'input_ids' or name == 'attention_mask' or name == 'position_ids' or name == 'tree_attention': continue
        inputs_dict[name] = np.zeros([1, n_heads, context - window, 128], dtype="float16")

    index = 0
    new_token = np.array([10])
    next_index = window
    old_j = 0
    total_input = actual_input
    print(f"\n\nAvailable Runtimes: {ort.get_available_providers()}\n\n")
    rt_session = ort.InferenceSession(model_file, providers=['CUDAExecutionProvider', 'CPUExecutionProvider']) #Our ONNX inference

    #Generating loop:
    while next_index < max_gen_tokens:
        if new_token.any() == tokenizer.eos_token_id:
            break
        # inference
        output = rt_session.run(output_names, inputs_dict)
        outs_dictionary = {name: content for (name, content) in zip(output_names, output)}


        # we prepare the inputs for the next inference
        for name in inputs_names:
            if name == 'input_ids':
                old_j = next_index
                if next_index < prompt_size:
                    if prompt_size - next_index >= window:
                        next_index += window
                    else:
                        next_index = prompt_size
                    j = next_index - window
                else:
                    next_index += 1
                    j = next_index - window
                    #---------------------------------------------------------------------


                    new_token = outs_dictionary['logits'].argmax(-1).reshape(1, window)
                    #------------------------------------------------------------------
                    total_input = np.concatenate((total_input, new_token[:, -1:]), axis=1)

                inputs_dict['input_ids'] = total_input[:, j:next_index].reshape(1, window)

            elif name == 'attention_mask':
                inputs_dict['attention_mask'] = np.concatenate(
                    (np.zeros((1, total_sequence - next_index), dtype='int64'), np.ones((1, next_index), dtype='int64')),
                    axis=1)
            elif name == 'position_ids':
                inputs_dict['position_ids'] = np.concatenate((np.zeros([1, total_sequence - next_index], dtype='int64'),
                                                              np.arange(next_index, dtype='int64').reshape(1, next_index)),
                                                             axis=1)
            elif name == 'tree_attention':
                continue
            else:
                old_name = name.replace("past_key_values", "present")
                inputs_dict[name] = outs_dictionary[old_name][:, :,
                                    next_index - old_j:context - window + (next_index - old_j), :]

    answer = tokenizer.decode(total_input[0], skip_special_tokens=True, clean_up_tokenization_spaces=False)
    print(answer)


    return
    # #Get the output and input information from the model
    # outputs = sess.get_outputs()
    # inputs = sess.get_inputs()
    #
    # #Take the outputs/inputs and get all their names:
    # output_names = [output.name for output in outputs]
    # input_names = [input.name for input in inputs]
    #
    # #Pass in output names, and a dictionary with input names as key and ids as value.
    # #Use numpy because ONNX requires numpy
    # tensor_output = sess.run(output_names,{input_names[0]: input_ids['input_ids'].numpy()})
    #
    # # Decode the model's output
    # result = tokenizer.decode(tensor_output[0], skip_special_tokens=True)
    # print(result)


if __name__ == "__main__":
    main()

def referenc_texts():
    pass
    # input_tokens = tokenizer.tokenize(input_text, add_special_tokens=False)