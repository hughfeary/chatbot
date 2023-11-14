from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer


my_bot = ChatBot(
    name="PyBot",
    read_only=True,
    logic_adapters=["chatterbot.logic.MathematicalEvaluation",
                    "chatterbot.logic.BestMatch"]
    )

weather_talk = [
    "Can you please get me the current weather?",
    "Sure, which location would you like?",
    "Can I please see the weather forecast?",
    "Sure, would you like the current weather or a 7 day forecast?"
]

small_talk = [
    "Hello",
    "Hi there!",
    "How are you doing?",
    "I'm doing great.",
    "That is good to hear",
    "Thank you.",
    "You're welcome."
]

math_talk_1 = [
    'pythagorean theorem',
    'a squared plus b squared equals c squared.'
]

math_talk_2 = [
    'law of cosines',
    'c**2 = a**2 + b**2 - 2 * a * b * cos(gamma)'
]

list_trainer = ListTrainer(my_bot)

for item in (small_talk, math_talk_1, math_talk_2, weather_talk):
    list_trainer.train(item)

corpus_trainer = ChatterBotCorpusTrainer(my_bot)
corpus_trainer.train('chatterbot.corpus.english')

while True:
    try:
        user_input = input("You:" )
        bot_response = my_bot.get_response(user_input)
        print(f'{my_bot.name}: {bot_response}')
    except (KeyboardInterrupt, EOFError, SystemExit):
        break
