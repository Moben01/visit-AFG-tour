
import requests
from django.shortcuts import render
import os
from dotenv import load_dotenv
load_dotenv()
import requests
from django.shortcuts import render

import requests
from django.shortcuts import render

def Art_and_Culture(request):
    api_key = "2c8f25d1c7a10cb132adfa1884766a2e"

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
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"
            response = requests.get(url, timeout=5)  # timeout added to avoid hanging
            city_name = city.split(",")[0]

            if response.status_code == 200:
                data = response.json()
                weather_data[city_name] = {
                    "temp": data["main"]["temp"],
                    "description": data["weather"][0]["description"].title(),
                    "icon": data["weather"][0]["icon"],
                }
            else:
                weather_data[city_name] = {
                    "temp": "N/A",
                    "description": "Data not available",
                    "icon": None,
                }
        except Exception as e:
            # Handle no internet or timeout
            city_name = city.split(",")[0]
            weather_data[city_name] = {
                "temp": "N/A",
                "description": "Data not available",
                "icon": None,
            }

    return render(request, 'things_to_do/Art_and_Culture.html', {'weather_data': weather_data})









def Experiences(request):
    return render(request, 'things_to_do/Experiences.html')


def food_and_drink(request):
    return render(request, 'things_to_do/food_and_drink.html')

def New_and_Trending(request):
    return render(request, 'things_to_do/New_and_Trending.html')
