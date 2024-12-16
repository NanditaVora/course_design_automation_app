import streamlit as st

jd_topic_scanner_page = st.Page("pages/stage_1_jd_topic_scanner.py", title="Stage 1: JD Topic Scanner", icon=":material/add_circle:")

# course_topic_generator_page = st.Page("pages/stage_999_course_topic_generator.py", title="Stage 2: Course Topic Generator", icon=":material/add_circle:")

college_syllabus_scanner_page = st.Page("pages/stage_2_college_syllabus_scanner.py", title="Stage 2: College Syllabus Scanner", icon=":material/add_circle:")

competition_topics_scanner_page = st.Page("pages/stage_3_competition_topics_scanner.py", title="Stage 3: Competition Topics Scanner", icon=":material/add_circle:")

ctks_validator_refiner_page = st.Page("pages/stage_4_ctks_validator_refiner.py", title="Stage 4: CTKS Validator and Refiner", icon=":material/add_circle:")

course_structure_designer_page = st.Page("pages/stage_5_course_structure_designer.py", title="Stage 5: Course Structure Designer", icon=":material/add_circle:")

sprint_content_designer_page = st.Page("pages/stage_6_sprint_content_designer.py", title="Stage 6: Sprint Content Designer", icon=":material/add_circle:")

pg = st.navigation([jd_topic_scanner_page, college_syllabus_scanner_page, competition_topics_scanner_page, ctks_validator_refiner_page, course_structure_designer_page, sprint_content_designer_page])
pg.run()