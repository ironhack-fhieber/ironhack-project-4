import re
import requests
import random
import string
from bs4 import BeautifulSoup
from pydub import AudioSegment
from langchain_core.prompts import PromptTemplate

def get_video_title(video_id):
    """
    Extracts the title of a YouTube video.

    Args:
        video_url (str): The URL of the YouTube video.

    Returns:
        str: The title of the YouTube video.
    """
    soup = BeautifulSoup(requests.get(f"https://www.youtube.com/watch?v={video_id}").text, 'html.parser')
    return soup.title.string.replace(" - YouTube", "").strip()


def clear_text(raw_text):
    """
    Cleans the input text by removing unwanted characters and formatting.

    Args:
        raw_text (str): The input text to be cleaned.

    Returns:
        str: The cleaned text.
    """

    # Remove bracketed content using regex
    raw_text = re.sub(r"\[.*?\]", "", raw_text)

    # Replace newline and non-breaking space characters with spaces
    raw_text = raw_text.replace("\n", " ").replace("\xa0", " ")

    # Remove speaker indicators using regex
    raw_text = re.sub(r">>.+?:", "", raw_text)

    # Remove all double Spaces
    raw_text = raw_text.replace("  ", " ")

    # Remove doubled stops
    raw_text = raw_text.replace(". . ", ". ")

    # Remove leading and trailing spaces
    return raw_text.strip()


def select_timestamps(sources):
    """
    Selects relevant timestamps from a list of source documents.

    Args:
        sources (list): A list of source documents, each containing a metadata dictionary with a "timestamp" key.

    Returns:
        list: A list of selected timestamps, sorted in ascending order and deduplicated.
        Timestamps that are too close to the previous timestamp are removed to avoid redundancy.
    """

    timestamps = [int(source.metadata["timestamp"]) for source in sources]
    timestamps = sorted(list(set(timestamps)))  # Deduplicate timestamps and sort it

    # now remove timestamps which are too close to the timestamp before
    result = []
    threshold = 200
    last_number = None  # Initialize to None to avoid skipping the first element

    for number in timestamps:
        if last_number is None or number - last_number >= threshold:
            result.append(number)
            last_number = number  # Update last_number for the next iteration

    return result


def generate_name(length=10):
    characters = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    return ''.join(random.choices(characters, k=length))


def convert_wav(wav_file):
    sound = AudioSegment.from_file(wav_file)

    # define path and convert wav to a pcm_s16le wav file
    pcm_path = f"uploads/{generate_name()}_pcm.wav"
    sound.export(pcm_path, format="wav", codec="pcm_s16le")
    return pcm_path


def prompt():
    template = """
    You are a helpful and informative AI assistant that is good at remembering previous turns in the conversation to give helpful and relevant answers. 
    You are given a transcript of the video called "{title}".
    {chatter} is asking questions. Please answer the following question, which comes after 'Question:'.
    If the question cannot be answered using the information provided, answer with "Sorry {chatter}, I don't know".

    Question: {question_text}
    """

    return PromptTemplate(
        input_variables=["title", "chatter", "question_text"],
        template=template
    )


def examples_prompt():
    template = """
    You are a helpful and informative AI assistant. You are given a transcript of the video called "{title}". 
    Please create 3 short interesting questions about the video a user might ask for. Return those 3 questions in a array like: 
    ['What is the video about?', 'Can you give me more information about Veo?', 'Are there any news about Android?']
    """

    return PromptTemplate(
        input_variables=['title'],
        template=template
    )

def create_prompt(title, chatter, question):
    """
        Helper function to create a formatted prompt.
    """
    return prompt().format(title=title, chatter=chatter, question_text=question)