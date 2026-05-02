import pandas as pd
import sqlite3

df = pd.read_csv('T20 Wc {2026}/matches.csv')

df_schedule = pd.DataFrame()
df_schedule['match_date'] = df['date']
df_schedule['team1'] = df['team1']
df_schedule['team2'] = df['team2']
df_schedule['format_type'] = 'T20'
df_schedule['series_name'] = 'ICC T20 World Cup 2026'
df_schedule['match_desc'] = df['stage'] + ' - ' + df['venue']

conn = sqlite3.connect('sports_analytics.db')

df_schedule.to_sql('upcoming_matches', conn, if_exists='replace', index=False)

conn.close()
print("✅ SUCCESS: T20 World Cup Schedule loaded into the Live tab!")