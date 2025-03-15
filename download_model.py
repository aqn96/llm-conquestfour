from transformers import AutoTokenizer, AutoModelForCausalLM
import os

# Define the model name and paths
model_name = 'mistralai/Mistral-7B-v0.1'
save_path = os.path.expanduser('~/models/mistral-7b')

print(f"Downloading optimized Mistral 7B model to {save_path}...")

# Download and save the tokenizer
print("Downloading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.save_pretrained(save_path)
print("Tokenizer downloaded and saved.")

# Download and save the model with float16 precision (more efficient than full precision)
# but without using bitsandbytes (which is problematic on macOS)
print("Downloading model (this may take a while)...")
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="float16",  # Use half precision
    device_map="auto",      # Let the model decide where to put things
    low_cpu_mem_usage=True  # More efficient loading
)
model.save_pretrained(save_path)
print("Model downloaded and saved successfully!")
print(f"Model is ready at: {save_path}")
