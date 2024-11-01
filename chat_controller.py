import os

from langchain.callbacks import LangChainTracer
from langchain.chains import RetrievalQA
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langsmith import Client
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled

import helpers

video_title = ''
raw_transcript = None

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')


def process_video(id):
    video_title = helpers.get_video_title(id)
    languages = ['en', 'de', 'es', 'pt']
    try:
        raw_transcript = YouTubeTranscriptApi.get_transcript(id, languages=languages)
    except TranscriptsDisabled:
        proxies = {'http': 'http://94.186.213.73:7212',
                   'https': 'http://94.186.213.73:7212'}
        raw_transcript = YouTubeTranscriptApi.get_transcript(id, languages=languages, proxies=proxies)

    # Initialize LangSmith client and tracer
    client = Client()
    tracer = LangChainTracer(client=client)

    chunks_with_metadata = create_chunks(raw_transcript)
    vectorstore = create_vectorstore(chunks_with_metadata)
    qa_chain = create_qa_chain(vectorstore, tracer)
    examples = create_example_questions(qa_chain, video_title)

    return qa_chain, video_title, examples


def create_chunks(raw_transcript):
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
            chunks_with_metadata.append({'content': helpers.clear_text(current_text), 'timestamp': current_start})
            current_text = ""
            current_start = entry['start']

        # Add the current text to the chunk with a space
        current_text += entry['text'] + " "

    # After the loop, ensure any remaining text is added as a final chunk
    if current_text:
        chunks_with_metadata.append({'content': helpers.clear_text(current_text), 'timestamp': current_start})

    return chunks_with_metadata


def create_vectorstore(chunks_with_metadata):
    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    texts = [chunk["content"] for chunk in chunks_with_metadata]
    metadata = [{"timestamp": chunk["timestamp"]} for chunk in chunks_with_metadata]

    return FAISS.from_texts(texts, embeddings, metadatas=metadata)


def create_qa_chain(vectorstore, tracer):
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.2, n=3)

    # Set up chat memory
    conversational_memory = ConversationBufferWindowMemory(
        memory_key='youtube_project_history',
        k=3,
        return_messages=True,
        output_key='result'
    )

    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    # Set up the RetrievalQA chain with vectorstore and tracer for LangSmith logging
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        memory=conversational_memory,
        retriever=retriever,
        return_source_documents=True,
        callbacks=[tracer]
    )

    return qa_chain


def create_example_questions(qa_chain, video_title):
    prompt_text = helpers.examples_prompt().format(title=video_title)
    result = qa_chain.invoke(input=prompt_text, output_key="result")
    example_questions = result["result"]

    return example_questions


def ask_question_with_timestamp(qa_chain, prompt_text):
    # Run the query to get the response and source documents
    result = qa_chain.invoke(input=prompt_text, output_key="result")
    answer_text = helpers.clear_text(result["result"])
    sources = result["source_documents"]

    # define timestamps
    timestamps = None
    if "I don't know." not in answer_text:
        timestamps = helpers.select_timestamps(sources)

    # Append timestamp information to the answer
    return {"answer": answer_text, "timestamps": timestamps}
