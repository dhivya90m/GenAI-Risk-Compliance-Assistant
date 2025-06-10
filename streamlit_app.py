"""
GenAI Risk & Compliance Assistant - Streamlit App
Author: [Your Name]
Date: [Date]
Description: Multi-agent analytics dashboard with RAG-powered Q&A for SEC filings.
"""

import streamlit as st
import altair as alt
from snowflake.snowpark.context import get_active_session

# ============================================================================
# SNOWFLAKE SESSION INITIALIZATION
# ============================================================================
session = get_active_session()  # Get active Snowflake session for data access

# ============================================================================
# STREAMLIT APP CONFIGURATION
# ============================================================================
st.set_page_config(page_title="GenAI Risk & Compliance Assistant", layout="wide")
st.title("GenAI Risk & Compliance Assistant")

# ============================================================================
# DASHBOARD TABS DEFINITION
# ============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview", 
    "Compliance Alerts", 
    "Risk Alerts", 
    "AI Summaries", 
    "Data Analytics"
])

# ============================================================================
# TAB 1: OVERVIEW - ALL FILINGS
# ============================================================================
with tab1:
    st.header("All Company Filings")
    df = session.table("SEC_DATA.PUBLIC.COMPANY_CHUNKS_PROD").limit(50).to_pandas()
    st.dataframe(df, use_container_width=True)

# ============================================================================
# TAB 2: COMPLIANCE ALERTS
# ============================================================================
with tab2:
    st.header("Compliance Alerts (Missing Key Metrics)")
    df_compliance = session.table("SEC_DATA.PUBLIC.NON_COMPLIANT_FILINGS").to_pandas()
    st.dataframe(df_compliance, use_container_width=True)
    st.write(f"**Total non-compliant filings:** {len(df_compliance)}")

# ============================================================================
# TAB 3: RISK ALERTS
# ============================================================================
with tab3:
    st.header("Risk Alerts (Negative Net Income or High Liabilities/Assets)")
    df_risk = session.table("SEC_DATA.PUBLIC.HIGH_RISK_FILINGS").to_pandas()
    st.dataframe(df_risk, use_container_width=True)
    st.write(f"**Total high-risk filings:** {len(df_risk)}")

# ============================================================================
# TAB 4: AI SUMMARIES
# ============================================================================
with tab4:
    st.header("AI-Generated Filing Summaries")
    df_summary = session.table("SEC_DATA.PUBLIC.FILING_SUMMARIES").limit(50).to_pandas()
    st.dataframe(
        df_summary[["COMPANY_NAME", "REPORT_TYPE", "PERIOD", "AI_SUMMARY"]],
        use_container_width=True
    )

# ============================================================================
# RAG-POWERED Q&A (GLOBAL EXPANDER)
# ============================================================================
with st.expander("Ask any question about company filings (RAG-powered)"):
    user_question = st.text_input("Enter your question (e.g., What was Apple's net income in 2024?)")
    
    if user_question:
        # --- RAG Pipeline Implementation ---
        # Step 1: Embed user question using Snowflake Cortex
        embedding_query = """
            SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768(
                'snowflake-arctic-embed-m-v1.5', ?
            ) AS question_embedding
        """
        question_embedding_df = session.sql(embedding_query, params=[user_question]).to_pandas()
        question_embedding = question_embedding_df.iloc[0, 0].tolist()  # Convert to Python list
        embedding_literal = str(question_embedding)  # Prepare for SQL interpolation

        # Step 2: Semantic search with vector similarity
        retrieval_query = f"""
            SELECT text_chunk
            FROM SEC_DATA.PUBLIC.DOC_CHUNKS
            ORDER BY VECTOR_COSINE_SIMILARITY(
                embedding, {embedding_literal}::VECTOR(FLOAT, 768)
            ) DESC
            LIMIT 3
        """
        relevant_chunks_df = session.sql(retrieval_query).to_pandas()
        context = "\n".join(relevant_chunks_df["TEXT_CHUNK"].tolist())

        # Step 3: LLM-powered answer generation
        prompt = f"Context:\n{context}\n\nQuestion: {user_question}\nAnswer:"
        answer_query = """
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'snowflake-arctic', ?
            ) AS answer
        """
        answer_df = session.sql(answer_query, params=[prompt]).to_pandas()
        answer = answer_df.iloc[0, 0]

        # Display formatted answer
        st.markdown("**Answer:**")
        st.write(answer)

# ============================================================================
# TAB 5: DATA ANALYTICS
# ============================================================================
with tab5:
    st.header("Data Analytics & Business Insights")
    
    # ------------------
    # Top Performers Section
    # ------------------
    st.subheader("Key Financial Metrics")
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 Companies by Revenue
        top_revenue = session.sql("""
            SELECT company_name, MAX(revenue) AS max_revenue
            FROM SEC_DATA.PUBLIC.COMPANY_CHUNKS_PROD
            WHERE revenue IS NOT NULL
            GROUP BY company_name
            ORDER BY max_revenue DESC
            LIMIT 10
        """).to_pandas()
        st.subheader("🏆 Top 10 Companies by Revenue")
        st.bar_chart(top_revenue.set_index("COMPANY_NAME"))

    with col2:
        # Companies with Largest Losses
        biggest_losses = session.sql("""
            SELECT company_name, MIN(net_income) AS min_net_income
            FROM SEC_DATA.PUBLIC.COMPANY_CHUNKS_PROD
            WHERE net_income IS NOT NULL
            GROUP BY company_name
            ORDER BY min_net_income ASC
            LIMIT 10
        """).to_pandas()
        st.subheader("📉 Companies with Largest Losses")
        st.bar_chart(biggest_losses.set_index("COMPANY_NAME"))

    # ------------------
    # Trend Analysis Section
    # ------------------
    st.subheader("Trend Analysis")
    company_list = top_revenue["COMPANY_NAME"].tolist()
    company = st.selectbox("Select a company to view revenue trend:", company_list)
    
    trend = session.sql(f"""
        SELECT period, revenue
        FROM SEC_DATA.PUBLIC.COMPANY_CHUNKS_PROD
        WHERE company_name = '{company}'
        AND revenue IS NOT NULL
        ORDER BY period
    """).to_pandas()

    if not trend.empty:
        # Data formatting
        trend.columns = [col.upper() for col in trend.columns]
        trend["PERIOD"] = trend["PERIOD"].astype(str)

        # Interactive Altair chart
        chart = alt.Chart(trend).mark_line(point=True).encode(
            x=alt.X("PERIOD", title="Reporting Period"),
            y=alt.Y("REVENUE", title="Revenue (USD)"),
            tooltip=["PERIOD", "REVENUE"]
        ).properties(
            title=f"Revenue Trend for {company}",
            width=600,
            height=350
        )
        st.altair_chart(chart, use_container_width=True)
        st.dataframe(trend.set_index("PERIOD"), use_container_width=True)
    else:
        st.warning(f"No revenue data available for {company}.")

    # ------------------
    # Anomaly Detection Section
    # ------------------
    st.subheader("Risk Detection")
    anomaly = session.sql("""
        WITH revenue_trend AS (
            SELECT company_name, period, revenue,
                   LAG(revenue) OVER (PARTITION BY company_name ORDER BY period) AS prev_revenue
            FROM SEC_DATA.PUBLIC.COMPANY_CHUNKS_PROD
            WHERE revenue IS NOT NULL
        )
        SELECT company_name, period, revenue, prev_revenue,
               (revenue - prev_revenue) / NULLIF(prev_revenue, 0) AS pct_change
        FROM revenue_trend
        WHERE prev_revenue IS NOT NULL 
          AND (revenue - prev_revenue) / NULLIF(prev_revenue, 0) < -0.5
        ORDER BY pct_change ASC
        LIMIT 10
    """).to_pandas()

    if not anomaly.empty:
        st.dataframe(anomaly, use_container_width=True)
    else:
        st.info("✅ No significant revenue drops detected in the top companies.")
