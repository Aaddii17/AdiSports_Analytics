import pandas as pd
import sqlite3

print("⏳ Reading raw Kaggle Schedule...")
df = pd.read_csv('T20 Wc {2026}/matches.csv')

# 1. Convert the text dates into actual mathematical Time objects
df['date'] = pd.to_datetime(df['date'])

# 2. THE FILTER: Slice out exactly what we want (March 28 to June 3)
start_date = '2026-03-28'
end_date = '2026-06-03'
mask = (df['date'] >= start_date) & (df['date'] <= end_date)
filtered_df = df.loc[mask].copy()

# 3. Convert dates back to neat strings for the database
filtered_df['date'] = filtered_df['date'].dt.strftime('%Y-%m-%d')

print(f"🧹 Filtered schedule down to {len(filtered_df)} valid upcoming matches.")

# 4. Build the final clean table
df_schedule = pd.DataFrame()
df_schedule['match_date'] = filtered_df['date']
df_schedule['team1'] = filtered_df['team1']
df_schedule['team2'] = filtered_df['team2']
df_schedule['format_type'] = 'T20'
df_schedule['series_name'] = 'ICC T20 World Cup 2026'
df_schedule['match_desc'] = filtered_df['stage'] + ' - ' + filtered_df['venue']

# 5. Push to the vault
conn = sqlite3.connect('sports_analytics.db')
print("💾 Saving perfectly timed matches to database...")
df_schedule.to_sql('upcoming_matches', conn, if_exists='replace', index=False)

conn.close()
print("✅ SUCCESS: Strict time-filtered schedule loaded into the Live tab!")