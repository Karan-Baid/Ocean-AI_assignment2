from typing import Dict, List
from backend.database import Database
from backend import llm_service

db = None

def init_processor(database):
    global db
    db = database


def format_email(email):
    return f"From: {email['sender']}\nSubject: {email['subject']}\n\n{email['body']}"


def process_single_email(email_id, with_summary=False):
    email = db.get_email_by_id(email_id)
    if not email:
        return None
    
    results = {"email_id": email_id}
    email_text = format_email(email)
    
    cat_prompt = db.get_prompt("categorization")
    if not cat_prompt:
        db.load_default_prompts()
        cat_prompt = db.get_prompt("categorization")
    
    category = llm_service.categorize_email(email_text, cat_prompt)
    if category:
        db.update_email_category(email_id, category)
        results["category"] = category
    
    if category in ["To-Do", "Important", "Meeting Request"]:
        task_prompt = db.get_prompt("action_item")
        tasks = llm_service.extract_tasks(email_text, task_prompt)
        
        db.delete_action_items_for_email(email_id)
        for task in tasks:
            if task.get('task'):
                db.save_action_item(
                    email_id, 
                    task['task'], 
                    task.get('deadline', 'Not specified')
                )
        results["tasks"] = tasks
    
    if with_summary:
        summary_prompt = db.get_prompt("summary")
        summary = llm_service.generate_summary(email_text, summary_prompt)
        if summary:
            db.update_email_summary(email_id, summary)
            results["summary"] = summary
    
    return results


def process_all_emails(with_summary=False):
    emails = db.get_all_emails()
    results = []
    
    for email in emails:
        if not email['processed']:
            result = process_single_email(email['id'], with_summary)
            if result:
                results.append(result)
    
    return results


def create_draft_reply(email_id, custom_instructions=""):
    email = db.get_email_by_id(email_id)
    if not email:
        return None
    
    reply_prompt = db.get_prompt("auto_reply")
    if not reply_prompt:
        db.load_default_prompts()
        reply_prompt = db.get_prompt("auto_reply")
    
    email_text = format_email(email)
    reply_body = llm_service.generate_reply(email_text, reply_prompt, custom_instructions)
    
    if reply_body:
        subject = email['subject']
        if not subject.startswith("Re:"):
            subject = f"Re: {subject}"
        
        metadata = {
            "original_email_id": email_id,
            "category": email.get('category')
        }
        draft_id = db.save_draft(email_id, subject, reply_body, metadata)
        return draft_id
    
    return None
