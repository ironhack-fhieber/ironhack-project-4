import os

from flask import Flask, render_template, request, jsonify

import chat_controller as cc
import helpers
import voice_controller as vc
from chain_manager import ChainManager
from gender_controller import get_gender

App = Flask(__name__)
App.secret_key = os.urandom(24)

manager = ChainManager()


@App.before_request
def load_data():
    os.environ["LANGCHAIN_PROJECT"] = 'youtube-project'
    os.environ['LANGCHAIN_TRACING_V2'] = 'true'
    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


@App.route('/')
def index():
    return render_template('index.html')


@App.route('/gender/<name>', methods=['GET'])
def gender(name):
    return get_gender(name)


@App.route('/process_video/<id>', methods=['POST'])
def process_video(id):
    if not manager.is_new(id):
        chain, title, examples = cc.process_video(id)
        manager.add_chain(id, title, chain, examples)

    instance = manager.get_chain(id)
    return jsonify({'title': instance['title'], 'examples': instance['examples']}), 201


@App.route('/process_voice', methods=['POST'])
def process_voice():
    file = request.files['file']  # Datei aus dem Request-Objekt erhalten

    tmp_path = f"uploads/{helpers.generate_name()}.wav"
    file.save(tmp_path)
    audio_path = helpers.convert_wav(tmp_path)
    return vc.convert_audio_to_text(audio_path)


@App.route('/question', methods=['POST'])
def question():
    data = request.get_json()

    video_id = data.get('id')
    chatter = data.get('chatter')
    question = data.get('question')

    # Retrieve the instance with error handling
    instance = manager.get_chain(video_id)
    if instance is None:
        return jsonify({'error': 'Invalid video ID'}), 404

    title = instance['title']
    qa_chain = instance['qa_chain']

    prompt = helpers.create_prompt(title, chatter, question)
    response = cc.ask_question_with_timestamp(qa_chain, prompt)
    return jsonify(response)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    App.run(host="0.0.0.0", port=port)
