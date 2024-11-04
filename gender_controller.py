import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

device = 'cuda' if torch.cuda.is_available() else 'cpu'

classifier = AutoModelForSequenceClassification.from_pretrained("padmajabfrl/Gender-Classification")
classifier.to(device)
tokenizer = AutoTokenizer.from_pretrained("padmajabfrl/Gender-Classification")


def get_gender(name):
    """Predicts the gender associated with a given name.

    This function uses a pre-trained deep learning model to classify the
    gender associated with a given name. It returns 'm' for male and 'f'
    for female.

    Args:
        name (str): The name to be classified.

    Returns:
        str: The predicted gender ('m' or 'f').

    Example:
        >>> get_gender("Alice")
        'f'
    """

    # Tokenisation and shortening to the maximum length
    tokens = tokenizer(name, return_tensors="pt").to(device)

    # Perform sentiment analysis for the shortened text
    logits = classifier(**tokens).logits
    predicted_index = torch.argmax(logits, dim=1).item()
    return {0: 'm', 1: 'f'}[predicted_index]
