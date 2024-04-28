import os
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import heapq


"""
Extracts all 'Name' fields from a JSON object and returns them in a list

Parameters:
    json_data: JSON data in string format

Returns:
    names: List of names extracted from the JSON data
"""

def extract_names(json_data):
    data = json.loads(json_data)
    names = []

    for recipe in data:  
        names.append(recipe['Name'])

    return names

# with open('backend\\data\\random-recipe.json', 'r', encoding='utf-8') as f:
#     json_data = f.read()
# names = extract_names(json_data)

# Pre-compute the vectorizer and the TF-IDF matrix
# vectorizer = TfidfVectorizer().fit(names)
# tfidf_matrix = vectorizer.transform(names)

file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'reduced-recipe.json')
file_path = os.path.normpath(file_path)  # Normalize path for cross-platform compatibility

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        json_data = f.read()
    names = extract_names(json_data)

    vectorizer = TfidfVectorizer().fit(names)
    tfidf_matrix = vectorizer.transform(names)


    """
    Returns similar dish names within the database using cosine similarity, filtered by a relevance threshold.

    Parameters:
        user_input: user input of String

        vectorizer: Precomputed TfidfVectorizer

        tfidf_matrix: Precomputed TF-IDF matrix

        recipe_list: List of recipes

        threshold: minimum cosine similarity score for a recipe to be considered similar

    Returns:
        top_results (list): ranked list of up to 10 results that meet the threshold
    """
    
    def cossimNameMatch(user_input, vectorizer=vectorizer, tfidf_matrix=tfidf_matrix, recipe_list=names, threshold=0.3):

        user_input_vector = vectorizer.transform([user_input])
        cosine_sim = cosine_similarity(user_input_vector, tfidf_matrix)[0]
        filtered_results = [(index, sim_score) for index, sim_score in enumerate(cosine_sim) if sim_score > threshold]
        top_results = heapq.nlargest(10, filtered_results, key=lambda x: x[1])
        dish_indices = [i[0] for i in top_results]
        top_results = [recipe_list[i] for i in dish_indices]

        return top_results

except FileNotFoundError as e:
    print(f"File not found: {e}")
except Exception as e:
    print(f"An error occurred: {e}")