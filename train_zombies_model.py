import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel, GPT2Config
from transformers import Trainer, TrainingArguments
import json
from datasets import Dataset
import pandas as pd

def train_model():
    print("Loading data...")
    # Load the training data
    with open('zombies_dataset_training_[TIMESTAMP].json', 'r', encoding='utf-8') as f:
        training_data = json.load(f)
    
    print("Initializing model...")
    # Initialize model and tokenizer
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    model = GPT2LMHeadModel.from_pretrained('gpt2')
    
    # Add special tokens
    special_tokens = {
        'pad_token': '<pad>',
        'sep_token': '<sep>',
        'additional_special_tokens': ['<map>', '<weapon>', '<perk>', '<location>']
    }
    tokenizer.add_special_tokens(special_tokens)
    model.resize_token_embeddings(len(tokenizer))
    
    print("Preparing dataset...")
    # Convert to DataFrame and then to Dataset
    df = pd.DataFrame(training_data)
    dataset = Dataset.from_pandas(df)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir="./zombies_model",
        num_train_epochs=5,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
        save_steps=500,
        eval_steps=100,
        evaluation_strategy="steps",
        load_best_model_at_end=True,
    )
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset.shuffle().select(range(int(len(dataset) * 0.8))),
        eval_dataset=dataset.shuffle().select(range(int(len(dataset) * 0.2))),
    )
    
    print("Starting training...")
    trainer.train()
    
    print("Saving model...")
    model.save_pretrained('./zombies_model_final')
    tokenizer.save_pretrained('./zombies_model_final')
    print("Training completed!")

if __name__ == "__main__":
    train_model() 