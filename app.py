import streamlit as st

jd_topic_scanner_page = st.Page("pages/jd_topic_scanner.py",title="Stage 1: JD Topic Scanner", icon=":material/add_circle:")

# course_topic_generator_page = st.Page("pages/course_topic_generator.py", title="Stage 2: Course Topic Generator", icon=":material/add_circle:")

college_syllabus_scanner_page = st.Page("pages/college_syllabus_scanner.py", title="Stage 2: College Syllabus Scanner", icon=":material/add_circle:")

ctks_validator_refiner_page = st.Page("pages/ctks_validator_refiner.py", title="Stage 3: CTKS Validator and Refiner", icon=":material/add_circle:")

course_structure_designer_page = st.Page("pages/course_structure_designer.py", title="Stage 4: Course Structure Designer", icon=":material/add_circle:")


pg = st.navigation([jd_topic_scanner_page, college_syllabus_scanner_page, ctks_validator_refiner_page, course_structure_designer_page])
pg.run()