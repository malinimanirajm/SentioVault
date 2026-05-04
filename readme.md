

# 🧠 Sentio Vault: Psychologically-Aware Financial Agent

Sentio Vault is a next-generation financial intelligence system that correlates fiscal data with psychological metrics. Unlike traditional expense trackers, Sentio uses **Agentic RAG (Retrieval-Augmented Generation)** to analyze the "Cognitive Load" behind transactions, providing safety guardrails when financial decisions are made under high stress.

## 🏗️ Technical Architecture

The system is built on a **Modular Node-Based Architecture** using LangGraph, ensuring stateful, multi-step reasoning.

*   **Vector Vault:** Weaviate v4 (Local) with `text2vec-openai` for semantic retrieval.
*   **Orchestration:** LangGraph state machine with conditional routing and persistence.
*   **State Management:** `TypedDict` state tracking for query context, cognitive load, and relevance grading.

### The Workflow Logic
1.  **Research Node:** Executes a semantic search against the Weaviate collection.
2.  **Grader Node:** A reflective check that evaluates if the retrieved data is relevant to the user query.
3.  **Safety Gate (Conditional):** Analyzes the `cognitive_load_score`. 
    *   If **> 0.8**, it routes to the **Compliance Node** to trigger a safety lockout.
    *   If **< 0.8**, it routes to the **Analyzer Node** for standard financial insights.

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **Vector Database** | Weaviate v4 |
| **Agent Framework** | LangGraph |
| **LLM Integration** | LangChain / OpenAI |
| **Data Handling** | Pandas |

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have [Docker](https://www.docker.com/) installed to run the local Weaviate instance.

### 2. Installation
```bash
git clone https://github.com/your-repo/sentio-vault.git
cd sentio-vault
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file:
```env
OPENAI_API_KEY=your_sk_key_here
```

### 4. Initialization Pipeline
Run the scripts in order to set up the database and ingest your data:
```bash
# Step 1: Create the Weaviate Schema
python setup_vault.py

# Step 2: Clean and Ingest Financial Data
python ingest_data.py

# Step 3: Launch the Agentic Orchestrator
python sentio_orchestrator.py
```

---

## 📊 Data Schema: `SentioTransaction`

The Weaviate collection is configured with the following properties:

| Property | Type | Description |
| :--- | :--- | :--- |
| `transaction_id` | Text | Unique identifier (used for UUIDv5 generation). |
| `category` | Text | Spending category (e.g., Entertainment, Food). |
| `amount` | Number | Transaction value in USD. |
| `cognitive_load_score` | Number | **Critical Metric:** 0.0 to 1.0 (Stress/Load level). |
| `decision_quality` | Number | User-reported or calculated quality of the purchase. |

---

## 🛡️ Safety Features
*   **Circuit Breaker:** The `compliance_node` prevents the LLM from providing financial advice if the retrieved context indicates the user is in a "High Stress" state.
*   **Persistence:** Uses `MemorySaver` to maintain thread-specific history, allowing for multi-turn conversations about financial trends.

---

## 📝 License
This project is licensed under the MIT License - see the LICENSE file for details.