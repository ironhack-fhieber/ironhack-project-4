import os
from flask import Flask, render_template, request, jsonify, g, session
import controller

App = Flask(__name__)
App.secret_key = os.urandom(24)

@App.before_request
def load_data():
  if 'video_url' in session and :
    # Lade Transkript und LLM-Objekt aus dem Cache (z.B. Redis)
    # basierend auf der video_url in der Session
    g.transcript = ''
    g.llm = ''

@App.route('/')
def index():
    return render_template('index.html')

@App.route('/process_video', methods=['POST'])
def process_video():
  video_url = request.form['video_url']
  # ... (Transcript holen und LLM initialisieren) ...
  session['video_url'] = video_url
  g.transcript = ''
  g.llm = ''
  return ''

@App.route('/question', methods=['POST'])
def question():
    if 'video_url' in session:
        video_url = session['video_url']
    return None


if __name__ == '__main__':
    App.run(debug=True)
