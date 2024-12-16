import streamlit as st
import os
import pandas
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
def get_course_outline_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.csv')]

# Function to design dropdown for course outline files
def create_file_selector(course_outline_directory,inputbox):

    # Get list of JD dump files
    course_outline_files = get_course_outline_files(course_outline_directory)

    # Dropdown to select a PDF file
    selected_course_outline = inputbox.selectbox("Select Course Outline File", course_outline_files)
    return selected_course_outline

def main():
    st.set_page_config(layout="wide")

    st.title("Welcome to Course Design Automation App")
    "**In this stage, GenAI helps to generate content for the course Sprint**"
    st.divider()

    if "course_outline" not in st.session_state:
        st.session_state.course_outline = ""

    with st.sidebar:
        inputbox = st.container(height=500)
        inputbox.title("Sprint Design Inputs")
        # Directory containing course outline files
        course_structure_directory = "outputs/stage-5-course_outline"

        # Create dropdown for course outline files
        course_outline_file = create_file_selector(course_structure_directory, inputbox)

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

        course_outline_file_content = pandas.read_csv(f"{course_structure_directory}/{course_outline_file}")
        # st.write(course_outline_file_content)
        if inputbox.button("Show Content"):
            st.session_state.course_outline = course_outline_file_content

    if not st.session_state.course_outline.empty:
        st.dataframe(st.session_state.course_outline,width=1000)
        if st.button("Generate Sprint Descriptions"):
            sprint_description_prompt = (f"""You are an expert course content designer. 
            
                                        Your task is to generate description for each sprint based on the details given below for each sprint:"
                                         ## Inputs
                                        - **Subject**: {subject}
                                        - **Course Type**: {course_type}
                                        - **Course Design Approach**: {course_design}
                                        - **Course Duration: {course_duration}
                                        - **Target Audience**: {audience_type}
                                        - **Audience Proficiency Level**: {audience_proficiency_level}
                                        - **List of Sprints:**
                                        
                                        {st.session_state.course_outline}
    
                                        The length of sprint description should not be more than 1000 words.    
                                        
                                        Refer to the sprint name, learning objectives for each sprint and then generate the sprint description.
                                        
                                        ## Output Format:
                                                    [{{
                                                    {{
                                                    "sprint_description":"Sprint description"
                                                    }},
                                                    {{
                                                    "sprint_description":"Sprint description"
                                                    }},
                                                    ...
                                                    }}       
                                                    
                                        ## Example:
                                        [{{
                                        {{
                                        "sprint_description":"In this sprint, you will embark on a comprehensive exploration of Python programming fundamentals, utilizing Google Colab as your coding environment. 
                                        Your journey begins with crafting a simple "Hello World" program using the print() function. 
                                        Following this, you will learn to use the input() function to capture user input, enhancing interactivity in your programs. 
                                        You will also declare variables, work with Python's primitive data types, and master type conversions between strings and numbers. 
                                        By developing basic algorithms and utilizing arithmetic and assignment operators, you'll effectively perform calculations and manage data, equipping yourself with essential skills for your programming endeavors.
                                        "
                                        }}
                                        }},..
                                        }}
                                        ]
                                        
                                        ## Additional Instructions:
                                        Do not include any opening or closing lines in your response or even any additional python code lines like import or print statements. 
                                        Return only the dataframe object as literal leaving no room for any syntactical error.
                                        Please check the syntax of the literal such as presence of correct quotes, colons, parenthesis once before generating the outcome.
                                          
                                         """)
            sprint_description_response = get_response(sprint_description_prompt)
            st.write(sprint_description_response)
            st.dataframe(json.loads(sprint_description_response),width=2000)

        if st.button("Generate Context Setting"):
            context_setting_prompt = (f"""You are an expert course content designer. 

                                        Your task is to generate content for setting the context for each sprint of the course with following inputs"
                                         ## Inputs
                                        - **Subject**: {subject}
                                        - **Course Type**: {course_type}
                                        - **Course Design Approach**: {course_design}
                                        - **Course Duration: {course_duration}
                                        - **Target Audience**: {audience_type}
                                        - **Audience Proficiency Level**: {audience_proficiency_level}
                                        - **List of Sprints:**

                                        {st.session_state.course_outline.to_string()}

                                        The purpose of the context setting is to throw 2 to 3 thought provoking questions to the learners that will generate the curiosity in their minds.
                                        To generate these questions, for each sprint listed under list of sprints, first read the details under the project_task_completed column and based on this content 
                                        generate thought provoking questions.
                                        
                                        Do not mention the technical terms that will be discussed in the sprint. Keep the questions problem specific.
                                        For example, if the sprint is on Polymorphism, the context setting should not have mention of Polymorphism or any of the related tech jargon.
                                        
                                        Or if the sprint is introducing concept of variables and data types, the context should not mention any of these or related terms.
                                        
                                        ## Output Format:
                                        [{{
                                        {{
                                        "context_setting":"Give a brief outline of the story pertaining to the problem_task_completed of the sprint.
                                        List down the questions in bulleted list format."
                                        }},
                                        {{
                                        "context_setting":"Give a brief outline of the story pertaining to the problem_task_completed of the sprint.
                                        List down the questions in bulleted list format."
                                        }},
                                        }}
                                        
                                        
                                        ### Example:
                                        [{{
                                        {{
                                        "context_setting": "Neeta, the recently recruited software developer, has been assigned a task to create a software application - Library Management System. 1. From where should Neeta begin her development journey? 2. What are the different type of data that her application will handle? 3. How would Java help her in her development tasks?"
                                        }}
                                        }}
                                        ]   
                                        
                                        ## Additional Instructions:
                                        Do not include any opening or closing lines in your response or even any additional python code lines like import or print statements. 
                                        Return only the dataframe object as literal leaving no room for any syntactical error.
                                        Please check the syntax of the literal such as presence of correct quotes, colons, parenthesis once before generating the outcome.
                                           
                                        """)
            # print(context_setting_prompt)
            context_setting_response = get_response(context_setting_prompt)
            st.write(context_setting_response)
            st.dataframe(json.loads(context_setting_response))
main()