from typing import List, Dict
from backend.database import Database
from backend import llm_service

db = None

def init_agent(database):
    global db
    db = database


def format_email_context(email):
    text = f"From: {email['sender']}\n"
    text += f"Subject: {email['subject']}\n"
    text += f"Date: {email['timestamp']}\n"
    
    if email.get('category'):
        text += f"Category: {email['category']}\n"
    
    if email.get('summary'):
        text += f"Summary: {email['summary']}\n\n"
    
    text += f"Body:\n{email['body']}"
    
    tasks = db.get_action_items_for_email(email['id'])
    if tasks:
        text += "\n\nAction Items:\n"
        for task in tasks:
            text += f"- {task['task']} (Deadline: {task['deadline']})\n"
    
    return text


def ask_question(question, email_id=None):
    context = ""
    
    if email_id:
        email = db.get_email_by_id(email_id)
        if email:
            context = format_email_context(email)
    
    return llm_service.chat_with_agent(question, context)


def search_emails(query):
    return db.search_emails(query)


def get_urgent_emails():
    important = db.get_emails_by_category("Important")
    todos = db.get_emails_by_category("To-Do")
    
    urgent = important + todos
    urgent.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return urgent


def get_inbox_summary():
    emails = db.get_all_emails()
    
    categories = {}
    for email in emails:
        cat = email.get('category', 'Uncategorized')
        categories[cat] = categories.get(cat, 0) + 1
    
    tasks = db.get_all_action_items()
    pending = [t for t in tasks if t['status'] == 'pending']
    
    summary = f"📧 Inbox Summary:\n\n"
    summary += f"Total Emails: {len(emails)}\n\n"
    
    summary += "By Category:\n"
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        summary += f"  • {cat}: {count}\n"
    
    summary += f"\n📋 Pending Tasks: {len(pending)}\n"
    
    if pending:
        summary += "\nTop Tasks:\n"
        for task in pending[:5]:
            summary += f"  • {task['task']}\n"
    
    return summary


def get_all_tasks():
    tasks = db.get_all_action_items()
    
    if not tasks:
        return "No tasks found."
    
    pending = [t for t in tasks if t['status'] == 'pending']
    
    summary = f"📋 Tasks Summary:\n\n"
    summary += f"Pending: {len(pending)}\n\n"
    
    if pending:
        summary += "Pending Tasks:\n"
        for task in pending:
            summary += f"  • {task['task']}\n"
            summary += f"    Deadline: {task['deadline']}\n"
            summary += f"    Email: {task['email_subject']}\n\n"
    
    return summary
