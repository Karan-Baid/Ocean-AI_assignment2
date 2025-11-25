# Email Productivity Agent

A prompt-driven email productivity agent built with Python and Streamlit. This application processes emails using AI (Groq's fast LLMs) to automatically categorize messages, extract action items, generate reply drafts, and provide intelligent chat-based inbox interaction.



## 🌟 Features

### Core Functionality
- **📧 Email Inbox Management**: Load and view mock emails with filtering and search
- **🤖 AI-Powered Categorization**: Automatically categorize emails (Important, To-Do, Spam, Newsletter, etc.)
- **📋 Action Item Extraction**: Identify tasks and deadlines from emails using LLM
- **✍️ Auto-Draft Replies**: Generate professional reply drafts based on email content
- **💬 Chat-Based Agent**: Ask questions about your inbox, search emails, and get summaries
- **🧠 Customizable Prompts**: Configure and modify AI behavior through prompt templates

### Safety Features
- **🚫 No Auto-Send**: All replies are saved as drafts only - nothing is sent automatically
- **🔒 Draft-Only Mode**: Safe environment for testing and reviewing AI-generated content
- **⚠️ Error Handling**: Graceful handling of API errors and rate limits

## 📋 Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Using the Mock Inbox](#using-the-mock-inbox)
- [Configuring Prompts](#configuring-prompts)
- [Usage Examples](#usage-examples)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

- **Python 3.8 or higher**
- **Groq API Key** (sign up at [Groq Console](https://console.groq.com) - **FREE** tier available!)



## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/email-agent.git
cd email-agent
```

Or download and extract the ZIP file, then navigate to the project directory:

```bash
cd email-agent
```

### 2. Create a Virtual Environment (Recommended)


```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `streamlit` - Web UI framework
- `langchain-groq` - Groq API client via LangChain
- `langchain-core` - LangChain core components
- `python-dotenv` - Environment variable management
- `pandas` - Data manipulation


## ⚙️ Configuration

### 1. Set Up Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

### 2. Add Your Groq API Key

Edit the `.env` file and add your API key:

```env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
GROQ_MODEL=llama3-70b-8192
```

**Getting a FREE Groq API Key:**
1. Go to [Groq Console](https://console.groq.com)
2. Sign up or log in (free account available!)
3. Navigate to API keys section
4. Create a new API key
5. Copy and paste it into your `.env` file


**Why Groq?**
- ⚡ **Blazing fast** - 10-100x faster than traditional LLM APIs
- 🆓 **Free tier** - Generous free quota for testing
- 🎯 **High quality** - State-of-the-art open-source models


## 🚀 Running the Application

Start the Streamlit application:

**Option 1: Using the start script**
```bash
./start.sh
```

**Option 2: Direct command**
```bash
streamlit run app.py
```

The application will open in your browser at: **http://localhost:8501**

### Alternative: Run on Custom Port

```bash
streamlit run app.py --server.port 8080
```


## 📧 Using the Mock Inbox

The application includes a mock inbox with 20 diverse sample emails.

### Loading the Mock Inbox

1. Navigate to the **📧 Inbox** page
2. Click the **"🔄 Load Mock Inbox"** button
3. The system will load 20 sample emails into the database

### Mock Inbox Contents

The mock inbox (`data/mock_inbox.json`) includes:

- **3 Meeting Requests** - Including agenda requests and calendar invites
- **4 Newsletters** - Tech news, promotional emails, course offerings
- **3 Spam Messages** - Lottery scams, suspicious links
- **5 Task Requests** - Bug fixes, code reviews, documentation updates
- **3 Project Updates** - Status reports, milestone reviews
- **2 Personal Emails** - Family invitations, informal messages

### Adding Custom Emails

Edit `data/mock_inbox.json` and add your own email objects:

```json
{
  "id": 21,
  "sender": "example@company.com",
  "subject": "Your Custom Subject",
  "body": "Email body content here...",
  "timestamp": "2025-11-22T10:00:00",
  "category": null
}
```

Then reload the mock inbox in the application.

## 🧠 Configuring Prompts

Prompts are the "brain" of the agent and control how the AI processes emails.

### Accessing the Prompt Panel

1. Navigate to **🧠 Prompts** in the sidebar
2. Click **"📥 Load Default Prompts"** (first time only)
3. Use tabs to edit different prompt types

### Prompt Types

#### 1. **Categorization Prompt**
Controls how emails are categorized into: Important, To-Do, Newsletter, Spam, etc.

**Default Prompt:**
```
Categorize this email into one of the following categories: Important, Newsletter, 
Spam, To-Do, Project Update, Meeting Request, Personal. Choose the most appropriate 
category based on the email content. Respond with ONLY the category name.
```


#### 2. **Action Item Extraction Prompt**
Extracts tasks and deadlines from email content.

**Default Prompt:**
```
Extract all actionable tasks from this email. For each task, identify what needs 
to be done and any mentioned deadline. Return your response as a JSON array with 
this format: [{"task": "...", "deadline": "..."}]
```


#### 3. **Auto-Reply Prompt**
Generates draft responses to emails.

**Default Prompt:**
```
Draft a professional and friendly reply to this email. Guidelines:
- If it's a meeting request, acknowledge it and ask for an agenda
- If it's a task request, confirm receipt and provide a timeline
- Keep the response concise (2-4 sentences)
- Use a professional but warm tone
```


#### 4. **Summary Prompt**
Creates concise summaries of emails.

**Customization Tips:**
- Adjust summary length
- Focus on specific aspects (decisions, actions, deadlines)
- Request bullet points or paragraph format

### Testing Prompts

After modifying a prompt:
1. Click **"💾 Save"** to save changes
2. Go to **📧 Inbox**
3. Click **"🔄 Process"** on an email to test the new prompt
4. Review the results and iterate

## 📖 Usage Examples

### Example 1: Processing Emails

1. **Load** the mock inbox
2. Click **"⚡ Process All Emails"** to categorize all emails at once
3. Expand individual emails to see:
   - Assigned category
   - Extracted action items (for To-Do emails)
   - AI-generated summary

### Example 2: Generating Reply Drafts

1. Open an email in the **📧 Inbox**
2. Click **"✍️ Draft Reply"**
3. Navigate to **✍️ Drafts** to view and edit the generated draft
4. Modify the subject or body as needed
5. Click **"💾 Save Changes"** to update

### Example 3: Using the Chat Agent

Navigate to **💬 Agent Chat** and try these queries:

**General Inbox Queries:**
```
- "Summarize my inbox"
- "Show me all urgent emails"
- "What tasks do I need to complete?"
- "Find emails about the Q4 planning meeting"
```

**Email-Specific Queries:**
1. Select an email from the dropdown
2. Ask questions like:
   ```
   - "Summarize this email"
   - "What does the sender want me to do?"
   - "Draft a reply declining this meeting"
   - "Extract all deadlines mentioned"
   ```

**Quick Actions:**
- Click **"📊 Summarize Inbox"** for inbox overview
- Click **"📋 Show Tasks"** for all action items
- Click **"⚠️ Urgent Emails"** for Important/To-Do emails

### Example 4: Searching and Filtering

**Search by Keywords:**
- Type "bug" in search box to find all bug-related emails
- Search "meeting" to find meeting requests

**Filter by Category:**
- Select "To-Do" to see only actionable emails
- Select "Spam" to review flagged spam

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────┐
│         Streamlit UI (app.py)           │
│  ┌───────┬────────┬────────┬─────────┐ │
│  │Inbox  │Prompts │ Chat   │ Drafts  │ │
│  └───────┴────────┴────────┴─────────┘ │
└──────────────┬──────────────────────────┘
               │
        ┌──────▼──────────────────────────┐
        │       Backend Services           │
        │  ┌────────────────────────────┐ │
        │  │  Email Processor           │ │
        │  │  - Categorization          │ │
        │  │  - Action Item Extraction  │ │
        │  │  - Summary Generation      │ │
        │  └────────────────────────────┘ │
        │  ┌────────────────────────────┐ │
        │  │  Email Agent               │ │
        │  │  - Query Processing        │ │
        │  │  - Inbox Search            │ │
        │  │  - Draft Generation        │ │
        │  └────────────────────────────┘ │
        │  ┌────────────────────────────┐ │
        │  │  LLM Service               │ │
        │  │  - Groq Integration        │ │
        │  │  - Error Handling          │ │
        │  │  - Retry Logic             │ │
        │  └────────────────────────────┘ │
        │  ┌────────────────────────────┐ │
        │  │  Database (SQLite)         │ │
        │  │  - Emails, Prompts         │ │
        │  │  - Drafts, Action Items    │ │
        │  └────────────────────────────┘ │
        └─────────────────────────────────┘
```

### Data Flow

1. **Email Ingestion**: Mock inbox JSON → Database
2. **Processing**: Email → LLM (with prompt) → Categorization/Actions/Summary → Database
3. **Chat Interaction**: User query + Email context → LLM → Response
4. **Draft Generation**: Email + Reply prompt → LLM → Draft → Database

## 📁 Project Structure

```
email-agent/
├── app.py                      # Main Streamlit application
├── start.sh                   # Quick start script
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variable template
├── .env                       # Your API keys (not in git)
├── README.md                  # This file
├── backend/
│   ├── __init__.py
│   ├── database.py            # SQLite database operations
│   ├── llm_service.py         # Groq API integration
│   ├── email_processor.py     # Email processing pipeline
│   └── agent.py               # Chat agent logic
├── data/
│   ├── mock_inbox.json        # 20 sample emails
│   ├── default_prompts.json   # Default prompt templates
│   └── email_agent.db         # SQLite database (auto-created)
└── utils/
    ├── __init__.py
    └── helpers.py             # Utility functions
```


## 🐛 Troubleshooting

### Issue: "Groq API key not found"

**Solution:**
1. Ensure `.env` file exists in the project root
2. Verify your API key is correctly set: `GROQ_API_KEY=gsk_...`
3. Restart the Streamlit application

### Issue: "Rate limit exceeded"

**Solution:**
- Groq has generous rate limits on the free tier
- Wait a moment and try again
- The application has built-in retry logic with exponential backoff
- For heavy usage, check your quota at [Groq Console](https://console.groq.com)


### Issue: "No emails found"

**Solution:**
1. Click **"🔄 Load Mock Inbox"** on the Inbox page
2. Check that `data/mock_inbox.json` exists
3. Verify the file contains valid JSON

### Issue: "Failed to categorize email"

**Possible Causes:**
- API key is invalid or expired
- Network connectivity issues
- Prompt is malformed

**Solution:**
1. Check your API key in `.env`
2. Verify internet connection
3. Go to **🧠 Prompts** and reload default prompts

### Issue: "Import errors when running app"

**Solution:**
```bash

pip install -r requirements.txt --force-reinstall
```


### Issue: Database errors

**Solution:**
```bash
# Delete and recreate database
rm data/email_agent.db
# Restart the application - it will recreate the database
streamlit run app.py
```



## 💡 Tips for Best Results

1. **Use llama-3.1-8b-instant** for best accuracy (it's very fast on Groq!)
2. **Try mixtral-8x7b-32768** for complex reasoning tasks
3. **Customize prompts** to match your workflow and terminology
4. **Process emails individually** first to understand AI behavior
5. **Review drafts** before using them (AI is helpful but not perfect)
6. **Iterate on prompts** based on results


## 📊 Key Features

This project demonstrates:

✅ **Email Processing**: Automated categorization and action item extraction  
✅ **Prompt-Driven AI**: Customizable prompts control all AI behavior  
✅ **Clean Architecture**: Modular code with backend services  
✅ **Interactive UI**: Streamlit interface with multiple views  
✅ **Safety First**: Draft-only mode with no automatic sending


## 🚀 Future Enhancements

Potential improvements:
- Real email integration (Gmail, Outlook APIs)
- Email thread tracking
- Priority scoring
- Calendar integration for meeting requests
- Attachment handling
- Multi-user support
- Advanced search with semantic similarity

---

**Built using Python, Streamlit, LangChain, and Groq**


