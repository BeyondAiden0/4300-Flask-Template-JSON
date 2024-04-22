import os
import json
from collections import Counter
import re
import numpy as np
import ast
from scipy.sparse.linalg import svds
from numpy import linalg as LA
from .reviews import rating_count_weight


"""
Creates a dictionary that maps ingredient names to their corresponding JSON file names 
within a given directory. The JSON files contains information about the ingredient
(flavor profiles, molecules, etc.)

Parameters:
    directory (str): A string representing the path to the directory containing JSON files.

Returns:
    dict: A dictionary where each key is a lowercase string representing the ingredient 
    name, and each value is a string representing the corresponding JSON file name.

Example:
    Given a directory with the following files:
        "0 Egg.json", "1 Bakery Products.json", "2 Egg.json"
    The function will return:
        {'egg': '2 Egg.json', 'bakery products': '1 Bakery Products.json'}
"""

def create_dict_from_directory(directory):
    dict_files = {}
    for item in os.listdir(directory):
        if item.endswith('.json'):
            key = (item.split(' ', 1)[1].rsplit('.', 1)[0]).lower()
            dict_files[key] = item
    return dict_files


"""
Returns a set of all flavor profile listed within an ingredient's json file 
"""

"""
Extracts and returns a set of all unique flavor profiles listed within an ingredient's JSON file.

Parameters:
    json_file (str): A string representing the path to the JSON file containing information about 
    an ingredient.

Returns:
    set: A set of strings, each representing a unique flavor profile associated with the ingredient.

Example:
    Given a JSON file with the following content:
    {
        "molecules": [
            {"name": "Molecule1", "flavor_profile": "sweet@fruity"},
            {"name": "Molecule2", "flavor_profile": "bitter"}
        ]
    }
    The function will return:
        {'sweet', 'fruity', 'bitter'}
"""

def get_flavor_profiles(json_file):
    flavor_profiles = set()
    with open(json_file, 'r') as f:
        data = json.load(f)
    for molecule in data['molecules']:
        if 'flavor_profile' in molecule:
            flavor_profiles.update(molecule['flavor_profile'].split('@'))
    flavor_profiles.discard('')
    return flavor_profiles


"""
Aggregates a set of all unique flavor profiles found within JSON files in a specified directory. 
This function compiles the unique flavors from all ingredients listed in the dataset.

Parameters:
    directory (str): A string representing the path to the directory containing JSON files with ingredient data.

Returns:
    list: A sorted list of unique flavor profile strings extracted from all JSON files in the directory.

Example:
    Given a directory with JSON files named '0 Egg.json', '1 Milk.json', etc., where each file contains flavor 
    profile data, the function will return a sorted list of all unique flavor profiles found in these files.
"""

def collect_flavor_profiles_from_directory(directory):
    all_flavor_profiles = set()
    for item in os.listdir(directory):
        if item.endswith('.json'):
            flavor_profiles = get_flavor_profiles(os.path.join(directory, item))
            all_flavor_profiles.update(flavor_profiles)
    all_flavor_profiles = sorted([fp for fp in all_flavor_profiles if fp])
    return all_flavor_profiles


"""
Analyzes an ingredient's JSON file to count the occurrences of each flavor profile keyword 
and returns a dictionary sorted by frequency in descending order.

Parameters:
    json_file (str): The path to the JSON file containing data about an ingredient.

Returns:
    dict: A dictionary where each key is a flavor profile keyword (str) and each value is 
    the occurrence count (int) of that keyword.

Example:
    Given a JSON file with the following content:
    {
        "molecules": [
            {"name": "Molecule1", "flavor_profile": "sweet@fruity"},
            {"name": "Molecule2", "flavor_profile": "sweet@bitter"}
        ]
    }
    The function will return:
        {'sweet': 2, 'fruity': 1, 'bitter': 1}
"""

def extract_keywords(json_file):
    keyword_counts = {}
    with open(json_file, 'r') as f:
        data = json.load(f)
        for molecule in data['molecules']:
            if 'flavor_profile' in molecule:
                keywords = molecule['flavor_profile'].split('@')
                for keyword in keywords:
                    if keyword: 
                        if keyword in keyword_counts:
                            keyword_counts[keyword] += 1
                        else:
                            keyword_counts[keyword] = 1
    return dict(sorted(keyword_counts.items(), key=lambda item: item[1], reverse=True))


"""
Aggregates the flavor profile keyword occurrences from a list of JSON files 
representing different ingredients. It returns a dictionary sorted by the 
frequency of each flavor name in descending order.

Parameters:
    json_files (list of str): A list of strings where each string is the filename 
    of a JSON file containing ingredient data.

Returns:
    dict: A dictionary where each key is a flavor profile keyword (str) and each value 
    is the total occurrence count (int) of that keyword across all provided JSON files.

Example:
    Given a list of JSON filenames ['0 Egg.json', '1 Milk.json'], the function will return a 
    dictionary with the total occurrence count of each flavor profile keyword found in these 
    files, sorted by frequency.
"""

def merge_counts(json_files):
    merged_keyword_counts = Counter()
    for json_file in json_files:
        full_path = os.path.join(data_dir, json_file)
        keyword_counts = extract_keywords(full_path)
        merged_keyword_counts.update(keyword_counts)
    merged_keyword_counts = dict(
        sorted(merged_keyword_counts.items(), key=lambda item: item[1], reverse=True))
    return merged_keyword_counts


"""
Standardizes a dish's flavor profile by ensuring all possible flavors are represented.

Parameters:
    dict_X (dict): A dictionary representing the flavor profile of a single dish, where keys 
    are flavor names (str) and values are occurrence counts (int).
    
    all_flavor_profiles (list of str): A list of all unique flavor names across the dataset.

Returns:
    dict: A standardized dictionary where each key is a flavor name (str) from the total set 
    of unique flavors, and each value is the occurrence count (int) of that flavor in the dish's 
    flavor profile.

Example:
    Given 
        `dict_X` as {'sweet': 2, 'bitter': 1} and 
        `all_flavor_profiles` as ['sweet', 'bitter', 'sour', 'salty'],
    the function will return {'sweet': 2, 'bitter': 1, 'sour': 0, 'salty': 0}.
"""

def compare_dict_with_flavor_profiles(dict_X, all_flavor_profiles):
    flavor_profile_counts = dict.fromkeys(all_flavor_profiles, 0)
    for key, value in dict_X.items():
        if key in flavor_profile_counts:
            flavor_profile_counts[key] += value
    return flavor_profile_counts


"""
Saves a text file containing a tuple containing three lists: dish names, dish IDs, and ingredients, 
from a given recipes file. Each list corresponds to the respective attribute of the recipes 
contained in the file.

Parameters:
    recipes (str): A string representing the path to the JSON file containing multiple recipes.

Returns:
    tuple: A tuple containing three lists:
        - The first list contains dish names (str), all converted to lowercase.
        - The second list contains dish IDs (int).
        - The third list contains lists of ingredients (list of str), where each 
        sublist corresponds to the ingredients of a single recipe.

Example:
    Given a recipes file with the following content:
    [
        {"Name": "Omelette", "RecipeId": 123, "RecipeIngredientParts": "\"Eggs\" \"Milk\" \"Salt\""},
        {"Name": "Pancakes", "RecipeId": 456, "RecipeIngredientParts": "\"Flour\" \"Eggs\" \"Milk\""}
    ]
    The function will return:
        (['omelette', 'pancakes'], [123, 456], [['eggs', 'milk', 'salt'], ['flour', 'eggs', 'milk']])
"""

def dish_id_ingr(recipes, base_dir):
    id = []
    ingr = []
    dishes = []
    with open(recipes, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for dish in data:
            dishes.append(dish["Name"].lower())
            id.append(dish["RecipeId"])
            ingr.append(
                ((re.findall(r'"(.*?)"', dish["RecipeIngredientParts"].casefold()))))
    info = (dishes, id, ingr)
    input_file_path = os.path.join(base_dir, "data", "dish_id_ingr.txt")
    with open(input_file_path, 'w') as file:
        file.write(json.dumps(info))

"""
Constructs a matrix representing the flavor profiles of dishes and applies Singular Value 
Decomposition (SVD) to this matrix. It saves the matrix of dishes against latent flavor 
dimensions (U)

Parameters:
    ndishes (int): The number of dishes, which determines the number of rows in the matrix.

    nflavors (int): The number of unique flavors, which determines the number of columns in the matrix.

    name_ing_data (tuple): A tuple containing lists of dish names, dish IDs, and ingredient lists.

    json_dict (dict): A dictionary mapping ingredient names to their flavor occurrence dictionaries.

    all_flavor_profiles (list of str): A list of all unique flavor names across the dataset.

Example:
    Given the number of dishes and flavors, along with the appropriate `name_ing_data`, `json_dict`, and 
    `all_flavor_profiles`, the function will construct the flavor profile matrix, apply SVD, and save the 
    resulting matrices to disk.
"""

def flavor_matrix(ndishes, nflavors, name_ing_data, json_dict, all_flavor_profiles):
    matrix = np.zeros((ndishes, nflavors), dtype=float)
    row = 0
    for ingredient_list in name_ing_data[2]:
        acc = []
        for ingredient in ingredient_list:
            if ingredient.lower() in json_dict.keys():
                acc.append(json_dict[ingredient.lower()])
        flavors = merge_counts(acc)
        for flavor in flavors.keys():
            ind = all_flavor_profiles.index(flavor)
            val = flavors[flavor]
            matrix[row][ind] = val
        row += 1
    dish_latentflavors, importance, latentflavor_flavors_trans = svds(matrix, k = 15)
    np.save((os.path.join(base_dir, "data","dish-latent-flavors-matrix.npy")), dish_latentflavors)
    #np.save((os.path.join(base_dir, "data","flavors-matrix.npy")), matrix)


"""
Retrieves the user's selected dish name from a stored file

Parameters:
    filename (str, optional): The name of the file containing the user's selected dish name. 
    Defaults to 'input_vector.txt'.

Returns:
    str: The name of the dish selected by the user.

Example:
    If the file 'input_vector.txt' contains the following content:
    "Spaghetti Carbonara"
    The function will return:
    "Spaghetti Carbonara"
"""

def load_user_input(filename):
    with open(filename, 'r') as file:
        content = file.read()
        input = ast.literal_eval(content)
    user_input_string = input
    return user_input_string


"""
Identifies and returns the top ten dishes most similar to the user's input based on cosine similarity 
and returns detailed information about these dishes, including their names, cosine similarity
scores, ranking scores (cosine similarity score weighted by rating), IDs, descriptions, recipes, 
ratings (1-5) and rating counts

Parameters:
    query_sim (str): The name of the dish similar to that which was inputted by the user.

    name_ing_data (tuple): A tuple containing lists of dish names, dish IDs, and ingredient lists.

    matrix_comp (numpy.ndarray): The matrix containing the flavor vectors that represents each dish.

    recipes (str): The path to the JSON file containing the recipes data.

Returns:
    list: A list of lists, where each inner list contains the name, cosine similarity score, ID, 
    description, and recipe instructions of a similar dish.

Example:
    Given a user's input dish name, the corresponding lists of dish names and IDs, a 
    matrix of flavor vectors, and a path to the recipes file, the function will return detailed 
    information for the top ten most similar dishes.
"""

def top_ten(query_sim, name_ing_data, matrix_comp, recipes,rating_count_weight):
    index = name_ing_data[0].index(query_sim.lower())
    vect = matrix_comp[index,:]

    dish_sim = []
    cos_sim = []
    for row,weight in zip(matrix_comp,rating_count_weight[2]):
        if (LA.norm(vect) * LA.norm(row)) != 0:
            cos = np.dot(vect, row) / (LA.norm(vect) * LA.norm(row))
            cos_sim.append(cos)
            dish_sim.append(weight*cos)
        else:
            dish_sim.append(0)
            cos_sim.append(0)
    dish_cossim = np.array(dish_sim)
    top = np.argsort(dish_cossim)[-11:]
    ordered = top[::-1]
    final = np.delete(ordered, np.where(ordered == index))
    if np.size(final) != 10:
        final = final[:10]  
    info = []
    cos_scores = np.array(cos_sim)
    top1 = np.argsort(cos_scores)[-11:]
    ordered1 = top1[::-1]
    final1 = np.delete(ordered1, np.where(ordered1 == index))
    if np.size(final1) != 10:
        final1 = final1[:10]
    with open(recipes, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for indx in final:
            name = data[indx]["Name"]
            id = data[indx]["RecipeId"]
            desc = data[indx]["Description"]
            recipe = data[indx]["RecipeInstructions"]
            rating = rating_count_weight[0][indx]
            count = rating_count_weight[1][indx]
            info.append([name, cos_sim[indx], dish_sim[indx], id, desc, recipe, rating, count])
    return(info)

#######################################################################################

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, "data", "flavors")
recipes_file = os.path.join(base_dir, "data", "random-recipe.json")
dish_id_ingr_path = os.path.normpath(os.path.join(base_dir, 'data', 'dish_id_ingr.txt'))

"""
Testing Purposes:
# Collect all unique flavor profiles from JSONs in the current directory
all_flavor_profiles = collect_flavor_profiles_from_directory(data_dir)

# Total Number of Dishes
ndishes = len(name_ing_data[0])

# Total Number of Flavors
nflavors = len(all_flavor_profiles)

json_dict = create_dict_from_directory(data_dir)
#matrix = flavor_matrix(ndishes, nflavors, name_ing_data, json_dict, all_flavor_profiles)
"""
# Contains (dish_name, dish_id, ingredients)
#dish_id_ingr(recipes_file, base_dir)

with open(dish_id_ingr_path, 'r') as file:
    content = file.read()
    input = ast.literal_eval(content)
name_ing_data = input

#U in SVD (dish against latent dimensions)
dish_latentflavors_path = os.path.join(base_dir, "data", "dish-latent-flavors-matrix.npy")
dish_latentflavors = np.load(dish_latentflavors_path)

"""
Test Purposes:
final_output1 = top_ten("Pulled Pork", name_ing_data, dish_latentflavors, recipes_file, rating_count_weight)
for each in final_output1:
    print("name ", each[0])
    print("id ", each[3])
    print("cosine "  , each[1])
    print("ranking " , each[2])
    print("rating " , each[6])
    print("count ", each[7])
    print("++++++++++++")
"""


