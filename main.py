from flask import *
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer
import pandas as pd
import requests
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import os
#importing itinerary desitations and lists stored separately to avoid clutter in main code
from bot_trainer import itinerary_trainer, help_trainer
from data import itinerary_destinations, weather_advice

file = open('API_keys.txt', 'r')
read = file.readlines()
file.close()
API_dict = json.loads(read[0])

app = Flask(__name__)
app.secret_key="12345"
app.secret_key = API_dict['flask_secret_key']
openweather_API_key = API_dict['openweather_API_key']
google_API_key = API_dict['google_API_key']

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trainer_conversations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String, nullable=False) 
    answer = db.Column(db.String, nullable=False)

def import_data():
    data_folder = 'data'
    for filename in os.listdir(data_folder):
        if filename.endswith('.csv'):
            file_path = os.path.join(data_folder, filename)
            df = pd.read_csv(file_path)
            for _, row in df.iterrows():
                conversation = Conversation(question=row['question'], answer=row['answer'])
                db.session.add(conversation)
    db.session.commit()

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
    storage_adapter = 'chatterbot.storage.SQLStorageAdapter', database_uri='sqlite:///trainer_conversations.db',
    logic_adapters=["chatterbot.logic.MathematicalEvaluation",
                    "chatterbot.logic.BestMatch"]
    )

list_trainer = ListTrainer(my_bot)
for item in (itinerary_trainer, help_trainer):
    list_trainer.train(item)

for conversation in Conversation.query.all():
    list_trainer.train([
        conversation.question,
        conversation.answer
    ])

@app.route('/', methods=["POST","GET"])
def chat_window():
    if 'conversation' not in session:
        session['conversation'] = []

    if request.method == 'POST':
        user_input = request.form.get('user_input')
        bot_response = my_bot.get_response(user_input).text

        if len(session['conversation']) >= 1 and session['conversation'][-1][-5:-1] == "comm":
            if user_input == "itinerary": #show the itinerary to the user and break out of location loop
                bot_response = my_bot.get_response("itinerary").text
                session['conversation'].extend([user_input, bot_response])
                session['conversation'] = session['conversation']
                return render_template('chat_window.html')

            session['location'] = []
            location_input = user_input.split(",")
            trimmed_locations = [item.strip().title() for item in location_input]
            print(trimmed_locations)
            for loc in trimmed_locations:
                if loc not in itinerary_destinations:
                    print('entering error if block')
                    bot_response = my_bot.get_response("location invalid").text
                    break
                elif trimmed_locations[-1]==loc:
                    for final_loc in trimmed_locations:
                        session['location'].extend([final_loc])
                    
                    session['conversation'].extend([user_input])
                    
                    return redirect(url_for('display_weather'))

        session['conversation'].extend([user_input, bot_response])
        session['conversation'] = session['conversation']
        return render_template('chat_window.html')

    return render_template('chat_window.html')

@app.route('/get_weather',methods=['get','post'])
def display_weather():
    data_dict = {}
    part = "minutely,hourly"

    if request.method == 'POST':
        user_input = request.form.get('user_input')
        bot_response = my_bot.get_response(user_input).text
        #if bot response is sure..enter weather ect
        #dont save that, but instead feed a prompt in that tells user to refresh chat to enter new instance
        session['conversation'].extend([user_input, bot_response])
        session['conversation'] = session['conversation']
        return render_template('weather_results.html')

    for location in session['location']:
        lat, long = get_coords(location)
        weather_url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={long}&exclude={part}&appid={openweather_API_key}"
        response = requests.get(weather_url)
        data_dict[location] = response.json()
    
    condition = data_dict[session['location'][0]]['current']['weather'][0]['main']
    dict = weather_advice(session['location'][0])
    bot_response = my_bot.get_response("user entered locations").text + f' {dict[condition]}'
    session['conversation'].extend([bot_response])
    session['conversation'] = session['conversation']

        #logic for one place and match to advise.
    return render_template('weather_results.html', data_dict=data_dict, format_description=format_description, convert_dt=convert_dt)


@app.route('/reset',methods=['post']) #route that handles the reset request
def reset_chat():
    session['conversation'] = []
    return redirect(url_for('chat_window'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        import_data()
    app.run()