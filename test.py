from flask import *
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer
import pandas as pd
import requests
from datetime import datetime
#importing itinerary desitations and lists stored separately to avoid clutter in main code
from bot_trainer import itinerary_destinations, itinerary_trainer, help_trainer


file = open('API_keys.txt', 'r')
read = file.readlines()
file.close()
API_dict = json.loads(read[0])

app = Flask(__name__)
app.secret_key="12345"
app.secret_key = API_dict['flask_secret_key']
openweather_API_key = API_dict['openweather_API_key']
google_API_key = API_dict['google_API_key']


def get_coords(location):
    return itinerary_destinations[location]["latitude"], itinerary_destinations[location]["longitude"]


def format_description(string):
    return string[0].upper() + string[1::]


def convert_dt(unix, loc="t"):
    if loc == "header":
        return datetime.utcfromtimestamp(unix).strftime('%a %e %b, %I:%M%p')
    else:
        return datetime.utcfromtimestamp(unix).strftime('%a %e %b')

my_bot = ChatBot(
    name="PyBot",
    read_only=True,
    logic_adapters=["chatterbot.logic.MathematicalEvaluation",
                    "chatterbot.logic.BestMatch"]
    )

#training block
weather_dialog = pd.read_csv('forecast_weather.csv')
# make csv file a flat list to be taken by the list trainer
q_list = weather_dialog[['question', 'answer']].values.flatten().tolist()
#help logic?


list_trainer = ListTrainer(my_bot)
for item in (q_list, itinerary_trainer, help_trainer):
    list_trainer.train(item)

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
            session['location'] = []
            location_input = user_input.split(",")
            trimmed_locations = [item.strip().title() for item in location_input]
            for loc in trimmed_locations:
                if loc not in itinerary_destinations:
                    print('entering error if block')
                    bot_response = my_bot.get_response("location invalid").text
                    break
                else:
                #gives feedback to user if a location is incorrect
                    for final_loc in trimmed_locations:
                        session['location'].extend([final_loc])
                    bot_response = my_bot.get_response("user entered locations").text
                    # done to ensure a response no matter the input
                    session['conversation'].extend([user_input, bot_response])
                    session['conversation'] = session['conversation']
                    #could this be a function to reduce code?
                    return redirect(url_for('display_weather'))

        session['conversation'].extend([user_input, bot_response])
        session['conversation'] = session['conversation']
        return render_template('index.html')

    return render_template('index.html')

@app.route('/get_weather',methods=['get','post'])
def display_weather():
    data_dict = {}
    part = "minutely,hourly"

    for location in session['location']:
        lat, long = get_coords(location)
        weather_url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={long}&exclude={part}&appid={openweather_API_key}"
        response = requests.get(weather_url)
        data_dict[location] = response.json()
        #logic for one place and match to advise.
    return render_template('weather_results.html', data_dict=data_dict, format_description=format_description, convert_dt=convert_dt)


@app.route('/reset',methods=['post']) #route that handles the reset request
def reset_chat():
    session['conversation'] = []
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
