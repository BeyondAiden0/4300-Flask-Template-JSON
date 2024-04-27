import os
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import numpy as np
from helpers.matrix import (
    name_ing_data,
    top_ten,
)
from helpers.cossimNameMatch import cossimNameMatch
from helpers.reviews import rating_count_weight


app = Flask(__name__)
CORS(app)

base_dir = os.path.dirname(os.path.abspath(__file__)) # backend directory
data_dir = os.path.join(base_dir, "data", "flavors")

# Assuming 'matrix.py' provides these details
from helpers.matrix import collect_flavor_profiles_from_directory, create_dict_from_directory, dish_id_ingr, recipes_file
all_flavor_profiles = collect_flavor_profiles_from_directory(data_dir)
json_dict = create_dict_from_directory(data_dir)
# name_ing_data = dish_id_ingr(recipes_file, base_dir)

# Load the SVD flavor matrix
dish_latentflavors_path = os.path.join(base_dir, "data", "dish-latent-flavors-matrix.npy")
dish_latentflavors = np.load(dish_latentflavors_path)

@app.route("/")
def home():
    """
    Render the homepage template.

    Returns:
        render_template: Renders the 'base.html' template for the homepage.
    """
    return render_template('base.html')

@app.route("/recipe_names", methods=["GET"])
def recipe_names():
    """
    Retrieve all dish names from the application's data source and send them as a JSON response.

    Returns:
        jsonify: JSON response containing a list of all dish names.
    """
    # Return all dish names as a list
    return jsonify(name_ing_data[0])

@app.route('/filter_names', methods=['GET'])
def filter_names():
    """
    Process a user's search query to filter and retrieve dish names that closely match the input, using cosine similarity.

    Returns:
        jsonify: JSON response containing a list of filtered dish names based on the user's query. If an error occurs,
                 returns a JSON object with an 'error' key and message detailing the exception.
        status (int): HTTP status code indicating success (200) or internal server error (500).
    """
    user_input = request.args.get('query', '')  # Get the user input from the query parameters
    if user_input:
        try:
            # Assuming cossimNameMatch and other required objects are defined/imported
            filtered_names = cossimNameMatch(user_input)
            return jsonify(filtered_names)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify([])

@app.route("/store_user_input", methods=["POST"])
def store_user_input():
    """
    Store a user's selected recipe name in a text file on the server.

    Returns:
        jsonify: JSON response indicating the status and message of the operation; typically confirming successful storage.
    """
    # Store the selected recipe name in 'input_vector.txt'
    user_input = request.json.get("userInput")
    input_file_path = os.path.join(base_dir, "input_vector.txt")
    with open(input_file_path, 'w') as file:
        file.write(json.dumps(user_input))
    return jsonify({"status": "success", "message": "User input stored"})

@app.route("/get_similar_dishes", methods=["POST"])
def get_similar_dishes():
    """
    Retrieve similar dishes based on a user's previously stored input. This function reads the user's input from a file,
    and then utilizes a series of computations involving flavor profiles and ratings to determine similar dishes.

    Returns:
        jsonify: JSON response containing a list of dishes similar to the user's input. Each dish includes details such as
                 name, similarity score, and user ratings. If an error occurs, returns a JSON object with an 'error' key
                 and message detailing the exception.
        status (int): HTTP status code indicating success (200) or internal server error (500).
    """
    # Load the user input from 'input_vector.txt'
    input_file_path = os.path.join(base_dir, "input_vector.txt")
    with open(input_file_path, 'r') as file:
        user_input = json.loads(file.read())
    
    # Fetch similar dishes based on the stored user input
    try:
        final_output = top_ten(user_input, name_ing_data, dish_latentflavors, recipes_file, rating_count_weight)
        return jsonify(final_output)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
