import requests
from lxml import html
import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from datetime import datetime
import pytz
import time
import os
import json


# get today's date
today_date = datetime.now().strftime('%Y-%m-%d')

# Define London timezone
london_tz = pytz.timezone('Europe/London')

urls = {
    'London': {
        'weather': 'https://www.bbc.com/weather/2643743',
        'tide': 'https://www.bbc.co.uk/weather/coast-and-sea/tide-tables/2/113'
    },
    'Birmingham': {
        'weather': 'https://www.bbc.com/weather/2655603',
        'tide': 'https://www.bbc.co.uk/weather/coast-and-sea/tide-tables/2/113'
    },
    'Manchester': {
        'weather': 'https://www.bbc.com/weather/2643123',
        'tide': 'https://www.bbc.co.uk/weather/coast-and-sea/tide-tables/2/113'
    },
    'Nottingham': {
        'weather': 'https://www.bbc.com/weather/2641170',
        'tide': 'https://www.bbc.co.uk/weather/coast-and-sea/tide-tables/2/113'
    },
    'Leeds': {
        'weather': 'https://www.bbc.com/weather/2644688',
        'tide': 'https://www.bbc.co.uk/weather/coast-and-sea/tide-tables/2/113'
    },
    'Liverpool': {
        'weather': 'https://www.bbc.co.uk/weather/2644210',
        'tide': 'https://www.bbc.co.uk/weather/coast-and-sea/tide-tables/2/113'
    },
    'Bristol': {
        'weather': 'https://www.bbc.co.uk/weather/2654675',
        'tide': 'https://www.bbc.co.uk/weather/coast-and-sea/tide-tables/2/113'
    },
    'Newcastle': {
        'weather': 'https://www.bbc.co.uk/weather/2641673',
        'tide': 'https://www.bbc.co.uk/weather/coast-and-sea/tide-tables/2/113'
    },
    'Southampton': {
        'weather': 'https://www.bbc.co.uk/weather/2637487',
        'tide': 'https://www.bbc.co.uk/weather/coast-and-sea/tide-tables/2/113'
    },
    'Brighton': {
        'weather': 'https://www.bbc.co.uk/weather/2654710',
        'tide': 'https://www.bbc.co.uk/weather/coast-and-sea/tide-tables/2/113'
    }
}




def map_level(code):
    """Maps single-letter codes to descriptive levels."""
    level = {'L': 'Low', 'M': 'Medium', 'H': 'High'}.get(code, 'Unknown')
    print(f"Map level: code={code}, level={level}")
    return level


def scrape_tide_times(session, location):
    """Scrapes tide times and heights from the URL based on location."""
    url = urls[location]['tide']
    print(f"Scraping tide times for {location} from {url}")

    response = session.get(url)
    print(f"HTTP GET response status: {response.status_code}")

    tree = html.fromstring(response.content)

    tide_times = []

    # Extract low tide times and heights
    low_tide_xpath_morning_time = f'//*[@id="section-{today_date}"]/table/tbody/tr[1]/td[1]/span'
    low_tide_xpath_morning_height = f'//*[@id="section-{today_date}"]/table/tbody/tr[1]/td[2]'
    low_tide_xpath_evening_time = f'//*[@id="section-{today_date}"]/table/tbody/tr[3]/td[1]/span'
    low_tide_xpath_evening_height = f'//*[@id="section-{today_date}"]/table/tbody/tr[3]/td[2]'

    low_tide_elem_morning_time = tree.xpath(low_tide_xpath_morning_time)
    low_tide_elem_morning_height = tree.xpath(low_tide_xpath_morning_height)
    low_tide_elem_evening_time = tree.xpath(low_tide_xpath_evening_time)
    low_tide_elem_evening_height = tree.xpath(low_tide_xpath_evening_height)

    print(f"Low tide morning time elements: {low_tide_elem_morning_time}")
    print(f"Low tide morning height elements: {low_tide_elem_morning_height}")
    print(f"Low tide evening time elements: {low_tide_elem_evening_time}")
    print(f"Low tide evening height elements: {low_tide_elem_evening_height}")

    low_tide_time_morning = low_tide_elem_morning_time[0].text.strip() if low_tide_elem_morning_time else "N/A"
    low_tide_height_morning = low_tide_elem_morning_height[0].text.strip() if low_tide_elem_morning_height else "N/A"
    low_tide_time_evening = low_tide_elem_evening_time[0].text.strip() if low_tide_elem_evening_time else "N/A"
    low_tide_height_evening = low_tide_elem_evening_height[0].text.strip() if low_tide_elem_evening_height else "N/A"

    print(f"Low tide morning time: {low_tide_time_morning}, height: {low_tide_height_morning}")
    print(f"Low tide evening time: {low_tide_time_evening}, height: {low_tide_height_evening}")

    tide_times.append((low_tide_time_morning, low_tide_height_morning, low_tide_time_evening, low_tide_height_evening))

    # Extract high tide times and heights
    high_tide_xpath_morning_time = f'//*[@id="section-{today_date}"]/table/tbody/tr[2]/td[1]/span'
    high_tide_xpath_morning_height = f'//*[@id="section-{today_date}"]/table/tbody/tr[2]/td[2]'
    high_tide_xpath_evening_time = f'//*[@id="section-{today_date}"]/table/tbody/tr[4]/td[1]/span'
    high_tide_xpath_evening_height = f'//*[@id="section-{today_date}"]/table/tbody/tr[4]/td[2]'

    high_tide_elem_morning_time = tree.xpath(high_tide_xpath_morning_time)
    high_tide_elem_morning_height = tree.xpath(high_tide_xpath_morning_height)
    high_tide_elem_evening_time = tree.xpath(high_tide_xpath_evening_time)
    high_tide_elem_evening_height = tree.xpath(high_tide_xpath_evening_height)

    print(f"High tide morning time elements: {high_tide_elem_morning_time}")
    print(f"High tide morning height elements: {high_tide_elem_morning_height}")
    print(f"High tide evening time elements: {high_tide_elem_evening_time}")
    print(f"High tide evening height elements: {high_tide_elem_evening_height}")

    high_tide_time_morning = high_tide_elem_morning_time[0].text.strip() if high_tide_elem_morning_time else "N/A"
    high_tide_height_morning = high_tide_elem_morning_height[0].text.strip() if high_tide_elem_morning_height else "N/A"
    high_tide_time_evening = high_tide_elem_evening_time[0].text.strip() if high_tide_elem_evening_time else "N/A"
    high_tide_height_evening = high_tide_elem_evening_height[0].text.strip() if high_tide_elem_evening_height else "N/A"

    print(f"High tide morning time: {high_tide_time_morning}, height: {high_tide_height_morning}")
    print(f"High tide evening time: {high_tide_time_evening}, height: {high_tide_height_evening}")

    tide_times.append(
        (high_tide_time_morning, high_tide_height_morning, high_tide_time_evening, high_tide_height_evening))

    return tide_times


def convert_to_datetime(time_str):
    """Converts a string time format into datetime format."""
    try:
        dt = datetime.strptime(time_str, '%H:%M')
        print(f"Converted time string '{time_str}' to datetime object {dt}")
        return dt
    except ValueError:
        print(f"Failed to convert time string '{time_str}'")
        return "N/A"


def get_weather_data(session, location, time_of_search):
    """Fetches weather data from the URL based on location and returns it as a dictionary."""
    url = urls[location]['weather']
    print(f"Fetching weather data for {location} from {url}")

    response = session.get(url)
    print(f"HTTP GET response status: {response.status_code}")

    tree = html.fromstring(response.content)

    # Helper function to extract and clean data
    def extract_and_clean(xpath, elem_index=0, suffix=None, convert_to_float=False):
        elem = tree.xpath(xpath)
        if elem:
            text = elem[elem_index].text.strip()
            if suffix:
                text = text[:-len(suffix)]
            print(f"Extracted text '{text}' from xpath '{xpath}'")
            return float(text) if convert_to_float else text
        print(f"No elements found for xpath '{xpath}'")
        return "N/A"

    # Fetch tide times dynamically
    tide_times = scrape_tide_times(session, location)

    weather_data = {
        'Time of Search': time_of_search,
        'High Temperature(°C)': extract_and_clean(
            '//*[@id="daylink-0"]/div[4]/div[1]/div/div[4]/div/div[1]/span[2]/span/span[1]', suffix='°',
            convert_to_float=True),
        'Low Temperature(°C)': extract_and_clean(
            '//*[@id="daylink-0"]/div[4]/div[1]/div/div[4]/div/div[2]/span[2]/span/span[1]', suffix='°',
            convert_to_float=True),
        'Current Temperature(°C)': extract_and_clean(
            '//*[@id="wr-forecast"]/div[4]/div/div[1]/div[2]/div/div/div/div[2]/ol/li[1]/button/div[1]/div[2]/div[3]/div[2]/div/div/div[2]/span/span[1]',
            suffix='°', convert_to_float=True),
        'Weather Condition': extract_and_clean(
            '//*[@id="wr-forecast"]/div[4]/div/div[1]/div[2]/div/div/div/div[2]/ol/li[1]/button/div[2]/div/span'),
        'Wind Speed(mph)': extract_and_clean(
            '//*[@id="wr-forecast"]/div[4]/div/div[1]/div[2]/div/div/div/div[2]/ol/li[1]/button/div[1]/div[2]/div[3]/div[4]/div/span[3]/span/span[1]'),
        'Humidity(%)': extract_and_clean(
            '//*[@id="wr-forecast"]/div[4]/div/div[1]/div[2]/div/div/div/div[2]/ol/li[1]/button/div[2]/div/div/div[1]/dl/dd[1]',
            suffix='%', convert_to_float=True),
        'Pressure(mb)': extract_and_clean(
            '//*[@id="wr-forecast"]/div[4]/div/div[1]/div[2]/div/div/div/div[2]/ol/li[1]/button/div[2]/div/div/div[1]/dl/dd[2]',
            suffix=' mb'),
        'Visibility': extract_and_clean(
            '//*[@id="wr-forecast"]/div[4]/div/div[1]/div[2]/div/div/div/div[2]/ol/li[1]/button/div[2]/div/div/div[1]/dl/dd[3]'),
        'Location': extract_and_clean('//*[@id="wr-location-name-id"]'),
        'Wind Direction': extract_and_clean(
            '//*[@id="wr-forecast"]/div[4]/div/div[1]/div[2]/div/div/div/div[2]/ol/li[1]/button/div[2]/div/div/div[4]'),
        'UV Index': map_level(extract_and_clean(
            '//*[@id="wr-forecast"]/div[4]/div/div[1]/div[4]/div/div[1]/div[2]/span[1]/span[1]/span[2]')),
        'Pollen': map_level(extract_and_clean(
            '//*[@id="wr-forecast"]/div[4]/div/div[1]/div[4]/div/div[1]/div[2]/span[1]/span[1]/span[2]')),
        'Pollution': map_level(extract_and_clean(
            '//*[@id="wr-forecast"]/div[4]/div/div[1]/div[4]/div/div[1]/div[2]/span[2]/span[1]/span[2]')),
        'Chance of Precipitation(%)': extract_and_clean(
            '//*[@id="wr-forecast"]/div[4]/div/div[1]/div[2]/div/div/div/div[2]/ol/li[1]/button/div[1]/div[2]/div[3]/div[3]/div[2]',
            suffix='%', convert_to_float=True),
        'Sunset': extract_and_clean(
            '//*[@id="wr-forecast"]/div[4]/div/div[1]/div[4]/div/div[1]/div[1]/span[2]/span[2]'),
        'Sunrise': extract_and_clean(
            '//*[@id="wr-forecast"]/div[4]/div/div[1]/div[4]/div/div[1]/div[1]/span[1]/span[2]'),
        'Low Tide Morning Time': tide_times[0][0],
        'Low Tide Morning Height(M)': tide_times[0][1],
        'High Tide Morning Time': tide_times[1][0],
        'High Tide Morning Height(M)': tide_times[1][1],
        'Low Tide Evening Time': tide_times[0][2],
        'Low Tide Evening Height(M)': tide_times[0][3],
        'High Tide Evening Time': tide_times[1][2],
        'High Tide Evening Height(M)': tide_times[1][3],

    }

    print(f"Weather data for {location}: {weather_data}")

    return weather_data


def list_worksheets(client, spreadsheet_url):
    """List all worksheet names in the Google Sheets document."""
    print(f"Listing worksheets for spreadsheet URL: {spreadsheet_url}")
    spreadsheet = client.open_by_url(spreadsheet_url)
    worksheets = spreadsheet.worksheets()
    for worksheet in worksheets:
        print(f"Worksheet title: {worksheet.title}")


def write_to_google_sheets(data, sheet_name, headers):
    """Writes data to a specified Google Sheets sheet."""
    # Setup Google Sheets API credentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # JSON credentials directly in the script
    # creds_dict = {
          
    #     }
    # token updated jan 2025

    # creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    # print("Google Sheets API credentials loaded")

    # Get credentials from environment variable
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    if not creds_json:
        raise ValueError("GOOGLE_CREDENTIALS environment variable not found")
    
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    print("Google Sheets API credentials loaded")

    client = gspread.authorize(creds)
    print("Authorized Google Sheets client")

    # Open the Google Sheet and select the worksheet
    spreadsheet = client.open_by_url(
        'https://docs.google.com/spreadsheets/d/1CPudH3miJZRKii6PAN_YBfV2QLdt9CezxUK0YBshsMg/edit?usp=sharing')
    worksheet = spreadsheet.worksheet(sheet_name)

    print(f"Selected worksheet: {sheet_name}")

    # # Clear existing content
    # worksheet.clear()
    # print("Cleared existing content in worksheet")

    # Check if headers are already present

    existing_values = worksheet.get_all_values()
    # If sheet has more than 1000 rows
    if len(existing_values) > 1000:
        print(f"Sheet {sheet_name} has exceeded 1000 rows. Clearing and preserving headers...")
        worksheet.clear()
        worksheet.append_row(headers)
        print("Headers rewritten successfully")
    elif not existing_values or existing_values[0] != headers:
        worksheet.append_row(headers)
        print(f"Appended headers: {headers}")
    else:
        print("Headers already exist; not appending headers.")


    # -------------------------------------------------------------
    # OLD CODE THAT DOES WORK BUT DOES NOT DELETE OLD CONTENT ONCE IT HAS REACHED A LIMIT
    # existing_values = worksheet.get_all_values()
    # if not existing_values or existing_values[0] != headers:
    #     worksheet.append_row(headers)
    #     print(f"Appended headers: {headers}")
    # else:
    #     print("Headers already exist; not appending headers.")
    # -------------------------------------------------------------
        

    # Append data
    for row in data:
        worksheet.append_row(row)
        print(f"Appended row data: {row}")


def get_sheet_name(location):
    sheet_names = {
        'London': 'Sheet1',
        'Birmingham': 'Sheet2',
        'Manchester': 'Sheet3',
        'Nottingham': 'Sheet4',
        'Leeds': 'Sheet5',
        'Liverpool': 'Sheet6',
        'Bristol': 'Sheet7',
        'Newcastle': 'Sheet8',
        'Southampton': 'Sheet9',
        'Brighton': 'Sheet10'
    }

    if location in sheet_names:
        return sheet_names[location]
    else:
        raise ValueError(f"Unknown location: {location}")


def main():
    # Setup Google Sheets client
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # creds_dict = creds_dict = {
         
    #     }
    # # creds updated jan 2025

    
    # creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    # print("Google Sheets API credentials loaded")

    # Get credentials from environment variable
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    if not creds_json:
        raise ValueError("GOOGLE_CREDENTIALS environment variable not found")
    
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    print("Google Sheets API credentials loaded")

    client = gspread.authorize(creds)
    print("Authorized Google Sheets client")

    # List worksheet names
    list_worksheets(client,
                    'https://docs.google.com/spreadsheets/d/1CPudH3miJZRKii6PAN_YBfV2QLdt9CezxUK0YBshsMg/edit?usp=sharing')

    locations = [
        'London', 'Birmingham', 'Manchester', 'Nottingham', 'Leeds',
        'Liverpool', 'Bristol', 'Newcastle', 'Southampton', 'Brighton'
    ]

    headers = [
        'Time of Search', 'High Temperature(°C)', 'Low Temperature(°C)', 'Current Temperature(°C)',
        'Weather Condition', 'Wind Speed(mph)', 'Humidity(%)', 'Pressure(mb)', 'Visibility', 'Location',
        'Wind Direction', 'UV Index', 'Pollen', 'Pollution', 'Chance of Precipitation(%)',
        'Sunset', 'Sunrise', 'Low Tide Morning Time', 'Low Tide Morning Height(M)',
        'High Tide Morning Time', 'High Tide Morning Height(M)', 'Low Tide Evening Time',
        'Low Tide Evening Height(M)', 'High Tide Evening Time', 'High Tide Evening Height(M)'
    ]

    for location in locations:
        # Use the current time for the weather data
        time_of_search = datetime.now(london_tz).strftime('%Y-%m-%d %H:%M:%S')
        print(f"Fetching data for location: {location} at {time_of_search}")

        with requests.Session() as session:
            # Get weather data
            weather_data = get_weather_data(session, location, time_of_search)

            # Get tide times
            tide_times = scrape_tide_times(session, location)

            # Prepare data for Google Sheets
            tide_times_data = [(
                weather_data['Time of Search'],
                weather_data['High Temperature(°C)'],
                weather_data['Low Temperature(°C)'],
                weather_data['Current Temperature(°C)'],
                weather_data['Weather Condition'],
                weather_data['Wind Speed(mph)'],
                weather_data['Humidity(%)'],
                weather_data['Pressure(mb)'],
                weather_data['Visibility'],
                weather_data['Location'],
                weather_data['Wind Direction'],
                weather_data['UV Index'],
                weather_data['Pollen'],
                weather_data['Pollution'],
                weather_data['Chance of Precipitation(%)'],
                weather_data['Sunset'],
                weather_data['Sunrise'],
                weather_data['Low Tide Morning Time'],
                weather_data['Low Tide Morning Height(M)'],
                weather_data['High Tide Morning Time'],
                weather_data['High Tide Morning Height(M)'],
                weather_data['Low Tide Evening Time'],
                weather_data['Low Tide Evening Height(M)'],
                weather_data['High Tide Evening Time'],
                weather_data['High Tide Evening Height(M)']
            )]

            print(f"Prepared data for Google Sheets: {tide_times_data}")

            # Get the appropriate sheet name based on the location
            sheet_name = get_sheet_name(location)

            print(f"Writing data to sheet: {sheet_name}")
            write_to_google_sheets(tide_times_data, sheet_name, headers)

if __name__ == "__main__":
    main()
