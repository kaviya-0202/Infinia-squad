import streamlit as st
import pandas as pd
import sys
sys.path.append(".")
from services.db_service import get_sorted_complaints, clear_all_complaints
from utils.helpers import get_urgency_color, get_sentiment_color

def show():
    st.markdown("""
        <div style='padding: 24px 0 8px 0'>
            <h2 style='color:#e8eaf0; font-size:22px; margin-bottom:4px; font-weight:500;'>Support Team Dashboard</h2>
            <p style='color:#9499b0; font-size:14px; margin:0;'>Complaints sorted by urgency — highest priority first</p>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    complaints = get_sorted_complaints()

    total = len(complaints)
    critical = len([c for c in complaints if c.get("urgency_label") == "Critical"])
    high = len([c for c in complaints if c.get("urgency_label") == "High"])
    negative = len([c for c in complaints if c.get("sentiment") == "Negative"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Complaints", total)
    col2.metric("Critical", critical)
    col3.metric("High Priority", high)
    col4.metric("Negative Sentiment", negative)

    st.divider()

    col1, col2 = st.columns([4, 1])
    with col1:
        st.subheader("Live Complaint Feed")
    with col2:
        if st.button("Clear All", type="secondary"):
            clear_all_complaints()
            st.rerun()

    if not complaints:
        st.info("No complaints submitted yet. Waiting for submissions...")
        return

    for c in complaints:
        urgency_color = get_urgency_color(c.get("urgency_label", "Medium"))
        sentiment_color = get_sentiment_color(c.get("sentiment", "Neutral"))

        with st.container():
            st.markdown(f"""
                <div style='
                    border-left: 4px solid {urgency_color};
                    background: #1a1d2e;
                    padding: 16px 20px;
                    border-radius: 0 8px 8px 0;
                    margin-bottom: 10px;
                '>
                    <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;'>
                        <div>
                            <span style='font-size:15px; font-weight:600; color:#e8eaf0;'>#{c.get("id")} — {c.get("name")}</span>
                            <span style='color:#9499b0; font-size:12px; margin-left:10px;'>{c.get("email")}</span>
                        </div>
                        <div style='display:flex; gap:8px;'>
                            <span style='background:{urgency_color}22; color:{urgency_color}; padding:3px 10px; border-radius:4px; font-size:12px; font-weight:600;'>
                                {c.get("urgency_label")} — {c.get("urgency_score")}/10
                            </span>
                            <span style='background:{sentiment_color}22; color:{sentiment_color}; padding:3px 10px; border-radius:4px; font-size:12px; font-weight:600;'>
                                {c.get("sentiment")} {c.get("sentiment_symbol")}
                            </span>
                        </div>
                    </div>
                    <p style='margin:0 0 6px 0; color:#ccc; font-size:13px;'>{c.get("complaint")}</p>
                    <p style='color:#9499b0; font-size:11px; margin:0;'>Summary: {c.get("summary")} &nbsp;|&nbsp; Submitted: {c.get("timestamp")}</p>
                </div>
            """, unsafe_allow_html=True)

    st.divider()
    st.subheader("Summary Table")

    df = pd.DataFrame(complaints)
    if not df.empty:
        display_df = df[["id", "name", "email", "urgency_score", "urgency_label", "sentiment", "summary", "timestamp"]].copy()
        display_df.columns = ["ID", "Name", "Email", "Score", "Priority", "Sentiment", "Summary", "Submitted On"]
        display_df["Submitted On"] = display_df["Submitted On"].astype(str)
        st.dataframe(display_df, use_container_width=True, hide_index=True,
            column_config={
                "Submitted On": st.column_config.TextColumn("Submitted On", width="medium"),
                "Summary": st.column_config.TextColumn("Summary", width="large"),
            }
        )