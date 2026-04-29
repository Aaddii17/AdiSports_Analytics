import sqlite3
conn = sqlite3.connect('sports_analytics.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS upcoming_matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_date TEXT,
        team1 TEXT,
        team2 TEXT,
        format_type TEXT,
        match_desc TEXT,
        series_name TEXT
    )
''')

conn.commit()
conn.close()

print("✅ SUCCESS: Database 'sports_analytics.db' created successfully!")
print("✅ SUCCESS: Table 'upcoming_matches' is ready to receive data.")