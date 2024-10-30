import os

from flask import Flask, render_template, request, g, session

from gender_controller import get_gender

App = Flask(__name__)
App.secret_key = os.urandom(24)


@App.before_request
def load_data():
    if 'video_id' in session:
        # Lade Transkript und LLM-Objekt aus dem Cache (z.B. Redis)
        # basierend auf der video_url in der Session
        g.transcript = ''
        g.llm = ''


@App.route('/')
def index():
    return render_template('index.html')


@App.route('/gender/<name>', methods=['GET'])
def gender(name):
    return get_gender(name)


@App.route('/process_video/<id>', methods=['POST'])
def process_video():
    video_id = id
    # ... (Transcript holen und LLM initialisieren) ...
    session['video_id'] = video_id
    g.transcript = ''
    g.llm = ''
    return ''


@App.route('/question', methods=['POST'])
def question():
    if 'video_id' in session:
        video_id = session['video_id']
    return None


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    App.run(host="0.0.0.0", port=port)
