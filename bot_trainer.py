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

itinerary_string = ', '.join(itinerary_destinations.keys())
itinerary_response = f'This action packed trip includes the following itinerary: {itinerary_string}'
itinerary_trainer = ['itinerary',
    itinerary_response,
    'show me the itinerary',
    itinerary_response,
    'where are you going?',
    itinerary_response,
    'what is the itinerary',
    itinerary_response,
    'which locations are you going to?',
    itinerary_response
    ]


help_advice = {
    'itinerary':'See all of the locations you can get the weather for',
    'weather':'Get the weather for your choice destination(s)'
}

help_options = []
for key,value in help_advice.items():
    help_options.append(f'{key}: {value}')
help_string = "\n".join(help_options)

help_trainer = ['help', help_string]


