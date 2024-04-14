import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import heapq


def extract_names(json_data):
    """
    Extracts all 'Name' fields from a JSON object and returns them in a list

    Arguments
    ========
        json_data: JSON data in string format

    Returns:
        names: List of names extracted from the JSON data
    """
    # Load the JSON data
    data = json.loads(json_data)

    # Initialize an empty list to store the names
    names = []

    # Iterate over each recipe in the data
    for recipe in data:  # add ['recipes'] after data if not using random-recipe.json
        # Add the name of the recipe to the list
        names.append(recipe['Name'])

    return names


print(os.getcwd())

with open('backend\\data\\random-recipe.json', 'r', encoding='utf-8') as f:
    json_data = f.read()
names = extract_names(json_data)

# Pre-compute the vectorizer and the TF-IDF matrix
vectorizer = TfidfVectorizer().fit(names)
tfidf_matrix = vectorizer.transform(names)


def cossimNameMatch(user_input, vectorizer=vectorizer, tfidf_matrix=tfidf_matrix, recipe_list=names):
    """
    Finds top 10 similar dish names within database using cosine similarity

    Arguments
    ========
        user_input: user input of String
        vectorizer: Precomputed TfidfVectorizer
        tfidf_matrix: Precomputed TF-IDF matrix
        recipe_list: List of recipes

    Returns:
        top_10_similar: ranked list of top 10 results
    """
    # Transform the user_input into the TF-IDF space
    user_input_vector = vectorizer.transform([user_input])

    # Compute the cosine similarity with the pre-computed vectors
    cosine_sim = cosine_similarity(user_input_vector, tfidf_matrix)

    # Get the pairwise similarity scores of all dishes with that dish
    sim_scores = list(enumerate(cosine_sim[0]))

    # Use a heap to maintain the top 10 scores
    top_10_similar = heapq.nlargest(10, sim_scores, key=lambda x: x[1])

    # Get the dish indices
    dish_indices = [i[0] for i in top_10_similar]

    # Return the top 10 most similar dishes
    top_10_similar = [recipe_list[i] for i in dish_indices]

    return top_10_similar


print(cossimNameMatch("pulled spork"))
