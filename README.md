# Recruitment Scoring & Review Dashboard

An internal web-based tool for recruitment workflow. This system allows reviewers to score candidates across various categories and view mock AI-generated summaries, while providing admins full system visibility.

---
## 🚀 Setup and Run Instructions

### Prerequisites
* [Docker](https://docker.com)
* [Docker Compose](https://docker.com)


### Environment Configuration
1. Duplicate the example environment file located at the root directory:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and verify the placeholder variables. *(Note: Authentic secrets are never committed to version control).*

### Launching the System
Run the following command at the repository root to build and spin up both the backend and frontend containers:
```bash
docker-compose up --build
```

Once deployment completes, the services will be active at:
* **Frontend Dashboard**: `http://localhost:5173`
* **Backend API Documentation (Swagger UI)**: `http://localhost:8000/docs`

---

## 🏗️ Architecture Decision Record (ADR)

### ADR 1: Selection of Core Framework (FastAPI)
* **Context**: The backend requires robust async capabilities to manage simulated external LLM generation tasks efficiently alongside typical CRUD operations.
* **Decision**: We chose **FastAPI** over alternatives like Flask or Django.
* **Trade-off**: FastAPI offers excellent native execution speed and automatic OpenAPI documentation, but has a smaller ecosystem of native plugins compared to mature frameworks like Django.

### ADR 2: Data Modeling Strategy (SQLite)
* **Context**: The requirements specify standard transactional candidate and scoring records with soft-delete behaviors, alongside strict time limits for implementation.
* **Decision**: We implemented a relational **SQLite** configuration equipped with specific database indexes.
* **Trade-off**: SQLite is serverless and lightweight, making it incredibly fast for local Docker environments. However, it lacks robust concurrent write scalability for massive horizontal production environments.

### ADR 3: Security & Role-Based Access Control (RBAC)
* **Context**: Reviewers must only see their own scores and are restricted from admin notes, while registrations must never allow arbitrary role configurations.
* **Decision**: Implemented stateless **JWT-based authentication** where user registration workflows strictly hardcode the default role to `reviewer` directly in the backend application logic.
* **Trade-off**: Hardcoding the default registration role prevents malicious role-spoofing from the client side, but it means future role promotions (e.g., granting admin privileges) must be handled through isolated administrative tools or raw database scripts.

---

## 🐛 Debugging Section

### Identified Bug
The provided snippet pulls every single entry from the database into local application memory (`db.execute("SELECT * FROM candidates").fetchall()`) and performs filtering, sorting, and pagination locally using Python list comprehensions.

### Why It Matters at Scale
1. **Memory Exhaustion**: If the `candidates` table grows to hundreds of thousands of applicants, executing a full table scan will consume massive amounts of application RAM, eventually causing the container to crash with Out-Of-Memory (OOM) faults.
2. **Network/I/O Bottlenecks**: Transferring massive raw datasets from the database layer to the application layer for every single paginated page request creates severe internal network latency.

### Correct Architectural Approach
Filtering and pagination must be offloaded directly to the database engine using explicit query constraints. The database should only return the exact slice of records needed for the requested page.

**Refactored Implementation Concept:**
```python
def search_candidates(status: str, keyword: str, page: int, page_size: int):
    offset = (page - 1) * page_size
    
    # Offload filtering and pagination entirely to the database engine
    query = """
        SELECT * FROM candidates 
        WHERE status = :status 
          AND (name LIKE :kw OR email LIKE :kw OR role_applied LIKE :kw)
        LIMIT :limit OFFSET :offset
    """
    params = {
        "status": status, 
        "kw": f"%{keyword}%", 
        "limit": page_size, 
        "offset": offset
    }
    return db.execute(query, params).fetchall()
```

--

## 💭 Learning Reflection
While I've used FastAPI before, handling the 2-second mock AI delay really emphasized the importance of coordinating async backend behavior with crisp frontend loading states so the UI never feels locked up. Given more time, I would set up a real background worker queue like Celery instead of relying on a basic async sleep, which would make the simulation much more production-ready under a heavy load.
---