"""
App definition for Flask Server endpoints
"""

import os

from flask import Flask, render_template, request, jsonify

import chat_controller as cc
import helpers
import voice_controller as vc
from chain_manager import ChainManager


App = Flask(__name__)
App.secret_key = os.urandom(24)

manager = ChainManager()


@App.before_request
def load_data():
    """
    Loads environment variables before each request.

    This function sets environment variables required by LangChain,
    including the project name, tracing settings, and a workaround
    for potential library conflicts.

    It's executed before every request to the Flask application.
    """

    os.environ["LANGCHAIN_PROJECT"] = 'youtube-project'
    os.environ['LANGCHAIN_TRACING_V2'] = 'true'
    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


@App.route('/')
def index():
    """
    Renders the index page.

    Returns:
        str: The HTML content of the index page.
    """

    return render_template('index.html')


@App.route('/process_video/<video_id>', methods=['POST'])
def process_video(video_id):
    """
    Process a YouTube video and initialize the QA chain.

    Args:
        video_id (str): The ID of the YouTube video.

    Returns:
        tuple: A tuple containing the JSON response and status code.
    """

    if not manager.is_new(video_id):
        chains, title, examples = cc.process_video(video_id)
        manager.add_chain(video_id, title, chains, examples)

    instance = manager.get_chain(video_id)
    examples = instance['examples']

    # create examples if not yet created
    if not examples:
        new_examples = cc.create_example_questions(instance['ex_chain'], instance['title'])
        manager.update_examples(video_id, new_examples)
        examples = new_examples

    return jsonify({'title': instance['title'], 'examples': examples}), 201


@App.route('/process_voice', methods=['POST'])
def process_voice():
    """
    Process voice input and convert it to text.

    Returns:
        str: The text extracted from the voice input.
    """

    file = request.files['file']

    tmp_path = f"uploads/{helpers.generate_name()}.wav"
    file.save(tmp_path)
    audio_path = helpers.convert_wav(tmp_path)

    # Get the text of the question
    text = vc.convert_audio_to_text(audio_path)

    # Remove the temporary files
    os.remove(tmp_path)
    os.remove(audio_path)

    return text


@App.route('/question', methods=['POST'])
def question():
    """
    Answer a question based on the context of a YouTube video.

    Returns:
        tuple: A tuple containing the JSON response and status code.
    """

    data = request.get_json()

    video_id = data.get('id')
    chatter = data.get('chatter')
    question_text = data.get('question')

    # Retrieve the instance with error handling
    instance = manager.get_chain(video_id)
    if instance is None:
        return jsonify({'error': 'Invalid video ID'}), 404

    title = instance['title']
    qa_chain = instance['qa_chain']

    prompt = helpers.create_prompt(title, chatter, question_text)
    response = cc.ask_question_with_timestamp(qa_chain, prompt)
    return jsonify(response)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    App.run(host="0.0.0.0", port=port)
