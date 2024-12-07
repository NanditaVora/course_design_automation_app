import streamlit as st
from azure_openai_llm import get_response
import json

def main():
    if "response" not in st.session_state:
        st.session_state.response = ""
    st.title("Welcome to Course Design Automation App")
    "**In this stage, GenAI plays the role of Subject Matter Expert and helps to generate topics on the given subject.**"


    with st.sidebar:
        inputs = st.container(height=500)
        inputs.title("Inputs for Topics Generation")
        subject = inputs.selectbox("Select Course",["MySQL Database","Java Programming","Object Oriented Programming using Java"])
        course_type = inputs.selectbox("Select Course Type",["Foundational","Advanced"])
        course_design = inputs.selectbox("Select Course Design Type",["Topic Driven","Problem Driven"])
        course_duration = inputs.text_input("Enter Course Duration Details","10 sessions each of 2 hour concept session")
        audience_type = inputs.selectbox("Select Audience Type",["College Students","Working Professionals"])
        audience_proficiency_level = inputs.selectbox("Select Proficiency Level",["Beginner - No Prior Background","Intermediate - Basic Programming Skills","Advanced - Has Work Experience"])
        if st.button("Generate Prompt"):
            topic_prompt = f"""
            Generate prompt using the following inputs that will help to generate topics with subtopics in tabular structure for training program:
            Subject: {subject}
            Course Design: {course_design}
            Course Type: {course_type}
            Course Duration: {course_duration}
            Audience Type: {audience_type}
            Audience Proficiency Level: {audience_proficiency_level}
            Ensure you only generate the prompt and not the response for the prompt.
            Do not include any introductory or closing lines in your response so that the prompt can be taken up as is.
            """
            prompt_response = get_response(topic_prompt)
            prompt_response

    # st.write("main of course topics generator called")
    if prompt := st.chat_input("Say something"):
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
                print(ctks_prompt)
                ctks_response = get_response((ctks_prompt))
                st.dataframe(json.loads(ctks_response))
main()