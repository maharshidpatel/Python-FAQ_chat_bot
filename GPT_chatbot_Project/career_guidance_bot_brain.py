"""
Author: Maharshi Patel, 000738366
Date: 17-11-2024
Description: The Career Guidance Bot uses two OpenAI APIs to assist users in exploring career paths and hobbies based on their interests and goals. The first API classifies user inputs into categories like career advice, hobbies, or general inquiries, using custom prompts for accurate classification. The second API generates personalized responses by leveraging context and classification details, ensuring the advice is tailored to the user's needs. By tracking user interactions, the bot provides relevant and insightful guidance, adapting its responses dynamically to help users navigate career choices and hobbies effectively.
"""

from openai import OpenAI

# OpenAI API key
openai_client = OpenAI(api_key = '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')

# Initialize context summary as a dictionary to better track user interests
context_summary = {
    "user_interests": [],
    "user_hobbies": [],
    "user_career_goals": [],
    "concerns": [],
    "user_inputs": [],
    "classification_details": []
}

# Define the system message to guide the conversation
base_system_message = """
You are a career advisor bot. Your goal is to help users explore career paths based on their interests, hobbies, or desired skills. 
You should also help guide users who want to explore new hobbies or find the right career sector. 
Always provide advice in a positive, constructive, and personalized manner, based on the user's input. 
If the user asks irrelevant questions, politely redirect them towards career or hobby-related topics.
Please answer concisely, keep the response brief, clear, and to the point.
"""

def classify_user_input(user_message):
    """
    Classify the user's input into one of several predefined categories using OpenAI's API.

    Parameters:
        user_message (str): The message from the user to be classified.

    Returns:
        tuple: A tuple containing the category for the user input and the reason for classification.
    """

    # Formulate a prompt to classify user input into specific categories
    prompt = f"""
    Classify the following user input into one of the categories below. Provide the output in the following format:
    Category: <category name>
    Reason: <explanation of why this category was selected>

    Categories:
    - Career Path: Career-related questions, job advice, or skills.
    - Hobby or Sport Interest: User asks about a hobby, sport, or activity.
    - Concern or Follow-Up: When the user provides a concern, feedback, or follow-up about a previous topic.
    - General Inquiry: User asks general questions, guidance, or any non-specific request.
    - Unclear: When the intent is unclear or ambiguous.

    User Input: "{user_message}"

    Please output the classification in the format:
    Category: <category name>
    Reason: <explanation of why this category was selected>
    """
    
    try:
        # Call to OpenAI API for classification
        response = openai_client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            temperature=0.2,
            max_tokens=150
        )
        # Get the raw API response text
        classification = response.choices[0].text.strip()
        
        # Parse the response to get category and details
        category, details = parse_classification(classification)
    except Exception as e:
        category, details = "Unclear", f"Error in classification: {str(e)}"
    
    return category, details


def parse_classification(classification):
    """
    Parse the raw classification text from OpenAI's API to extract the category and the reason.

    Parameters:
        classification (str): The raw classification result from OpenAI API.

    Returns:
        tuple: A tuple containing the category and reason for the classification.
    """
    try:
        # Check if the response contains the expected format
        if "Category:" in classification and "Reason:" in classification:
            
            # Extract category and details
            category = classification.split("Category: ")[1].split("\n")[0].strip()
            details = classification.split("Reason: ")[1].strip()
            return category, details
        
        else:
            # If format is unexpected, return "Unclear"
            return "Unclear", "Response format did not match the expected structure."
    
    except Exception as e:
        
        # Provide fallback values if parsing fails
        return "Unclear", f"Error parsing classification: {str(e)}"


# Update context based on the classification
def update_context_summary(category, user_message, details=None):
    """
    Update the context summary based on the user's message and its classification.

    Parameters:
        category (str): The category determined for the user input.
        user_message (str): The original message from the user.
        details (str, optional): Additional details or reasons for classification, if available.
    
    This function updates the appropriate context list based on the message category, appends the latest user input, 
    and ensures that only the last 7 inputs are kept in each category for efficient context tracking.
    """

    # Update the appropriate context category based on the classification
    if category == "Career Path":
        context_summary["user_career_goals"].append(user_message)
    
    elif category == "Hobby or Sport Interest":
        context_summary["user_hobbies"].append(user_message)
    
    elif category == "Concern or Follow-Up":
        context_summary["concerns"].append(user_message)
    
    elif category == "General Inquiry":
        context_summary["user_interests"].append(user_message)

    # Append the latest user input to the 'user_inputs' list
    context_summary["user_inputs"].append(user_message)
    
    # If additional details are provided, track them for better context
    if details:
        context_summary["classification_details"].append(details)

    # Limit context history to the last 7 inputs for each category
    for key in context_summary:
        context_summary[key] = context_summary[key][-7:]

# Check if the inquiry relates to any previous context
def is_clearly_related_to_context(user_message, context_summary):
    """
    Check if the user's current message is contextually related to any previous inputs.

    Parameters:
        user_message (str): The latest message from the user.
        context_summary (dict): The current summary of the user's context.

    Returns:
        bool: True if the message is contextually related to previous inputs, False otherwise.
    """
    
    # Combine career goals and hobbies for context matching
    related_context = context_summary["user_career_goals"] + context_summary["user_hobbies"]

    # Check if any word from previous context appears in the user message
    for context_item in related_context:
        if any(word in user_message.lower() for word in context_item.lower().split()):
            return True
    return False

def generate_career_response(user_message, category, context_summary, details):
    """
    Generate a tailored response based on the user's input category and context.

    Parameters:
        user_message (str): The message from the user.
        category (str): The category of the user's input (e.g., Career Path, Hobby).
        context_summary (dict): The current context summary with the user's history.
        details (str): Additional classification details to include in the response.

    Returns:
        str: The generated response based on the user's message.
    """

    # Initialize system_content to hold the base system message
    system_content = base_system_message

    # Respond if the category is unclear
    if category == "Unclear":
        system_content += ( "You are having trouble understanding the user's latest input. Ask them to provide more context or clarify their question. Encourage the user to give additional details or specify what they are looking for so you can assist them better." )
    
    # Adjust system content based on classification
    if category == "Career Path":

        # Tailor response if input relates to previous career goals
        if is_clearly_related_to_context(user_message, context_summary):
            system_content += (
                "You are a career advisor bot, and the user's latest inquiry seems related to their previous career goals or interests."
                "Provide personalized recommendations with insights into their interests and potential paths."
            )
        else:
            system_content += "You are providing personalized career path recommendations based on user interests."
    
    elif category == "Hobby or Sport Interest":

        # Tailor response if input relates to previous hobbies
        if is_clearly_related_to_context(user_message, context_summary):
            system_content += (
                "You are a hobby advisor bot, and the user's latest inquiry is connected to their previous hobbies or interests."
                "Guide them on how they can explore and enhance these hobbies further."
            )
        else:
            system_content += (
                "You are a hobby advisor bot. User expresses an interest in latest inquiry, make it engaging and fun, suggesting how they can explore the hobby in an enjoyable way, with potential career paths related to that hobby."
            )
    
    elif category == "General Inquiry":

        # Use context to provide relevant responses for general inquiries
        if is_clearly_related_to_context(user_message, context_summary):
            system_content += (
                "Detecting that the user's latest inquiry might relate to previous topics."
                "Use context to provide an insightful answer if relevant, or keep it concise."
            )
        else:
            system_content += (
                "The user's latest inquiry might be a general question. Provide minimal answers and encourage the user to specify their interests for a more detailed response."
            )

    # Add additional details if available
    if details:
        system_content += f"\n\nContext Based on Latest Input: {details}\n"
    
    # Creating the formatted string for the user message content
    related_context_content = ""

    if context_summary['user_inputs']:
        related_context_content += f"List of recent User Inputs (chronologically ordered): {context_summary['user_inputs']}\n\n"
        
    if context_summary['classification_details']:
        related_context_content += f"List of Classification Details for the Latest User Inputs (chronologically ordered): {context_summary['classification_details']}\n\n"
    
    # print(system_content)
    # print(related_context_content)

    try:
        # Generate response using OpenAI's Chat API
        chat_response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[ 
                {"role": "system", "content": system_content},
                {"role": "user", "content": related_context_content},
                {"role": "user", "content": user_message}
            ],
            temperature=0.6,
            max_tokens=350
        )
        # Return the response content from the AI
        response_content = chat_response.choices[0].message.content
        return response_content
    except Exception as e:
        return f"Error generating response: {str(e)}"

# Handle user input and classification
def handle_user_input(user_message):
    """
    Handle user input by classifying it, updating context, and generating a response.

    Parameters:
        user_message (str): The message from the user.

    Returns:
        str: Response to the user's input.
    """

    # Classify the user's message
    category, details = classify_user_input(user_message)

    # Update context summary with the classification results
    update_context_summary(category, user_message, details)
    
    # Generate a career or hobby-related response based on context and category
    response = generate_career_response(user_message, category, context_summary, details)
    
    return response

# Main loop for user interaction
if __name__ == "__main__":
    
    print("\nWelcome to the Career Guidance Bot!\n")
    
    # Continuous loop to handle user input
    while True:
        user_message = input(">>> ")
        
        if user_message.lower() in ['quit', 'exit']:
            print("Goodbye! Best of luck with your career journey!")
            break
        
        # Generate and display response
        response = handle_user_input(user_message)
        print(f"Bot: {response}\n")