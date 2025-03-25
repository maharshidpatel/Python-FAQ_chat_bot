"""
Author: Maharshi Patel, 000738366
Date: 24-10-2024
Description: This file loads regex patterns and answers from external sources to match user inputs and generate responses. 
            It uses Named Entity Recognition (NER), handles spelling errors, and applies fallback strategies like 
            noun chunk extraction to ensure flexible and conversational responses.
"""
import regex as re
import spacy
from file_input import file_input

# Load spaCy large model
nlp = spacy.load('en_core_web_lg')

# Global variables for intents and responses.
global intents
global responses

# Regex patterns for greeting and ending utterances to identify user intent.
greeting_utterances = (
    r"\b(hello|hi|hey|howdy|whats up|good (morning|afternoon|evening))\b|"
    r"\b(hi there|hey there|yo|how you doing|hows it going)\b|"
    r"\b(help|assist)\b"
)

ending_utterances = (
    r"\b(goodbye|bye|see you|see you later|take care|farewell|later|peace out)\b|"
    r"\b(catch you later|talk to you soon|have a great day|thanks|thank you)\b"
)

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
    Loads FAQ data from text files.

    Returns:
        tuple: A tuple containing two lists - regexs and answers.
    """
    # Load questions and answers from given files.
    regexs = file_input("regexs.txt")
    answers = file_input("answers.txt")

    return regexs, answers

def normalize(text):
    """
    Cleans and formats the input text by trimming spaces, replacing non-alphanumeric characters with spaces, collapsing multiple spaces, 
    and converting to lowercase for case-insensitive matching.

    Args:
        text (str): The raw input text.

    Returns:
        str: The normalized text, ready for further processing.
    """
    # Remove leading and trailing whitespace
    text = text.strip()  
    
    # Remove unwanted characters, leaving spaces and specified punctuation
    text = re.sub(r'[^\w\s]', ' ', text)  
    
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Convert to lowercase
    text = text.lower()
    
    return text

def named_entity_with_external_links(utterance):
    """
    This function extracts named entities from the user's input and provides relevant responses with external links.
    Entities include persons, organizations, locations, and facilities. For example, for a 'PERSON' entity, it 
    returns a Wikipedia link, for 'ORG', a Google search link, and for 'LOC' or 'GPE', a Google Maps link. 
    If no entity is detected, it returns None to allow other fallback strategies to be used.

    Args:
        utterance (str): The user's input.

    Returns:
        str or None: A response with an external link or None if no entity is detected.
    """
    # Process the input using spaCy to analyze it for named entities.
    doc = nlp(utterance)

    # Loop through each detected named entity in the input.
    for ent in doc.ents:
        # If the entity is a person, generate a Wikipedia link response.
        if ent.label_ == "PERSON":
            response = f"I don't have information on {ent.text}, but you can try Wikipedia: https://en.wikipedia.org/wiki/{ent.text.replace(' ', '_')}."
            return response
        
        # If the entity is an organization, generate a Google search link response.
        elif ent.label_ == "ORG":
            response = f"You can search more about {ent.text} on Google: https://www.google.com/search?q={ent.text.replace(' ', '+')}."
            return response
        
        # For locations or facilities, provide a Google Maps search link.
        elif ent.label_ in {"GPE", "LOC", "FAC"}:
            response = f"Try searching for {ent.text} on Google Maps: https://www.google.com/maps/search/{ent.text.replace(' ', '%20')}."
            return response
    
    # If no entities are found, return None so other fallback strategies can be triggered.
    return None

def noun_chunks(utterance):
    """
    This fallback function uses noun chunks to generate a response when the bot can't understand the user's input.
    Noun chunks are key phrases containing nouns, excluding unhelpful parts like pronouns and determiners.
    If valid chunks are found, the first chunk is used to generate a response. If no valid chunks are found,
    it returns None to allow other fallback mechanisms.

    Args:
        utterance (str): The user's input.

    Returns:
        str or None: A response based on noun chunks, or None if no valid chunks are found.
    """
    # Process the input using spaCy to extract noun chunks.
    doc = nlp(utterance)
    
    # Filter out noun chunks that contain pronouns or determiners, as they aren't meaningful.
    meaningful_chunks = [
        chunk.text for chunk in doc.noun_chunks 
        if not any(token.pos_ in {"PRON", "DET"} for token in chunk)
    ]
    
    # If valid noun chunks are found, return a response using the first chunk.
    if meaningful_chunks:
        return f"I'm not sure about details on {meaningful_chunks[0]}, but I can help with your shopping-related questions."
    
    # If no noun chunks are found, return None to let other fallback mechanisms handle it.
    return None

def classify_speech_act(utterance):
    """
    This function classifies the user's input as a question, command, or statement by analyzing sentence structure.
    It considers punctuation (like '?' for questions or '!' for commands) and the presence of interrogative words (e.g., 'what', 'how').
    Commands are typically identified by imperative verbs. If no clear pattern is found, it defaults to a statement.

    Args:
        utterance (str): The user's input.

    Returns:
        str: A classification of the speech act ('question', 'command', or 'statement').
    """
    # Process the input to analyze its structure.
    doc = nlp(utterance)
    
    # Clean the input by removing extra spaces.
    utterance = utterance.strip()
    
    # Check the last character to see if it's a question or command indicator.
    last_char = utterance[-1] if utterance else ''
    
    # List of common question words used to detect questions.
    question_words = {
        "who", "what", "when", "where", "why", "how", "is", "are", "am", "do", "does",
        "did", "can", "could", "will", "would", "shall", "should", "whom", "whose", "which"
    }
    
    # If the last character is a '?', classify it as a question.
    if last_char == '?':
        return "question"
    
    # If the last character is '!', check if it indicates a question or command.
    elif last_char == '!':
        # If the first word is a question word, it's still a question.
        if doc and doc[0].text.lower() in question_words:
            return "question"
        # If the sentence root is a verb, it's likely a command.
        elif any(token.pos_ == "VERB" and token.dep_ == "ROOT" for token in doc):
            return "command"
        else:
            return "statement"

    # If the first word is a question word, classify it as a question.
    elif doc and doc[0].text.lower() in question_words:
        return "question"
    
    # If the first word is a verb, it's likely a command.
    elif doc and doc[0].pos_ == "VERB":
        return "command"
    
    # Default classification is 'statement' if none of the above conditions are met.
    else:
        return "statement"

def speech_act(utterance):
    """
    A fallback strategy based on speech act classification. It generates different responses depending on whether
    the input is classified as a question, command, or statement. For statements, it tries to use noun chunks
    to make a more specific response. If no specific answer can be formed, it provides a generic response.

    Args:
        utterance (str): The user's input.

    Returns:
        str: A fallback response based on the classification of the input.
    """
    # Classify the input as a question, command, or statement.
    speech_act_type = classify_speech_act(utterance)
    
    # If the input is a question, provide a fallback response for unanswered questions.
    if speech_act_type == "question":
        return "I'm sorry, I don't have the answer to that, but I'm here to assist with shopping-related questions."
    
    # If the input is a command, provide a command-specific fallback response.
    elif speech_act_type == "command":
        return "I'm not sure how to help with that, but feel free to ask any shopping-related questions!"
    
    # If it's a statement, try using noun chunks to provide a more specific response.
    else:
        noun_chunk_response = noun_chunks(utterance)
        if noun_chunk_response:
            return noun_chunk_response
        else:
            return "That's interesting! If you have any questions about shopping, I'm here to help."

def understand(utterance):
    """
    This function attempts to understand the user's input by comparing it against predefined intents.
    It first checks for greeting and ending patterns. If none match, it tokenizes the input and 
    compares each token with the predefined patterns using regex. Tokens that are common shopping-related 
    words (like 'order' or 'product') influence the score more. The intent with the highest score is returned, 
    along with the score, to guide response generation.

    How scoring and regex matching work:
    If no match is found for greetings or endings, the input is tokenized into words (ignoring short words smaller than 4 letters).
    The function assigns 2 points if the entire input matches an intent pattern using regex.
    Each individual word is then scored:
        Exact word matches get 1 point.
        Common shopping-related words (like 'order', 'product') get an additional 0.5 points.
        Typo-tolerant matches are scored lower:
            For words with 6 or fewer letters that have typos, 0.25 points are assigned.
            For words longer than 6 letters with typos, 0.5 points are assigned.
    The intent with the highest total score is selected, ensuring flexibility with different phrasings or minor typos in the input.

    Args:
        utterance (str): The user's input.

    Returns:
        tuple: The best matching intent and its score.
    """
    max_score = 0
    best_pattern_index = -1

    # List of common words that influence the scoring, related to shopping.
    common_words = {
        "order", "orders", "purchase", "purchases", "delivery", 
        "item", "items", "product", "products", "when"
    }

    try:
        # Check if the input matches a greeting pattern.
        if re.search(greeting_utterances, utterance, flags=re.IGNORECASE):
            return 'greeting', 0
        
        # Check if the input matches an ending pattern.
        elif re.search(ending_utterances, utterance, flags=re.IGNORECASE):
            return 'ending', 0
        
        # Tokenize the input and filter out short tokens.
        tokens = [token for token in re.findall(r'\b\w+\b', utterance) if len(token) > 3]
        
        # Loop through each predefined intent pattern and calculate a score.
        for index, pattern in enumerate(intents):
            score = 0

            # If the entire utterance matches the pattern, give it a higher score.
            if re.search(pattern, utterance, flags=re.IGNORECASE):
                score += 2

            # Compare each token with the pattern to further adjust the score.
            for token in tokens:
                exact_match = re.search(fr'\b{token}\b', pattern, flags=re.IGNORECASE)
                typo_allowed = 1 if len(token) <= 6 else 2
                typo_match = re.search(fr'\b({token}){{e<={typo_allowed}}}\b', pattern, flags=re.IGNORECASE)

                if exact_match:
                    if token in common_words:
                        score += 0.5
                    else:
                        score += 1
                elif typo_match:
                    if len(token) <= 6:
                        score += 0.25
                    else:
                        score += 0.5

            # Update the best matching pattern if this score is the highest.
            if score > max_score:
                max_score = score
                best_pattern_index = index

        # Return the best pattern index and its corresponding score.
        return best_pattern_index, max_score

    except Exception as e:
        # Handle any errors that occur during understanding.
        print(f"Error in understanding the utterance: {e}")
        return -1, 0

def generate(intent, max_score, utterance, global_name="!"):
    """
    This function generates a response based on the detected intent and confidence score.
    If the intent is clear (greeting or ending), it returns predefined responses. If the score 
    for a matched intent is high, it returns the corresponding FAQ response. If the intent is unclear, 
    it uses fallback strategies like named entity recognition, speech act classification, and noun chunks 
    to generate a suitable response.

    Args:
        intent (str): The identified intent.
        max_score (float): The confidence score for the intent.
        utterance (str): The user's input.
        global_name (str): A placeholder for the user's name (default to "!").

    Returns:
        str: The generated response for the chatbot to use.
    """
    # Return a greeting response if the intent matches.
    if intent == 'greeting':
        return greeting_response(global_name)
    
    # Return an ending response if the intent matches.
    elif intent == 'ending':
        return ending_response(global_name)
    
    # If the intent is valid and the score is sufficient, return the corresponding FAQ response.
    if intent != -1 and max_score > 1:
        return responses[intent]
    
    # Fallback 1: Named Entity Recognition with external links.
    named_entity_recognition_response = named_entity_with_external_links(utterance)
    if named_entity_recognition_response:
        return named_entity_recognition_response
    
    # Fallback 2: Speech Act Classification (with noun chunks for statements).
    speech_act_response = speech_act(utterance)
    if speech_act_response:
        return speech_act_response
    
    # Default fallback response if no other responses are found.
    return "I am sorry, I don't have the information you are looking for, but I am here to assist with shopping-related questions."

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

        # Determine the user's intent and score for regex match.
        intent, max_score = understand(normalized_utterance)
        
        # Generate a response based on the intent.
        response = generate(intent, max_score, utterance)

        if response is None:  # In case the response is not found
            response = "Sorry, I don't know the answer to that!"

        print(response, "\n")

        # End the interaction if the user says any ending utterances.
        if intent == 'ending':
            break

if __name__ == "__main__":
    main()