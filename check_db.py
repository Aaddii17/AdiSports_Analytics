import sqlite3
import pandas as pd

conn = sqlite3.connect('sports_analytics.db')

try:
    df_matches = pd.read_sql_query("SELECT * FROM match_summary LIMIT 1", conn)
    print("MATCH SUMMARY COLUMNS:", df_matches.columns.tolist())
except Exception as e:
    print("Match Summary error:", e)

try:
    df_history = pd.read_sql_query("SELECT * FROM ipl_history LIMIT 1", conn)
    print("IPL HISTORY COLUMNS:", df_history.columns.tolist())
except Exception as e:
    print("IPL History error:", e)

conn.close()