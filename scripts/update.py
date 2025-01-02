import gspread
import pandas as pd
import sqlite3
from oauth2client.service_account import ServiceAccountCredentials
import json  # Add this import
import os
import os




# Define the paths
database_file_path = 'data/nationwide_weather.db'
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1CPudH3miJZRKii6PAN_YBfV2QLdt9CezxUK0YBshsMg/edit?usp=sharing'

# Set up Google Sheets credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
try:
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    if not creds_json:
        raise ValueError("GOOGLE_CREDENTIALS environment variable not found")
    
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    print("Google Sheets API credentials loaded")
except Exception as e:
    print(f"Error loading credentials: {e}")
    raise
client = gspread.authorize(creds)
sheet = client.open_by_url(spreadsheet_url)

# Connect to the SQLite database
conn = sqlite3.connect(database_file_path)
cursor = conn.cursor()

# Process each sheet in the spreadsheet
for sheet_index in range(1, 11):  # Adjust this range based on the number of sheets you have
    worksheet_name = f'Sheet{sheet_index}'
    print(f"Processing {worksheet_name}...")

    # Read the data from the Google Sheets
    worksheet = sheet.worksheet(worksheet_name)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    for _, row in df.iterrows():
        # For each table, check if the record exists and insert if not
        location = row['Location']
        cursor.execute('''
            SELECT location_id FROM Locations WHERE name = ?
        ''', (location,))
        location_id = cursor.fetchone()
        if location_id is None:
            cursor.execute('''
                INSERT INTO Locations (name)
                VALUES (?)
            ''', (location,))
            location_id = cursor.lastrowid
        else:
            location_id = location_id[0]

        weather_condition = row['Weather Condition']
        cursor.execute('''
            SELECT weather_condition_id FROM WeatherConditions WHERE description = ?
        ''', (weather_condition,))
        weather_condition_id = cursor.fetchone()
        if weather_condition_id is None:
            cursor.execute('''
                INSERT INTO WeatherConditions (description)
                VALUES (?)
            ''', (weather_condition,))
            weather_condition_id = cursor.lastrowid
        else:
            weather_condition_id = weather_condition_id[0]

        wind_direction = row['Wind Direction']
        cursor.execute('''
            SELECT wind_direction_id FROM WindDirections WHERE description = ?
        ''', (wind_direction,))
        wind_direction_id = cursor.fetchone()
        if wind_direction_id is None:
            cursor.execute('''
                INSERT INTO WindDirections (description)
                VALUES (?)
            ''', (wind_direction,))
            wind_direction_id = cursor.lastrowid
        else:
            wind_direction_id = wind_direction_id[0]

        uv_index = row['UV Index']
        cursor.execute('''
            SELECT uv_index_id FROM UVIndexLevels WHERE level = ?
        ''', (uv_index,))
        uv_index_id = cursor.fetchone()
        if uv_index_id is None:
            cursor.execute('''
                INSERT INTO UVIndexLevels (level)
                VALUES (?)
            ''', (uv_index,))
            uv_index_id = cursor.lastrowid
        else:
            uv_index_id = uv_index_id[0]

        pollen = row['Pollen']
        cursor.execute('''
            SELECT pollen_id FROM PollenLevels WHERE level = ?
        ''', (pollen,))
        pollen_id = cursor.fetchone()
        if pollen_id is None:
            cursor.execute('''
                INSERT INTO PollenLevels (level)
                VALUES (?)
            ''', (pollen,))
            pollen_id = cursor.lastrowid
        else:
            pollen_id = pollen_id[0]

        pollution = row['Pollution']
        cursor.execute('''
            SELECT pollution_id FROM PollutionLevels WHERE level = ?
        ''', (pollution,))
        pollution_id = cursor.fetchone()
        if pollution_id is None:
            cursor.execute('''
                INSERT INTO PollutionLevels (level)
                VALUES (?)
            ''', (pollution,))
            pollution_id = cursor.lastrowid
        else:
            pollution_id = pollution_id[0]

        visibility = row['Visibility']
        cursor.execute('''
            SELECT visibility_id FROM VisibilityLevels WHERE description = ?
        ''', (visibility,))
        visibility_id = cursor.fetchone()
        if visibility_id is None:
            cursor.execute('''
                INSERT INTO VisibilityLevels (description)
                VALUES (?)
            ''', (visibility,))
            visibility_id = cursor.lastrowid
        else:
            visibility_id = visibility_id[0]

        # For WeatherReports, insert if not exists based on time_of_search
        time_of_search = row['Time of Search']
        cursor.execute('''
            SELECT COUNT(*) FROM WeatherReports WHERE time_of_search = ?
        ''', (time_of_search,))
        if cursor.fetchone()[0] == 0:
            # Prepare values for insertion into WeatherReports
            values = (
                time_of_search, row['High Temperature(°C)'], row['Low Temperature(°C)'], row['Current Temperature(°C)'],
                weather_condition_id, row['Wind Speed(mph)'], row['Humidity(%)'], row['Pressure(mb)'], visibility_id,
                location_id, wind_direction_id, uv_index_id, pollen_id, pollution_id,
                row['Chance of Precipitation(%)'], row['Sunset'], row['Sunrise'],
                row['Low Tide Morning Time'], row['Low Tide Morning Height(M)'],
                row['High Tide Morning Time'], row['High Tide Morning Height(M)'],
                row['Low Tide Evening Time'], row['Low Tide Evening Height(M)'],
                row['High Tide Evening Time'], row['High Tide Evening Height(M)']
            )

            # Insert data into WeatherReports
            cursor.execute('''
                INSERT INTO WeatherReports (
                    time_of_search, high_temperature, low_temperature, current_temperature,
                    weather_condition_id, wind_speed, humidity, pressure, visibility_id,
                    location_id, wind_direction_id, uv_index_id, pollen_id, pollution_id,
                    chance_of_precipitation, sunset, sunrise, low_tide_morning_time,
                    low_tide_morning_height, high_tide_morning_time, high_tide_morning_height,
                    low_tide_evening_time, low_tide_evening_height, high_tide_evening_time,
                    high_tide_evening_height
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', values)

# Commit changes and close the connection
conn.commit()


# Define CTE queries for each table to remove duplicates
cte_queries = {
    'Locations': '''
        WITH RankedLocations AS (
            SELECT rowid, name,
                   ROW_NUMBER() OVER (PARTITION BY name ORDER BY rowid) AS rn
            FROM Locations
        )
        DELETE FROM Locations
        WHERE rowid IN (
            SELECT rowid
            FROM RankedLocations
            WHERE rn > 1
        );
    ''',
    'WeatherConditions': '''
        WITH RankedWeatherConditions AS (
            SELECT rowid, description,
                   ROW_NUMBER() OVER (PARTITION BY description ORDER BY rowid) AS rn
            FROM WeatherConditions
        )
        DELETE FROM WeatherConditions
        WHERE rowid IN (
            SELECT rowid
            FROM RankedWeatherConditions
            WHERE rn > 1
        );
    ''',
    'UVIndexLevels': '''
        WITH RankedUVIndexLevels AS (
            SELECT rowid, level,
                   ROW_NUMBER() OVER (PARTITION BY level ORDER BY rowid) AS rn
            FROM UVIndexLevels
        )
        DELETE FROM UVIndexLevels
        WHERE rowid IN (
            SELECT rowid
            FROM RankedUVIndexLevels
            WHERE rn > 1
        );
    ''',
    'PollenLevels': '''
        WITH RankedPollenLevels AS (
            SELECT rowid, level,
                   ROW_NUMBER() OVER (PARTITION BY level ORDER BY rowid) AS rn
            FROM PollenLevels
        )
        DELETE FROM PollenLevels
        WHERE rowid IN (
            SELECT rowid
            FROM RankedPollenLevels
            WHERE rn > 1
        );
    ''',
    'PollutionLevels': '''
        WITH RankedPollutionLevels AS (
            SELECT rowid, level,
                   ROW_NUMBER() OVER (PARTITION BY level ORDER BY rowid) AS rn
            FROM PollutionLevels
        )
        DELETE FROM PollutionLevels
        WHERE rowid IN (
            SELECT rowid
            FROM RankedPollutionLevels
            WHERE rn > 1
        );
    ''',
    'WindDirections': '''
        WITH RankedWindDirections AS (
            SELECT rowid, description,
                   ROW_NUMBER() OVER (PARTITION BY description ORDER BY rowid) AS rn
            FROM WindDirections
        )
        DELETE FROM WindDirections
        WHERE rowid IN (
            SELECT rowid
            FROM RankedWindDirections
            WHERE rn > 1
        );
    ''',
    'VisibilityLevels': '''
        WITH RankedVisibilityLevels AS (
            SELECT rowid, description,
                   ROW_NUMBER() OVER (PARTITION BY description ORDER BY rowid) AS rn
            FROM VisibilityLevels
        )
        DELETE FROM VisibilityLevels
        WHERE rowid IN (
            SELECT rowid
            FROM RankedVisibilityLevels
            WHERE rn > 1
        );
    '''
}

# Process each table
for table_name, cte_sql in cte_queries.items():
    print(f"Processing {table_name}...")
    cursor.execute(cte_sql)
    conn.commit()
    print(f"Removed duplicates from {table_name}.")

# Close the connection
conn.close()

print("All tables processed successfully.")
