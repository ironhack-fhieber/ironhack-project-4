![logo](static/images/logo.png?raw=true)

# Ironhack Project: Fabi’s Tube Buddy

In this project, a chatbot is developed that leverages the power of large language models (LLMs) to interact with users based on the content of a YouTube video. The chatbot is built using the LangChain framework, which enables efficient integration with various LLMs, embedding models, and data sources.

## Functionality

The project comprises several key steps:

1. **Transcript Extraction:** The YouTube Transcript API is used to retrieve the transcript of a specified YouTube video. If the transcript is not publicly available, the code incorporates the usage of proxies to overcome this limitation.
2. **Text Preprocessing:** The extracted transcript is cleaned and formatted to remove unwanted characters and ensure the text is suitable for further processing. This involves removing timestamps, speaker indicators, and other unnecessary elements.
3. **Embedding and Storage:** The processed transcript is divided into chunks, and embeddings are generated using OpenAI's embedding model. These embeddings represent the semantic meaning of each chunk. The embeddings, along with the corresponding text chunks and their timestamps, are stored in a `FAISS` vectorstore. This vectorstore allows for efficient retrieval of relevant text based on user queries.
4. **LLM Integration:** The project utilizes the `ChatOpenAI` class from LangChain to integrate with OpenAI's LLMs. It defines prompts that guide the LLM in understanding and responding to user questions based on the video's content.
5. **Conversational Chatbot:** A `ConversationalRetrievalChain` is employed to provide a chat-like interface. This chain stores the conversation history and enables the chatbot to respond to follow-up questions effectively.
6. **Example Questions:** The project includes the functionality to generate example questions based on the transcript's content. This helps users understand the scope of information the chatbot can provide.

## Usage

The project's primary usage is as a tool for interacting with YouTube videos in a more comprehensive manner. Users can ask questions related to the video's content, and the chatbot will respond using the information derived from the transcript. This is especially beneficial for educational videos, where users may need to seek specific information or clarifications on certain topics.

## Files and Folders

**Files**
* `app.py`: The flask server handler
* `chain_manager.py`: Handle the saving of multiple chains
* `chat_controller.py`: Generate chains and vectorstore as well the response payloads for chat requests to flask server
* `gender_controller.py`: Determines the gender of the current chatter to set the icon beside the text
* `helpers.py`: Some useful helper methods which being used in several places
* `voice_contoller.py`: Converts audio questions as wav files to text

* `chat.ipynb`: Jupyter Notebook containing the code for building a chatbot using LangChain that can answer questions about a YouTube video by processing its transcript, embedding it using OpenAI, and leveraging a large language model for conversational responses. It also includes features for generating example questions and tracking the conversation history.
* `gender.ipynb`: Jupyter Notebook containing the code for loading a pre-trained gender classification model and applying it to predict the gender of a list of names.
* `voice_to_text.ipynb`: Jupyter Notebook containing the code for transcribing speech to text from a WAV audio file using the SpeechRecognition and pydub libraries, featuring a helper function for transcription and a converter section for processing audio.

* `presentation.pdf`: The presentation slides

**Folders**
* `static/*`: Assets used for website
* `templates/*`: Template files for flask server
* `test_files/*`: Test voice files for testing voice recognition
* `uploads/`: Temp folder for voice files uploaded to the server

## Instructions

1. Clone the repository.
2. Start the Flask Server
3. Go to http://localhost:5000

## Results

The results of the different models and preprocessing techniques are summarized in the notebook.

## Libraries

The following libraries are used in this project:

* `bs4`
* `faiss-cpu`
* `flask`
* `langchain`
* `langchain-community`
* `langchain_openai`
* `langsmith`
* `requests`
* `torch`
* `transformer`
* `youtube-transcript-api`

More information about the packages can be found the requirements.txt

Make sure to install these libraries before running the code.

## Contact

For any questions or feedback, please contact me.
