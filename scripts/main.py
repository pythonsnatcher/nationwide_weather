import requests
from lxml import html
import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from datetime import datetime
import pytz
import time

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
    creds_dict = {
          "type": "service_account",
          "project_id": "weather-data-429210",
          "private_key_id": "57f949e51c1bc58946026deb253a45f5d2f7aaa6",
          "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCVKqzdsrIH7PwN\noAm4ta0bJi1xsRNvbciYlFOXWD0DDgOtnUIOnkWfec/vzubr1+2s1ml67vaL3WGB\nE8It2EOoE5ctbiOBINV8VFhLbh+JLggISwvP5r/dV33VDNDEhb4M1t4Nh2oItfIT\nRP951Cbw9nkdJE0QKfzkvjWvwowW8osI4jelvUhQn2BfAhABguPa7p0kgHd67NJI\neLuPKvLr6tpTEAMbrGabYuarpQOjl7U1ABvbs68d+xCFpcU6ly5cUmZh1NM9YV1f\nItbCi7q/eqL5SbUNbsmDhNpev6oV2tzIXLaDrhd/2wBfhPBRgxQbO6ntTKFln9QA\n5DOQsYzTAgMBAAECggEAEs/9r+goM9UGOjcDgtwcJ4m6aYBKUd9SpouZD0P9ozOn\n8G7I30xuvhzVcLUeF9h1DTtCtP0LnbrJ3/GR/R4tSjajoQMm+dNzmT6PSX7AqMMO\nwvJUBwsJtOyiiLVuZEVJzBdn4eTre+Br1f+kXhpiNDmhhLSzU2U4Pnu5YZ/znbZq\ndr9q9Uy/+zM0axgjc+uysGd0XC5W/Y425ZZZ4jWca3zWgwRw/bDwnSR8yM0TsgtW\nBT5ZjoITA+UuWyUQ9q1O9VQzJdV0bDnkC6/J/Oj3KnN4W4P22yiHehDbsJX9H7fx\nAqh7OMQnLHWBRhi2GporJF/8UwqzBn42vL12FO8wQQKBgQDND0i0kLzxKs6RxeAc\ngb48+W9xd3j7Oi7IPm3UYqZvJJabdV5NYBxW6qKtZTYvgmzT4WsuW+lsvPmfAVYR\nJbFFlUtupnXom5G0zh3sYyhnyfyOPxW7Bxt7EXj+URmBFZ0D4gdBy1ggH1dN18AH\nxr8K8ELVbGlTcEJISM5cM13UuwKBgQC6OOQVNbezXYztNeuGg7e6SYpBffMcPZuV\nYaLZ2+FZ/kw2nG+ibBa98MS063B3Esjr9pHI91CiQDWybPSEL2G1UoNheMgHscNC\nzZtkIsFQSu/ZifVMBsHmlfbeHV9dj3fDrNfv/oTMiHgKDQ4+378b1oFgp31Rza6S\n2sTFPlsyyQKBgQDAt1SFHmHz5V8t8OGm6Oh5NZNe+AFjWlMNLl7Z87ynR6OjhrKR\n1XnM1cb9XtmF3PWaS4gHkanW3+NZZFAW3W21D5JM83Rsn4hYfD3zI12d7V7F8NPj\nadKR3uHvYRivEDj4pTxcwVaZGdta9SEsLcTt6s9k9PYnzKD+fi4yyLOucQKBgQCd\nEktfkHWn9qpdknNcfFFF8a2J3CBom5ZVg4sG0y3a6GGEVqLaju0HvMNODqBH7zJF\nxS3mIqSClkI0gy4jKIvzkut6FZQy2T9nY2FELwR7Ixn3lSOvwqteQPN/GatMkSxl\nga6JoVaF5j3JzIVNhw/8/QsXaW6Mxz4OZDRAYn4t8QKBgQCLarqOXPSkiKYoGz6u\nSDpK97DfCjzaexGIjY0207c5YOlNriwXYCGdKCsQ9IDzFn+D7Auj1CxAroavr/eB\nkzHpd5xR2yj55YxNqGtpevlaOp/8/TJMt3Y6ND3F9Ziiu8pksO7KIW0lJJdYa5k5\n7Nq1tMlvH7EzhghN9YxhARSK/g==\n-----END PRIVATE KEY-----\n",
          "client_email": "weather-data@weather-data-429210.iam.gserviceaccount.com",
          "client_id": "117847726458310784712",
          "auth_uri": "https://accounts.google.com/o/oauth2/auth",
          "token_uri": "https://oauth2.googleapis.com/token",
          "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
          "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/weather-data%40weather-data-429210.iam.gserviceaccount.com",
          "universe_domain": "googleapis.com"
        }

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
    if not existing_values or existing_values[0] != headers:
        worksheet.append_row(headers)
        print(f"Appended headers: {headers}")
    else:
        print("Headers already exist; not appending headers.")

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
    creds_dict = {
        "type": "service_account",
        "project_id": "weather-data-429210",
        "private_key_id": "af2c31cf7a66d123c4177f73f04fd01dca645a70",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCrVky4KtVU4WMl\nv82TyT/jTDyNv4Auk475CsROQgLSgIA6/EZ9fd+sIwbImEPkNw4bThe+coobn+Je\nu5lRg7yRVmXakqDCFPjq+2nV2riB0M2dBn3sgiCSxusYc1G0ieC3tpNBncy8M8ga\n/kBnAT9HRm/RHQP3so7hgRRghPE1ZmFq9buzDueqIy1TTTD89ZWnAS/sLNxefJhg\nIRMSCf1IBS/7fakNtch1WGbZr4Z1HuKXR8MajmCN1iOR1hcAHOn50uwGp78sYnel\nj8E2PC1sK1MMIGQc/k1UwG6jo1YV1k0Eu2IyXA3JukiSwBLfc2qHCw5Bq2+EGDjI\n6ChLkZllAgMBAAECggEAVYlZ9796jUuQQfJFYXhhKsqOmH14Msh74hzb7+3IluqM\nGeaEEnZaygcahd5uVmqd4kfUVsG77Rqe2ohxfF52L2CgrMPy+bGaq0Ukix0Ma9Kg\nM7pf90jnlh80kxpPOgBzbYP6dBGhenundMJlyIa43o5tmEoSBwDfj/jvAVidSvim\nTlweUrhBeT+5psdrsmHAk/Xv1Tqf9hPdnU8J9uz+5ATgjpIuB8InDlFD+yjhWHkZ\nF1FpoJaDaN69wHnYCE2TQVdbprkiPsOa9151kj+Gc/yBOMgGSvjsH7qTC9bptlz6\nzkgUHCjLum1Q/2r9jQj+9jHSB2H+O3q9j9wvPpZr6QKBgQDdYBVzqUee7r6sngY5\nDeKhBeIMpiHt4P4UMV0MmBQEaoRHm9LZSELlYQ/Btye2NDl4fIIByYHeEYEl6Chd\nxZtXJ1Z04P4txLmb0T4m+4/BVWwztwXklrO09Kgm62lYhbtqYbJfHJY4H41Xfqk9\nIePRkXkoTWoV7hA/Q4O0dVYVQwKBgQDGIqy6iNPBN3KQZmYDG9WKuFMsAx/gSor1\nqL5duBxUNyhkpVCLTtQvdS3aElvGCjMpWKTqmSxm8s74EQ7qLVU2YIq6u+avV47e\nN01qtrKtISFDQI/7RKKEhwoYoQEAMpT3/NpUEO4hoWdtEw50h4lmi37mFeZy2PQr\ns8sVt+xYNwKBgQCkWMbUPSIsvbXU1ORtyv8q6AEvvs6FmXlHaHZZ+TUzKhjWSLq6\nEMmJHQvjlqPmwtK/vj+OMBk30er9R2NgammuxEeNMdPCCsB5C1iG/E93CoHvyrqX\nP8JeXxvO+QoWbAH9MlaIAeML+3ClOiVOezB0zvkRkJdnfHuXW/oVKN8lnQKBgCfT\nTm7ME+wxbfiybGzRinGwrR8anayirx3DxkfmOuN+lsLsK61ksee8IPRFXmcHI9N6\nuuNg2Hj08z8PhrTxWcBtVVVFcY/rBI+MBCagBHgiQaJX9tjlqdkDn7blneLhR+o0\ny9m78XGXFMfq3av0llyjS2WKH2EUVLf4EqkR6BKvAoGAIE02RZ6Cj5fJa7WeTh/f\na1PV0pEzH4A44tOM68C6aDimDUdm37WLCR/5fmH+DT4IHljzg2rWSSzpD0rWMA2G\neScy6Qs0efX8BuasmZHzg15DuiAiZqvUFoejt9gsFQ0lxd42IZOiukCX1rn/ghXF\nacrHmWIWcgU31Uo0Z+Hyxws=\n-----END PRIVATE KEY-----\n",
        "client_email": "weather-data@weather-data-429210.iam.gserviceaccount.com",
        "client_id": "117847726458310784712",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/weather-data%40weather-data-429210.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }
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
