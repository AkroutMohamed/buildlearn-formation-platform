# BuildLearn

BuildLearn is a French-language learning platform focused on construction products. It includes public course discovery, student learning and quizzes, instructor course management, and an administrator workspace. A retrieval-augmented chat feature uses Ollama and Qdrant to answer questions from acquired product documents.

## Stack

- Frontend: Next.js 16, React 19, TypeScript, Tailwind CSS 4
- Backend: FastAPI, SQLAlchemy 2, PostgreSQL, Alembic
- AI: Ollama and Qdrant

## Project layout

- `frontend/src/`: pages, components, services, and types
- `backend/app/`: API routes, models, services, repositories, and AI pipeline
- `backend/alembic/`: database migrations
- `backend/tests/`: Python tests
- `backend/scripts/`: maintenance and evaluation scripts
- `docs/ai/`: architecture and evaluation notes

## Local setup

Install and run PostgreSQL, Qdrant, and Ollama separately. Create a database, then configure the backend:

```powershell
cd backend
Copy-Item .env.example .env
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
.\venv\Scripts\alembic upgrade head
.\venv\Scripts\uvicorn app.main:app --reload
```

Set a unique `JWT_SECRET_KEY` and the correct `DATABASE_URL` in `backend/.env`. See `docs/ai/AI_ARCHITECTURE.md` for the AI service setup and data pipeline.

In another terminal, configure and run the frontend:

```powershell
cd frontend
Copy-Item .env.local.example .env.local
npm ci
npm run dev
```

The frontend opens at `http://localhost:3000`; the API defaults to `http://127.0.0.1:8000`.

## Checks

```powershell
cd backend
.\venv\Scripts\python -m pytest -q

cd ..\frontend
npm run lint
npx tsc --noEmit
```

Local credentials, acquired data, uploads, Qdrant storage, dependencies, and build output are excluded from this repository.
