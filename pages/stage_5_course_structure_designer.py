import os

import pandas
import streamlit as st

from docx import Document
import csv
import json

from azure_openai_llm import get_response


# Function to read topics from a file
def read_from_file(file_path):
    try:
        if file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as file:
                topics = file.read().splitlines()
        elif file_path.endswith('.docx'):
            doc = Document(file_path)
            topics = [para.text for para in doc.paragraphs if para.text.strip() != '']
        elif file_path.endswith('.csv'):
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                topics = [row for row in reader]
        else:
            raise ValueError("Unsupported file format. Please provide a .txt or .docx file.")
        return topics
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
        return []
    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")
        return []


# Function to get list of csv files from a given directory
def get_ctks_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.csv')]

# Function to design dropdown for ctks files
def create_file_selector(ctks_directory,inputbox):

    # Get list of JD dump files
    ctks_files = get_ctks_files(ctks_directory)

    # Dropdown to select a PDF file
    selected_ctks = inputbox.selectbox("Select CTKS file for Course Outline Design", ctks_files)
    return selected_ctks

def main():
    st.set_page_config(layout="wide")
    st.title("Welcome to Course Design Automation App")
    "**In this stage, GenAI plays the role of Content Writer and helps to generate a course structure based on the given CTKS**"
    st.divider()

    if "problem_statement_response" not in st.session_state:
        st.session_state.problem_statement_response = ""

    if "course_outline_response" not in st.session_state:
        st.session_state.course_outline_response = ""


    with st.sidebar:
        inputbox = st.container(height=500)
        inputbox.title("Course Design Inputs")
        # Directory containing Jd dum files
        ctks_directory = "outputs/stage-4-ctks_with_recommendations"
        # ctks_directory = "outputs/ctks_refined"
        # Create dropdown for jd dump files
        ctks_file = create_file_selector(ctks_directory, inputbox)

        subject_list = pandas.read_csv("inputs/subject_list.csv")

        subject = inputbox.selectbox("Select topic that needs to be searched in the selected competition file",
                                        subject_list.columns)

        course_type = inputbox.selectbox("Select Course Type", ["Foundational", "Advanced"])
        course_design = inputbox.selectbox("Select Course Design Type",["Problem Driven", "Topic Driven"])
        course_duration = inputbox.text_input("Enter Course Duration Details",
                                            "10 sessions each of 2 hour concept session")
        audience_type = inputbox.selectbox("Select Audience Type", ["College Students", "Working Professionals"])
        audience_proficiency_level = inputbox.selectbox("Select Proficiency Level", ["Beginner - No Prior Background",
                                                                                   "Intermediate - Basic Programming Skills",
                                                                                   "Advanced - Has Work Experience"])
        project_included = inputbox.checkbox("Include Topic for Project")

        ctks_file_content = read_from_file(f"{ctks_directory}/{ctks_file}")

        if inputbox.button("Suggest Problem Statements"):
            problem_statement_prompt = f"""
              # Comprehensive Course Design Strategy

                ## Course Configuration Inputs
                - **Subject**: {subject}
                - **Course Type**: {course_type}
                - **Course Design Approach**: {course_design}
                - **Course Duration: {course_duration}
                - **Target Audience**: {audience_type}
                - **Audience Proficiency Level**: {audience_proficiency_level}
                
                
                ## CTKS (Competency, Tasks, Knowledge, Skills) Input
                {ctks_file_content}
                
                ### Problem Statement Design
                    Based on the course configuration inputs given above and the scope defined by the CTKS listed above, generate:
                        - Exactly 3 Problem Statements, each one giving due justice to all the tasks and competencies:
                          1. **Mentor Demo Problem**: 
                             - Title (For eg. Expense Tracker)
                             - Purpose (For eg. Class Demonstration0
                             - Objective (For eg. Allow users to manage and track their expenses, and get predictions for future expenses)
                             - Detailed topic coverage (For eg. Covers all programming fundamentals, exception and file handling, OOPs basics, data structures, and using Groq API for building LLM application)
                          2. **Guided Student Problem**:
                             - Title
                             - Purpose
                             - Objective
                             - Detailed topic coverage
                          3. **Hands-on Unguided Practice Problem**:
                             - Title
                             - Purpose
                             - Objective
                             - Detailed topic coverage
                        
                ### Design Considerations
                    - The structure of all the 3 problems will be same, only the data model will be different.
                    - Map learning outcomes to industry-relevant skills
                    - Each of the problems will have similar set of tasks to be performed, so that the demos, guided practice, and unguided practice tasks are in sync. 

            Output Format:
                    The problem statements generated should be downloadable as Python dataframe object literal 
                    [
                    {{
                        {{"title":"value"}},
                        {{"purpose":"value"}},
                        {{"objective":"value"}},
                        {{"detailed coverage":"value"}}
                    }},
                    {{
                        {{"title":"value"}},
                        {{"purpose":"value"}},
                        {{"objective":"value"}},
                        {{"detailed coverage":"value"}}
                    }}
                    ]
     
            Additional Instructions
            Do not include any opening or closing lines in your response or even any additional python code lines like import or print statements. 
            Return only the dataframe object as literal leaving no room for any syntactical error.
            Please check the syntax of the literal such as presence of correct quotes, colons, parenthesis once before generating the outcome.
            """
            st.session_state.problem_statement_response = get_response(problem_statement_prompt)

    if st.session_state.problem_statement_response:
        st.dataframe(json.loads(st.session_state.problem_statement_response))
        if st.button("Generate Course Outline"):
            course_outline_generation_prompt = f""" 
            
            Persona: Curriculum and Learning Design Expert
            Role: 
            The Curriculum and Learning Design Expert is a GenAI persona that helps create structured, engaging course outlines. 
            Specializing in problem-driven courses, this expert integrates case studies, hands-on learning, and real-world application, ensuring each session promotes active participation and aligns learning objectives with practical problem-solving tasks to maximize student engagement and competency development.
            
            Task:
            Create a course outline for a foundational course targeting college students with no prior knowledge. 
            
            The course will focus on a central mentor demo case study, evolving across sessions with smaller examples to reinforce key objectives. 
            
            Each session will feature hands-on, SMART learning objectives aligned with the competencies, tasks, knowledge, and skills (CTKS) required to solve the case study.   
            
            # Comprehensive Course Design Strategy

            ## Course Configuration Inputs
            - **Subject**: {subject}
            - **Course Type**: {course_type}
            - **Course Design Approach**: {course_design}
            - **Course Duration: {course_duration}
            - **Target Audience**: {audience_type}
            - **Audience Proficiency Level**: {audience_proficiency_level}
            - **Is Project Included**: {project_included}
            
            
            ## CTKS (Competency, Tasks, Knowledge, Skills) Input
            {ctks_file_content}
            
            ## Problem Statements Input:
            {st.session_state.problem_statement_response}
            
            ### Output Format:
                The course outline should be returned as a Python dataframe object literal with the following structure:  
                [{{{{"sprint_no": "number"}},
                {{"sprint_name":"matches with the CTKS Task and syncs with the requirement fulfilled by the demo solution built in this sprint"}},
                {{"learning_objectives":["SMART Learning Objective","SMART Learning Objective",...]}},
                {{"problem_task_completed":"List the tasks completed in this sprint for building the solution based on each identified knowledge and skill, in a bulleted format."}}
                }},
                {{
                {{"sprint_no": value}},
                {{"sprint_name":"matches with the CTKS Task and syncs with the requirement fulfilled by the demo solution built in this sprint"}},
                {{"learning_objectives":["SMART Learning Objective","SMART Learning Objective",...]}},
                {{"problem_task_completed":"List the tasks completed in this sprint for building the solution based on each identified knowledge and skill, in a bulleted format."}}
                }},
                ...]
     
            ### Additional Instructions:
                Do not include any opening or closing lines in your response or even any additional python code lines like import or print statements. 
                Return only the dataframe object as literal leaving no room for any syntactical error.
                Please check the syntax of the literal such as presence of correct quotes, colons, parenthesis once before generating the outcome.
                
            """
            print(course_outline_generation_prompt)
            st.session_state.course_outline_response = get_response(course_outline_generation_prompt)
    if st.session_state.course_outline_response:
        # st.session_state.course_outline_response
        try:
            st.dataframe(json.loads(st.session_state.course_outline_response))
        except json.JSONDecodeError as e:
            st.write(f"Error: {e}")
            # print(f"Invalid JSON: {some_string}")

main()