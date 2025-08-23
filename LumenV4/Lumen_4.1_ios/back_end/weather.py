import requests

AIR_API_KEY='343ba1c09398c0782cfedd97116f0d04'
WE_API_KEY = 'c89e4b28bbc9e5293f4426d3c4dd3ab8'
LATITUDE = 22.63277778
LONGITUDE = 88.40333333

def get_weather(api_key, latitude, longitude):
    base_url = "http://api.weatherstack.com/current"
    
    params = {
        'access_key': api_key,
        'query': f"{latitude},{longitude}",
        'units': 'm'
    }

    try:
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.text}")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_air_quality(api_key, latitude, longitude):
    base_url = "https://api.openweathermap.org/data/2.5/air_pollution"
    params = {
        'lat': latitude,
        'lon': longitude,
        'appid': api_key
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if response.status_code == 200:
            return data
        else:
            print(f"Error: {data['error']['message']}")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def weather_current():
    air_quality_data = get_weather(WE_API_KEY, LATITUDE, LONGITUDE)
    print(air_quality_data)
    return air_quality_data

def current_air_quality():
    
    air_quality_data = get_air_quality(AIR_API_KEY, LATITUDE, LONGITUDE)
    return air_quality_data

if __name__ == "__main__":
    print(weather_current())
    
    print(current_air_quality())
