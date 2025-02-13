# Call of Duty Black Ops 2 Zombies AI

A specialized language model trained to know everything about Call of Duty Black Ops 2 Zombies. This AI can answer questions about maps, weapons, easter eggs, and strategies.

## Table of Contents
- [Setup](#setup)
  - [Environment Setup](#1-environment-setup)
  - [Dependencies Installation](#2-dependencies-installation)
  - [Chrome WebDriver Setup](#3-chrome-webdriver-setup)
- [Usage](#usage)
  - [Data Collection](#1-data-collection)
  - [Model Training](#2-model-training)
  - [Chat Interface](#3-chat-interface)
- [Project Structure](#project-structure)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Setup

### 1. Environment Setup

First, create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv zombies_env

# Activate virtual environment
# On Windows:
zombies_env\Scripts\activate
# On macOS/Linux:
source zombies_env/bin/activate
```

### 2. Dependencies Installation

Install all required packages:
```bash
pip install -r requirements.txt
```

This will install:
- Web scraping tools (requests, beautifulsoup4, selenium)
- NLP libraries (nltk, transformers)
- Machine learning frameworks (torch)
- Utility packages (pandas, tqdm)

### 3. Chrome WebDriver Setup

1. Download ChromeDriver from: https://sites.google.com/chromium.org/driver/
2. Make sure the version matches your Chrome browser version
3. Add it to your system PATH or place it in your project directory

## Usage

### 1. Data Collection

The data collector will scrape information from various sources:
```bash
python zombies_data_collector.py
```

During collection, you can:
- Select data sources (Wiki, YouTube, Game Guides)
- Choose data types (Maps, Weapons, Perks)
- Monitor progress in real-time

The script generates two files:
- `zombies_dataset_structured_[TIMESTAMP].json`: Raw structured data
- `zombies_dataset_training_[TIMESTAMP].json`: Processed training data

### 2. Model Training

Train the model using the collected data:
```bash
python train_zombies_model.py
```

Training process:
1. Loads and preprocesses training data
2. Initializes GPT-2 model
3. Fine-tunes on zombies data
4. Saves model to `./zombies_model_final`

Default training parameters:
- Epochs: 5
- Batch size: 4
- Learning rate: Adaptive
- Evaluation steps: 100

### 3. Chat Interface

Start chatting with the AI:
```bash
python zombies_chat.py
```

Example questions:
- "What are the best strategies for TranZit?"
- "How do I upgrade the Ray Gun?"
- "What are all the perks in Black Ops 2 Zombies?"
- "Explain the Origins easter egg steps"

Type 'quit' to exit the chat.

## Project Structure

```
zombies_ai/
├── requirements.txt           # Project dependencies
├── zombies_data_collector.py # Data collection script
├── train_zombies_model.py    # Model training script
├── zombies_chat.py          # Chat interface
├── zombies_model_final/     # Trained model directory
└── data/                    # Generated data files
    ├── zombies_dataset_structured_[TIMESTAMP].json
    └── zombies_dataset_training_[TIMESTAMP].json
```

## Customization

### Adding More Sources

Edit `zombies_data_collector.py` to add more sources:
```python
self.sources = {
    "YouTube Guides": {
        "video_ids": [
            # Add your YouTube video IDs here
        ]
    },
    "Game Guides": {
        "urls": [
            # Add more guide URLs here
        ]
    }
}
```

### Adjusting Training Parameters

Edit `train_zombies_model.py` to modify training behavior:
```python
training_args = TrainingArguments(
    num_train_epochs=5,          # Number of training epochs
    per_device_train_batch_size=4, # Batch size
    learning_rate=5e-5,          # Learning rate
    # ... other parameters
)
```

### Modifying Chat Behavior

Edit `zombies_chat.py` to customize response generation:
```python
outputs = self.model.generate(
    inputs,
    max_length=200,          # Maximum response length
    temperature=0.7,         # Response creativity (0.0-1.0)
    top_k=50,               # Top K sampling
    top_p=0.95,             # Nucleus sampling
    # ... other parameters
)
```

## Troubleshooting

1. **Data Collection Issues**
   - Check your internet connection
   - Verify Chrome WebDriver version matches your Chrome browser
   - Ensure you have necessary permissions for file operations

2. **Training Issues**
   - Ensure you have enough GPU/CPU memory
   - Try reducing batch size if you encounter memory errors
   - Check if training data files exist and are properly formatted

3. **Chat Interface Issues**
   - Verify model files are present in `zombies_model_final` directory
   - Check if the timestamp in filenames matches your data files

## Contributing

Feel free to contribute by:
1. Adding more data sources
2. Improving data cleaning
3. Enhancing the model architecture
4. Adding new features to the chat interface

## License

This project is for educational purposes only. Call of Duty and Black Ops are trademarks of Activision.
