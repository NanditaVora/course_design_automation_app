import streamlit as st

course_topic_generator_page = st.Page("pages/course_topic_generator.py", title="Stage 1: Course Topic Generator", icon=":material/add_circle:")

college_syllabus_scanner_page = st.Page("pages/college_syllabus_scanner.py", title="Stage 2: College Syllabus Scanner", icon=":material/add_circle:")

ctks_validator_refiner_page = st.Page("pages/ctks_validator_refiner.py", title="Stage 3: CTKS Validator and Refiner", icon=":material/add_circle:")

pg = st.navigation([course_topic_generator_page, college_syllabus_scanner_page, ctks_validator_refiner_page])
pg.run()