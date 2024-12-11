import streamlit as st
import os
from docx import Document
import csv
import json

from azure_openai_llm import get_response
# from ollama_llm import get_response

# Function to read topics from a file
def read_from_file(file_path):
    # st.write(file_path)
    try:
        if file_path.endswith("Select File"):
            topics = ""
        elif file_path.endswith('.txt'):
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

# Function to get list of College Syllabus files from a given directory
def get_files(directory,file_type):
    return [f for f in os.listdir(directory) if f.endswith(file_type)]


# Function to design dropdown for college syllabus files
def create_file_selector(directory,file_type,inputbox):
    # inputbox.title("College Syllabus and CTKS File Selector")

    # Get list of PDF files
    files = get_files(directory,file_type)
    files.insert(0,"Select File")
    # Dropdown to select a PDF file
    if file_type==".csv":
        selected_file = inputbox.selectbox("Select Dump File",files)
    if file_type==".docx":
        selected_file = inputbox.selectbox("Select College Syllabus File", files)
    return selected_file

def main():
    st.set_page_config(layout="wide")
    if "review_response" not in st.session_state:
        st.session_state.review_response = ""

    if "refine_ctks_response" not in st.session_state:
        st.session_state.refine_ctks_response = ""

    if "recommended_ctks_response" not in st.session_state:
        st.session_state.recommended_ctks_response = ""

    if "structured_topics_response" not in st.session_state:
        st.session_state.structured_topics_response = ""
    st.title("Welcome to Course Design Automation App")
    """
    **In this stage, GenAI plays the role of Expert Content Creator and helps to generate CTKS based on topics and sub-topics finalized by user.**
    """

    st.divider()

    with st.sidebar:
        inputbox = st.container(height=500)
        inputbox.title("Inputs for CTKS Validation")

        # Directory containing College Syllabus files
        college_syllabus_directory = "outputs/college_syllabus"

        # Create dropdown for college syllabus files
        college_syllabus_file = create_file_selector(college_syllabus_directory, ".docx", inputbox)

        # Directory containing CTKS files
        # ctks_directory = "outputs/ctks_from_jd"
        dump_directory = "outputs/stage-1-course_topics"
        # ctks_file = create_file_selector(ctks_directory, ".csv", inputbox)
        dump_file = create_file_selector(dump_directory, ".csv", inputbox)
        subject = inputbox.selectbox("Select Subject", ["MySQL Database", "Java: Object Oriented Programming",
                                                     "Python Programming Fundamentals","Low-Code No-Code: User Developer"])
        course_type = inputbox.selectbox("Select Course Type", ["Foundational", "Advanced"])
        course_duration = inputbox.text_input("Enter Course Duration Details",                                            "10 sessions each of 2 hour concept session")
        audience_type = inputbox.selectbox("Select Audience Type", ["College Students", "Working Professionals"])
        audience_proficiency_level = inputbox.selectbox("Select Proficiency Level", ["Beginner - No Prior Background",
                                                                                   "Intermediate - Basic Programming Skills",
                                                                                   "Advanced - Has Work Experience"])
        project_included = inputbox.checkbox("Include Topic for Project")

        if inputbox.button("Read Files and Compare Topics"):
            college_syllabus_topics = read_from_file(f"outputs/college_syllabus/{college_syllabus_file}")
            # ctks_topics = read_from_file(f"outputs/ctks_from_jd/{ctks_file}")
            dump_topics=read_from_file(f"outputs/stage-1-course_topics/{dump_file}")
            structure_topics_prompt = f"""
                I have documents with course topics from different sources as given below:
                
                1. College Syllabus Topics:

                {college_syllabus_topics}
                
                2. Dump Topics:

                {dump_topics}
                
                Please help me organize these topics into a structured, comparative tabular format. 
                
                The table should consolidate all the topics read from the given files and create one single table with following columns:
                1. Topic
                2. Sub-topic
                3. Exists in College Syllabus (Y, if the content similar to Topic / Sub-topic are found in College Syllabus topics, else N)
                4. Exists in Dumps (Y, if the content similar to Topic / Sub-topic are found in dump topics, else N)
                5. Accept Topic (If Exists in College Syllabus and if Exists in Dump, then Y. If both are N, then N, else TBD)

               The consolidated table should be downloadable as Python dataframe object literal like 
                    [
                    {{
                    {{"topic":"value"}},
                    {{"sub_topic":"value"}},
                    {{"exists_in_college_syllabus":"Y"/"N"/"NA"-only if no topic is listed in college syllabus topics)}},
                    {{"exists_in_dump":"Y"/"N"/"NA"-only if no topic is listed in dump topics)}},
                    {{"Accept Topic for CTKS":"Y"/"N"}}
                    }}
                    ,
                    ...
                    ]
                     
                Additional Instructions
                    Do not include any opening or closing lines in your response or even any additional python code lines like import or print statements. 
                    Return only the dataframe object as literal ensuring correct syntax and leaving no room for syntactical error. 
                    Please check the syntax of the literal such as presence of correct quotes, colons, parenthesis once before generating the outcome.
                
            """
            print(structure_topics_prompt)
            st.session_state.structured_topics_response = get_response(structure_topics_prompt)
            # st.session_state.structured_topics_response
    if st.session_state.structured_topics_response:
        edited_topics = st.data_editor(json.loads(st.session_state.structured_topics_response),width=2000,height=1000)
        # st.dataframe(edited_topics)
        if st.button("Generate CTKS"):
            refine_ctks_prompt = f"""
                Study the table given below:
                
                {edited_topics}
                
                This table has list of topics and sub-topics which are included or not included in college syllabus and in the job requirement dump file.
                The table also has a column Accept Topic for CTKS whose entry is marked by user as Y or N.
                
                Your task is to create a Competency Task Knowledge and Skill CTKS framework in tabular format for this course basis the following considerations:
                - Course Duration - {course_duration}
                - Audience Profile - {audience_type} - {audience_proficiency_level}
                - Course objective - To strengthen {course_type} concepts of {subject}.
                - Project to be Included? - {project_included}
                
                **Important Instructions - Read Carefully and Thoroughly**
                - For generating CTKS, from the table select only the topics and sub-topics where the value is "Y" for the column - "Accept Topic for CTKS".
                - For generating CTKS, ignore all the topics and sub-topics for which the value is "N" or "TBD" in the column - "Accept Topic for CTKS".
                - To design the CTKS, you may group the logically related sub-topics and topics, but do not over pack them.Include only one topic per CTKS.
                - Each session specified in course duration should map with one CTKS. For eg., if there are 10 sessions specified in the course duration, then there should be 10 CTKS statements.
                - The modified CTKS SHOULD NOT increase the overall course duration. 
                - If the number of topics and sub-topics with value "Y" for column - "Accept Topic for CTKS" are less than distribute them logically across multiple CTKS.
                - Also, the CTKS of each session should not be tightly packed ensuring smooth and pleasing learning experience.
                - Give a logical bottoms-up approach while building CTKS, such that every row of CTKS fulfills the pre-requisite understanding for the subsequent CTKS.

                - For example, for the session covering topics on introduction to Java, variables, datatypes, declaration statements, and operators you may have one CTKS, such as 
                Competency- Understand Java Basics
                Task - Write Hello World program in Java
                Knowledge - Variable declaration, Datatypes in Java, Java Operators
                Skill - Write simple Java program, Write program to perform arithmetic operations
                
                Example Format:
                    The CTKS should be downloadable as Python dataframe object literal like 
                    [
                    {{
                    {{"competency": "value"}},
                    {{"task": ["val1", "val2"]}},
                    {{"knowledge": ["val1", "val2"]}},
                    {{"skill": ["val1", "val2"]}}
                    }}
                    ,
                    ...]
                    
                    Do Not: No field should be left blank or have None type value    
                Additional Instructions
                    Do not include any opening or closing lines in your response or even any additional python code lines like import or print statements. 
                    Return only the dataframe object as literal.
                    Please check the syntax of the literal such as presence of correct quotes, colons, parenthesis once before generating the outcome.
                
            """
            st.session_state.refine_ctks_response = get_response(refine_ctks_prompt)
        if st.session_state.refine_ctks_response:
            st.dataframe(json.loads(st.session_state.refine_ctks_response))

            recommended_topics = st.text_area("Enter list of topics separated by comma that you would want to recommend and modify the above CTKS")
            if st.button("Generate CTKS basis Recommendations"):
                recommended_ctks_prompt = f"""
                    Modify the CTKS given below without altering the count of rows to include the following list of recommended topics- {recommended_topics}:
                    
                    {st.session_state.refine_ctks_response}
                    
                    **Important Instructions - Read Carefully and Thoroughly**
                    - To design the CTKS, you may group the logically related sub-topics and topics, but do not over pack them. Include only one topic per CTKS.
                    - Each session specified in course duration should map with one CTKS. For eg., if there are 10 sessions specified in the course duration, then there should be 10 CTKS statements.
                    - Give a logical bottoms-up approach while building CTKS, such that every row of CTKS fulfills the pre-requisite understanding for the subsequent CTKS.
                    - The CTKS of each session should not be tightly packed ensuring smooth and pleasing learning experience.
                    
                    Inputs for generating CTKS based on recommendations:
                    - Course Duration - {course_duration}
                    - Audience Profile - {audience_type} - {audience_proficiency_level}
                    - Course objective - To strengthen {course_type} concepts of {subject}.
                    The CTKS should be downloadable as Python dataframe object literal like 
                    [
                        {{
                        {{"competency": "value"}},
                        {{"task": ["val1", "val2"]}},
                        {{"knowledge": ["val1", "val2"]}},
                        {{"skill": ["val1", "val2"]}}
                        }}
                        ,
                    ...]
                        Do Not: No field should be left blank or have None type value    
                    Additional Instructions
                        Do not include any opening or closing lines in your response or even any additional python code lines like import or print statements. 
                        Return only the dataframe object as literal.
                        Please check the syntax of the literal such as presence of correct quotes, colons, parenthesis once before generating the outcome.
                
                    
                """
                st.session_state.recommended_ctks_response = get_response(recommended_ctks_prompt)
                st.dataframe(json.loads(st.session_state.recommended_ctks_response))
            # st.balloons()
main()