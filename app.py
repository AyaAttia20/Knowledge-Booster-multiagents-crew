import sys
import pysqlite3

sys.modules["sqlite3"] = pysqlite3
sys.modules["sqlalchemy.dialects.sqlite.pysqlite"] = pysqlite3

import asyncio
import nest_asyncio

try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

nest_asyncio.apply()

import os
import re
import streamlit as st
from datetime import datetime

from crewai import Crew, Agent, Task
from crewai_tools import SerperDevTool  

import google.generativeai as genai
import cohere

# تحميل مفاتيح API من البيئة
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")
os.environ["COHERE_API_KEY"] = os.getenv("COHERE_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

# إعداد APIs
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
co = cohere.Client(os.environ["COHERE_API_KEY"])

# أدوات البحث
search_tool = SerperDevTool()

# تعريف الـ Agents
book_agent = Agent(
    role="Book Finder",
    goal="Find free books and PDFs for a topic.",
    backstory="Specialist in locating free books from online sources.",
    tools=[search_tool],
    allow_delegation=False
)

podcast_agent = Agent(
    role="Podcast Curator",
    goal="Find quality podcasts on the topic.",
    backstory="Finds high-quality, English educational podcasts.",
    tools=[search_tool],
    allow_delegation=False
)

youtube_agent = Agent(
    role="YouTube Explorer",
    goal="Discover YouTube videos that explain a topic simply.",
    backstory="Finds easy-to-understand videos about your topic.",
    tools=[search_tool],
    allow_delegation=False
)

# مهام Agents
book_task = Task(
    description="Find 2 books or PDFs for the topic: {topic}. Include title and access link.",
    expected_output="List of book titles with links.",
    agent=book_agent
)

podcast_task = Task(
    description="Find 2 podcast episodes on the topic: {topic}. Include links and brief context.",
    expected_output="Podcast links and descriptions.",
    agent=podcast_agent
)

youtube_task = Task(
    description="Find 2 educational YouTube videos that explain {topic}. Prefer summaries or explainers.",
    expected_output="List of videos with links and why they were selected.",
    agent=youtube_agent
)

# تشكيل الـ Crew
crew = Crew(
    agents=[book_agent, podcast_agent, youtube_agent],
    tasks=[book_task, podcast_task, youtube_task],
    verbose=False,
    memory=False
)

# --- دوال مساعدة ---
def parse_crew_results(result):
    outputs = {
        "books_results": "No books found.",
        "podcasts_results": "No podcasts found.",
        "youtube_results": "No YouTube videos found.",
    }

    for task_output in result.tasks_output:
        agent_name = task_output.agent.lower()
        if "book" in agent_name:
            outputs["books_results"] = task_output.raw.strip()
        elif "podcast" in agent_name:
            outputs["podcasts_results"] = task_output.raw.strip()
        elif "youtube" in agent_name:
            outputs["youtube_results"] = task_output.raw.strip()

    return outputs["books_results"], outputs["podcasts_results"], outputs["youtube_results"]

def convert_to_markdown_links(text):
    lines = text.strip().splitlines()
    md_links = []
    for line in lines:
        url_match = re.search(r'(https?://\S+)', line)
        if url_match:
            url = url_match.group(1)
            title = line.replace(url, "").strip(" -•–:")
            md_links.append(f"- [{title if title else url}]({url})")
        else:
            if line.strip():
                md_links.append(f"- {line.strip()}")
    return "\n".join(md_links) if md_links else "No results found."

# --- واجهة Streamlit ---
st.set_page_config(page_title="Knowledge Booster", layout="centered")
st.title("🌟 Knowledge Booster")
st.markdown("Get **books**, **podcasts**, and **videos** on any topic using AI agents.")

topic = st.text_input("Enter a topic", placeholder="e.g. Artificial Intelligence")

if st.button("🔍 Search"):
    if not topic:
        st.warning("Please enter a topic.")
    else:
        with st.spinner("Running agents..."):
            result = crew.kickoff(inputs={"topic": topic})
            books_raw, podcasts_raw, youtube_raw = parse_crew_results(result)

            st.subheader("📚 Books")
            st.markdown(convert_to_markdown_links(books_raw))

            st.subheader("🎧 Podcasts")
            st.markdown(convert_to_markdown_links(podcasts_raw))

            st.subheader("📺 YouTube Videos")
            st.markdown(convert_to_markdown_links(youtube_raw))

            # حفظ تقرير ماركداون
            report_md = f"""# 📘 Knowledge Booster Report

**Topic:** {topic}  
**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📚 Books  
{convert_to_markdown_links(books_raw)}

---

## 🎧 Podcasts  
{convert_to_markdown_links(podcasts_raw)}

---

## 📺 YouTube Videos  
{convert_to_markdown_links(youtube_raw)}
"""
            file_name = f"{topic.replace(' ', '_')}_report.md"
            with open(file_name, "w") as f:
                f.write(report_md)

            with open(file_name, "rb") as f:
                st.download_button("📥 Download Markdown Report", data=f, file_name=file_name, mime="text/markdown")
