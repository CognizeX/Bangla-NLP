# **TITLE : `Not-Selected`**

![NLP Library](public/nlp-lib.jpg)

> This Project Maintain by Github Action (CI/CD) for NLP Model Deployment and API Testing.

## **Account**

- **Email**: [nlp.aiub.101@gmail.com](mailto:nlp.aiub.101@gmail.com)
- **Password**: **Nlp101!##**

## NLP Project Timeline

| ID | Phase | Start Date | End Date | Status |
| --- | --- | --- | --- | --- |
| 1 | Planning | April 13 | April 16 | 🟡 |
| 6 | Coding | April 13 | April 28 | 🎯 |
| 2 | Design | April 17 | April 19 | ⏳ |
| 3 | Backend | April 20 | April 22 | ⏳ |
| 4 | Frontend | April 23 | April 25 | ⏳ |
| 5 | Testing | April 26 | April 27 | ⏳ |
| 6 | Delivery | April 28 | April 28 | ⏳ |

> Completed (✅), In Progress (🟡), Pending (⏳), Milestone (🎯)

## **Course Details**

- **Name**: Natural Language Processing (**NLP**)
- **Code**: CSC 4233
- **Institution**: American International University-Bangladesh (**AIUB**)
- **Semester**: Spring 2025-2026
- **Instructor**: [Dr. Md. Saef Ullah Miah](https://ping543f.github.io)

## System Requirements

- **Google Colab**: For online codebase.
- **Python**: 3.12+
- **Docker Compose**: For multi-container orchestration
- System: Windows 10/11 64-bit

### Included AI / Web Stack

- `FastAPI` for backend APIs
- `TensorFlow` for deep learning workflows
- `scikit-learn` for classical ML and evaluation
- `FastAPI Cloud` for cloud deployment support

## Server Hosting

- **Only Backend**: [FastAPI](https://fastapicloud.com)
- **Frontend**: [Next.js](https://nextjs.org/)
- **Database**: [Supabase](https://supabase.com/)
- **Vector DB**: [Pinecone](https://www.pinecone.io/)
- **Model Hosting**: [HuggingFace Spaces](https://huggingface.co/spaces) or [Replicate](https://replicate.com/)

## Docker Setup (Windows 10/11)

### PROJECT STRUCTURE: `MVC`

## 1.0 `🔥 Build`: Docker Contaner

```bash
docker build -t nlp:latest .
```

## 1.1 `🚀 Run`: Docker Contaner

```bash
# CPU
docker run -it nlp:latest /bin/bash
# GPU
docker run --gpus all -it nlp:latest
# Production
docker run -d -p 8000:8000 nlp:latest
```

### 1.2 Check Libraries ⚖️

```bash
docker exec -it nlp-container bash & pip list | grep -E 'transformers|torch|torch-geometric|fastapi|streamlit|tensorflow|tensorboard|sklearn|nltk'
```

### 1.3 Run 🌐: `FastAPI`, `Streamlit`, `TensorBoard` & `Jupyter Notebook` ✅

```bash
docker compose up -d --build && docker compose exec -d nlp streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8501 && docker compose exec -d nlp tensorboard --logdir /app/runs --host 0.0.0.0 --port 6006 && docker compose up -d --build jupyter && docker compose ps
```

### 1.4 Watch: `Logs ✨`

```bat
docker compose logs -f nlp
docker compose logs -f jupyter
```

### 🔗 Access services

- [Fastapi](http://localhost:8000)
- [Swagger UI](http://localhost:8000/docs)
- [Streamlit](http://localhost:8501)
- [TensorBoard](http://localhost:6006)
- [Jupyter Notebook](http://localhost:8888/)

### 1.8 📊 Database

Create table as Like **seeding data on Database**

```bash
docker exec -it nlp-postgres psql -U nlp -d nlpdb -c "CREATE TABLE IF NOT EXISTS documents (id SERIAL PRIMARY KEY, title TEXT, content TEXT);"
```

- **Add Row:**

```bash
docker exec -it nlp-postgres psql -U nlp -d nlpdb -c "INSERT INTO documents (title, content) VALUES ('doc1', 'sample text');"
```

- Create vector collection (**Qdrant, size=384**):

```bash
curl -X PUT "http://localhost:6333/collections/docs" -H "Content-Type: application/json" -d "{\"vectors\":{\"size\":384,\"distance\":\"Cosine\"}}"
```

- **Seed Vector Data**

```bash
curl -X PUT "http://localhost:6333/collections/docs/points" -H "Content-Type: application/json" -d "{\"points\":[{\"id\":1,\"vector\":[0.1,0.2,0.3,0.4],\"payload\":{\"title\":\"doc1\"}}]}"
```

### Test API (Unit Test)

```bash
cd tests & pytest test_api.py
# or in docker
docker compose exec nlp sh -lc "cd /app && PYTHONPATH=/app pytest -q"
```

> Test API with `Manualy` for High Stabalaty and Performance
