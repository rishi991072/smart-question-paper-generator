# Smart Question Paper Generator — Offline Edition

A simple full-stack college project that creates question-paper drafts from a textbook PDF without MongoDB, paid APIs, or API keys.

## Stack
- React + Vite frontend
- Python FastAPI backend
- SQLite local database (created automatically)
- PyMuPDF for PDF text extraction
- Offline keyword extraction and question templates
- ReportLab for PDF export

## Run on Windows

### Backend
```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```
API docs: http://localhost:8000/docs

### Frontend (new terminal)
```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```
Open http://localhost:5173

Default login: `admin` / `ChangeMe123!` (change in backend/.env).

## How generation works
The backend extracts text from the PDF, identifies important terms and sentences, and creates descriptive prompts plus fill-in-the-statement MCQs using local templates. It then arranges questions into configured sections and 1–4 sets, and exports PDFs. No external model or API is called.

## Limitations
- This is a rule-based offline generator, NOT a true generative AI/LLM system. Generated questions can be repetitive or weak; review and edit them before official use.
- MCQ distractors are keyword-based and may not always be plausible.
- Scanned/image-only PDFs are not supported; OCR is not included.
- Topic distribution is best-effort keyword balancing, not guaranteed semantic unit classification.
- SQLite file `backend/question_papers.db` is created automatically. No database installation is needed.


### Access note
Login and token authentication have been removed for this local college-project version. Anyone who can access the running frontend/API can upload PDFs, generate papers, and download results. Do not expose this version publicly or deploy it to an internet-accessible server without adding access control.
