# TaxSaarthi

TaxSaarthi is an explainable financial decision-support prototype for the InnoVision hackathon. It analyzes a CSV transaction statement using transparent rule-based logic and shows summaries, categories, and potential issues.

> This is an informational prototype. It is not certified tax advice, financial advice, fraud detection, or tax filing software.

## Project structure

```text
backend/     FastAPI API and Pandas analysis services
frontend/    React + Vite + Tailwind dashboard
```

## Requirements

- Python 3.10 or newer
- Node.js and npm

## Run the backend

Open a terminal in the project root:

```powershell
Set-Location .\backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend URLs:

- Health check: http://127.0.0.1:8000/health
- API docs: http://127.0.0.1:8000/docs

## Run the frontend

Open a second terminal in the project root:

```powershell
Set-Location .\frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Open http://127.0.0.1:5173/ in your browser.

## Sample data

Upload `backend/sample_data/sample_transactions.csv` from the dashboard.

CSV files currently require these columns:

```text
date,description,amount,type
```

The `type` value should be `income` or `expense`.

## Current API

- `GET /health`
- `POST /api/upload`
- `GET /api/analyze`

## Current analysis

The MVP currently provides:

- Income, expense, and savings totals
- Rule-based transaction categories
- Category explanations
- Potentially high expense alerts
- Repeated transaction alerts
- Suggested next steps

Analysis is currently stored in memory for the running backend process. SQLite persistence, report export, and human review are planned next.
