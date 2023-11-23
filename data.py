def weather_advice(location):
    weather_match = {
        'Thunderstorm':f'Looks like you are in for some thunderstorms in {location}. Might be best to stay inside!',
        'Drizzle':f'You might encouter a spot of rain in {location}. Bring a rainjacket!',
        'Rain':f"It's raining in {location}, don't forget an umbrella!",
        'Snow':f"You might see some snow in {location}, make sure to rug up!",
        'Clear':f"Clear skys today in {location}, consider wearing a hat to keep to sun off.",
        'Clouds':f"A bit cloudy today in {location}, hopefully any sightseeing is not obstructed!",
        'Mist':f"Some mist today in {location}, drive carefully.",
        'Smoke':f"Smokey today in {location}, make sure to check local safety advice.",
        'Haze':f"Hazey today in {location}, make sure to check local safety advice.",
        'Dust':f"A bit of dust around in {location}, consider bringing a facemask.",
        'Ash':f"Some ash in {location}, make sure to check local safety advice",
        'Squall':f"A sharp uptake of wind in {location}, make sure to check local safety advice",
        'Tornado':f"A possible tornado in {location}, make sure to check local safety advice",
    }
    return weather_match


itinerary_destinations = {
        'Lake District National Park': {'latitude': 54.4609, 'longitude': -3.0886},
        'Corfe Castle': {'latitude': 50.6395, 'longitude': -2.0566},
        'The Cotswolds': {'latitude': 51.8330, 'longitude': -1.8433},
        'Cambridge': {'latitude': 52.2053, 'longitude': 0.1218},
        'Bristol': {'latitude': 51.4545, 'longitude': -2.5879},
        'Oxford': {'latitude': 51.7520, 'longitude': -1.257},
        'Norwich': {'latitude': 52.6309, 'longitude': 1.2974},
        'Stonehenge': {'latitude': 51.1789, 'longitude': -1.8262},
        'Watergate Bay': {'latitude': 50.4429, 'longitude': -5.0553},
        'Birmingham': {'latitude': 52.4862, 'longitude': -1.8904}
    }