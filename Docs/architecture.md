# GenAI Risk & Compliance Assistant — System Architecture

## Overview
This system is a Snowflake-native GenAI application for financial compliance, risk analytics, and AI-powered Q&A, using SEC data and multi-agent orchestration.

## Architecture Diagram
![generated-image](https://github.com/user-attachments/assets/1c2ebff7-cae2-4d17-9cdc-73b37ca903cc)


## Components

### 1. Data Layer (Snowflake)
- **Raw SEC Tables:** `NUM`, `PRE`, `SUB`, `TAG`
- **Aggregated Views:** `COMPANY_CHUNKS_PROD` (key metrics per filing)
- **Agent Views:** `NON_COMPLIANT_FILINGS`, `HIGH_RISK_FILINGS`, `FILING_SUMMARIES`
- **RAG Chunks:** `DOC_CHUNKS` with vector embeddings

### 2. AI/ML Layer
- **Snowflake Cortex LLM:** For summarization and Q&A
- **Vector Search:** Semantic retrieval using `VECTOR_COSINE_SIMILARITY`
- **RAG Pipeline:** Embeds user queries, retrieves relevant chunks, and generates answers

### 3. Application Layer (Streamlit)
- **Compliance Agent Tab:** Flags missing key metrics
- **Risk Agent Tab:** Highlights financial anomalies
- **AI Summaries Tab:** LLM-generated summaries for each filing
- **Data Analytics Tab:** Charts, trends, anomaly detection
- **RAG Q&A Expander:** Open-ended, context-rich Q&A

### 4. Security & Audit
- **Access Control:** Snowflake roles and privileges
- **Audit Logging:** All queries/actions logged in Snowflake

## Data Flow

1. **Data Ingestion:** SEC files loaded into raw tables
2. **Aggregation:** Key metrics computed in `COMPANY_CHUNKS_PROD`
3. **Agent Logic:** Compliance/risk/summarization views created for business logic
4. **RAG Preparation:** Chunks and embeddings generated for semantic search
5. **User Interaction:** Streamlit app provides analytics, agent alerts, and RAG-powered Q&A

## Key Design Decisions

- Chose Snowflake-native Streamlit for seamless security and scalability
- Used Cortex LLM for both summarization and RAG Q&A
- Designed modular SQL for easy extension (new agents, metrics, or documents)
- All business logic and AI steps are auditable and reproducible

## Extensibility

- Add more agents (e.g., fraud detection, ESG compliance)
- Integrate new data sources (e.g., internal policies, regulatory bulletins)
- Deploy externally via Streamlit Community Cloud (with Snowflake connector)

## References

- [Snowflake Cortex Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex)
- [SEC XBRL Data Guide](https://www.sec.gov/dera/data/financial-statement-data-sets.html)

