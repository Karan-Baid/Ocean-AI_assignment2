"""
Database operations for Email Productivity Agent.
Handles SQLite database setup and CRUD operations for emails, prompts, drafts, and action items.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class Database:
    """Database manager for Email Productivity Agent."""
    
    def __init__(self, db_path: str = "data/email_agent.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def init_database(self):
        """Create database tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Emails table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY,
                sender TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                category TEXT,
                processed INTEGER DEFAULT 0,
                summary TEXT
            )
        ''')
        
        # Prompts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_type TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Drafts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id INTEGER,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email_id) REFERENCES emails (id)
            )
        ''')
        
        # Action items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS action_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id INTEGER NOT NULL,
                task TEXT NOT NULL,
                deadline TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email_id) REFERENCES emails (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ==================== Email Operations ====================
    
    def load_emails_from_json(self, json_path: str = "data/mock_inbox.json") -> int:
        """Load emails from JSON file into database."""
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Mock inbox file not found: {json_path}")
        
        with open(json_path, 'r') as f:
            emails = json.load(f)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Clear existing emails (for fresh start)
        cursor.execute("DELETE FROM emails")
        cursor.execute("DELETE FROM action_items")
        
        # Insert emails
        for email in emails:
            cursor.execute('''
                INSERT INTO emails (id, sender, subject, body, timestamp, category, processed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                email['id'],
                email['sender'],
                email['subject'],
                email['body'],
                email['timestamp'],
                email.get('category'),
                0
            ))
        
        conn.commit()
        count = len(emails)
        conn.close()
        
        return count
    
    def get_all_emails(self) -> List[Dict]:
        """Get all emails from database."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, sender, subject, body, timestamp, category, processed, summary
            FROM emails
            ORDER BY timestamp DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_email_by_id(self, email_id: int) -> Optional[Dict]:
        """Get a specific email by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, sender, subject, body, timestamp, category, processed, summary
            FROM emails
            WHERE id = ?
        ''', (email_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def update_email_category(self, email_id: int, category: str):
        """Update email category."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE emails
            SET category = ?, processed = 1
            WHERE id = ?
        ''', (category, email_id))
        conn.commit()
        conn.close()
    
    def update_email_summary(self, email_id: int, summary: str):
        """Update email summary."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE emails
            SET summary = ?
            WHERE id = ?
        ''', (summary, email_id))
        conn.commit()
        conn.close()
    
    def get_emails_by_category(self, category: str) -> List[Dict]:
        """Get all emails in a specific category."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, sender, subject, body, timestamp, category, processed, summary
            FROM emails
            WHERE category = ?
            ORDER BY timestamp DESC
        ''', (category,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def search_emails(self, query: str) -> List[Dict]:
        """Search emails by subject or body."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, sender, subject, body, timestamp, category, processed, summary
            FROM emails
            WHERE subject LIKE ? OR body LIKE ?
            ORDER BY timestamp DESC
        ''', (f'%{query}%', f'%{query}%'))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ==================== Prompt Operations ====================
    
    def save_prompt(self, prompt_type: str, content: str):
        """Save or update a prompt."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if prompt exists
        cursor.execute('SELECT id FROM prompts WHERE prompt_type = ?', (prompt_type,))
        exists = cursor.fetchone()
        
        if exists:
            # Update existing
            cursor.execute('''
                UPDATE prompts
                SET content = ?, updated_at = CURRENT_TIMESTAMP
                WHERE prompt_type = ?
            ''', (content, prompt_type))
        else:
            # Insert new
            cursor.execute('''
                INSERT INTO prompts (prompt_type, content)
                VALUES (?, ?)
            ''', (prompt_type, content))
        
        conn.commit()
        conn.close()
    
    def get_prompt(self, prompt_type: str) -> Optional[str]:
        """Get a specific prompt by type."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT content FROM prompts WHERE prompt_type = ?', (prompt_type,))
        row = cursor.fetchone()
        conn.close()
        
        return row['content'] if row else None
    
    def get_all_prompts(self) -> Dict[str, str]:
        """Get all prompts as a dictionary."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT prompt_type, content FROM prompts')
        rows = cursor.fetchall()
        conn.close()
        
        return {row['prompt_type']: row['content'] for row in rows}
    
    def load_default_prompts(self, json_path: str = "data/default_prompts.json"):
        """Load default prompts from JSON file."""
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Default prompts file not found: {json_path}")
        
        with open(json_path, 'r') as f:
            prompts = json.load(f)
        
        for prompt_type, content in prompts.items():
            self.save_prompt(prompt_type, content)
    
    # ==================== Draft Operations ====================
    
    def save_draft(self, email_id: Optional[int], subject: str, body: str, 
                   metadata: Optional[Dict] = None) -> int:
        """Save a draft email."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute('''
            INSERT INTO drafts (email_id, subject, body, metadata)
            VALUES (?, ?, ?, ?)
        ''', (email_id, subject, body, metadata_json))
        
        draft_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return draft_id
    
    def get_all_drafts(self) -> List[Dict]:
        """Get all drafts."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT d.id, d.email_id, d.subject, d.body, d.metadata, d.created_at,
                   e.subject as original_subject
            FROM drafts d
            LEFT JOIN emails e ON d.email_id = e.id
            ORDER BY d.created_at DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        drafts = []
        for row in rows:
            draft = dict(row)
            if draft['metadata']:
                draft['metadata'] = json.loads(draft['metadata'])
            drafts.append(draft)
        
        return drafts
    
    def get_draft_by_id(self, draft_id: int) -> Optional[Dict]:
        """Get a specific draft by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, email_id, subject, body, metadata, created_at
            FROM drafts
            WHERE id = ?
        ''', (draft_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            draft = dict(row)
            if draft['metadata']:
                draft['metadata'] = json.loads(draft['metadata'])
            return draft
        return None
    
    def update_draft(self, draft_id: int, subject: str, body: str):
        """Update an existing draft."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE drafts
            SET subject = ?, body = ?
            WHERE id = ?
        ''', (subject, body, draft_id))
        conn.commit()
        conn.close()
    
    def delete_draft(self, draft_id: int):
        """Delete a draft."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM drafts WHERE id = ?', (draft_id,))
        conn.commit()
        conn.close()
    
    # ==================== Action Item Operations ====================
    
    def save_action_item(self, email_id: int, task: str, deadline: str = "Not specified"):
        """Save an action item."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO action_items (email_id, task, deadline)
            VALUES (?, ?, ?)
        ''', (email_id, task, deadline))
        conn.commit()
        conn.close()
    
    def get_action_items_for_email(self, email_id: int) -> List[Dict]:
        """Get all action items for a specific email."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, email_id, task, deadline, status, created_at
            FROM action_items
            WHERE email_id = ?
            ORDER BY created_at DESC
        ''', (email_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_all_action_items(self) -> List[Dict]:
        """Get all action items across all emails."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT a.id, a.email_id, a.task, a.deadline, a.status, a.created_at,
                   e.subject as email_subject, e.sender
            FROM action_items a
            JOIN emails e ON a.email_id = e.id
            ORDER BY a.created_at DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_action_item_status(self, item_id: int, status: str):
        """Update action item status (pending/completed)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE action_items
            SET status = ?
            WHERE id = ?
        ''', (status, item_id))
        conn.commit()
        conn.close()
    
    def delete_action_items_for_email(self, email_id: int):
        """Delete all action items for a specific email."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM action_items WHERE email_id = ?', (email_id,))
        conn.commit()
        conn.close()
