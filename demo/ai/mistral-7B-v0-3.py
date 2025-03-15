#=====================
#Transformers:
#======================
#NEEDS SENTENCEPIECE:
#   pip install sentencepiece
#NEEDS TRANSFORMERS:
#   pip install onnx onnxruntime transformers


from transformers import AutoModelForCausalLM, AutoTokenizer
local_model_path = "./models/Mistral-7B-Instruct-v0.3"
tokenizer = AutoTokenizer.from_pretrained(local_model_path, use_fast=True)

# model_id = "mistralai/Mistral-7B-v0.3"
# model = AutoModelForCausalLM.from_pretrained(local_model_path)

model = AutoModelForCausalLM.from_pretrained(local_model_path, attn_implementation="eager")
messages = [
    {"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"},
    {"role": "user", "content": "Who are you?"},
]

# template_string =""""
# {% for message in messages %})
#     {% if message['role'] == 'user' %}
#         {{  message['content'] }}
#     {% elif message['role'] == 'system' %}
#         {{ bos_token + message['content']}}
#     {% elif message['role'] == 'assistant' %}
#         {{ ' '  + message['content'] + ' ' }}
#     {% endif %}
# {% endfor %}
# """

template_string = """
{% for message in messages %}
    {% if message['role'] == 'user' %}
        {{ bos_token + '[INST] ' + message['content'] + ' [/INST]' }}
    {% elif message['role'] == 'system' %}
        {{ '<<SYS>>\\n' + message['content'] + '\\n<</SYS>>\\n\\n' }}
    {% elif message['role'] == 'assistant' %}
        {{ ' '  + message['content'] + ' ' + eos_token }}
    {% endif %}
{% endfor %}
"""

tokenizer.chat_template=template_string
prompt = tokenizer.apply_chat_template(messages,tokenize=False)
inputs = tokenizer(prompt, return_tensors="pt")

outputs = model.generate(**inputs, max_new_tokens=100,temperature=0.9)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))


exit(0)
#===================================================
#EXPORT TO ONNX
#====================================================

model.eval()

import torch

# Dummy input
# dummy_input = tokenizer("Hello my name is", return_tensors="pt").input_ids
#
# # Export the model
# torch.onnx.export(
#     model,                              # The model
#     (dummy_input,),                     # The input tuple
#     "mistral_model.onnx",               # The output ONNX file
#     input_names=["input_ids"],          # Input tensor name
#     output_names=["output"],            # Output tensor name
#     dynamic_axes={"input_ids": {0: "batch_size", 1: "sequence_length"},
#                   "output": {0: "batch_size", 1: "sequence_length"}},
#     opset_version=13                    # ONNX opset version
# )

#SOLUTION 2
dummy_input = tokenizer("Hello my name is", return_tensors="pt")
input_ids = dummy_input.input_ids
attention_mask = dummy_input.attention_mask

# Export the model with attention_mask
torch.onnx.export(
    model,
    (input_ids, attention_mask),  # Pass input_ids and attention_mask as a tuple
    "mistral_model.onnx",
    input_names=["input_ids", "attention_mask"],
    output_names=["output"],
    dynamic_axes={
        "input_ids": {0: "batch_size", 1: "sequence_length"},
        "attention_mask": {0: "batch_size", 1: "sequence_length"},
        "output": {0: "batch_size", 1: "sequence_length"}
    },
    opset_version=13
)

#SOLUTION 3
# Script the model
# scripted_model = torch.jit.script(model)
#
# # Export the scripted model to ONNX
# torch.onnx.export(
#     scripted_model,
#     (dummy_input.input_ids,),  # Provide only input_ids
#     "mistral_model.onnx",
#     input_names=["input_ids"],
#     output_names=["output"],
#     dynamic_axes={
#         "input_ids": {0: "batch_size", 1: "sequence_length"},
#         "output": {0: "batch_size", 1: "sequence_length"}
#     },
#     opset_version=13
# )



# #--------Test and run-----------
# import onnxruntime as ort
#
# session = ort.InferenceSession("mistral_model.onnx")
# input_name = session.get_inputs()[0].name
# output_name = session.get_outputs()[0].name
#
# # Convert input to ONNX-friendly format
# onnx_input = dummy_input.numpy()
#
# # Inference
# result = session.run([output_name], {input_name: onnx_input})
# print(result)

