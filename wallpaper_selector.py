#!/usr/bin/env python3
import sys
from datetime import datetime, timezone, timedelta
import urllib.request
import json
import time
import os

def get_timezone_offset(lat, lng, retries=3, delay=2):
    url = f"https://www.timeapi.io/api/TimeZone/coordinate?latitude={lat}&longitude={lng}"
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
            if "standardUtcOffset" in data and "seconds" in data["standardUtcOffset"]:
                return timedelta(seconds=data["standardUtcOffset"]["seconds"])
        except (urllib.error.URLError, json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Attempt {attempt+1} failed to fetch timezone data ({e}). Retrying...", file=sys.stderr)
            time.sleep(delay)
    print("Warning: All retries failed. Defaulting to UTC+0", file=sys.stderr)
    return timedelta(hours=0)

def get_sunrise_sunset(lat, lng):
    url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lng}&formatted=0"
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
    sunrise = datetime.fromisoformat(data["results"]["sunrise"])
    sunset = datetime.fromisoformat(data["results"]["sunset"])
    dayLength = timedelta(seconds = int(data["results"]["day_length"]))
    return sunrise, sunset, dayLength
    
def get_background(lat, lng):
    timezone_offset = get_timezone_offset(lat, lng)
    current_time = datetime.now(timezone.utc) + timezone_offset
    sunrise, sunset, dayLength = get_sunrise_sunset(lat, lng)
    sunrise = sunrise + timezone_offset
    sunset = sunset + timezone_offset
    hour = timedelta(minutes=60)
    morningEnd = sunrise + (dayLength * 0.25)
    noonEnd = sunrise + (dayLength * 0.75)
    eveningEnd = sunset - hour
    if sunrise - hour <= current_time <= sunrise + hour:
        return "sunrise.png"
    if sunrise < current_time <= morningEnd:
        return "morning.png"
    if morningEnd < current_time <= noonEnd:
        return "noon.png"
    if noonEnd < current_time <= eveningEnd:
        return "evening.png"
    if eveningEnd <= current_time <= sunset + hour:
        return "sunset.png"
    return "night.png"
    
def set_wallpaper(image_filename):
    os.system(f"gsettings set org.gnome.desktop.background picture-uri 'file://{os.getcwd()}/images/{image_filename}'")
    
if __name__ == "__main__":
    if len(sys.argv) != 3:
	    print("Please provide the latitude and longitude", file=sys.stderr)
	    sys.exit(1)
    lat = sys.argv[1]
    lng = sys.argv[2]
    background = get_background(lat, lng)
    set_wallpaper(background)
    print(background)
