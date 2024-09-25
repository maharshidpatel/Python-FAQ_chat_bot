from file_input import file_input

# Global variables for intents and responses.
global intents
global responses

# List of common greeting phrases.
greeting_utterances = [
    "hello", "hi", "hey", "good morning", "good afternoon", 
    "good evening", "greetings", "whats up", "howdy", 
    "hi there", "hey there", "yo", "hows it going", "how you doing"
]

# List of common ending phrases.
ending_utterances = [
    "goodbye", "bye", "see you", "see you later", "take care", 
    "have a great day", "catch you later", "talk to you soon", 
    "farewell", "later", "peace out", "thanks bye", "thanks", "thank you"
]

# Predefined responses for greetings and endings
def greeting_response(global_name):
    """
    Generates a greeting response personalized with the author's name.

    Args:
        global_name (str): The author's Discord global name.

    Returns:
        str: A personalized greeting response.
    """
    return f"Hello{global_name} How can I assist you with your shopping today?"

def ending_response(global_name):
    """
    Generates an ending response personalized with the author's name.

    Args:
        global_name (str): The author's Discord global name.

    Returns:
        str: A personalized ending response.
    """
    return f"Goodbye{global_name} Feel free to reach out anytime you need help. Have a great day!"


def load_FAQ_data():
    """
    Loads FAQ data from text files, normalizing the questions.

    Returns:
        tuple: A tuple containing two lists - normalized questions and answers.
    """
    # Load questions and answers from given files.
    questions = file_input("questions.txt")
    answers = file_input("answers.txt")

    normalized_questions = []

    # Normalize each question for better matching.
    for question in questions:
        normalized_question = normalize(question)
        normalized_questions.append(normalized_question)
    
    return normalized_questions, answers

def normalize(text):
    """
    Normalizes text by converting to lowercase, removing whitespace and removing non-alphanumeric characters.

    Args:
        text (str): The input text to normalize.

    Returns:
        str: The normalized text.
    """
    # Convert to lowercase.
    text = text.lower()
    # Split text into words.
    text_words_list = text.split()

    # Remove punctuation and non-alphanumeric characters.
    for word in text_words_list:
        for char in word:
            if not char.isalnum():
                current_index = text_words_list.index(word)
                word = word.replace(char,"")

                text_words_list[current_index] = word
    
    # Remove empty strings from the list.
    while "" in text_words_list:
        text_words_list.remove("")

    # Join the list back into a single string.
    text = ' '.join(text_words_list)

    return text

def understand(utterance):
    """
    Determines the intent of the given utterance based on predefined phrases.

    Args:
        utterance (str): The input message to analyze.

    Returns:
        str or int: Returns 'greeting' or 'ending' if matched, or an index if FAQ intent is found.
                    Returns -1 if no match is found.
    """
    try:
        # Check if the utterance is a greeting
        if utterance in greeting_utterances:
            return 'greeting'
        
        # Check if the utterance is an ending
        elif utterance in ending_utterances:
            return 'ending'
        
        # Check if the utterance matches any FAQ intent
        else:
            return intents.index(utterance)
        
    except ValueError:
        # Return -1 if no intent is matched.
        return -1
    
def generate(intent, global_name = "!"):
    """
    Generates a response based on the detected intent.

    Args:
        intent (str or int): The detected intent, either as a string ('greeting', 'ending') or index.
        global_name (str, optional): The author's global name. Defaults to '!'.

    Returns:
        str: The response message generated for the detected intent.
    """
    # Return responses for greetings
    if intent == 'greeting':
        return greeting_response(global_name)
    
    # Return responses for endings
    elif intent == 'ending':
        return ending_response(global_name)
    
    # Return a default response if the intent is not found
    elif intent == -1:
        return "Sorry, I don't know the answer to that!"
    
    # Return the FAQ response
    return responses[intent]

# Load intents and responses from files
intents, responses = load_FAQ_data()

def main():
    """
        Implements a chat session in the shell.
    """
    print("Hello! How can I assist you with your shopping today?\n")
    
    while True:
        # Get user input.
        utterance = input(">>> ")
        
        # Normalize the message content to be forgiving with case matching, whitespace, and punctuation.
        normalized_utterance = normalize(utterance)

        # Determine the user's intent.
        intent = understand(normalized_utterance)
        
        # Generate a response based on the intent.
        response = generate(intent)

        print(response, "\n")

        # End the interaction if the user says any ending utterances.
        if intent == 'ending':
            break

if __name__ == "__main__":
    main()