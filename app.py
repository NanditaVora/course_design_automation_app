import streamlit as st

course_topic_generator_page = st.Page("pages/course_topic_generator.py", title="Course Topic Generator", icon=":material/add_circle:")

college_syllabus_scanner_page = st.Page("pages/college_syllabus_scanner.py", title="Course Syllabus Scanner", icon=":material/add_circle:")

pg = st.navigation([course_topic_generator_page, college_syllabus_scanner_page])
pg.run()