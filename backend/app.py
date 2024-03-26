import json
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
import pandas as pd
from helpers.matrix import query_vector, top_ten, load_user_input_and_vector, name_ing_data, recipes_file
try:
    # Try to perform relative import (when running as a package/module)
    from helpers.cosineSimilarity import all_dish_cos_sim_matrix
except ImportError:
    # Fallback to modifying the sys.path to import (when running as a script)
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    from cosineSimilarity import all_dish_cos_sim_matrix

# ROOT_PATH for linking with all your files.
# Feel free to use a config.py or settings.py with a global export variable
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..", os.curdir))

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Specify the path to the JSON file relative to the current script
json_file_path = os.path.join(current_directory, 'init.json')

# Assuming your JSON data is stored in a file named 'init.json'
with open(json_file_path, 'r') as file:
    data = json.load(file)
    recipes_df = pd.DataFrame(data['recipes'])
    reviews_df = pd.DataFrame(data['reviews'])

app = Flask(__name__)
CORS(app)

# Sample search using json with pandas


def json_search(query):
    merged_df = pd.merge(recipes_df, reviews_df,
                         left_on='RecipeId', right_on='RecipeId', how='inner')
    matches = merged_df[merged_df['Name'].str.lower(
    ).str.contains(query.lower())]
    matches_filtered = matches[[
        'Name', 'AuthorName', 'Description', 'RecipeInstructions', 'AggregatedRating']]
    matches_filtered_json = matches_filtered.to_json(orient='records')
    return matches_filtered_json


@app.route("/")
def home():
    return render_template('base.html', title="sample html")


@app.route("/recipes")
def recipes_search():
    # Assume the query parameter is 'name' for recipe name
    text = request.args.get("name")
    return json_search(text)

# This Flask endpoint receives the user input sent from the frontend and can process or store it


@app.route('/store_user_input', methods=['POST'])
def store_user_input():
    data = request.json
    userInput = data['userInput']
    userVector = query_vector(userInput) # Generate the vector from user input
    outputTuple = (userInput, userVector.tolist()) # Prepare the tuple to be written to file

    # Process userInput or store it here:
    # 1. Save userInput to a file
    with open('input_vector.txt', 'w') as file:
        file.write(str(outputTuple))

    # 2. User userInput as input to method in other python script
    # otherPythonMethod(userInput)
    # (1) To use userInput in other python script:
    # def process_user_input():
    # with open('user_input.txt', 'r') as file:
    #     userInput = file.read()

    return jsonify({"status": "success", "userInput": userInput})

@app.route("/top_similar", methods=["POST"])
def top_similar():
    data = request.json
    user_input = data['userInput']
    
    # You need to ensure you have a method to generate a flavor profile vector from user_input
    # For demonstration, let's say it returns a vector
    user_input_vector = query_vector(user_input)

    # Use the vector to find the top 10 similar dishes
    top_dishes = top_ten(user_input, all_dish_cos_sim_matrix, name_ing_data[0], recipes_file)

    # Format the response
    response = [{"Name": dish[1], "AuthorName": dish[2], "Description": dish[3], "RecipeInstructions": dish[4], "AggregatedRating": dish[5]} for dish in top_dishes]
    
    return jsonify(response)


@app.route("/get_similar_dishes", methods=["POST"])
def get_similar_dishes():
    data = request.json
    selected_dish = data['selectedDish']
    
    # Assume query_vector returns a flavor profile vector for the selected dish
    # And top_ten returns the top 10 similar dishes based on cosine similarity
    similar_dishes_info = top_ten(selected_dish, all_dish_cos_sim_matrix, name_ing_data[0], recipes_file)
    
    return jsonify(similar_dishes_info)

if 'DB_NAME' not in os.environ:
    app.run(debug=True, host="0.0.0.0", port=5000)
