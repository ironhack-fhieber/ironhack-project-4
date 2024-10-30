import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

device = 'cuda' if torch.cuda.is_available() else 'cpu'

classifier = AutoModelForSequenceClassification.from_pretrained("padmajabfrl/Gender-Classification")
classifier.to(device)
tokenizer = AutoTokenizer.from_pretrained("padmajabfrl/Gender-Classification")


def get_gender(name):
    # Tokenisation and shortening to the maximum length
    tokens = tokenizer(name, return_tensors="pt").to(device)

    # Perform sentiment analysis for the shortened text
    logits = classifier(**tokens).logits
    predicted_index = torch.argmax(logits, dim=1).item()
    return {0: 'm', 1: 'f'}[predicted_index]
