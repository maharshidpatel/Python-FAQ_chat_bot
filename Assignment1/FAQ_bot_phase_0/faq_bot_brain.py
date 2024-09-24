from file_input import file_input

global intents
global responses

def load_FAQ_data():
    questions = file_input("questions.txt")
    answers = file_input("answers.txt")

    return questions, answers

def understand(utterance):
    
    try:
        return intents.index(utterance)
    except ValueError:
        return -1
    
def generate(intent):
    
    if intent == -1:
        return "Sorry, I don't know the answer to that!"

    return responses[intent]

intents, responses = load_FAQ_data()