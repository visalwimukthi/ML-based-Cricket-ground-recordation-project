import requests

API_KEY = "0943842962317c345fa1bc34ac6486ea"

def get_weather(city, date):
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        if "list" not in data: return "Unknown"
        for item in data["list"]:
            if date in item["dt_txt"]:
                return item["weather"][0]["main"]
        return "Clear"
    except:
        return "Unknown"

def weather_icon(label):
    label = label.lower()
    if "rain" in label: return "🌧️"
    if "cloud" in label: return "☁️"
    if "clear" in label: return "☀️"
    return "🌤️"