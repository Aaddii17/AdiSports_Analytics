import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="AdiSports Analytics", page_icon="🏏", layout="wide")

st.title("🏏 AdiSports Analytics Hub")

@st.cache_data
def load_live_data():
    conn = sqlite3.connect('sports_analytics.db')
    query = "SELECT match_date, team1, team2, format_type, series_name, match_desc FROM upcoming_matches"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@st.cache_data
def load_historical_data():
    conn = sqlite3.connect('sports_analytics.db')
    query = """
        SELECT batter, SUM(runs_batter) as total_runs 
        FROM ipl_history 
        GROUP BY batter 
        ORDER BY total_runs DESC 
        LIMIT 10
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

df_matches = load_live_data()
df_history = load_historical_data()

st.sidebar.header("🔍 Filter Live Matches")
formats = ["All Formats"] + df_matches['format_type'].unique().tolist() if not df_matches.empty else ["All Formats"]
selected_format = st.sidebar.selectbox("Select Format", formats)
search_team = st.sidebar.text_input("Search for a Team:")

filtered_df = df_matches.copy()
if selected_format != "All Formats":
    filtered_df = filtered_df[filtered_df['format_type'] == selected_format]
if search_team:
    filtered_df = filtered_df[
        filtered_df['team1'].str.contains(search_team, case=False, na=False) |
        filtered_df['team2'].str.contains(search_team, case=False, na=False)
    ]

tab1, tab2 = st.tabs(["🔴 Live & Upcoming", "📊 Historical Analytics"])

with tab1:
    st.subheader("📅 Live & Upcoming Matches")
    if not filtered_df.empty:
        cols = st.columns(3)
        for index, row in filtered_df.iterrows():
            col = cols[index % 3] 
            with col:
                with st.container(border=True):
                    st.caption(f"{row['match_desc']} • {row['series_name'][:25]}... • **{row['format_type']}**")
                    st.markdown(f"🛡️ **{row['team1']}**")
                    st.markdown(f"⚔️ **{row['team2']}**")
                    st.caption(f"🕒 {row['match_date']}")
    else:
        st.warning("No matches found matching your filters.")

with tab2:
    st.subheader("🏆 All-Time IPL Top Run Scorers (2008 - 2025)")
    st.markdown("Processing 278,000+ rows of ball-by-ball data...")
    
    if not df_history.empty:
        chart_data = df_history.set_index('batter')
        
        st.bar_chart(chart_data, use_container_width=True)
    else:
        st.error("Historical data not found. Check your database!")