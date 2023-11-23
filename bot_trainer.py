from data import itinerary_destinations

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
    'itinerary':'See all of the locations you can get the weather for.',
    'weather':'Get the weather for your choice destination(s).'
}

help_options = []
for key,value in help_advice.items():
    help_options.append(f'{key} - {value}')
help_string = "\n\n".join(help_options)

help_trainer = ['help', help_string]


