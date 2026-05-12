

# 🧠 Sentio Vault: Psychologically-Aware Financial Agent

Sentio Vault is a next-generation financial intelligence system that correlates fiscal data with psychological metrics. Unlike traditional expense trackers, Sentio uses **Agentic RAG (Retrieval-Augmented Generation)** to analyze the "Cognitive Load" behind transactions, providing safety guardrails and insights when financial decisions are made under high stress.

## 🏗️ Technical Architecture

The system is built on a **Modular Node-Based Architecture** using LangGraph, ensuring stateful, multi-step reasoning and mathematical verification.

* **Hybrid Vector Vault:** Weaviate v4 (Local) with `nomic-embed-text` (Ollama) for private, local semantic retrieval.
* **Cloud Intelligence:** Powered by **Amazon Bedrock (Nova Micro)** for high-speed, cost-effective reasoning.
* **State Management:** `TypedDict` state tracking for query context, User ID isolation, and cognitive load scores.
* **Durable Backups:** Automated transaction mirroring to **AWS S3**.

### The Workflow Logic

1. **Cache Check:** Checks Weaviate for similar past queries to reduce LLM latency and costs.
2. **Research Node:** Executes a **filtered** semantic search (**User_ID + Category**) against the Weaviate collection.
3. **Analyzer Node:** Generates financial insights, specifically flagging high `cognitive_load_score` entries.
4. **Reflection Node (Self-Correction):** A secondary agentic pass that critiques the analysis for mathematical accuracy and safety compliance before reaching the user.

---

## 🛠️ Tech Stack

| Component | Technology |
| --- | --- |
| **Agent Framework** | LangGraph |
| **LLM Reasoning** | Amazon Bedrock (Nova Micro) |
| **Vector Database** | Weaviate v4 (Local) |
| **Embeddings** | Ollama (Nomic-Embed-Text) |
| **API Framework** | FastAPI |
| **Frontend UI** | Streamlit |
| **Cloud Storage** | AWS S3 |

---

## 🚀 Getting Started

### 1. Prerequisites

* [Docker](https://www.docker.com/) (to run Weaviate)
* [Ollama](https://ollama.com/) (running `nomic-embed-text` model)
* AWS CLI configured with Amazon Bedrock access.

### 2. Environment Setup

Create a `.env` file in the root directory (this file is git-ignored for security):

```env
AWS_REGION="us-east-1"
S3_BUCKET_NAME="your-unique-vault-name"
WEAVIATE_PORT=8081

```

### 3. Initialization Pipeline

Execute the scripts in order to establish the environment:

```bash
# Step 1: Initialize the HCI-Ready Schema
python setup_vault.py

# Step 2: Backup to S3 and Ingest Local Data
python ingest_data.py

# Step 3: Launch the Backend API
python main.py

# Step 4: Start the Streamlit Dashboard
streamlit run app.py

```

---

## 📊 Data Schema: `SentioTransaction`

The system processes 22 distinct parameters, focusing on these core properties for agentic reasoning:

| Property | Type | Description |
| --- | --- | --- |
| `user_id` | Text | Ensures strict data isolation in multi-user environments. |
| `category` | Text | Primary filter for contextual retrieval. |
| `amount` | Number | Transaction value in USD. |
| `cognitive_load_score` | Number | **HCI Metric:** 0.0 to 1.0 (Stress/Mental effort during purchase). |
| `decision_quality` | Number | Qualitative assessment of the financial choice. |

---

## 🛡️ Safety & Privacy

* **Multi-Tenant Isolation:** Uses Weaviate's `Filter` class to ensure a user can **only** retrieve their own financial data.
* **Local-First Retrieval:** Raw transaction data and embeddings remain local; only relevant anonymized context is passed to the LLM.
* **Reflective Logic:** The `reflection_node` acts as a guardrail, catching hallucinations or calculation errors before they reach the user interface.

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.