from flask import *
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import pandas as pd
import requests
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import os
from bot_trainer import itinerary_trainer, help_trainer
from data import itinerary_destinations, weather_advice

app = Flask(__name__) # initialisation of flask app

#read text file with API keys assign to variables
file = open('API_keys.txt', 'r')
read = file.readlines()
file.close()
API_dict = json.loads(read[0])

app.secret_key = API_dict['flask_secret_key']
openweather_API_key = API_dict['openweather_API_key']

# create database and confgiure application to use it
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trainer_conversations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) #linking flask app and SQLAlchemy

# class to define structure of the database table


#class to encapsulate location information, weather data and handle some data processing

# read all of the csv files and add data to conversation table
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

class Location:
    def __init__(self, location): # initialise class with name and coordinates
        self.location = location
        self.lattitude, self.longitude = get_coords(self.location)
        self.weather_data = None
        self.current_dt = None
        self.current_weather_description = None
        self.current_temp = None

    def retrieve_weather(self): #send a get request to Openweather API to get weather data
        lat = self.lattitude
        long = self.longitude
        weather_url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={long}&exclude=minutely,hourly&appid={openweather_API_key}"
        response = requests.get(weather_url)
        status = response.status_code
        if status == 200: # assign key data to object attributes
            self.weather_data = response.json()
            self.current_weather_description = self.weather_data['current']['weather'][0]['main'] 
            self.current_dt = convert_dt(self.weather_data['current']['dt'],loc="header")
            self.current_temp = round(self.weather_data['current']['temp']-273.15,1)
        return status

    def get_max_temp(self,day): # retrieve max temp depending on requested day
        if self.weather_data:
            return round(self.weather_data['daily'][day]['temp']['max']-273.15,1)
        
    def get_min_temp(self,day):# retrieve min temp depending on requested day
        if self.weather_data:
            return round(self.weather_data['daily'][day]['temp']['min']-273.15,1)
        
    def weather_description(self,day):# retrieve weather description depending on requested day
        if self.weather_data:
            return format_description(self.weather_data['daily'][day]['weather'][0]['description'])
    
    def get_dt(self,day):# retrieve date/time depending on requested day
        if self.weather_data:
            return convert_dt(self.weather_data['daily'][day]['dt'])


class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String, nullable=False) 
    answer = db.Column(db.String, nullable=False)

# initialisation of chatbot
my_bot = ChatBot(
    name="PyBot",
    read_only=True,
    #configure datbase with the chatbot
    storage_adapter = 'chatterbot.storage.SQLStorageAdapter', database_uri='sqlite:///trainer_conversations.db',
    logic_adapters=["chatterbot.logic.MathematicalEvaluation",
                    "chatterbot.logic.BestMatch"]
    )

# train the chatbot with itinerary and help formating
list_trainer = ListTrainer(my_bot)
for item in (itinerary_trainer, help_trainer):
    list_trainer.train(item)

# train the chatbot from contents of the database
for conversation in Conversation.query.all():
    list_trainer.train([
        conversation.question,
        conversation.answer
    ])

@app.route('/', methods=["POST","GET"])
def chat_window():
    if 'conversation' not in session:
        #initialise a list
        session['conversation'] = []

    if request.method == 'POST':
        # user input is retrieved from input box and then passed into the bot for a response
        user_input = request.form.get('user_input')
        bot_response = my_bot.get_response(user_input).text

        # condition on when to expect weather input based on trained bot response
        if len(session['conversation']) >= 1 and session['conversation'][-1][-5:-1] == "comm":
            if user_input == "itinerary": 
                # break out of the 'weather' loop and show the itinerary
                bot_response = my_bot.get_response("itinerary").text
                session['conversation'].extend([user_input, bot_response])
                session['conversation'] = session['conversation']
                return render_template('chat_window.html')

            session['location'] = []
            # clean the user input
            location_input = user_input.split(",")
            trimmed_locations = [item.strip().title() for item in location_input]
            
            #check if locations are in the itinerary
            for loc in trimmed_locations:
                if loc not in itinerary_destinations:
                    # display feedback to the user regarding invalid location
                    bot_response = my_bot.get_response("location invalid").text
                    break
                elif trimmed_locations[-1]==loc:
                    # if valid, store locations as session variables
                    for final_loc in trimmed_locations:
                        session['location'].extend([final_loc])
                    session['conversation'].extend([user_input])

                    #redirect to "/get_weather" endpoint to get weather
                    return redirect(url_for('display_weather'))

        session['conversation'].extend([user_input, bot_response])
        session['conversation'] = session['conversation']
        return render_template('chat_window.html')

    return render_template('chat_window.html')


@app.route('/get_weather',methods=['get','post'])
def display_weather():
    location_obj_list = []

    # if the user submits a new message, the chat continues
    #the user is redirected to the "chat_window" endpoint to maintain functionality
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        bot_response = my_bot.get_response(user_input).text
        session['conversation'].extend([user_input, bot_response])
        session['conversation'] = session['conversation']
        return redirect(url_for('chat_window'))
    
    try:
        #loop through each location 
        for loc in session['location']:
            location_obj = Location(loc) # instantiate new object for each location
            status = location_obj.retrieve_weather() # call method to send GET request to Openweather
            if status != 200: #error handling
                raise Exception(f"Failed to retrieve weather data for {loc}. Status code: {status} ")
            location_obj_list.append(location_obj) # list of location objects which are later utilised

        weather_advice_list = []
        for obj in location_obj_list:
            # get weather advice from dictionary for each requested location
            weather_advice_list.append(weather_advice(obj.location)[obj.current_weather_description])
        bot_response = my_bot.get_response("user entered locations").text + f' {" ".join(weather_advice_list)}'
        session['conversation'].extend([bot_response])
        session['conversation'] = session['conversation']

        #pass the location objects to the HTML template to display results
        return render_template('weather_results.html', objs=location_obj_list)
    
    except Exception as e:
        return f"There has been an error. {str(e)}"


@app.route('/reset',methods=['post']) #route that handles the reset request
def reset_chat():
    session['conversation'] = []
    return redirect(url_for('chat_window'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        import_data()
    app.run()