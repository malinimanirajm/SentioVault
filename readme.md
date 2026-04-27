
# 🏦 SentioVault
**Sentiment-Aware Financial Orchestration**

SentioVault is an AI agent that monitors **Cognitive Load** to protect users from impulsive financial decisions. It combines **Weaviate** for long-term memory and **LangGraph** for behavioral routing.

---

### 🧠 The Logic
- **Analyze:** If the user is calm (Load < 0.8), the agent provides standard insights.
- **Protect:** If the user is stressed (Load > 0.8), the agent triggers **Compliance Mode** to halt high-risk trades.

### 🛠 Quick Start
1. **Configure:** Add `WEAVIATE_URL` and `OPENAI_API_KEY` to your `.env`.
2. **Setup:** Create the schema.
   ```bash
   python setup_vault.py
   ```
3. **Ingest:** Load the 2024-2025 dataset.
   ```bash
   python ingest_data.py
   ```
4. **Run:** Launch the orchestrator.
   ```bash
   python sent_orchestration.py
   ```

### 📂 Architecture
- `setup_vault.py`: Defines the Weaviate schema.
- `ingest_data.py`: Handles batch vectorization of financial records.
- `sent_orchestration.py`: The LangGraph state machine and decision logic.

---
*Built for the future of empathetic FinTech.*