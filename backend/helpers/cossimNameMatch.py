from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import json

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
    for recipe in data['recipes']:
        # Add the name of the recipe to the list
        names.append(recipe['Name'])

    return names

def cossimNameMatch(user_input, recipe_list):
    """
    Finds top 10 similar dish names within database using cosine similarity

    NOTE:
    cossimNameMatch needs you to pass the JSON data as a string to it. 
    So if the JSON data is in a file, we can read it into a string as such:
        with open('fast_test.json', 'r') as f:
            json_data = f.read()
        names = extract_names(json_data)

    And then feed cossimNameMatch something like:
        cossimNameMatch("pork", names)

    Arguments
    ========
        user_input: user input of String

        recipe_list: intended database (must be a List, can use )

    Returns:
        top_10_similar: ranked list of top 10 results
    """
    # Adding user input to the recipe list
    recipe_list.append(user_input)

    # Vectorizing the text data
    vectorizer = TfidfVectorizer().fit_transform(recipe_list)

    # Compute the cosine similarity matrix
    cosine_sim = linear_kernel(vectorizer, vectorizer)

    # Get the index of the user_input in the cosine_sim matrix
    idx = len(cosine_sim) - 1

    # Get the pairwsie similarity scores of all dishes with that dish
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the dishes based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the 10 most similar dishes
    sim_scores = sim_scores[1:11]

    # Get the dish indices
    dish_indices = [i[0] for i in sim_scores]

    # Return the top 10 most similar dishes
    top_10_similar = [recipe_list[i] for i in dish_indices]

    return top_10_similar