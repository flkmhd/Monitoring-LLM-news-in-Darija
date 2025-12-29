# 🚀 Veille LLM Agent System

An intelligent AI-powered news monitoring system that automatically fetches the latest LLM/AI news, processes them through 4 specialized agents using Google Gemini, and sends you the top 5 ideas in Moroccan Darija via WhatsApp every day.

## 📋 Overview

This FastAPI backend:
1. **Fetches** the 20 most recent LLM/AI news articles from TheNewsAPI.com
2. **Processes** them through a 4-agent pipeline powered by Google Gemini 2.0 Flash
3. **Delivers** the top 5 ideas in Darija via Telegram using a Bot
4. **Runs automatically** every day at 9:00 AM

## 🏗️ Architecture

```
TheNewsAPI → Agent 1 (Analyze) → Agent 2 (Extract Ideas) → 
Agent 3 (Select Top 5) → Agent 4 (Translate to Darija) → Telegram Bot
```

### Agent Pipeline

- **Agent 1 - News Analyzer**: Categorizes articles and scores technical relevance
- **Agent 2 - Idea Extractor**: Extracts ~10 innovative ideas from articles
- **Agent 3 - Reflection Agent**: Validates and selects the top 5 ideas
- **Agent 4 - Darija Translator**: Translates ideas to Moroccan Darija

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **LLM**: Google Gemini 2.0 Flash (free tier)
- **News API**: TheNewsAPI.com
- **Messaging**: Telegram Bot API
- **Scheduling**: APScheduler
- **Language**: Python 3.10+

## 📦 Installation

### 1. Clone or navigate to the project directory

```bash
cd veille-llm-backend
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your API keys
```

Required API keys:
- **TheNewsAPI**: Get from [thenewsapi.com](https://www.thenewsapi.com/)
- **Google Gemini**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

## ⚙️ Configuration

Edit your `.env` file:

```env
# TheNewsAPI.com
NEWSAPI_KEY=your_actual_key_here
NEWSAPI_LIMIT=20

# Google Gemini
GEMINI_API_KEY=your_actual_key_here

# Telegram Bot Keys (See "How to create a Bot" below)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Scheduling
SCHEDULE_TIME=09:00
TIMEZONE=Europe/Paris

# Logging
LOG_LEVEL=INFO
```

## 🚀 Running the Application

### Development mode

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Production mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📡 API Endpoints

### `GET /`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "service": "Veille LLM Agent System",
  "timestamp": "2025-12-23T21:00:00"
}
```

### `POST /trigger`
Manually trigger the pipeline

**Response:**
```json
{
  "message": "Pipeline executed successfully",
  "execution": {
    "execution_id": "uuid",
    "started_at": "timestamp",
    "completed_at": "timestamp",
    "status": "completed",
    "articles_fetched": 20,
    "ideas_extracted": 10,
    "telegram_sent": true
  }
}
```

### `GET /status`
Get current pipeline status

**Response:**
```json
{
  "is_running": false,
  "last_execution": { ... },
  "next_scheduled_run": "2025-12-24T09:00:00+01:00"
}
```

### `GET /history?limit=10`
Get execution history

**Response:**
```json
{
  "count": 10,
  "executions": [ ... ]
}
```

## 🧪 Testing

### Test the complete pipeline

```bash
# Start the server
uvicorn main:app --reload

# In another terminal, trigger manually
curl -X POST http://localhost:8000/trigger
```

### Check pipeline status

```bash
curl http://localhost:8000/status
```

### View execution history

```bash
curl http://localhost:8000/history
```

## 🤖 How to Create a Telegram Bot

To receive your daily news on Telegram, follow these simple steps:

### 1. Create the Bot 🤖
1. Open Telegram and search for **[@BotFather](https://t.me/BotFather)** (the official bot builder).
2. Click **Start** or type `/start` to begin the conversation.
3. Send the command `/newbot` to create a new bot.
4. **Name**: BotFather will ask for a name. Enter something like `My Tech News Bot`.
5. **Username**: Next, it will ask for a username. It **must** end in `bot` (e.g., `VeilleLLM_bot`).
6. 🎉 **Success!** BotFather will send you a message with your **TOKEN**.
   👉 **Copy this token** (it looks like `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`) into your `.env` file:
   ```env
   TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
   ```

### 2. Get Your Chat ID 🆔
1. Search for your new bot by its username and click **Start**.
   > **Important**: You MUST send `/start` to your own bot first, otherwise it cannot message you.
2. Now, search for **[@userinfobot](https://t.me/userinfobot)** and click **Start**.
3. It will reply with your details. Look for the `Id` field number.
   👉 **Copy this number** (e.g., `123456789`) into your `.env` file:
   ```env
   TELEGRAM_CHAT_ID=123456789
   ```

### 3. Verify ✅
Run the pipeline manually to test:
```bash
python run_pipeline.py
```
You should receive a message instantly!

## 🏃‍♂️ Daily Execution (Script Mode)

You can run the pipeline as a standalone script without keeping the server open. This is perfect for scheduling with Windows Task Scheduler.

### 1. Run manually
```bash
# Activate venv
venv\Scripts\activate

# Run the script
python run_pipeline.py
```

### 2. Schedule on Windows
1. Open **Task Scheduler**
2. Create Basic Task -> "Veille LLM Daily"
3. Trigger: Daily at 9:00 AM
4. Action: Start a program
   - Program/script: `path\to\python.exe` (from your venv)
   - Arguments: `run_pipeline.py`
   - Start in: `path\to\your\project\folder`

## 📅 Scheduling

The pipeline runs automatically every day at the configured time (default: 9:00 AM Europe/Paris).

To change the schedule:
1. Edit `SCHEDULE_TIME` in `.env` (format: `HH:MM`)
2. Edit `TIMEZONE` if needed
3. Restart the application

## 📊 Logging

Logs are written to:
- **Console**: Real-time output
- **File**: `app.log` (persistent)

Log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`

Set via `LOG_LEVEL` in `.env`

## 🔧 Troubleshooting

### "Missing required environment variables"
- Make sure you've copied `.env.example` to `.env`
- Fill in all required API keys

### "Gemini API call failed"
- Check your `GEMINI_API_KEY` is valid
- Verify you haven't exceeded the free tier limit (60 RPM)

### "Telegram message not received"
- Verify your Bot Token and Chat ID
- Check if you have started a conversation with the bot (`/start`)
- Check logs for specific API error messages

### "No news articles fetched"
- Check your `NEWSAPI_KEY` is valid
- Verify you haven't exceeded the free tier limit (200 requests/day)

## 📈 API Rate Limits

- **Gemini Free Tier**: 60 requests/minute (we use ~4/day ✓)
- **TheNewsAPI Free**: 200 requests/day (we use 1/day ✓)
- **Telegram**: No limit for reasonable bot usage (we use 1/day ✓)

## 🗂️ Project Structure

```
veille-llm-backend/
├── main.py                 # FastAPI app & pipeline orchestration
├── config.py               # Configuration & env variables
├── models.py               # Pydantic models
├── prompts.py              # All agent prompts
├── utils.py                # Utility functions
├── scheduler.py            # APScheduler setup
├── agents/
│   ├── news_fetcher.py     # Agent 1: News analysis
│   ├── idea_extractor.py   # Agent 2: Idea extraction
│   ├── reflection_agent.py # Agent 3: Top 5 selection
│   └── darija_translator.py# Agent 4: Darija translation
├── services/
│   ├── newsapi_service.py  # TheNewsAPI integration
│   ├── gemini_service.py   # Google Gemini integration
│   └── telegram_service.py # Telegram Bot integration
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🤝 Contributing

This is a personal project, but feel free to fork and customize for your needs!

## 📄 License

MIT License - feel free to use and modify as needed.

## 🎯 Next Steps

After setup:
1. ✅ Test each service individually
2. ✅ Run the pipeline manually via `/trigger`
3. ✅ Verify Telegram message delivery
4. ✅ Let the scheduler run for a few days
5. ✅ Adjust prompts based on results

---

**Built with ❤️ using FastAPI, Google Gemini, and Telegram**
