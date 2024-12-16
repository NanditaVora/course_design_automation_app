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
    st.session_state.dump_response = ""
    st.session_state.content_written = False
    st.session_state.file_downloaded = False
    st.session_state.buffer = BytesIO()

# Initialize embeddings and vector store
def initialize_vector_store(uploaded_file):
    import pandas as pd

    # Load CSV file using pandas
    csv_path = f"inputs/jds/{uploaded_file}"

    # Detect file encoding

    with open(csv_path, 'rb') as f:
        result = detect(f.read())
        encoding = result['encoding']

    df = pd.read_csv(csv_path,encoding=encoding)

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
    query
    # query = f"""
    #     List down the topics and sub-topics related to {scan_topic} which are in demand from the candidates whose experience level is {experience}.
    #     The topics and the sub-topics should be relevant to the audience with the {learner_profile} level profile.
    #     Ensure that you include all the subtopics or specific areas covered under these main topics.
    #     Output Format:
    #     •	Main Topic 1
    #         o	Subtopic 1.1
    #         o	Subtopic 1.2
    #     •	Main Topic 2
    #         o	Subtopic 2.1
    #         o	Subtopic 2.2
    #     Example:
    #     •	Database Management Systems
    #         o	Introduction to DBMS
    #         o	Data Models
    #         o	SQL Queries
    #     •	Advanced Database Topics
    #         o	Normalization
    #         o	Transactions
    #         o	Indexing
    #     Please ensure the list covers unique list of topics and their detailed list of sub-topics having the mention of the given subject {scan_topic} or closely related to {scan_topic}.
    #
    #     Do not include any introductory lines or closing lines in your response, so that the response can as is downloaded.
    #
    #     Output Requirements:
    #             - Format: JSON-like list of dictionaries
    #             - Structure:
    #               [{{
    #                 "topic": "Topic Name",
    #                 "sub_topics": ["sub_topic_1", "sub_topic_2",...]
    #               }}, ...]
    #     Thank you!
    # """
    # query
    chain = create_llm_chain(vectorstore, query)
    response = chain.invoke({"input": query})
    return response['answer']

# Handle the Get Response button
def handle_get_response(uploaded_file, scan_topic, experience, learner_profile):

    # Get Response Button
    if st.button('Get Response'):
        if uploaded_file and scan_topic:
            response = process_query(uploaded_file, scan_topic, experience, learner_profile)
            st.session_state.dump_response = response
            return response
        else:
            st.warning("Please upload a file and enter a prompt.")
            return None

# Function to get list of dump files from a given directory
def get_dump_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.csv')]

# Function to design dropdown for job description dump files
def create_file_selector(dump_directory,inputbox):

    # Get list of dump files
    dump_files = get_dump_files(dump_directory)

    # Dropdown to select a PDF file
    selected_file = inputbox.selectbox("Select dump file for Scanning", dump_files)
    return selected_file

def main():
    st.set_page_config(layout="wide")

    st.title("Welcome to Course Design Automation App")
    "**In this stage, GenAI plays the role of File Scanner and helps list topics from the selected dump file with job descriptions for the given topic.**"
    st.divider()
    with st.sidebar:
        inputbox = st.container(height=400)
        inputbox.title("Job Description File and Subject Selector")
        # Directory containing dump files
        dump_directory = "inputs/jds"

        # Create dropdown for dump files
        dump_file = create_file_selector(dump_directory, inputbox)

        subject_list = pandas.read_csv("inputs/subject_list.csv")

        scan_topic = inputbox.selectbox("Select topic that needs to be searched in the selected competition file",
                                        subject_list.columns)

        experience = inputbox.selectbox("Select Experience Level",["Fresher","1-5 years","5-10 years", "10+ years"])

        learner_profile = inputbox.selectbox("Select Learner's Profile", ["Beginner","Intermediate","Advanced"])

        handle_get_response(dump_file, scan_topic, experience, learner_profile)

    if "dump_response" not in st.session_state:
        initalize_session_state()
    if st.session_state.dump_response:
        st.header("Response")
        # st.markdown(st.session_state.dump_response)
        st.dataframe(json.loads(st.session_state.dump_response))
        # Save Response Button
        # if st.button("Generate CTKS"):
        #     ctks_prompt = f"""
        #         Instructions for Generating Competency Task Knowledge Skill (CTKS):
        #
        #         Input:
        #         - Scan Topic: {scan_topic}
        #         - Available Topics: {st.session_state.dump_response}
        #         - Learner Proficiency Level: {learner_profile}
        #
        #         Filtering Criteria:
        #         1. From the Available Topics,Strictly select ONLY topics directly related to {scan_topic}
        #         2. From the Available Topics, exclude topics from different domains or technologies
        #         3. Assess each topic against these relevance filters:
        #            - Must directly contribute to {scan_topic} mastery
        #            - Align with {learner_profile} learning progression
        #            - Fit within a 2-hour concept session
        #            - Avoid redundant or overly complex subtopics
        #
        #         CTKS Generation Guidelines:
        #         1. **Competency**:
        #            - Define a clear, measurable learning outcome
        #            - Focus on holistic capability development
        #            - Reflect the specific {scan_topic} domain expertise
        #
        #         2. **Task**:
        #            - List practical, executable actions
        #            - Ensure tasks are achievable within session timeframe
        #            - Progressive complexity matching learner profile
        #
        #         3. **Knowledge**:
        #            - Theoretical foundations specific to {scan_topic}
        #            - Include core concepts, principles, and contextual understanding
        #            - Avoid deep-dive technical intricacies
        #
        #         4. **Skills**:
        #            - Hands-on, application-oriented capabilities
        #            - Direct correlation with tasks and competency
        #            - Skill progression from basic to intermediate level
        #
        #         Output Requirements:
        #         - Generate exactly 10 CTKS sets
        #         - Format: JSON-like list of dictionaries
        #         - Structure:
        #           [{{
        #             "competency": "Concise competency description",
        #             "task": ["Task 1", "Task 2"],
        #             "knowledge": ["Knowledge Point 1", "Knowledge Point 2"],
        #             "skill": ["Skill 1", "Skill 2"]
        #           }}, ...]
        #
        #         Constraints:
        #         - No additional text, comments, or code
        #         - Return only the CTKS JSON-like list
        #         - Ensure 100% relevance to {scan_topic}
        #     """
        #     # ctks_prompt = f"""
        #     #                     Refer to the topics given below for the subject {scan_topic}:
        #     #                      {st.session_state.jd_response}
        #     #
        #     #                     Instructions:
        #     #                     From the above topics, include only those topics that are required to develop a course on {scan_topic} for the learners whose proficiency level is {learner_profile} and generate CTKS - Competency, Task, Knowledge, Skill.
        #     #                     The course will be of 10 sessions each with 2 hour of concept session. Hence, ignore all the topics which will otherwise tightly pack the content and overwhelm these leaners.
        #     #                     Refer to the following points for clarity on CTKS:
        #     #
        #     #                     1. **Competency**: The overall ability or proficiency that the learner should achieve.
        #     #                     2. **Task**: Specific tasks or activities that the learner should be able to perform.
        #     #                     3. **Knowledge**: The theoretical understanding and information that the learner should acquire.
        #     #                     4. **Skills**: The practical abilities and techniques that the learner should develop.
        #     #
        #     #                     Map each topic selected with one set of CTKS. Hence, if there are 10 sessions, there should be a set of 10 CTKS.
        #     #                     Example Format:
        #     #                     The CTKS should be downloadable as Python dataframe object literal like
        #     #                     [{{"competency":"value"}},{{"task":["val1","val2"]}},{{"knowledge":["val1","val2"]}},{{"skill":["val1","val2"]}}].
        #     #
        #     #
        #     #                     Additional Instructions
        #     #                     Do not include any opening or closing lines in your response or even any additional python code lines like import or print statements.
        #     #                     Return only the dataframe object as literal.
        #     #                     """
        #     # print(ctks_prompt)
        #     ctks_response = get_response((ctks_prompt))
        #     st.dataframe(json.loads(ctks_response))
        #     st.balloons()
        #


main()