import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="AdiSports Analytics", page_icon="🏏", layout="wide")
st.title("🏏 AdiSports Analytics Hub")

@st.cache_data
def load_live_data():
    conn = sqlite3.connect('sports_analytics.db')
    query = "SELECT match_date, team1, team2, format_type, series_name, match_desc FROM upcoming_matches"
    try:
        df = pd.read_sql_query(query, conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

@st.cache_data
def load_season_dashboard(selected_year):
    conn = sqlite3.connect('sports_analytics.db')
    where_clause = "" if selected_year == "All-Time" else f"WHERE date LIKE '%{selected_year}'"
    
    q_matches = f"SELECT COUNT(DISTINCT match_id) as total FROM ipl_history {where_clause}"
    df_matches = pd.read_sql_query(q_matches, conn)
    total_matches = df_matches['total'][0] if not df_matches.empty else 0

    q_batters = f"""
        SELECT batter, SUM(runs_batter) as total_runs 
        FROM ipl_history {where_clause} 
        GROUP BY batter ORDER BY total_runs DESC LIMIT 5
    """
    df_batters = pd.read_sql_query(q_batters, conn)

    q_bowlers = f"""
        SELECT bowler, COUNT(player_dismissed) as total_wickets 
        FROM ipl_history 
        {where_clause} AND player_dismissed IS NOT NULL 
        GROUP BY bowler ORDER BY total_wickets DESC LIMIT 5
    """
    try:
        df_bowlers = pd.read_sql_query(q_bowlers, conn)
    except:
        df_bowlers = pd.DataFrame() 
    q_scores = f"""
        SELECT match_id, date, batting_team, SUM(runs_batter) as team_score 
        FROM ipl_history {where_clause} 
        GROUP BY match_id, batting_team 
        ORDER BY date DESC LIMIT 10
    """
    df_scores = pd.read_sql_query(q_scores, conn)

    conn.close()
    return total_matches, df_batters, df_bowlers, df_scores

df_live = load_live_data()

st.sidebar.header("🔍 Filter Live Matches")
formats = ["All Formats"] + df_live['format_type'].unique().tolist() if not df_live.empty else ["All Formats"]
selected_format = st.sidebar.selectbox("Select Format", formats)
search_team = st.sidebar.text_input("Search for a Team:")

filtered_df = df_live.copy()
if not filtered_df.empty:
    if selected_format != "All Formats":
        filtered_df = filtered_df[filtered_df['format_type'] == selected_format]
    if search_team:
        filtered_df = filtered_df[
            filtered_df['team1'].str.contains(search_team, case=False, na=False) |
            filtered_df['team2'].str.contains(search_team, case=False, na=False)
        ]

tab1, tab2 = st.tabs(["🔴 Live & Upcoming", "🏏 IPL Season Explorer"])

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
        st.warning("No live matches found.")

with tab2:
    years = ["All-Time"] + [str(year) for year in range(2025, 2007, -1)]
    selected_year = st.selectbox("Select IPL Season:", years)
    
    st.markdown("---")
    
    total_matches, df_batters, df_bowlers, df_scores = load_season_dashboard(selected_year)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="🏏 Matches Played", value=total_matches)
        
    with col2:
        if not df_batters.empty:
            orange_cap = df_batters.iloc[0]
            st.metric(label="🟠 Orange Cap", value=orange_cap['batter'], delta=f"{orange_cap['total_runs']} Runs", delta_color="normal")
            
    with col3:
        if not df_bowlers.empty:
            purple_cap = df_bowlers.iloc[0]
            st.metric(label="🟣 Purple Cap", value=purple_cap['bowler'], delta=f"{purple_cap['total_wickets']} Wickets", delta_color="normal")

    st.markdown("---")
    
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.subheader("Top Run Scorers")
        if not df_batters.empty:
            st.bar_chart(df_batters.set_index('batter'), color="#f5a623")
            
    with chart_col2:
        st.subheader("Top Wicket Takers")
        if not df_bowlers.empty:
            st.bar_chart(df_bowlers.set_index('bowler'), color="#9013fe")
        else:
            st.info("Wicket data column not found in CSV. We will map this next!")

    st.markdown("---")
    
    st.subheader("📝 Recent Match Summaries (Foundation for Points Table)")
    st.caption("Here is the raw aggregation of total runs per team per match. Calculating exact winners and NRR requires mapping this data together!")
    if not df_scores.empty:
        st.dataframe(df_scores, use_container_width=True)