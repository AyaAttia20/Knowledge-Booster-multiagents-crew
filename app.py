import streamlit as st
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool

search_tool = SerperDevTool()

book_agent = Agent(
    role="Book Finder",
    goal="Find free books and PDFs for a topic.",
    backstory="Specialist in locating free books from online sources.",
    tools=[search_tool],
    allow_delegation=False
)

book_task = Task(
    description="Find 2 books or PDFs for the topic: {topic}. Include title and access link.",
    expected_output="List of book titles with links.",
    agent=book_agent
)

crew = Crew(agents=[book_agent], tasks=[book_task])

topic = st.text_input("Enter a topic")

if st.button("Search"):
    if topic:
        result = crew.kickoff(inputs={"topic": topic})
        st.write(result.tasks_output[0].raw)
    else:
        st.warning("Enter a topic")
