import pandas
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
    if directory.__contains__("competition"):
        selected_file = inputbox.selectbox("Select Competition File", files)
    elif file_type==".csv":
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
        college_syllabus_directory = "outputs/stage-2-college_syllabus"

        # Create dropdown for college syllabus files
        college_syllabus_file = create_file_selector(college_syllabus_directory, ".docx", inputbox)

        # Directory containing Competition topic files
        competition_topics_directory = "outputs/stage-3-competition_topics"

        # Create dropdown for college syllabus files
        competition_topics_file = create_file_selector(competition_topics_directory, ".csv", inputbox)

        # Directory containing CTKS files
        # ctks_directory = "outputs/ctks_from_jd"
        dump_directory = "outputs/stage-1-employer_topics"
        # ctks_file = create_file_selector(ctks_directory, ".csv", inputbox)
        dump_file = create_file_selector(dump_directory, ".csv", inputbox)
        subject_list = pandas.read_csv("inputs/subject_list.csv")

        subject = inputbox.selectbox("Select topic that needs to be searched in the selected competition file",
                                        subject_list.columns)


        course_type = inputbox.selectbox("Select Course Type", ["Foundational", "Advanced"])
        course_duration = inputbox.text_input("Enter Course Duration Details",                                            "10 sessions each of 2 hour concept session")
        audience_type = inputbox.selectbox("Select Audience Type", ["College Students", "Working Professionals"])
        audience_proficiency_level = inputbox.selectbox("Select Proficiency Level", ["Beginner - No Prior Background",
                                                                                   "Intermediate - Basic Programming Skills",
                                                                                   "Advanced - Has Work Experience"])
        project_included = inputbox.checkbox("Include Topic for Project")

        if inputbox.button("Read Files and Compare Topics"):
            college_syllabus_topics = read_from_file(f"outputs/stage-2-college_syllabus/{college_syllabus_file}")
            # ctks_topics = read_from_file(f"outputs/ctks_from_jd/{ctks_file}")
            dump_topics=read_from_file(f"outputs/stage-1-employer_topics/{dump_file}")

            competition_topics = read_from_file(f"outputs/stage-3-competition_topics/{competition_topics_file}")
            if len(competition_topics) <= 0:
                competition_topics = "Competition Topics Not Available - Please Ignore"
            if len(dump_topics) <= 0:
                dump_topics = "Dump Topics Not Available - Please Ignore"
            if len(college_syllabus_topics) <= 0:
                college_syllabus_topics = "College Syllabus Topics Not Available - Please Ignore"
            structure_topics_prompt = f"""
            
                **Persona**: Academic Curriculum Analyzer 🧠📚
                **Role**: You are a meticulous academic curriculum specialist with expertise in {subject} course design. 
                Your goal is to systematically map and compare {subject} curriculum topics across different academic sources.
                **Key Capabilities:**
                - Comprehensive topic mapping
                - Cross-referencing syllabus contents
                - Identifying curriculum gaps and overlaps
                - Objective topic evaluation
                
                **Objective:** Help educational institutions and curriculum designers create a standardized, comprehensive Java programming curriculum by analyzing topics from multiple sources.
                **Constraints:**
                - Use data-driven approach
                - Maintain academic rigor
                - Ensure no topic is overlooked
                - Provide neutral, systematic analysis
            
                I have documents with course topics from different sources as given below:
                
                1. College Syllabus Topics:

                {college_syllabus_topics}
                
                2. Dump Topics:

                {dump_topics}
                
                3. Competition Topics:
                
                {competition_topics}
                
                Please help me organize these topics into a structured, comparative tabular format. 
                
                The table should consolidate all the topics read from the given files only and create one single table with following columns:
                1. Topic
                2. Sub-topic  
                3. Exists in College Syllabus (Y, if the content similar to Topic / Sub-topic are found in College Syllabus topics, else N)
                4. Exists in Dumps (Y, if the content similar to Topic / Sub-topic are found in dump topics, else N)
                5. Exists in Competition (Y, if the content similar to Topic / Sub-topic are found in competition topics, else N)
                6. Accept Topic (If Exists in College Syllabus and if Exists in Competition Topics and if Exists in Dump, then Y. If both are N, then N, else TBD)

                Do not exclude any topic or sub-topic from the given topics.
                
               The consolidated table should be downloadable as Python dataframe object literal like 
                    [
                    {{
                    {{"topic":"value"}},
                    {{"sub_topic":"value"}},
                    {{"exists_in_college_syllabus":"Y"/"N"/"NA"-only if no topic is listed in college syllabus topics)}},
                    {{"exists_in_dump":"Y"/"N"/"NA"-only if no topic is listed in dump topics)}},
                    {{"exists_in_dump":"Y"/"N"/"NA"-only if no topic is listed in competition topics)}},                
                    {{"Accept Topic for CTKS":"Y"/"N"}}
                    }}
                    ,
                    ...
                    ]
                     
                Additional Instructions
                    Do not include any opening or closing lines in your response or even any additional python code lines like import or print statements. 
                    Return only the dataframe object as literal ensuring correct syntax and leaving no room for syntactical error. 
                    Please check the syntax of the literal such as presence of correct double quotes, colons, parenthesis once before generating the outcome.
                
            """
            print(structure_topics_prompt)
            st.session_state.structured_topics_response = get_response(structure_topics_prompt)
            # st.session_state.structured_topics_response
    if st.session_state.structured_topics_response:
        edited_topics = st.data_editor(json.loads(st.session_state.structured_topics_response),width=2000,height=1000)
        # st.dataframe(edited_topics)
        if st.button("Generate CTKS"):
            refine_ctks_prompt = f"""
                You are an AI Curriculum and Competency Development Specialist. 
                Your task is to design a comprehensive Competency, Task, Knowledge, and Skill (CTKS) framework for the following topics and sub-topics. 
                
                Study the table given below for the list of topics and subtopics:
                
                    {edited_topics}
                
                For each subject, ensure that the competencies are sequenced logically, building foundational knowledge first and advancing toward more complex topics. 
                The goal is to structure the learning process in a way that enhances learner understanding and mastery.
                
                Each CTKS framework must address the following:

                - Competency: Identify the specific competency being developed within the topic.
                - Task: Describe tasks or activities that learners can perform using the competency.
                - Knowledge: Outline the theoretical or factual knowledge required to acquire the competency.
                - Skill: Define the practical skills learners will develop through hands-on application of the competency.
                        
                The given table has list of topics and sub-topics which are included or not included in college syllabus, competition topics, and in the job requirement dump file.
                The table also has a column Accept Topic for CTKS whose entry is marked by user as Y or N.
                
                Your task is to create a Competency Task Knowledge and Skill CTKS framework in tabular format for this course basis the following considerations:
                - Course Duration - {course_duration}
                - Audience Profile - {audience_type} - {audience_proficiency_level}
                - Course objective - To strengthen {course_type} concepts of {subject}.
                - Project to be Included? - {project_included}
                
                **Important Instructions - Read Carefully and Thoroughly**
                
                1. Topic Selection:
                    - Include only the topics and sub-topics marked as "Y" in the "Accept Topic for CTKS" column of the provided table.
                    - Exclude all topics and sub-topics marked as "N" or "TBD" in the "Accept Topic for CTKS" column.
                2. Competency Design:
                    - Strategy: Logically group the topics and sub-topics selected ensuring they help learners to acquire a particular competency.
                        
                        For example: Group the topics and sub-topics like introduction to Java, variables, datatypes, declaration statements, and operators, and structure the CTKS as follows:
                        - Competency: Understand Java Basics
                        - Task: Write a "Hello World" program in Java
                        - Knowledge: Variable declaration, Datatypes in Java, Java Operators
                        - Skill: Write a simple Java program, perform arithmetic operations in Java
                    - Competency Count: Should match with the number of sessions stated in {course_duration} for the course.
                    - Sequencing: Guidelines for Sequencing:
                            - Do not strictly follow the sequence of topics and sub-topics given in the table of topics and sub-topics.
                            - Start with Fundamentals: Begin with foundational concepts and principles before progressing to more advanced topics. 
                                For example, in banking and finance, concepts like budgeting and saving should be taught before more complex ones like investment strategies and financial modeling.
                            - Logical Progression: Organize concepts in a logical sequence where each new idea builds on the previous one. 
                                For example, in data analytics, basic data collection and cleaning should precede analysis and interpretation techniques.
                            - Practical Application: Ensure that learners can apply the competencies through real-world tasks or case studies. 
                                For example, in digital marketing, learners should first learn about audience segmentation before diving into campaign execution and measurement.
                            - Progress from Simple to Complex: Organize the learning path to progress from simpler tasks and concepts to more complex ones. 
                                In software engineering, for example, start with understanding basic algorithms before moving on to more complex topics like system design. 
                            - Relevance: Each competency should focus on a specific, clear learning goal that is directly relevant to the target audience.
                3. Session Mapping:
                    - The modified CTKS should not alter the overall course duration. For example, if the course duration is calculated as 10 sessions, you must provide exactly 10 CTKS statements—neither more nor less.
                    - If there are fewer topics marked "Y" in the table than the required number of CTKS, distribute them logically across multiple CTKS. Ensure that the CTKS framework maintains a smooth progression.
                    - Each CTKS should be spaced out appropriately, ensuring that the learning experience remains engaging and not overcrowded.
                4. Logical Flow:
                    - Follow a bottom-up approach when designing the CTKS. This ensures that the foundational concepts are covered first, and each CTKS prepares the learner for the next session.
                    - Avoid redundancy: Do not repeat the same CTKS. If a topic is complex and requires more depth, split it into separate CTKS, ensuring each has a clear focus.
                
                
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
            print(refine_ctks_prompt)
            st.session_state.refine_ctks_response = get_response(refine_ctks_prompt)
        if st.session_state.refine_ctks_response:
            st.dataframe(json.loads(st.session_state.refine_ctks_response))

            recommended_topics = st.text_area("Enter list of topics separated by comma that you would want to recommend and modify the above CTKS")
            if st.button("Generate CTKS basis Recommendations"):
                recommended_ctks_prompt = f"""
                    Modify the CTKS given below without altering the count of rows to include the following list of recommended topics- {recommended_topics}:
                    
                    {st.session_state.refine_ctks_response}
                    
                    **Important Instructions - Read Carefully and Thoroughly**
                    - To design the CTKS, you may group the logically related sub-topics and topics, but do not over pack them. 
                    - If course duration computes to 10 sessions, there should be 10 CTKS statements - neither more nor less.
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