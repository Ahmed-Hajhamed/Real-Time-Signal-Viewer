import requests

# Using your provided API key
api_key = "9a4c014a085132d244fe6c7157a576d2"
city_name = "Cairo"
url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}"

# Fetch the weather data
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    print("Weather Data for Cairo:", data)
else:
    print("Error fetching data:", response.status_code)
