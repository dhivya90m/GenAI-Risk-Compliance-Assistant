"""
GenAI Risk & Compliance Assistant - Production Template
Description: Enterprise-ready, multi-agent analytics dashboard with RAG-powered Q&A, automation, monitoring.
"""

import streamlit as st
import pandas as pd
import altair as alt
import tempfile
from snowflake.snowpark.context import get_active_session

# ============================================================================
# 1. SNOWFLAKE SESSION INITIALIZATION
# ============================================================================
session = get_active_session()

# ============================================================================
# 2. STREAMLIT APP CONFIGURATION
# ============================================================================
st.set_page_config(page_title="GenAI Risk & Compliance Assistant", layout="wide")
st.title("GenAI Risk & Compliance Assistant")

# ============================================================================
# 3. SIDEBAR: DATA UPLOAD & PIPELINE STATUS
# ============================================================================
with st.sidebar:
    st.header("Upload SEC Data Files")
    table_mapping = {
        'sub': ('sub', '@SEC_DATA.PUBLIC.SEC_DATA_STAGE/sub/'),
        'num': ('num', '@SEC_DATA.PUBLIC.SEC_DATA_STAGE/num/'),
        'tag': ('tag', '@SEC_DATA.PUBLIC.SEC_DATA_STAGE/tag/'),
        'pre': ('pre', '@SEC_DATA.PUBLIC.SEC_DATA_STAGE/pre/')
    }
    for fname in table_mapping:
        uploaded_file = st.file_uploader(f"Upload {fname}.txt", type=["txt"], key=fname)
        if uploaded_file:
            table_name, stage_path = table_mapping[fname]
            # Save uploaded file to a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_file_path = tmp_file.name
            with st.spinner(f"Uploading {uploaded_file.name} to {stage_path}..."):
                session.file.put(
                    tmp_file_path,
                    stage_path,
                    overwrite=True
                )
                st.success(f"{uploaded_file.name} uploaded to {stage_path}. Snowpipe will auto-ingest into {table_name} table.")
                try:
                    df_preview = session.sql(f"SELECT * FROM {table_name} LIMIT 5").to_pandas()
                    st.dataframe(df_preview)
                except Exception as e:
                    st.error(f"Preview failed: {str(e)}")

# ============================================================================
# 4. MAIN TABS
# ============================================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Overview", 
    "Compliance Alerts", 
    "Risk Alerts", 
    "AI Summaries", 
    "Data Analytics",
    "Monitoring"
])

# ============================================================================
# 5. TAB 1: OVERVIEW - ALL FILINGS
# ============================================================================
with tab1:
    st.header("All Company Filings")
    try:
        df = session.table("SEC_DATA.PUBLIC.COMPANY_CHUNKS_PROD").limit(50).to_pandas()
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Failed to load filings: {e}")

# ============================================================================
# 6. TAB 2: COMPLIANCE ALERTS
# ============================================================================
with tab2:
    st.header("Compliance Alerts (Missing Key Metrics)")
    try:
        df_compliance = session.table("SEC_DATA.PUBLIC.NON_COMPLIANT_FILINGS").to_pandas()
        st.dataframe(df_compliance, use_container_width=True)
        st.write(f"**Total non-compliant filings:** {len(df_compliance)}")
    except Exception as e:
        st.error(f"Failed to load compliance alerts: {e}")

# ============================================================================
# 7. TAB 3: RISK ALERTS
# ============================================================================
with tab3:
    st.header("Risk Alerts (Negative Net Income or High Liabilities/Assets)")
    try:
        df_risk = session.table("SEC_DATA.PUBLIC.HIGH_RISK_FILINGS").to_pandas()
        st.dataframe(df_risk, use_container_width=True)
        st.write(f"**Total high-risk filings:** {len(df_risk)}")
    except Exception as e:
        st.error(f"Failed to load risk alerts: {e}")

# ============================================================================
# 8. TAB 4: AI SUMMARIES
# ============================================================================
with tab4:
    st.header("AI-Generated Filing Summaries")
    try:
        df_summary = session.table("SEC_DATA.PUBLIC.FILING_SUMMARIES").limit(50).to_pandas()
        st.dataframe(
            df_summary[["COMPANY_NAME", "REPORT_TYPE", "PERIOD", "AI_SUMMARY"]],
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Failed to load summaries: {e}")

# ============================================================================
# 9. RAG-POWERED Q&A (EXPANDER) - SNOWFLAKE CORTEX ONLY
# ============================================================================
with st.expander("Ask any question about company filings (RAG-powered)"):
    user_question = st.text_input("Enter your question (e.g., What was Apple's net income in 2024?)")
    if user_question:
        try:
            # --- Native RAG Pipeline (Snowflake Cortex) ---
            embedding_query = """
                SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768(
                    'snowflake-arctic-embed-m-v1.5', ?
                ) AS question_embedding
            """
            question_embedding_df = session.sql(embedding_query, params=[user_question]).to_pandas()
            question_embedding = question_embedding_df.iloc[0, 0].tolist()
            embedding_literal = str(question_embedding)
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
            prompt = f"Context:\n{context}\n\nQuestion: {user_question}\nAnswer:"
            answer_query = """
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    'snowflake-arctic', ?
                ) AS answer
            """
            answer_df = session.sql(answer_query, params=[prompt]).to_pandas()
            answer = answer_df.iloc[0, 0]
            st.markdown("**Answer:**")
            st.write(answer)
            st.markdown("**Context Chunks Used:**")
            st.dataframe(relevant_chunks_df[["TEXT_CHUNK"]])
        except Exception as e:
            st.error(f"RAG Q&A failed: {e}")

# ============================================================================
# 10. TAB 5: DATA ANALYTICS
# ============================================================================
with tab5:
    st.header("Data Analytics & Business Insights")
    try:
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

        # Revenue Trend for a Selected Company
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
            trend.columns = [col.upper() for col in trend.columns]
            trend["PERIOD"] = trend["PERIOD"].astype(str)
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

        # Anomaly Detection: Revenue Drops
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
    except Exception as e:
        st.error(f"Data analytics failed: {e}")

# ============================================================================
# 11. TAB 6: MONITORING & OBSERVABILITY
# ============================================================================

with tab6:
    st.header("Monitoring & Observability")

    st.subheader("Snowpipe Status")
    try:
        pipes = session.sql("SHOW PIPES IN SCHEMA SEC_DATA.PUBLIC").to_pandas()
        # Filter for your four pipes by name (column 1)
        pipes_of_interest = pipes[pipes[1].isin(["SUB_PIPE", "NUM_PIPE", "TAG_PIPE", "PRE_PIPE"])]
        if not pipes_of_interest.empty:
            # Rename columns for display
            pipes_of_interest = pipes_of_interest.rename(
                columns={
                    1: "Pipe Name",
                    4: "Definition",
                    0: "Created On",
                    6: "Notification Channel",
                    7: "Comment",
                    13: "Kind"
                }
            )
            st.dataframe(
                pipes_of_interest[["Pipe Name", "Definition", "Created On", "Notification Channel", "Comment", "Kind"]]
            )
        else:
            st.info("No relevant Snowpipes found in SEC_DATA.PUBLIC.")
    except Exception as e:
        st.error(f"Error fetching Snowpipe status: {e}")


     # --- Task Status ---
    st.subheader("Task Status")
    try:
        tasks = session.sql("SHOW TASKS IN SCHEMA SEC_DATA.PUBLIC").to_pandas()
        #st.write("Task columns (for debugging):", tasks.columns.tolist())

        # Map indices to column names for first 14 columns (0–13)
        rename_map = {
            1: "Task Name",
            7: "Warehouse",
            8: "Schedule",
            10: "State",
            12: "Condition"
        }
        # Rename only the columns we want to display
        tasks = tasks.rename(columns=rename_map)

        if not tasks.empty:
            st.dataframe(tasks[["Task Name", "Warehouse", "Schedule", "State", "Condition"]])
        else:
            st.info("No tasks configured in SEC_DATA.PUBLIC.")
    except Exception as e:
        st.error(f"Error fetching tasks: {e}")

    # --- Table Row Counts ---
    st.subheader("Table Row Counts")
    try:
        tables = ["NUM", "SUB", "TAG", "PRE", "COMPANY_CHUNKS_PROD", "DOC_CHUNKS"]
        row_counts = []
        for tbl in tables:
            count = session.sql(f"SELECT COUNT(*) AS count FROM SEC_DATA.PUBLIC.{tbl}").to_pandas()["COUNT"][0]
            row_counts.append({"Table": tbl, "Rows": count})
        st.dataframe(pd.DataFrame(row_counts))
    except Exception as e:
        st.error(f"Error fetching row counts: {e}")




