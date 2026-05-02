import pandas as pd
import sqlite3

print("⏳ Reading raw Kaggle Schedule...")
df = pd.read_csv('T20 Wc {2026}/matches.csv')

# Bypassing the strict date filter so the app isn't empty!
filtered_df = df.copy()

print(f"🧹 Bypassed filter. Loading all {len(filtered_df)} matches.")

df_schedule = pd.DataFrame()
df_schedule['match_date'] = filtered_df['date']
df_schedule['team1'] = filtered_df['team1']
df_schedule['team2'] = filtered_df['team2']
df_schedule['format_type'] = 'T20'
df_schedule['series_name'] = 'ICC T20 World Cup 2026'
df_schedule['match_desc'] = filtered_df['stage'] + ' - ' + filtered_df['venue']

conn = sqlite3.connect('sports_analytics.db')
print("💾 Saving matches to database...")
df_schedule.to_sql('upcoming_matches', conn, if_exists='replace', index=False)

conn.close()
print("✅ SUCCESS: Schedule loaded into the Live tab!")