import os
from io import BytesIO

import pandas
from docx import Document
import streamlit as st
from dotenv import load_dotenv
import json

from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
import chromadb
from charset_normalizer import detect


# from azure_openai_llm import get_response
# from ollama_llm import get_response

# Initialize session state
def initalize_session_state():
    st.session_state.competition_response = ""
    st.session_state.content_written = False
    st.session_state.file_downloaded = False
    st.session_state.buffer = BytesIO()


# Initialize embeddings and vector store
def initialize_vector_store(uploaded_file):
    import pandas as pd

    # Load CSV file using pandas
    csv_path = f"inputs/competition_topics/{uploaded_file}"

    # Detect file encoding

    with open(csv_path, 'rb') as f:
        result = detect(f.read())
        encoding = result['encoding']

    df = pd.read_csv(csv_path, encoding=encoding)

    # Create a combined text representation of the data
    # Example: Concatenate all columns into a single string per row
    df['combined_text'] = df.apply(lambda row: ' '.join(row.astype(str)), axis=1)

    # Convert rows to LangChain Document objects
    documents = [Document(page_content=text) for text in df['combined_text'].tolist()]

    # Split the documents into smaller chunks
    splitter = RecursiveCharacterTextSplitter()
    split_documents = splitter.split_documents(documents)

    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5",
                                       encode_kwargs={"normalize_embeddings": True})

    # Clear ChromaDB system cache
    chromadb.api.client.SharedSystemClient.clear_system_cache()

    # Create vector store
    vectorstore = Chroma.from_documents(split_documents, embedding=embeddings)
    # Debug: Check if vectorstore is initialized
    if vectorstore is None:
        raise ValueError("Failed to initialize the vectorstore.")
    return vectorstore


# Create the LLM chain
def create_llm_chain(vectorstore, query):
    if vectorstore is None:
        raise ValueError("Failed to initialize the vectorstore.")
    retriever = vectorstore.as_retriever()
    load_dotenv()
    llm = AzureChatOpenAI(
        azure_deployment=os.environ.get('DEPLOYMENT_NAME_POC'),
        temperature=0,
        request_timeout=None,
        max_retries=2,
        api_key=os.environ.get('AZURE_OPENAI_API_KEY_POC'),
        api_version=os.environ.get('API_VERSION_POC'),
        azure_endpoint=os.environ.get('AZURE_OPENAI_ENDPOINT_POC')
    )

    template = """
    You are an assistant for question-answering tasks.
    Use the provided context only to answer the following question:

    <context>
    {context}
    </context>

    Question: {input}
    """
    prompt = ChatPromptTemplate.from_template(template)
    doc_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, doc_chain)


# Process the file and query to get the response
def process_query(uploaded_file, scan_topic, experience, learner_profile):
    vectorstore = initialize_vector_store(uploaded_file)
    query = f"""
        Objective: Generate a comprehensive list of {scan_topic} topics and subtopics for a RAG-based learning content recommendation system.
        For example:
        Topic: Java Programming Basics
        Sub-topics: variables, declarations, data types, operators, conditional statements, loop statements
        Topic: Java Programming Concepts
        Sub-topics: Exception handling, File handling, Functions
        Input Source:
        - Vector Store: Semantic search database containing content.
        - Target Audience: {experience}/{learner_profile} in {scan_topic}

        Topic Generation Process:
        1. Logically group subtopics into coherent main topics

        Vector Store Retrieval Criteria:

        - Prioritize topics with high semantic relevance
        - Consider industry trends and learning pathways

        Output Format:
        - Structured JSON list of dictionaries
        - Each dictionary contains:
          * "topic": Main topic name (string)
          * "sub_topics": List of detailed subtopics (array of strings)

        Example Output:
        [
          {{
            "topic": "Core Java Programming",
            "sub_topics": [
              "Java Syntax and Structure",
              "Object-Oriented Programming Principles",
              "Exception Handling",
              "Java Collections Framework"
            ]
          }},...
        ]

        Additional Constraints:
        - Ensure unique, non-redundant topics
        - Derive topics directly from vector store content
        - Maintain focus on practical, skill-building knowledge
        - No additional text, comments, or code
        - Return only the JSON-like list

    """

    chain = create_llm_chain(vectorstore, query)
    response = chain.invoke({"input": query})
    return response['answer']


# Handle the Get Response button
def handle_get_response(uploaded_file, scan_topic, experience, learner_profile):
    # Get Response Button
    if st.button('Get Response'):
        if uploaded_file and scan_topic:
            response = process_query(uploaded_file, scan_topic, experience, learner_profile)
            st.session_state.competition_response = response
            return response
        else:
            st.warning("Please upload a file and enter a prompt.")
            return None


# Function to get list of competition files from a given directory
def get_competition_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.csv')]


# Function to design dropdown for job description competition files
def create_file_selector(competition_directory, inputbox):
    # Get list of competition files
    competition_files = get_competition_files(competition_directory)

    # Dropdown to select a PDF file
    selected_file = inputbox.selectbox("Select competition file for Scanning", competition_files)
    return selected_file


def main():
    st.set_page_config(layout="wide")

    st.title("Welcome to Course Design Automation App")
    "**In this stage, GenAI plays the role of File Scanner and helps list topics from the selected competition file with job descriptions for the given topic.**"
    st.divider()
    with st.sidebar:
        inputbox = st.container(height=400)
        inputbox.title("Job Description File and Subject Selector")
        # Directory containing competition files
        competition_directory = "inputs/competition_topics"

        # Create dropdown for competition files
        competition_file = create_file_selector(competition_directory, inputbox)

        subject_list = pandas.read_csv("inputs/subject_list.csv")

        scan_topic = inputbox.selectbox("Select topic that needs to be searched in the selected competition file", subject_list.columns)

        experience = inputbox.selectbox("Select Experience Level", ["Fresher", "1-5 years", "5-10 years", "10+ years"])

        learner_profile = inputbox.selectbox("Select Learner's Profile", ["Beginner", "Intermediate", "Advanced"])

        handle_get_response(competition_file, scan_topic, experience, learner_profile)

    if "competition_response" not in st.session_state:
        initalize_session_state()
    if st.session_state.competition_response:
        st.header("Response")
        # st.markdown(st.session_state.competition_response)
        st.dataframe(json.loads(st.session_state.competition_response))



main()