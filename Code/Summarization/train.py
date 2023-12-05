import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration, Trainer, TrainingArguments
from datasets import load_metric
from datasets import load_dataset

data = load_dataset("lighteval/legal_summarization", "BillSum")

print(data.items())

def show_samples(dataset, num_samples=3, seed=42):
    sample = dataset['train'].shuffle(seed=seed).select(range(num_samples))
    for example in sample:
        print(f"\n'>> Article: {example['article']}'")
        print(f"'>> Summary: {example['summary']}'")

show_samples(data)

# Load the model and tokenizer
model_name = "t5-base"
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

# Tokenize the dataset
def tokenize_function(examples):
    inputs = tokenizer(examples["article"], max_length=512, truncation=True, padding="max_length", return_tensors="pt")
    targets = tokenizer(examples["summary"], max_length=150, truncation=True, padding="max_length", return_tensors="pt")

    # Ensure decoder_input_ids are used during training
    inputs["decoder_input_ids"] = targets["input_ids"]
    inputs["labels"] = targets["input_ids"].clone()

    return inputs

tokenized_datasets = data.map(tokenize_function, batched=True)

# Define the training arguments
training_args = TrainingArguments(
    output_dir="./legal_summarization",
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    gradient_accumulation_steps=4,
    save_steps=1000,
    evaluation_strategy="steps",
    eval_steps=500,
    save_total_limit=2,
    num_train_epochs=3
)