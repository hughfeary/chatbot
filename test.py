from flask import *
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer
import pandas as pd
import requests

file = open('API_keys.txt', 'r')
read = file.readlines()
file.close()
API_dict = json.loads(read[0])

app = Flask(__name__)
app.secret_key="12345"
app.secret_key = API_dict['flask_secret_key']
openweather_API_key = API_dict['openweather_API_key']
google_API_key = API_dict['google_API_key']

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


def get_coords(location):
    return itinerary_destinations[location]["latitude"], itinerary_destinations[location]["longitude"]

my_bot = ChatBot(
    name="PyBot",
    read_only=True,
    logic_adapters=["chatterbot.logic.MathematicalEvaluation",
                    "chatterbot.logic.BestMatch"]
    )

weather_dialog = pd.read_csv('forecast_weather.csv')
# make csv file a flat list to be taken by the list trainer
q_list = weather_dialog[['question', 'answer']].values.flatten().tolist()
list_trainer = ListTrainer(my_bot)
list_trainer.train(q_list)

#this needs to be multiple things long otherwise it will incorrectly train
# for item in (q_list):
#     list_trainer.train(item)

corpus_trainer = ChatterBotCorpusTrainer(my_bot)
corpus_trainer.train('chatterbot.corpus.english')



@app.route('/', methods=["POST","GET"])
def index():
    if 'conversation' not in session:
        session['conversation'] = []

    if request.method == 'POST':
        user_input = request.form.get('user_input')
        bot_response = my_bot.get_response(user_input).text

        if len(session['conversation']) >= 1 and session['conversation'][-1][-5:-1] == "comm":
            session['location'] = {}
            location_input = user_input.split(",")
            trimmed_locations = [item.strip().title() for item in location_input]
            print(trimmed_locations)
            for loc in trimmed_locations:
                if loc not in itinerary_destinations:
                    print('entering error if block')
                    bot_response = my_bot.get_response("location invalid").text
                    break
                else:
                #gives feedback to user if a location is incorrect
                    for i, item in enumerate(trimmed_locations):
                        session['location'][str(index)] = [item]
                    bot_response = my_bot.get_response("user entered locations").text
                    # done to ensure a response no matter the input

        # if bot_response == 'No problem I will retrieve that data now':
        #     session['location'] = 'Bristol'
        #     session['conversation'].extend([user_input, bot_response])
        #     session['conversation'] = session['conversation']
        #     return redirect(url_for('display_weather'))

        session['conversation'].extend([user_input, bot_response])
        session['conversation'] = session['conversation']
        return render_template('index.html')
    return render_template('index.html')

@app.route('/get_weather',methods=['get','post'])
def display_weather():
    lat, long = get_coords(session['location'])
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={long}&appid={openweather_API_key}"
    response = requests.get(weather_url)
    print(response.json())
    return render_template('weather_results.html', result=response.json())


@app.route('/reset',methods=['post']) #route that handles the reset request
def reset_chat():
    session['conversation'] = []
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
