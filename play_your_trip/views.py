from django.shortcuts import render
from dotenv import load_dotenv
load_dotenv()
import requests

# Create your views here.

def visa_guide(request):
    return render(request, 'plan_your_trip/visa_guide.html')

def essentials(request):
    return render(request, 'plan_your_trip/essentials.html')

def flight(request):
    return render(request, 'plan_your_trip/flight.html')

def Accommodation(request):
    return render(request, 'plan_your_trip/Accommodation.html')

def Getting_to_around_afg(request):
    return render(request, 'plan_your_trip/Getting_to_around_afg.html')

def safety(request):
    return render(request, 'plan_your_trip/safety.html')

def weather(request):
    api_key = "2c8f25d1c7a10cb132adfa1884766a2e"

    # City names with country code Afghanistan (AF)
    cities = [
        "Kabul,AF",
        "Herat,AF",
        "Kandahar,AF",
        "Jalalabad,AF",
        "Kunduz,AF",
        "Ghazni,AF",
        "Balkh,AF",
        "Puli Khumri,AF",
        "Taloqan,AF",
        "Logar,AF",
        "Nangarhar,AF",
        "Badakhshan,AF",
        "Farah,AF",
        "Baghlan,AF",
    ]

    weather_data = {}

    for city in cities:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"
        print(f"Request URL: {url}")
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            city_name = city.split(",")[0]  # Remove country code for display
            weather_data[city_name] = {
                "temp": data["main"]["temp"],
                "description": data["weather"][0]["description"].title(),
                "icon": data["weather"][0]["icon"],
            }
        else:
            city_name = city.split(",")[0]
            weather_data[city_name] = {
                "temp": "N/A",
                "description": "Data not available",
                "icon": None,
            }
    return render(request, 'plan_your_trip/weather.html', {'weather_data': weather_data})

def currency(request):
    return render(request, 'plan_your_trip/currecy.html')