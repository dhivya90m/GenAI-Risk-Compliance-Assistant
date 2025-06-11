# GenAI Risk & Compliance Assistant

A multi-agent GenAI solution for financial compliance, risk analytics, and AI-powered Q&A—built natively on Snowflake with a modern Streamlit dashboard.

---

## Overview

This project demonstrates how to combine advanced data engineering, Retrieval-Augmented Generation (RAG), and Large Language Models (LLMs) to automate complex compliance and risk workflows on real SEC financial data. Inspired by GenAI strategies at leading financial institutions, it showcases:

- **Automated compliance checks** and risk flagging  
- **RAG-powered, context-rich Q&A** using Snowflake Cortex LLMs  
- **Executive-ready summaries** of company filings  
- **Interactive analytics dashboard** for business and technical users  
- **Enterprise-grade security and auditability**  

---

## What I Built & Automated

- **Automated Data Ingestion:**  
  - Configured four Snowpipes (one per SEC raw table) for auto-ingest, so new files uploaded via Streamlit or CLI are instantly loaded—no manual SQL after setup.
  - Used internal Snowflake stages for secure, cost-effective storage.
- **Change Data Capture & Streaming:**  
  - Set up Streams on each raw table to track new/changed rows, enabling efficient, incremental processing.
- **End-to-End Task Orchestration:**  
  - Built triggered Tasks that:
    - Transform raw data into analytics-ready “company chunks” as soon as new data lands.
    - Create human-readable text “chunks” for AI and RAG pipelines.
    - Generate vector embeddings for each chunk using Snowflake Cortex, fully automated via triggered tasks.
- **Multi-Agent GenAI Logic:**  
  - **Compliance Agent:** Flags missing or non-compliant filings.
  - **Risk Agent:** Detects losses and financial anomalies.
  - **Summarization Agent:** Uses LLMs to create plain-English, audit-ready summaries for every filing.
- **RAG Q&A Pipeline:**  
  - Embedded both user queries and document chunks using Snowflake Cortex.
  - Implemented semantic search with vector similarity to retrieve relevant context.
  - Used LLMs to generate grounded, context-rich answers to any plain-English question about company filings.
- **Interactive, Real-Time Dashboard:**  
  - Developed a Streamlit app (native in Snowflake) featuring:
    - Automated file upload and ingestion status
    - Compliance/risk alerts and AI-generated summaries
    - RAG-powered Q&A
    - Advanced analytics (top companies, revenue trends, anomaly detection, charts)
    - Live monitoring of Snowpipes, tasks, and table row counts
- **Security, Auditability, and Scalability:**  
  - All data and actions are governed and auditable within Snowflake.
  - Access controls and logging ensure regulatory compliance.
  - Architecture is scalable and cloud-native—ready for new data sources, regulations, and business needs.

---

## Architecture

- **Data Engineering & Automation Layer:**  
  - SEC XBRL tables (`NUM`, `PRE`, `SUB`, `TAG`) are auto-ingested via Snowpipe.
  - Streams track new/changed data for event-driven, incremental processing.
  - Tasks trigger SQL transformations, aggregation, and AI enrichment (chunking, embedding) automatically.
  - Aggregated and agent views: `COMPANY_CHUNKS_PROD`, `NON_COMPLIANT_FILINGS`, `HIGH_RISK_FILINGS`, `FILING_SUMMARIES`.
  - RAG chunks: `DOC_CHUNKS` table with AI-generated text and vector embeddings for semantic retrieval.
- **AI/ML & Retrieval Layer:**  
  - Snowflake Cortex LLM for summarization, Q&A, and embedding generation.
  - Vector search using `VECTOR_COSINE_SIMILARITY` and Cortex embeddings.
  - RAG pipeline: embeds user queries, retrieves context, and generates grounded answers.
- **Application & Analytics Layer (Streamlit):**  
  - Automated file upload; ingestion and processing are fully automated.
  - Compliance, risk, and summarization agent tabs.
  - AI summaries, advanced analytics, and RAG Q&A expander.
  - Monitoring tab for Snowpipes, tasks, and table row counts.
- **Security, Governance & Auditability:**  
  - All access managed with Snowflake roles and privileges.
  - All queries and AI actions are logged and auditable.
  - Data lineage: all transformations and AI steps are reproducible and traceable.

For a detailed system diagram and data flow, see [`docs/architecture.md`](docs/architecture.md).

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
3. **Configure your Snowflake credentials:**  
   [How to set up Snowflake credentials](https://docs.snowflake.com/en/user-guide/python-connector-example)
4. **Run the app:**
   streamlit run app/streamlit_app.py

---

## Data Model

| Table | What It Stores                               | Key Columns                  | Example Use                                                      |
|-------|----------------------------------------------|------------------------------|------------------------------------------------------------------|
| NUM   | All reported financial numbers (facts)       | ADSH, TAG, VALUE, DDATE      | Revenue, net income, assets, etc. for each filing                |
| PRE   | How financial facts are organized in statements | ADSH, TAG, PLABEL, STMT      | Order/label of facts in the balance sheet, income statement, etc.|
| SUB   | Company and filing metadata                  | ADSH, NAME, FORM, PERIOD     | Which company, which report, when filed                          |
| TAG   | Definitions for each financial fact (tag)    | TAG, TLABEL, DATATYPE        | What “NetIncomeLoss” or “Assets” means                           |

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
- Uses LangChain and modern AI frameworks for multi-turn chat and RAG orchestration.

---

## Advancements & Industry Context

- **Event-driven automation:** No manual ETL—Snowpipe, Streams, and Tasks orchestrate the pipeline.
- **Agentic AI:** Multi-agent orchestration (compliance, risk, summarization) for dynamic, context-aware workflows.[6][1]
- **RAG at scale:** Robust, explainable RAG pipeline with semantic search and LLMs, all within Snowflake.[5]
- **Enterprise security:** All logic, data, and AI actions are governed, auditable, and fully within Snowflake’s security perimeter.[3][4]
- **Real-time analytics:** Dashboards and monitoring tabs provide up-to-the-minute insights and pipeline health.
- **Extensible architecture:** Easily add new agents, data sources, or external integrations as regulations and business needs evolve.

---

   
