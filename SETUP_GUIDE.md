# AI-PMS v2.0 - Setup Guide

## 🚀 Complete Installation & Setup Instructions

### Project Structure

```
dataset/
├── frontend/           # React frontend with glassmorphism UI
│   ├── src/
│   │   ├── components/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
├── backend/            # FastAPI backend with LLM integration
│   ├── app.py
│   ├── llm_processor.py
│   ├── data_processor.py
│   ├── wbs_hierarchy.py
│   ├── dependency_analyzer.py
│   ├── resource_analyzer.py
│   ├── transcript_analyzer.py
│   ├── conflict_detector.py
│   ├── risk_predictor.py
│   └── requirements.txt
│
└── datasets/           # Data files
    ├── metro_rail_wbs_data.csv
    ├── progress_review_meeting_transcript.md
    ├── design_coordination_meeting_transcript.md
    └── safety_readiness_briefing_transcript.md
```

---

## Part 1: Backend Setup (Python/FastAPI)

### Step 1: Install Python Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

**Dependencies installed:**
- `fastapi` - Modern Python web framework
- `uvicorn` - ASGI server
- `google-generativeai` - Gemini LLM integration (optional)
- `pandas` - Data processing
- `numpy` - Numerical operations
- `networkx` - Graph algorithms

### Step 2: Configure LLM (Optional but Recommended)

For enhanced AI analysis, set your Gemini API key:

```powershell
# Windows PowerShell
$env:GEMINI_API_KEY="your-api-key-here"

# Or add to .env file
echo GEMINI_API_KEY=your-api-key-here >> .env
```

**How to get Gemini API Key:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and set it as environment variable

**Note:** The system works without an API key using intelligent rule-based fallback!

### Step 3: Start the Backend Server

```powershell
cd backend
python app.py
```

**Or use uvicorn directly:**
```powershell
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Test the API:**
Open browser: `http://localhost:8000`
You should see:
```json
{
  "status": "running",
  "service": "AI-PMS Backend",
  "version": "2.0",
  "llm_status": "Ready (Fallback Mode Available)"
}
```

---

## Part 2: Frontend Setup (React/Vite)

### Step 1: Install Node.js (if not installed)

Download from: https://nodejs.org/ (LTS version recommended)

Verify installation:
```powershell
node --version  # Should show v18+ or v20+
npm --version   # Should show 9+ or 10+
```

### Step 2: Install Frontend Dependencies

```powershell
cd frontend
npm install
```

**Dependencies installed:**
- `react` - UI library
- `framer-motion` - Animation library
- `axios` - HTTP client
- `react-icons` - Icon library
- `vite` - Build tool

### Step 3: Start the Development Server

```powershell
npm run dev
```

**Expected output:**
```
VITE v5.0.0  ready in 500 ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

### Step 4: Open the Application

Open browser: `http://localhost:3000`

---

## Part 3: Quick Start Guide

### Method 1: Start Both Servers Automatically

**Create a startup script:**

```powershell
# start-all.ps1
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python app.py"
Start-Sleep -Seconds 3
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"
```

**Run it:**
```powershell
.\start-all.ps1
```

### Method 2: Manual Start (Recommended for Development)

**Terminal 1 - Backend:**
```powershell
cd backend
python app.py
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

---

## Part 4: Using the Application

### 🎯 Main Features

#### 1. **Project Overview** (Home Page)
- View overall project health
- See completion metrics
- Check resource conflicts
- Quick navigation to other features

#### 2. **Meeting Transcript Analyzer**
- Click "Analyze Meeting" tab
- Paste your meeting transcript
- Click "Load Sample" to try with demo data
- Click "Analyze with AI" to process

**Transcript Format:**
```
**Speaker Name**: Their comments
**Another Speaker**: Their response
...
```

#### 3. **Action Items Dashboard**
- View extracted tasks with priority scores (1-10)
- Filter by urgency: Critical/High/Medium/Low
- Sort by priority or assignee
- Switch between Grid and Kanban views
- Beautiful glassmorphism cards with animations

#### 4. **Conflict Detection**
- See contradicting information
- View parties involved
- Check severity levels
- Review key decisions and risks

---

## Part 5: API Endpoints

### Base URL: `http://localhost:8000`

#### 1. **Health Check**
```
GET /
```

#### 2. **Analyze Transcript**
```
POST /api/analyze-transcript
Content-Type: application/json

{
  "transcript": "Meeting transcript text...",
  "meeting_title": "Weekly Review",
  "meeting_date": "2026-03-11"
}
```

**Response:**
```json
{
  "meeting_title": "Weekly Review",
  "meeting_date": "2026-03-11",
  "action_items": [
    {
      "task": "Fix Task 1315 dependency",
      "assignee": "CE",
      "deadline": "March 15th",
      "priority_score": 9,
      "urgency": "Critical",
      "impact": "High",
      "context": "..."
    }
  ],
  "conflicts": [...],
  "summary": "...",
  "key_decisions": [...],
  "risks_identified": [...],
  "total_action_items": 5,
  "high_priority_count": 2
}
```

#### 3. **Get Project Status**
```
GET /api/project-status
```

#### 4. **Get Resource Conflicts**
```
GET /api/resource-conflicts
```

#### 5. **Get Meeting Insights**
```
GET /api/meeting-insights
```

---

## Part 6: Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`
**Solution:**
```powershell
cd backend
pip install -r requirements.txt
```

**Problem:** Port 8000 already in use
**Solution:**
```powershell
# Find and kill the process
Get-Process -Name "python" | Stop-Process -Force

# Or use a different port
uvicorn app:app --port 8001
```

**Problem:** Can't load CSV data
**Solution:**
- Ensure `datasets/metro_rail_wbs_data.csv` exists
- Check file path in `app.py` (should be `../datasets/`)

### Frontend Issues

**Problem:** `npm: command not found`
**Solution:** Install Node.js from nodejs.org

**Problem:** Port 3000 already in use
**Solution:**
```powershell
# Vite will automatically try 3001, or specify:
npm run dev -- --port 3002
```

**Problem:** API calls failing (CORS error)
**Solution:**
- Ensure backend is running on port 8000
- Check Vite proxy config in `vite.config.js`

### General Tips

1. **Check both terminals are running**
2. **Clear browser cache** if UI doesn't update
3. **Restart both servers** if strange errors occur
4. **Check console** (F12) for JavaScript errors
5. **Check backend logs** for Python errors

---

## Part 7: Advanced Configuration

### Custom Port Configuration

**Backend (`backend/app.py`):**
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Change port here
```

**Frontend (`frontend/vite.config.js`):**
```javascript
export default defineConfig({
  server: {
    port: 3001,  // Change frontend port
    proxy: {
      '/api': {
        target: 'http://localhost:8001',  // Match backend port
        changeOrigin: true
      }
    }
  }
})
```

### Production Build

**Frontend:**
```powershell
cd frontend
npm run build
```

Creates optimized build in `frontend/dist/`

**Serve production build:**
```powershell
npm run preview
```

---

## Part 8: System Requirements

### Minimum:
- **OS:** Windows 10/11, macOS 10.15+, or Linux
- **Python:** 3.8 or higher
- **Node.js:** 18.0 or higher
- **RAM:** 4GB
- **Disk:** 500MB free space

### Recommended:
- **Python:** 3.10+
- **Node.js:** 20.0+
- **RAM:** 8GB+
- **OpenAI API Key** for enhanced analysis

---

## 🎉 You're All Set!

Your AI-Powered Project Management System is ready to use!

**Next Steps:**
1. Try the sample meeting transcript
2. Explore action items with different filters
3. Check out the glassmorphism design
4. Test conflict detection
5. Customize for your own projects

**Need Help?**
- Check the console logs (F12 in browser)
- Review API responses in Network tab
- Ensure both servers are running
- Verify file paths are correct

---

## 📋 Quick Reference

**Start Backend:**
```powershell
cd backend
python app.py
```

**Start Frontend:**
```powershell
cd frontend
npm run dev
```

**Access App:**
```
Frontend: http://localhost:3000
Backend API: http://localhost:8000
API Docs: http://localhost:8000/docs
```

**Key Features:**
- ✨ Glassmorphism UI with backdrop blur
- 🎬 Framer Motion animations
- 🤖 AI-powered transcript analysis
- 📊 Priority scoring (1-10)
- ⚠️ Conflict detection
- 📱 Responsive design
- 🎨 Beautiful translucent cards

Enjoy your intelligent dashboard! 🚀
