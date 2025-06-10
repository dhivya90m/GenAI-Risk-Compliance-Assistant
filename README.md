# GenAI Risk & Compliance Assistant

A multi-agent GenAI solution for financial compliance, risk analytics, and AI-powered Q&A—built natively on Snowflake with a modern Streamlit dashboard.

---

## Overview

This project demonstrates how to combine advanced data engineering, Retrieval-Augmented Generation (RAG), and Large Language Models (LLMs) to automate complex compliance and risk workflows on real SEC financial data. Inspired by the GenAI strategies of leading financial institutions, it showcases:

- **Automated compliance checks** and risk flagging
- **RAG-powered, context-rich Q&A** using Snowflake Cortex LLMs
- **Executive-ready summaries** of company filings
- **Interactive analytics dashboard** for business and technical users
- **Enterprise-grade security and auditability**

---

## Architecture

- **Data Layer:** SEC XBRL tables (`NUM`, `PRE`, `SUB`, `TAG`) and aggregated views (e.g., `COMPANY_CHUNKS_PROD`)
- **AI/ML Layer:** Snowflake Cortex for LLM-based summarization, semantic search, and RAG Q&A
- **Application Layer:** Streamlit app with multi-agent logic (compliance, risk, summarization) and analytics
- **Security:** All access and actions are managed by Snowflake roles and logging

For a detailed system diagram and data flow, see [`Docs/architecture.md`](Docs/architecture.md).

---

## Key Features

- **Multi-Agent Orchestration:**  
  - Compliance Agent: Flags missing or non-compliant filings  
  - Risk Agent: Detects financial anomalies and losses  
  - Summarization Agent: Generates audit-ready, plain-English summaries  
- **RAG-Powered Q&A:**  
  - Ask any question about company filings in natural language  
  - Retrieves relevant context and generates answers with LLMs  
- **Advanced Analytics:**  
  - Top companies by revenue, largest losses, anomaly detection, and interactive trend charts  
- **Streamlit Dashboard:**  
  - Intuitive, multi-tab UI for business users and analysts  
  - AI-powered insights and interactive data exploration

---

## Quick Start

1. **Clone this repo:**
2. **Install dependencies:**
   3. **Configure your Snowflake credentials.**
- [How to set up Snowflake credentials](https://docs.snowflake.com/en/user-guide/python-connector-example)
4. **Run the app:**
streamlit run app/streamlit_app.py


---

## Data Model (Plain English)

| Table | What It Stores                               | Key Columns                  | Example Use                                                      |
|-------|----------------------------------------------|------------------------------|------------------------------------------------------------------|
| NUM   | All reported financial numbers (facts)       | ADSH, TAG, VALUE, DDATE      | Revenue, net income, assets, etc. for each filing                |
| PRE   | How financial facts are organized in statements | ADSH, TAG, PLABEL, STMT      | Order/label of facts in the balance sheet, income statement, etc.|
| SUB   | Company and filing metadata                  | ADSH, NAME, FORM, PERIOD     | Which company, which report, when filed                          |
| TAG   | Definitions for each financial fact (tag)    | TAG, TLABEL, DATATYPE        | What “NetIncomeLoss” or “Assets” means                           |

---

## 📸 Screenshots

![Dashboard Screenshot](images/dashboard_screenshot.png)

---

## Documentation

- [System Architecture](docs/architecture.md)
- [Data Model](docs/data_model.md)
- [SQL Setup Scripts](sql/)

---

## Contributing

Pull requests and suggestions are welcome! For major changes, please open an issue first to discuss what you’d like to change.

---

## Acknowledgments

- Inspired by GenAI and RAG best practices at JPMC and other leading financial institutions.
- Built with [Snowflake Cortex](https://docs.snowflake.com/en/user-guide/snowflake-cortex), [Streamlit](https://streamlit.io/), and SEC XBRL data.

---



