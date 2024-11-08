"""
Chat Controller creates the llm, vectorstore and chains and the
creation of the transcript of YouTube videos, as well
the Functionality of a conversation chatbot about videos.
"""

import os

from langchain.callbacks import LangChainTracer
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langsmith import Client
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled

import helpers

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')


def process_video(video_id):
    """Processes a YouTube video to enable question answering.

    This function takes a YouTube video ID, retrieves the transcript,
    chunks it, creates a vectorstore, and sets up a question-answering chain.
    It also generates example questions based on the video title.

    Args:
       video_id: The YouTube video ID.

    Returns:
        A tuple containing:
            - qa_chain: The RetrievalQA chain for question answering.
            - video_title: The title of the YouTube video.
            - examples: Example questions generated for the video.
    """

    video_title = helpers.get_video_title(video_id)
    languages = ['en', 'de', 'es', 'pt']
    try:
        raw = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
    except TranscriptsDisabled:
        proxies = {'http': 'http://94.186.213.73:7212',
                   'https': 'http://94.186.213.73:7212'}
        raw = YouTubeTranscriptApi.get_transcript(video_id, languages=languages, proxies=proxies)

    # Initialize LangSmith client and tracer
    client = Client()
    tracer = LangChainTracer(client=client)

    chunks_with_metadata = create_chunks(raw)
    vectorstore = create_vectorstore(chunks_with_metadata)
    chains = create_chains(vectorstore, tracer)
    examples = create_example_questions(chains['examples'], video_title)

    return chains, video_title, examples


def create_chunks(raw_transcript):
    """Divides the raw transcript into smaller chunks with metadata.

    This function takes the raw YouTube transcript and splits it into
    manageable chunks of text, each with a corresponding start timestamp.
    This is done to facilitate efficient processing and retrieval of information.

    Args:
        raw_transcript: A list of dictionaries, where each dictionary
                       represents a segment of the transcript with 'text' and
                       'start' keys.

    Returns:
        A list of dictionaries, where each dictionary represents a chunk
        and contains 'content' (the text of the chunk) and 'timestamp'
        (the start time of the chunk).
    """

    # Initialize the list to hold the chunks with metadata and the variables for current chunk
    chunks_with_metadata = []
    current_text = ""
    current_start = None

    # Maximum length for each chunk
    max_chunk_length = 1000

    # Iterate over each entry in raw_transcript
    for entry in raw_transcript:
        # Set the start time for the first entry in the current chunk
        if current_start is None:
            current_start = entry['start']

        # Check if adding the current text would exceed the max_chunk_length
        if len(current_text) + len(entry['text']) + 1 > max_chunk_length:
            # If it does, save the current chunk and reset the variables
            content = helpers.clear_text(current_text)
            chunks_with_metadata.append({'content': content, 'timestamp': current_start})
            current_text = ""
            current_start = entry['start']

        # Add the current text to the chunk with a space
        current_text += entry['text'] + " "

    # After the loop, ensure any remaining text is added as a final chunk
    if current_text:
        content = helpers.clear_text(current_text)
        chunks_with_metadata.append({'content': content, 'timestamp': current_start})

    return chunks_with_metadata


def create_vectorstore(chunks_with_metadata):
    """Creates a vectorstore from the provided chunks.

    This function takes a list of chunks with metadata and uses OpenAI embeddings
    to create a FAISS vectorstore. This vectorstore is used for efficient
    similarity search during question answering.

    Args:
        chunks_with_metadata: A list of dictionaries, where each dictionary
                             represents a chunk and contains 'content'
                             (the text of the chunk) and 'timestamp'
                             (the start time of the chunk).

    Returns:
        A FAISS vectorstore instance containing the embedded chunks.
    """

    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    texts = [chunk['content'] for chunk in chunks_with_metadata]
    metadata = [{'timestamp': chunk['timestamp']} for chunk in chunks_with_metadata]

    return FAISS.from_texts(texts, embeddings, metadatas=metadata)


def create_chains(vectorstore, tracer):
    """Creates a question-answering chain.

    This function sets up a RetrievalQA chain using the provided vectorstore,
    a conversational memory, and a LangChain tracer for logging.
    It utilizes the 'stuff' chain type and the GPT-3.5-turbo language model.

    Args:
        vectorstore: The FAISS vectorstore containing the embedded chunks.
        tracer: The LangChain tracer for logging interactions with LangSmith.

    Returns:
        dict: A dictionary containing chains 'questions' for question answering
              and 'examples' for example creation.
    """

    llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.2)

    # Set up chat memory
    conversational_memory = ConversationBufferWindowMemory(
        memory_key='chat_history',
        k=3,
        return_messages=True,
        output_key='answer'
    )

    retriever = vectorstore.as_retriever(search_type='similarity', search_kwargs={'k': 4})

    # ConversationalRetrievalChain chain with vectorstore, memory and tracer for LangSmith logging
    # Used for chat
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        memory=conversational_memory,
        callbacks=[tracer]
    )

    # RetrievalQA chain with vectorstore and tracer for LangSmith logging
    # Used for initial example creation
    example = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type='stuff',
        retriever=retriever,
        callbacks=[tracer]
    )

    return {'questions': qa_chain, 'examples': example}


def create_example_questions(chain, title):
    """Generates example questions for the video.

    This function uses the provided QA chain and video title to generate
    a set of example questions that can be asked about the video content.
    It leverages a predefined prompt template to guide the question generation process.

    Args:
        chain: The RetrievalQA chain used for question answering.
        title: The title of the YouTube video.

    Returns:
        A list of example questions generated for the video.
    """

    prompt_text = helpers.examples_prompt().format(title=title)
    result = chain.invoke(input=prompt_text, output_key='result')
    example_questions = helpers.parse_array_string(result['result'])

    return example_questions


def ask_question_with_timestamp(qa_chain, prompt_text):
    """Queries the QA chain and retrieves the answer with timestamps.

    This function takes a question as input, queries the provided QA chain,
    and returns the answer along with relevant timestamps from the source documents.
    If the answer is "I don't know.", timestamps will be None.

    Args:
        qa_chain: The ConversationalRetrievalChain chain used for question answering.
        prompt_text: The question to be asked.

    Returns:
        A dictionary containing the answer and timestamps. The keys are:
            - 'answer': The answer to the question.
            - 'timestamps': A list of relevant timestamps, or None if the answer
                           is "I don't know.".
    """

    # Get the messages of the memory
    chat_history = qa_chain.memory.chat_memory.messages

    # Run the query to get the response and source documents
    result = qa_chain({'question': prompt_text, 'chat_history': chat_history})
    answer_text = helpers.clear_text(result['answer'])
    sources = result['source_documents']

    # define timestamps
    timestamps = None
    if "I don't know." not in answer_text:
        timestamps = helpers.select_timestamps(sources)

    # Append timestamp information to the answer
    return {'answer': answer_text, 'timestamps': timestamps}
