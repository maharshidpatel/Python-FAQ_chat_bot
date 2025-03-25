"""
Author: Maharshi Patel, 000738366
Date: 28-10-2024
Description: This script implements an article recommendation system using TF-IDF for text vectorization
and cosine similarity for measuring article relevance. The system allows users to load articles from a 
CSV file, generate random recommendations, and view selected articles along with new recommendations 
based on their choices.
"""

from csv import DictReader
from random import random, sample
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Constant for the initial number of articles to recommend
INITIAL_ARTICLE_COUNT = 10

def load_articles(filename, filetype="csv"):
    """Loads articles from a specified CSV file and generates titles.

    Args:
        filename (str): The name of the file to load.
        filetype (str): The type of the file (default is "csv").

    Returns:
        list: A list of articles, each represented as a dictionary.
    """
    articles = []
    # Load articles from a CSV file
    if filetype == "csv":
        with open(filename, encoding="utf-8") as csvfile:
            reader = DictReader(csvfile)
            for row in reader:
                articles.append(row)

    # Generate titles based on the first seven words of the text
    for row in articles:
        row["title"] = ' '.join(row["text"].split()[:7])

    print(len(articles), "articles loaded")
    return articles

def vectorize_articles(articles, 
                       ngram_range=(3, 5), 
                       analyzer='char', 
                       min_df=2, 
                       max_df=0.85):
    
    """
    Vectorizes articles using TF-IDF with character n-grams and filtering.

    Args:
        articles (list): A list of articles.
        ngram_range (tuple): The range of n-grams to use (default is (3, 5)).
        analyzer (str): The type of analyzer to use (default is 'char').
        min_df (int): Minimum document frequency (default is 2).
        max_df (float): Maximum document frequency (default is 0.85).

    Returns:
        array: A matrix of cosine similarity scores.
    """

    article_texts = []
    # Collect article texts for vectorization
    for article in articles:
        article_texts.append(article["text"])

    # Initialize the TfidfVectorizer with optimized parameters
    vectorizer = TfidfVectorizer(
        analyzer=analyzer,       
        ngram_range=ngram_range, 
        min_df=min_df,           
        max_df=max_df
    )

    # Transform the articles into a TF-IDF matrix
    tfidf_matrix = vectorizer.fit_transform(article_texts)
    
    print("TF-IDF matrix shape:", tfidf_matrix.shape)
    return cosine_similarity(tfidf_matrix)

def get_random_article_recommendations(articles, number_of_recommendations=INITIAL_ARTICLE_COUNT):
    """Generates a list of random article recommendations from the articles list.

    Args:
        articles (list): A list of articles.
        number_of_recommendations (int): The number of recommendations to generate.

    Returns:
        list: A list of indices representing recommended articles.
    """

    total_articles = len(articles)
    return sample(range(total_articles), number_of_recommendations)

def display_recommendations(recommendations, articles):
    """Displays article recommendations.

    Args:
        recommendations (list): A list of recommended article indices.
        articles (list): A list of articles.
    """

    print("\nHere are some recommendations for you:\n")
    for i in range(len(recommendations)):
        article_number = recommendations[i]
        print(f"{i + 1}. {articles[article_number]['title']}")

def display_article(article_number, articles):
    """Displays a specific article based on its index.

    Args:
        article_number (int): The index of the article to display.
        articles (list): A list of articles.
    """

    print("\n")
    print("Article", article_number + 1)
    print("=========================================")
    print(articles[article_number]["title"])
    print()
    print(articles[article_number]["text"])
    print("=========================================")

def new_recommendations(last_article_chosen_index, articles, similarity_matrix, previous_recommendations, number_of_similar_articles=8, number_of_dissimilar_articles=2):
    """Generates new recommendations based on the last article read.

    Args:
        last_article_chosen_index (int): Index of the last article read.
        articles (list): A list of articles.
        similarity_matrix (array): The matrix of similarity scores.
        previous_recommendations (list): Previously recommended articles.
        number_of_similar_articles (int): Number of similar articles to recommend.
        number_of_dissimilar_articles (int): Number of dissimilar articles to recommend.

    Returns:
        list: A combined list of similar and dissimilar article indices.
    """

    # Get the similarity scores for the last chosen article
    last_article_similarity_scores = similarity_matrix[last_article_chosen_index]
    
    # Prepare a sorted list of similar articles based on their similarity scores
    similar_article_indices_with_scores = sorted(
        [(index, score) for index, score in enumerate(last_article_similarity_scores)],
        key=lambda x: x[1], 
        reverse=True
    )
    
    # Prepare a list to store similar articles
    similar_article_indices = []

    # Set to track the text content of recommended articles to avoid duplicates
    recommended_article_texts = set()

    # Loop through the sorted list of similar articles
    for article_index, similarity_score in similar_article_indices_with_scores:
        # Check if the article is not the last chosen article and not already recommended
        if article_index != last_article_chosen_index and article_index not in previous_recommendations and similarity_score < 1.0:
            # Get the text of the current article
            current_article_text = articles[article_index]["text"]
            
            # Check if the text is already in the recommended texts set
            if current_article_text not in recommended_article_texts:
                similar_article_indices.append(article_index)  # Add the article index to the list
                recommended_article_texts.add(current_article_text)  # Add the text to the set
        
        # Stop if we have enough similar articles
        if len(similar_article_indices) >= number_of_similar_articles:
            break  

    # Create a set of already used articles to avoid duplicates
    used_article_indices = set(similar_article_indices) | {last_article_chosen_index} | set(previous_recommendations)
    
    # Find available articles that have not been used
    available_article_indices = list(set(range(len(articles))) - used_article_indices)
    
    # Ensure we have enough articles to sample from
    if len(available_article_indices) < number_of_dissimilar_articles:
        dissimilar_article_indices = available_article_indices  # Fallback to available articles if not enough
    else:
        dissimilar_article_indices = sample(available_article_indices, number_of_dissimilar_articles)

    return similar_article_indices + dissimilar_article_indices


def display_new_recommendations(recommendation_indices, articles):
    """Displays new recommendations combining similar and dissimilar articles.

    Args:
        recommendation_indices (list): A list of indices for the recommended articles.
        articles (list): A list of articles.
    """ 
    
    # Count the number of recommendations
    number_of_recommendations = len(recommendation_indices)
    
    # Determine how many recommendations are similar and how many are dissimilar
    number_of_similar_recommendations = number_of_recommendations - 2
    
    print("\nHere are some new recommendations for you:\n")
    
    # Display similar articles
    print(f"{number_of_similar_recommendations} recommendations based on your choice:\n")
    for index in range(number_of_similar_recommendations):
        article_index = recommendation_indices[index]
        print(f"{index + 1}. {articles[article_index]['title']}")

    # Display dissimilar articles
    print("\nOr if you want something different, how about:\n")
    for index in range(number_of_similar_recommendations, number_of_recommendations):
        article_index = recommendation_indices[index]
        print(f"{index + 1}. {articles[article_index]['title']}")


def main():
    articles = load_articles('bbc_news.csv')
    similarity_matrix = vectorize_articles(articles)
    
    # Get initial random recommendations
    random_recommendations = get_random_article_recommendations(articles)

    # Display the initial set of recommendations once
    display_recommendations(random_recommendations, articles)
    
    while True:
        choice = input("\nYour choice? (or 'q' to quit): ").strip()
        
        if choice.lower() == 'q':
            print("\nThank you for using the article recommendation system! Goodbye!")
            break
        
        try:
            choice_index = int(choice) - 1  # Adjust for zero-based index
            
            if 0 <= choice_index < INITIAL_ARTICLE_COUNT:
                # Display the selected article
                display_article(random_recommendations[choice_index], articles)
                
                # Generate new recommendations based on the user's choice
                new_recommendations_list = new_recommendations(
                    random_recommendations[choice_index],
                    articles,
                    similarity_matrix,
                    random_recommendations
                )
                
                # Display new recommendations
                display_new_recommendations(new_recommendations_list, articles)
                
                # Update recommendations to avoid repetition
                random_recommendations = new_recommendations_list
            else:
                print("Invalid choice. Please select a number between 1 and", INITIAL_ARTICLE_COUNT)
        
        except ValueError:
            print("Invalid input. Please enter a number or 'q' to quit.")    
        except IndexError:
            print("An error occurred while displaying the article. Please try again.")

if __name__ == "__main__":
    main()
