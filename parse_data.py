import json
import sqlite3

conn = sqlite3.connect('sports_analytics.db')
cursor = conn.cursor()

try:
    with open('cached_sports_data.json', 'r') as file:
        data = json.load(file)
except FileNotFoundError:
    print("❌ ERROR: Could not find 'cached_sports_data.json'. Run fetch_data.py first!")
    exit()

print("🔄 Processing data and saving to database...")

matches_added = 0

try:
    schedules = data['response']['schedules']
    
    for day in schedules:
        if 'scheduleAdWrapper' in day:
            match_date = day['scheduleAdWrapper']['date']
            match_list = day['scheduleAdWrapper']['matchScheduleList']
        elif 'date' in day:
            match_date = day['date']
            match_list = day['matchScheduleList']
        else:
            continue
        
        for series in match_list:
            series_name = series['seriesName']
            
            for match in series['matchInfo']:
                team1 = match['team1']['teamName']
                team2 = match['team2']['teamName']
                format_type = match.get('matchFormat', 'Unknown')
                desc = match.get('matchDesc', 'N/A')
                
                cursor.execute('''
                    INSERT INTO upcoming_matches (match_date, team1, team2, format_type, match_desc, series_name)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (match_date, team1, team2, format_type, desc, series_name))
                
                matches_added += 1

    conn.commit()
    print(f"✅ SUCCESS: {matches_added} upcoming matches have been permanently saved to the database!")

except KeyError as e:
    print(f"❌ DATA ERROR: The API structure changed. Missing key: {e}")

finally:
    conn.close()