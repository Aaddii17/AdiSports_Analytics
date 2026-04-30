import pandas as pd
import sqlite3

print("⏳ Reading massive CSV file. This might take a few seconds...")

df = pd.read_csv('ipl_history.csv')

print(f"📊 Loaded {len(df)} rows into memory! Connecting to the vault...")

conn = sqlite3.connect('sports_analytics.db')

print("💾 Saving to database...")
df.to_sql('ipl_history', conn, if_exists='replace', index=False)

conn.close()
print("✅ SUCCESS: Historical data is now permanently locked in the vault!")