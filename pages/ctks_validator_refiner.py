import streamlit as st
import os
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



# Function to get list of College Syllabus files from a given directory
def get_files(directory,file_type):
    return [f for f in os.listdir(directory) if f.endswith(file_type)]


# Function to design dropdown for college syllabus files
def create_file_selector(directory,file_type,inputbox):
    # inputbox.title("College Syllabus and CTKS File Selector")

    # Get list of PDF files
    files = get_files(directory,file_type)

    # Dropdown to select a PDF file
    if file_type==".csv":
        selected_file = inputbox.selectbox("Select CTKS File", files)
    if file_type==".docx":
        selected_file = inputbox.selectbox("Select College Syllabus File", files)
    return selected_file

def main():

    if "review_response" not in st.session_state:
        st.session_state.review_response = ""

    if "refine_ctks_response" not in st.session_state:
        st.session_state.refine_ctks_response = ""

    if "recommended_ctks_response" not in st.session_state:
        st.session_state.recommended_ctks_response = ""
    st.title("Welcome to Course Design Automation App")
    """
    **In this stage, GenAI plays the role of Content Validator and helps to review and critique the CTKS designed in Stage 1.**
    """
    """
    **It also suggests refined CTKS based on the inputs from college syllabus topics.**
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
        ctks_directory = "outputs/ctks_from_jd"

        ctks_file = create_file_selector(ctks_directory, ".csv", inputbox)

        subject = inputbox.selectbox("Select Course", ["MySQL Database", "Java: Object Oriented Programming",
                                                     "Python Programming Fundamentals"])
        course_type = inputbox.selectbox("Select Course Type", ["Foundational", "Advanced"])
        course_duration = inputbox.text_input("Enter Course Duration Details",                                            "10 sessions each of 2 hour concept session")
        audience_type = inputbox.selectbox("Select Audience Type", ["College Students", "Working Professionals"])
        audience_proficiency_level = inputbox.selectbox("Select Proficiency Level", ["Beginner - No Prior Background",
                                                                                   "Intermediate - Basic Programming Skills",
                                                                                   "Advanced - Has Work Experience"])
        project_included = inputbox.checkbox("Include Topic for Project")

        if inputbox.button("Read Files and Compare Topics"):
            college_syllabus_topics = read_from_file(f"outputs/college_syllabus/{college_syllabus_file}")
            ctks_topics = read_from_file(f"outputs/ctks/{ctks_file}")

            structure_topics_prompt = f"""
                I have documents with course topics from different sources. 
                Please help me organize these into a structured, comparative tabular format. 

                Guidelines for creating the table:
                - Create columns: 
                  1. Topic/Subtopic
                  2. Source (CTKS/College Name)
                  3. Frequency of Appearance
                  4. Relevance Score (1-5 scale)
                  5. Additional Notes
                
                Specific requirements:
                - Standardize topic names (remove duplicates with slight variations)
                - If a topic appears in multiple sources, consolidate entries
                - Highlight unique topics specific to each source
                - Provide a brief explanation for relevance scoring
                
                Preferred output format:
                - Excel/CSV compatible format
                - Sortable columns
                - Clear, concise topic descriptions
                
                Please process the following documents into separate tables:
                1. {ctks_topics}
                2. {college_syllabus_topics}
                
            """
            structured_topics_response = get_response(structure_topics_prompt)
            # st.markdown(structured_topics_response)
            review_prompt = f"""
                Study the tabular data given below:
                {structured_topics_response}
                Using this data, perform a comprehensive comparative analysis:

                Comparative Analysis Objectives:
                1. Topic Coverage Analysis
                - Identify common topics across sources
                - Calculate percentage of topic coverage
                - Highlight unique topics in each source
                
                2. Depth and Relevance Evaluation
                - Compare depth of topic coverage
                - Assess relevance to target audience
                - Identify potential knowledge gaps
                
                3. Comparative Metrics
                - Create a matrix showing:
                  * Topics in most college syllabi
                  * Topics unique to CTKS
                  * Topics missing from CTKS
                  * Overlap percentage
                
                4. Detailed Comparison Criteria
                - Evaluate each topic on:
                  * Comprehensiveness
                  * Current industry relevance
                  * Alignment with learning objectives
                  * Potential for practical application
                
                Specific Analytical Requirements:
                - Provide percentage of topic coverage
                - Rank topics by importance
                - Suggest topic consolidation or expansion
                - Highlight areas needing curriculum enhancement
                
                Desired Output:
                - Structured comparative report
                - Quantitative analysis
                - Qualitative insights
                - Recommended curriculum modifications
                
                Context for Analysis:
                - Course Objective: To introduce the concepts of this subject
                - Target Audience: First or Second Year College Graduates having no prior knowledge of the subject
                
                Please provide a comprehensive, data-driven comparative analysis that offers actionable insights for curriculum improvement.
            
            """

            st.session_state.review_response = get_response(review_prompt)
    if st.session_state.review_response:
        st.markdown(st.session_state.review_response)
        if st.button("Generate Refined CTKS"):
            refine_ctks_prompt = f"""
                Study the analysis given below:
                {st.session_state}
                Based on this analysis, provide a refined CTKS in tabular format for this course basis the following considerations:
                - Course Duration - {course_duration}
                - Audience Profile - {audience_type} - {audience_proficiency_level}
                - Course objective - To strengthen {course_type} concepts of {subject}.
                Example Format:
                    The CTKS should be downloadable as Python dataframe object literal like 
                    [{{"competency":"value"}},{{"task":["val1","val2"]}},{{"knowledge":["val1","val2"]}},{{"skill":["val1","val2"]}}].
                    
                    Do Not: No field should be left blank or have None type value    
                Additional Instructions
                    Do not include any opening or closing lines in your response or even any additional python code lines like import or print statements. 
                    Return only the dataframe object as literal.
            """
            st.session_state.refine_ctks_response = get_response(refine_ctks_prompt)
        if st.session_state.refine_ctks_response:
            st.dataframe(json.loads(st.session_state.refine_ctks_response))

            recommended_topics = st.text_area("Enter list of topics separated by comma that you would want to recommend and modify the above CTKS")
            if st.button("Generate CTKS basis Recommendations"):
                recommended_ctks_prompt = f"""
                    Modify the CTKS given below without altering the count of rows to include the following list of recommended topics- {recommended_topics}:
                    
                    {st.session_state.refine_ctks_response}
                    
                    The modified CTKS SHOULD NOT increase the course duration, but try to adjust the topics within the same duration.
                    
                    Inputs for generating CTKS based on recommendations:
                    - Course Duration - {course_duration}
                    - Audience Profile - {audience_type} - {audience_proficiency_level}
                    - Course objective - To strengthen {course_type} concepts of {subject}.
                    Example Format:
                        The CTKS should be downloadable as Python dataframe object literal like 
                        [{{"competency":"value"}},{{"task":["val1","val2"]}},{{"knowledge":["val1","val2"]}},{{"skill":["val1","val2"]}},{{"rationale":"why this competency is included?"}}].
                        
                        Do Not: No field should be left blank or have None type value    
                    Additional Instructions
                        Do not include any opening or closing lines in your response or even any additional python code lines like import or print statements. 
                        Return only the dataframe object as literal.
                    
                """
                st.session_state.recommended_ctks_response = get_response(recommended_ctks_prompt)
                st.dataframe(json.loads(st.session_state.recommended_ctks_response))
            # st.balloons()
main()