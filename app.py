import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="AdiSports Analytics", page_icon="🏏", layout="wide")

st.title("🏏 AdiSports Analytics Hub")

@st.cache_data
def load_data():
    conn = sqlite3.connect('sports_analytics.db')
    query = "SELECT match_date, team1, team2, format_type, series_name, match_desc FROM upcoming_matches"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

df_matches = load_data()

st.sidebar.header("🔍 Filter Matches")

formats = ["All Formats"] + df_matches['format_type'].unique().tolist()
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
                
                st.button("Forecast & Details", key=f"btn_{index}", use_container_width=True)
else:
    st.warning("No matches found matching your filters. Try a different search!")