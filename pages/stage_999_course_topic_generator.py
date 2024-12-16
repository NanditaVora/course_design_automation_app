import pandas
import streamlit as st
from azure_openai_llm import get_response
import json
from docx import Document
import csv

def main():
    st.set_page_config(layout="wide")

    if "response" not in st.session_state:
        st.session_state.response = ""
        st.session_state.topic_prompt = ""
    st.title("Welcome to Course Design Automation App")
    "**In this stage, GenAI plays the role of Subject Matter Expert and helps to generate topics on the given subject.**"
    st.divider()

    with st.sidebar:
        response_button_clicked = st.button("Generate Prompt")
        inputs = st.container(height=500)
        inputs.title("Inputs for Prompt Generation")
        subject_list = pandas.read_csv("inputs/subject_list.csv")

        subject = inputs.selectbox("Select topic that needs to be searched in the selected competition file",
                                        subject_list.columns)


        course_type = inputs.selectbox("Select Course Type",["Foundational","Advanced"])
        # course_design = inputs.selectbox("Select Course Design Type",["Problem Driven", "Topic Driven"])
        course_duration = inputs.text_input("Enter Course Duration Details","10 sessions each of 2 hour concept session")
        audience_type = inputs.selectbox("Select Audience Type",["College Students","Working Professionals"])
        audience_proficiency_level = inputs.selectbox("Select Proficiency Level",["Beginner - No Prior Background","Intermediate - Basic Programming Skills","Advanced - Has Work Experience"])
        project_included = inputs.checkbox("Include Topic for Project")

        if response_button_clicked:
            topic_prompt = f"""
            
            Generate a precise, structured prompt template that will help create a comprehensive training program curriculum with topics and subtopics based on the following inputs:
            Subject: {subject}
            
            Course Type: {course_type}
            Course Duration: {course_duration}
            Audience Type: {audience_type}
            Audience Proficiency Level: {audience_proficiency_level}
            Should Topic for Project be Included: {project_included}
            
            IMPORTANT CONSTRAINTS:
            1. Produce ONLY the prompt template.
            2. Do not generate any actual topics or content.
            3. The output must be a clear, copyable prompt that another AI can use to generate the curriculum.
            4. Ensure the prompt explicitly instructs the AI to create a tabular structure with main topics and subtopics.
            5. The prompt should request a comprehensive, hierarchical breakdown of the training program content.
            6. Give due justice to the title of the subject - {subject}
            Format the response as a single, direct prompt that can be immediately used by another AI system.
            
            The prompt should be designed to extract detailed information for curriculum development, using the following sample:

            You are an expert curriculum designer tasked with creating a detailed training program outline. 
            
            Generate a comprehensive, multi-level topic and subtopic structure in a tabular format based on the given specifications in following tabular structure:
            
            | Serial Number | Main Topic | Subtopics |
            |----------------|------------|-----------|           
             
           """
            prompt_response = get_response(topic_prompt)
            st.code(prompt_response,language=None)

    if prompt := st.chat_input("Copy the Generated Prompt, Edit it if required and Press Enter to Execute"):
        st.chat_message("user").write(prompt)
        st.session_state.response = get_response(prompt + """
                    Provide the list of topics as Python dataframe object literal like 
                    {"key":["val1","val2"]}
                    and do not include any opening or closing lines in your response or even any additional python code lines like import or print statements. Return only the dataframe object as literal.
                    """
                    )
        # st.dataframe(topic_response)
        # st.session_state.response = topic_response
    if st.session_state.response:
        # st.write(st.session_state.response)
        array_object = json.loads(st.session_state.response)
        st.dataframe(array_object)
        if st.session_state.response:
            if st.button("Generate CTKS"):
                ctks_prompt = f"""
                    Refer to the topics given below for the subject MySQL Foundation Course:
                     {st.session_state.response}
                    
                    Instructions:
                    Please generate the Competency, Task, Knowledge, and Skills (CTKS) for the MySQL foundation course based on the topics listed above with the relevant details for the program which is of duration is 40 hours, divided into 10 sessions, each with 2 hours of concept learning and 2 hours of practice session. There should be only 10 CTKS with each CTKS getting mapped against one 2 hour concept session ensuring it covers all the topics listed.
                    The CTKS should be suitable for a beginner-level course and should include the following:
                    
                    1. **Competency**: The overall ability or proficiency that the learner should achieve.
                    2. **Task**: Specific tasks or activities that the learner should be able to perform.
                    3. **Knowledge**: The theoretical understanding and information that the learner should acquire.
                    4. **Skills**: The practical abilities and techniques that the learner should develop.
                    
                    Example Format:
                    The CTKS should be downloadable as Python dataframe object literal like 
                    [{{"competency":"value"}},{{"task":["val1","val2"]}},{{"knowledge":["val1","val2"]}},{{"skill":["val1","val2"]}}].
                    
                    Additional Instructions
                    Do not include any opening or closing lines in your response or even any additional python code lines like import or print statements. 
                    Return only the dataframe object as literal.
                    """
                # print(ctks_prompt)
                ctks_response = get_response((ctks_prompt))
                st.dataframe(json.loads(ctks_response))
                st.balloons()
main()