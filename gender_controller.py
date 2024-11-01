import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification

classifier = AutoModelForSequenceClassification.from_pretrained("padmajabfrl/Gender-Classification")
classifier.to('cpu')
tokenizer = AutoTokenizer.from_pretrained("padmajabfrl/Gender-Classification")


def get_gender(name):
    # Tokenisation
    tokens = tokenizer(name, return_tensors="pt").to('cpu')
    logits = classifier(**tokens).logits

    # Convert logits to a NumPy array
    logits_np = logits.detach().numpy()

    # Get the predicted index using NumPy's argmax
    predicted_index = np.argmax(logits_np, axis=1)[0]
    return {0: 'm', 1: 'f'}[predicted_index]
