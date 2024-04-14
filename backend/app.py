import os
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import numpy as np
from helpers.matrix import (
    name_ing_data,
    top_ten,
    flavor_matrix
)

app = Flask(__name__)
CORS(app)

base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, "data", "flavors")

# Assuming 'matrix.py' provides these details
from helpers.matrix import collect_flavor_profiles_from_directory, create_dict_from_directory, dish_id_ingr, recipes_file
all_flavor_profiles = collect_flavor_profiles_from_directory(data_dir)
json_dict = create_dict_from_directory(data_dir)
name_ing_data = dish_id_ingr(recipes_file)

# Load the flavor matrix
flavor_matrix_path = os.path.join(base_dir, "data", "flavors-matrix.npy")
flavor_matrix = np.load(flavor_matrix_path)

@app.route("/")
def home():
    return render_template('base.html')

@app.route("/recipe_names", methods=["GET"])
def recipe_names():
    # Return all dish names as a list
    return jsonify(name_ing_data[0])

@app.route("/store_user_input", methods=["POST"])
def store_user_input():
    # Store the selected recipe name in 'input_vector.txt'
    user_input = request.json.get("userInput")
    input_file_path = os.path.join(base_dir, "input_vector.txt")
    with open(input_file_path, 'w') as file:
        file.write(json.dumps(user_input))
    return jsonify({"status": "success", "message": "User input stored"})

@app.route("/get_similar_dishes", methods=["POST"])
def get_similar_dishes():
    # Load the user input from 'input_vector.txt'
    input_file_path = os.path.join(base_dir, "input_vector.txt")
    with open(input_file_path, 'r') as file:
        user_input = json.loads(file.read())
    
    # Fetch similar dishes based on the stored user input
    try:
        final_output = top_ten(user_input, name_ing_data, flavor_matrix, recipes_file)
        return jsonify(final_output)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
