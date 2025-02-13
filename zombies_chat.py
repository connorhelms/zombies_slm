from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import json

class ZombiesBot:
    def __init__(self):
        print("Initializing Zombies Bot...")
        self.tokenizer = GPT2Tokenizer.from_pretrained('./zombies_model_final')
        self.model = GPT2LMHeadModel.from_pretrained('./zombies_model_final')
        self.model.eval()
        
        # Load structured data for reference
        with open('zombies_dataset_structured_[TIMESTAMP].json', 'r', encoding='utf-8') as f:
            self.knowledge_base = json.load(f)
    
    def generate_response(self, prompt, max_length=200):
        # Prepare input
        inputs = self.tokenizer.encode(prompt + self.tokenizer.sep_token, return_tensors='pt')
        
        # Generate response
        outputs = self.model.generate(
            inputs,
            max_length=max_length,
            num_return_sequences=1,
            temperature=0.7,
            top_k=50,
            top_p=0.95,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
            no_repeat_ngram_size=3
        )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Clean up response
        response = response.replace(prompt, '').strip()
        return response
    
    def get_specific_info(self, query_type, name):
        """Get specific information from knowledge base"""
        if query_type in self.knowledge_base:
            if name in self.knowledge_base[query_type]:
                return self.knowledge_base[query_type][name]
        return None

def main():
    print("Loading Zombies Bot...")
    bot = ZombiesBot()
    print("\nZombies Bot initialized! Ask me anything about Call of Duty Black Ops 2 Zombies!")
    print("Type 'quit' to exit")
    
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye!")
            break
        
        response = bot.generate_response(user_input)
        print(f"\nBot: {response}")

if __name__ == "__main__":
    main() 