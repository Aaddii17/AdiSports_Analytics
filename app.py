import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="AdiSports Analytics", page_icon="🏏", layout="wide")
st.title("🏏 AdiSports Analytics Hub")

# --- DATA LOADERS ---
@st.cache_data
def load_live_data():
    conn = sqlite3.connect('sports_analytics.db')
    try:
        df = pd.read_sql_query("SELECT match_date, team1, team2, format_type, series_name, match_desc FROM upcoming_matches", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

@st.cache_data
def get_points_table(df_matches):
    if df_matches.empty:
        return pd.DataFrame()

    teams = pd.concat([df_matches['team1'], df_matches['team2']]).dropna().unique()
    pt_dict = {team: {'M': 0, 'W': 0, 'L': 0, 'NR/Tie': 0, 'Pts': 0} for team in teams}

    for _, row in df_matches.iterrows():
        t1, t2 = row['team1'], row['team2']
        w = row.get('winner', None)
        
        if pd.isna(t1) or pd.isna(t2):
            continue
            
        pt_dict[t1]['M'] += 1
        pt_dict[t2]['M'] += 1
        
        if pd.isna(w) or w not in [t1, t2]:
            pt_dict[t1]['NR/Tie'] += 1
            pt_dict[t2]['NR/Tie'] += 1
            pt_dict[t1]['Pts'] += 1
            pt_dict[t2]['Pts'] += 1
        else:
            loser = t2 if w == t1 else t1
            pt_dict[w]['W'] += 1
            pt_dict[w]['Pts'] += 2
            if loser in pt_dict:
                pt_dict[loser]['L'] += 1

    pt_df = pd.DataFrame.from_dict(pt_dict, orient='index').reset_index()
    pt_df.rename(columns={'index': 'Team'}, inplace=True)
    pt_df = pt_df.sort_values(by=['Pts', 'W'], ascending=[False, False]).reset_index(drop=True)
    pt_df.index += 1
    return pt_df

@st.cache_data
def load_season_dashboard(selected_year):
    conn = sqlite3.connect('sports_analytics.db')
    
    # 1. Fetch MACRO Data (Match Summaries) dynamically
    try:
        df_matches = pd.read_sql_query("SELECT * FROM match_summary", conn)
    except Exception as e:
        st.error("⚠️ Database Error: 'match_summary' table is missing from your vault! (Did you run load_matches.py?)")
        df_matches = pd.DataFrame()

    # Filter matches by year using Pandas (safer than SQL string matching)
    if not df_matches.empty and selected_year != "All-Time":
        # Automatically detect what Kaggle named the date column
        date_col = 'match_date' if 'match_date' in df_matches.columns else 'date'
        
        if 'Season' in df_matches.columns:
            df_matches = df_matches[df_matches['Season'].astype(str).str.contains(selected_year)]
        elif date_col in df_matches.columns:
            df_matches = df_matches[df_matches[date_col].astype(str).str.contains(selected_year)]

    total_matches = len(df_matches)

    # 2. Fetch MVP Data
    df_mom = pd.DataFrame()
    if not df_matches.empty and 'player_of_match' in df_matches.columns:
        df_mom = df_matches['player_of_match'].value_counts().reset_index()
        df_mom.columns = ['player_of_match', 'awards']

    # 3. Fetch MICRO Data (Batters & Bowlers)
    where_ball = "" if selected_year == "All-Time" else f"WHERE date LIKE '%{selected_year}%'"
    
    try:
        df_batters = pd.read_sql_query(f"SELECT batter, SUM(runs_batter) as runs FROM ipl_history {where_ball} GROUP BY batter ORDER BY runs DESC LIMIT 5", conn)
    except:
        df_batters = pd.DataFrame()

    try:
        # Bulletproof Wicket Query (handles all Kaggle naming conventions)
        q_bowlers = f"""
            SELECT bowler, COUNT(*) as wickets 
            FROM ipl_history {where_ball} 
            WHERE player_dismissed IS NOT NULL AND player_dismissed != '' AND player_dismissed != 'NA'
            GROUP BY bowler ORDER BY wickets DESC LIMIT 5
        """
        df_bowlers = pd.read_sql_query(q_bowlers, conn)
    except:
        df_bowlers = pd.DataFrame()

    conn.close()
    return total_matches, df_batters, df_bowlers, df_mom, df_matches

# --- APP UI ---
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
        filtered_df = filtered_df[filtered_df['team1'].str.contains(search_team, case=False, na=False) | filtered_df['team2'].str.contains(search_team, case=False, na=False)]

tab1, tab2 = st.tabs(["🔴 Live & Upcoming", "🏏 IPL Season Explorer"])

with tab1:
    st.subheader("📅 Live & Upcoming Matches")
    if not filtered_df.empty:
        cols = st.columns(3)
        for index, row in filtered_df.iterrows():
            with cols[index % 3]:
                with st.container(border=True):
                    st.caption(f"{row['match_desc']} • {row['series_name'][:25]}... • **{row['format_type']}**")
                    st.markdown(f"🛡️ **{row['team1']}**")
                    st.markdown(f"⚔️ **{row['team2']}**")
                    st.caption(f"🕒 {row['match_date']}")
    else:
        st.warning("No live matches found.")

with tab2:
    years = ["All-Time"] + [str(y) for y in range(2025, 2007, -1)]
    selected_year = st.selectbox("Select IPL Season:", years)
    st.markdown("---")

    total_matches, df_batters, df_bowlers, df_mom, df_matches_raw = load_season_dashboard(selected_year)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🏏 Matches", total_matches)
    if not df_batters.empty: c2.metric("🟠 Orange Cap", df_batters.iloc[0]['batter'], f"{df_batters.iloc[0]['runs']} Runs", delta_color="normal")
    if not df_bowlers.empty: c3.metric("🟣 Purple Cap", df_bowlers.iloc[0]['bowler'], f"{df_bowlers.iloc[0]['wickets']} Wickets", delta_color="normal")
    if not df_mom.empty: c4.metric("⭐ Most MVP", df_mom.iloc[0]['player_of_match'], f"{df_mom.iloc[0]['awards']} Awards", delta_color="normal")

    st.markdown("---")

    col_pt, col_charts = st.columns([1.5, 1])

    with col_pt:
        st.subheader(f"📊 {selected_year} Points Table")
        pt_df = get_points_table(df_matches_raw)
        if not pt_df.empty:
            st.dataframe(pt_df, use_container_width=True)
        else:
            st.info("Points Table data not available for this selection.")

    with col_charts:
        st.subheader("Top Run Scorers")
        if not df_batters.empty: st.bar_chart(df_batters.set_index('batter'), color="#f5a623")
        st.subheader("Top Wicket Takers")
        if not df_bowlers.empty: st.bar_chart(df_bowlers.set_index('bowler'), color="#9013fe")