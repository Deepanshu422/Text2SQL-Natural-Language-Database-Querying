# 🛡️ Defensive Enterprise Text2SQL Engine

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-LCEL-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-Fast_Inference-F55036?style=for-the-badge)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

An enterprise-grade Natural Language to SQL engine designed to translate complex business queries into validated database statements. 

Built around a **5-stage defense-in-depth pipeline**, the engine uses deterministic Abstract Syntax Tree (AST) query validation, connection sandboxing, and dynamic schema inspection to block SQL injections, prevent schema hallucinations, and eliminate destructive DDL/DML operations before execution.

![Demo 1](images/demo-1.png)

![Demo 2](images/demo-2.png)

---

## 🏗️ Architectural Decisions & Integrity Guarantees

This service was designed with strict enterprise security and data governance principles in mind:

1. **Deterministic AST Security over Regex:** Instead of fragile keyword blacklists that fail against comments or block legitimate queries (e.g., searching for `'Dropbox'`), `SQLGlot` parses the raw query into a formal syntax tree. It blocks statement stacking (`SELECT ...; DROP ...`) and deterministically rejects any mutating AST node (`exp.Drop`, `exp.Delete`, `exp.Update`, `exp.Alter`).
2. **Hardware/Driver-Level Sandboxing (Least Privilege):** Software checks are not enough. SQLite connects via a strict read-only URI mode (`file:data.db?mode=ro`). Even if an injection bypassed software validation, write operations fail at the operating system file-system level.
3. **Dynamic Schema Introspection:** Hardcoding massive DDL blocks leads to hallucinations and token exhaustion. The `Schema Inspector` queries the live database catalog at runtime to extract only what matters. It feeds the LLM a clean, high-signal structure: `Table: invoices | Columns: invoice_id (TEXT), amount (DECIMAL) | Foreign Keys: org_id -> organizations.org_id`.
4. **Separation of Execution & Synthesis:** The engine uses two distinct LangChain LCEL pipelines powered by ultra-fast **Groq** inference. The first generates raw SQL at temperature 0.0. The second receives the validated row-level data and synthesizes it into executive business prose, decoupling database internals from the end-user UI.
5. **Fail-Safe UI Design:** If an adversarial prompt triggers an AST violation, the orchestrator intercepts the `SQLSecurityError` and returns a clean, safe UI message explaining the blocked constraint, preventing stack trace leaks.

---

## 🧠 System Architecture: The 5-Stage Pipeline

```text
[ Natural Language Question ]
              │
              ▼
    [ 1. Dynamic Schema Inspector ]
    (Extracts live tables, columns, data types, and foreign key relations)
              │
              ▼
    [ 2. LangChain SQL Generator ]
    (LCEL Chain: Groq LLM + Few-Shot SQLite dialect constraints @ temp=0.0)
              │
              ▼
    [ 3. Deterministic AST & Safety Validator ]
    (SQLGlot compilation: enforces strictly 1 statement, root SELECT, zero DDL/DML)
                      │
        ┌─────────────┴────────────────────────┐
        ▼ (Passes)                             ▼ (Fails AST Check)
[ 4. Sandboxed Execution Engine ]          [ Safe UI Error Handshake ]
(SQLAlchemy read-only URI: ?mode=ro)       (Explains violation without leaking internals)
        │
        ▼ (Raw Row Records)
[ 5. Natural Language Synthesizer ]
(LCEL Chain: converts raw JSON rows to executive business prose)
        │
        ▼
[ Streamlit Web Dashboard (:8502) ]
(Business summary + technical audit drawer with validated SQL & data tables)

```

---

## 🚀 Quick Start (Developer Experience)

This project includes a `Makefile` to automate the local development, database seeding, and testing workflow.

### Prerequisites

* Python 3.11+
* [Groq API Key](https://console.groq.com/keys)
* Docker & Docker Compose (Optional, for containerization)

### 1. Initial Setup

```bash
# Clone the repository
git clone [https://github.com/Deepanshu422/Text2SQL-Natural-Language-Database-Querying.git](https://github.com/Deepanshu422/Text2SQL-Natural-Language-Database-Querying.git)

cd text2sql-engine

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make install

```

**Environment Variables (`.env`)**

```env
GROQ_API_KEY=your_actual_groq_api_key_here
DATABASE_URL=sqlite:///data/enterprise.db
MODEL_NAME=openai/gpt-oss-120b
LOG_LEVEL=INFO

```

### 2. The Development Loop

Instead of memorizing complex commands, use the provided `Makefile`:

* `make init-db` — Dynamically seeds the local SQLite database (`data/enterprise.db`) from `data/seed_data.sql`.
* `make test` — Runs the full test suite (AST security bounds & end-to-end integration).
* `make run` — Launches the Streamlit executive dashboard on `http://localhost:8502`.
* `make clean` — Removes cached Python `.pyc` files and bytecode.

*(Run just `make` to see the full help menu in your terminal).*

---

## 🧪 Automated Testing & Security Validation

Enterprise data tooling requires rigorous pre-flight checks. Run the test suite:

```bash
make test

```

The test suite validates:

* **Benign Query Preservation:** Validates that standard queries and multi-table joins pass cleanly.
* **False-Positive Prevention:** Ensures words like `'Dropbox'` or `'deleted_count'` inside literals/aliases do not falsely trigger security trips.
* **Hard DML Rejections:** Direct drops, deletes, and inserts are instantly blocked.
* **Multi-Statement Injection Blocks:** Verifies `SELECT * FROM users; DROP TABLE users;` triggers a critical security exception.

---

## 🐳 Containerized Production Deployment

To run the fully containerized application mapped to port `8502` using Docker Compose (includes unprivileged `appuser` security hardening):

```bash
# Build and launch container in background
make docker-up

# View startup logs and healthcheck status
docker compose logs -f

# Shut down the container safely
make docker-down

```