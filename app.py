import streamlit as st
import pandas as pd
from datetime import datetime
from backend.database import Database
from backend import email_processor, agent



# Page configuration
st.set_page_config(
    page_title="Email Productivity Agent",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 1.5rem;
        font-weight: 500;
    }
    .email-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
        background: white;
    }
    .category-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.25rem;
    }
    .category-important { background: #ff4444; color: white; }
    .category-todo { background: #ff9800; color: white; }
    .category-meeting { background: #2196f3; color: white; }
    .category-project { background: #4caf50; color: white; }
    .category-newsletter { background: #9c27b0; color: white; }
    .category-spam { background: #757575; color: white; }
    .category-personal { background: #00bcd4; color: white; }
    .action-item {
        padding: 0.5rem;
        border-left: 3px solid #ff9800;
        margin: 0.5rem 0;
        background: #fff3e0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = Database()

# Initialize processor and agent with database
if 'initialized' not in st.session_state:
    from backend import email_processor, agent
    email_processor.init_processor(st.session_state.db)
    agent.init_agent(st.session_state.db)
    st.session_state.initialized = True
    
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
    
if 'selected_email_id' not in st.session_state:
    st.session_state.selected_email_id = None
    
if 'emails_loaded' not in st.session_state:
    st.session_state.emails_loaded = False

if 'prompts_loaded' not in st.session_state:
    st.session_state.prompts_loaded = False



def get_category_badge_html(category):
    if not category:
        return ""
    cat_class = category.lower().replace(" ", "")
    return f'<span class="category-badge category-{cat_class}">{category}</span>'


def format_timestamp(timestamp_str):
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%b %d, %Y %I:%M %p")
    except:
        return timestamp_str


def inbox_viewer_page():
    st.title("📧 Email Inbox")
    
    # Load emails button
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        if st.button("🔄 Load Mock Inbox", use_container_width=True):
            try:
                count = st.session_state.db.load_emails_from_json()
                st.session_state.emails_loaded = True
                st.success(f"✅ Loaded {count} emails from mock inbox")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error loading emails: {e}")
    
    with col2:
        if st.button("⚡ Process All Emails", use_container_width=True, disabled=not st.session_state.emails_loaded):
            with st.spinner("Processing emails with LLM..."):
                try:
                    results = email_processor.process_all_emails(with_summary=False)
                    st.success(f"✅ Processed {len(results)} emails")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    with col3:
        if st.button("📊 View Summary", use_container_width=True):
            summary = agent.get_inbox_summary()
            st.info(summary)
    
    st.divider()
    
    # Filters
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input("🔍 Search emails", placeholder="Search by subject or content...")
    
    with col2:
        categories = ["All", "Important", "To-Do", "Meeting Request", "Project Update", "Newsletter", "Spam", "Personal"]
        selected_category = st.selectbox("Filter by Category", categories)
    
    # Get emails
    if search_query:
        emails = st.session_state.db.search_emails(search_query)
    elif selected_category != "All":
        emails = st.session_state.db.get_emails_by_category(selected_category)
    else:
        emails = st.session_state.db.get_all_emails()
    
    if not emails:
        st.info("📭 No emails found. Click 'Load Mock Inbox' to get started.")
        return
    
    st.write(f"**Showing {len(emails)} email(s)**")
    
    # Display emails
    for email in emails:
        with st.expander(f"**{email['subject']}** - {email['sender']}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**From:** {email['sender']}")
                st.markdown(f"**Date:** {format_timestamp(email['timestamp'])}")
                if email['category']:
                    st.markdown(get_category_badge_html(email['category']), unsafe_allow_html=True)
            
            with col2:
                if st.button("🔄 Process", key=f"process_{email['id']}", use_container_width=True):
                    with st.spinner("Processing..."):
                        email_processor.process_single_email(email['id'], with_summary=True)
                        st.success("✅ Processed")
                        st.rerun()
                
                if st.button("✍️ Draft Reply", key=f"reply_{email['id']}", use_container_width=True):
                    with st.spinner("Generating reply..."):
                        draft_id = email_processor.create_draft_reply(email['id'])
                        if draft_id:
                            st.success(f"✅ Draft created (ID: {draft_id})")
                        else:
                            st.error("❌ Failed to create draft")
            
            st.markdown("---")
            st.markdown(f"**Email Body:**")
            st.write(email['body'])
            
            # Show summary if available
            if email.get('summary'):
                st.info(f"**Summary:** {email['summary']}")
            
            # Show action items
            action_items = st.session_state.db.get_action_items_for_email(email['id'])
            if action_items:
                st.markdown("**📋 Action Items:**")
                for item in action_items:
                    st.markdown(f"""
                    <div class="action-item">
                        <strong>Task:</strong> {item['task']}<br>
                        <strong>Deadline:</strong> {item['deadline']}
                    </div>
                    """, unsafe_allow_html=True)


def prompt_configuration_page():
    st.title("🧠 Prompt Configuration")
    
    st.markdown("""
    Configure the prompts that guide the AI agent's behavior. These prompts control how emails are 
    categorized, how action items are extracted, and how replies are generated.
    """)
    
    # Load default prompts if not loaded
    if not st.session_state.prompts_loaded:
        if st.button("📥 Load Default Prompts"):
            try:
                st.session_state.db.load_default_prompts()
                st.session_state.prompts_loaded = True
                st.success("✅ Default prompts loaded")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    st.divider()
    
    # Get current prompts
    prompts = st.session_state.db.get_all_prompts()
    
    # Tabs for different prompt types
    tab1, tab2, tab3, tab4 = st.tabs(["📁 Categorization", "📋 Action Items", "✉️ Auto-Reply", "📝 Summary"])
    
    with tab1:
        st.subheader("Email Categorization Prompt")
        st.markdown("This prompt guides how emails are categorized (Important, To-Do, Spam, etc.)")
        
        current_prompt = prompts.get('categorization', '')
        new_prompt = st.text_area(
            "Categorization Prompt",
            value=current_prompt,
            height=200,
            key="cat_prompt"
        )
        
        if st.button("💾 Save Categorization Prompt", key="save_cat"):
            st.session_state.db.save_prompt('categorization', new_prompt)
            st.success("✅ Prompt saved")
    
    with tab2:
        st.subheader("Action Item Extraction Prompt")
        st.markdown("This prompt extracts tasks and deadlines from emails.")
        
        current_prompt = prompts.get('action_item', '')
        new_prompt = st.text_area(
            "Action Item Prompt",
            value=current_prompt,
            height=200,
            key="action_prompt"
        )
        
        if st.button("💾 Save Action Item Prompt", key="save_action"):
            st.session_state.db.save_prompt('action_item', new_prompt)
            st.success("✅ Prompt saved")
    
    with tab3:
        st.subheader("Auto-Reply Generation Prompt")
        st.markdown("This prompt controls how automatic reply drafts are generated.")
        
        current_prompt = prompts.get('auto_reply', '')
        new_prompt = st.text_area(
            "Auto-Reply Prompt",
            value=current_prompt,
            height=200,
            key="reply_prompt"
        )
        
        if st.button("💾 Save Auto-Reply Prompt", key="save_reply"):
            st.session_state.db.save_prompt('auto_reply', new_prompt)
            st.success("✅ Prompt saved")
    
    with tab4:
        st.subheader("Email Summary Prompt")
        st.markdown("This prompt generates concise summaries of email content.")
        
        current_prompt = prompts.get('summary', '')
        new_prompt = st.text_area(
            "Summary Prompt",
            value=current_prompt,
            height=200,
            key="summary_prompt"
        )
        
        if st.button("💾 Save Summary Prompt", key="save_summary"):
            st.session_state.db.save_prompt('summary', new_prompt)
            st.success("✅ Prompt saved")


def email_agent_page():
    st.title("💬 Email Agent Chat")
    
    st.markdown("""
    Ask questions about your emails, request summaries, or get help managing your inbox.
    """)
    
    # Email context selector
    emails = st.session_state.db.get_all_emails()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        email_options = {f"[{e['id']}] {e['subject'][:50]}...": e['id'] for e in emails}
        email_options = {"None - General Query": None, **email_options}
        
        selected = st.selectbox(
            "📧 Select email for context (optional)",
            options=list(email_options.keys())
        )
        st.session_state.selected_email_id = email_options[selected]
    
    with col2:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    # Quick action buttons
    st.markdown("**Quick Actions:**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Summarize Inbox", use_container_width=True):
            summary = agent.get_inbox_summary()
            st.session_state.chat_history.append({"role": "user", "content": "Summarize my inbox"})
            st.session_state.chat_history.append({"role": "assistant", "content": summary})
            st.rerun()
    
    with col2:
        if st.button("📋 Show Tasks", use_container_width=True):
            tasks = agent.get_all_tasks()
            st.session_state.chat_history.append({"role": "user", "content": "Show my action items"})
            st.session_state.chat_history.append({"role": "assistant", "content": tasks})
            st.rerun()
    
    with col3:
        if st.button("⚠️ Urgent Emails", use_container_width=True):
            urgent = agent.get_urgent_emails()
            response = f"Found {len(urgent)} urgent emails:\n\n"
            for email in urgent[:5]:
                response += f"• [{email['category']}] {email['subject']} - {email['sender']}\n"
            st.session_state.chat_history.append({"role": "user", "content": "Show urgent emails"})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col4:
        if st.button("🔍 Search", use_container_width=True):
            st.info("Use the chat below to search: 'Find emails about...'")
    
    st.divider()
    
    # Chat display
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**Agent:** {message['content']}")
            st.markdown("---")
    
    # Chat input
    user_query = st.text_input("💭 Ask the agent...", placeholder="e.g., Summarize this email, What tasks do I have?, Draft a reply")
    
    if st.button("Send", use_container_width=True) and user_query:
        with st.spinner("Thinking..."):
            try:
                # Process query with agent
                response = agent.ask_question(
                    question=user_query,
                    email_id=st.session_state.selected_email_id
                )
                
                # Add to history
                st.session_state.chat_history.append({"role": "user", "content": user_query})
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")


def draft_manager_page():
    st.title("✍️ Draft Manager")
    
    st.markdown("View, edit, and manage your email drafts. **No drafts are actually sent** - this is a safe playground.")
    
    # Get all drafts
    drafts = st.session_state.db.get_all_drafts()
    
    if not drafts:
        st.info("📭 No drafts yet. Generate drafts from the Inbox page or use the Email Agent.")
        return
    
    st.write(f"**{len(drafts)} draft(s)**")
    
    # Display drafts
    for draft in drafts:
        with st.expander(f"**{draft['subject']}**", expanded=False):
            st.markdown(f"**Created:** {format_timestamp(draft['created_at'])}")
            
            if draft.get('original_subject'):
                st.markdown(f"**In Reply To:** {draft['original_subject']}")
            
            # Edit mode
            col1, col2 = st.columns([4, 1])
            
            with col1:
                edited_subject = st.text_input(
                    "Subject",
                    value=draft['subject'],
                    key=f"subj_{draft['id']}"
                )
            
            with col2:
                if st.button("🗑️ Delete", key=f"del_{draft['id']}", use_container_width=True):
                    st.session_state.db.delete_draft(draft['id'])
                    st.success("✅ Deleted")
                    st.rerun()
            
            edited_body = st.text_area(
                "Body",
                value=draft['body'],
                height=200,
                key=f"body_{draft['id']}"
            )
            
            if st.button("💾 Save Changes", key=f"save_{draft['id']}"):
                st.session_state.db.update_draft(draft['id'], edited_subject, edited_body)
                st.success("✅ Draft updated")
            
            # Show metadata if available
            if draft.get('metadata'):
                with st.expander("📊 Metadata"):
                    st.json(draft['metadata'])


# Main app
def main():
    
    # Sidebar navigation
    st.sidebar.title("📧 Email Agent")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Navigation",
        ["📧 Inbox", "🧠 Prompts", "💬 Agent Chat", "✍️ Drafts"],
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    
    # Status indicators
    st.sidebar.markdown("### Status")
    
    emails = st.session_state.db.get_all_emails()
    processed = sum(1 for e in emails if e['processed'])
    st.sidebar.metric("Emails Loaded", len(emails))
    st.sidebar.metric("Processed", f"{processed}/{len(emails)}")
    
    drafts = st.session_state.db.get_all_drafts()
    st.sidebar.metric("Drafts", len(drafts))
    
    action_items = st.session_state.db.get_all_action_items()
    pending = sum(1 for a in action_items if a['status'] == 'pending')
    st.sidebar.metric("Pending Tasks", pending)
    
  
    
    # Route to pages
    if page == "📧 Inbox":
        inbox_viewer_page()
    elif page == "🧠 Prompts":
        prompt_configuration_page()
    elif page == "💬 Agent Chat":
        email_agent_page()
    elif page == "✍️ Drafts":
        draft_manager_page()


if __name__ == "__main__":
    main()
