import pandas as pd
import sqlite3

print("⏳ Reading Match Summary CSV...")
df = pd.read_csv('matches.csv')

conn = sqlite3.connect('sports_analytics.db')

print("💾 Saving to database...")
df.to_sql('match_summary', conn, if_exists='replace', index=False)

conn.close()
print("✅ SUCCESS: Match summaries are locked in the vault!")