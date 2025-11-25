import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import json

load_dotenv()

try:
    import streamlit as st
    api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
    model = st.secrets.get("GROQ_MODEL", os.getenv("GROQ_MODEL", "llama3-70b-8192"))
except:
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "llama3-70b-8192")

if not api_key:
    raise ValueError("GROQ_API_KEY not found. Please configure it in Streamlit secrets or .env file")

llm = ChatGroq(groq_api_key=api_key, model_name=model, temperature=0.7)



def call_llm(prompt, system_msg="You are a helpful assistant.", temp=0.7):
    try:
        messages = [
            SystemMessage(content=system_msg),
            HumanMessage(content=prompt)
        ]
        response = llm.invoke(messages)
        return response.content.strip()
    except Exception as e:
        print(f"Error: {e}")
        return None


def categorize_email(email_text, prompt_template):
    full_prompt = f"{prompt_template}\n\nEmail:\n{email_text}"
    result = call_llm(full_prompt, "You are an email categorizer.", 0.3)
    
    if result:
        return result.strip().strip('"').strip("'")
    return None


def extract_tasks(email_text, prompt_template):
    full_prompt = f"{prompt_template}\n\nEmail:\n{email_text}"
    result = call_llm(full_prompt, "Extract tasks from emails.", 0.3)
    
    if result:
        try:
            tasks = json.loads(result)
            if isinstance(tasks, list):
                return tasks
        except:
            import re
            match = re.search(r'\[.*\]', result, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    pass
    return []


def generate_reply(email_text, prompt_template, extra_instructions=""):
    full_prompt = f"{prompt_template}\n\nOriginal Email:\n{email_text}"
    if extra_instructions:
        full_prompt += f"\n\nExtra instructions: {extra_instructions}"
    
    return call_llm(full_prompt, "You are an email writer.", 0.7)


def generate_summary(email_text, prompt_template):
    full_prompt = f"{prompt_template}\n\nEmail:\n{email_text}"
    return call_llm(full_prompt, "Summarize emails concisely.", 0.5)


def chat_with_agent(question, email_context=""):
    if email_context:
        prompt = f"Email:\n{email_context}\n\nQuestion: {question}"
    else:
        prompt = question
    
    return call_llm(prompt, "You are a helpful email assistant.", 0.7)
