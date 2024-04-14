import os
import json
from collections import Counter
import re
import numpy as np
import ast
from scipy.sparse.linalg import svds
from sklearn.metrics.pairwise import cosine_similarity
from numpy import linalg as LA


"""
Returns a dictionary of the format: {"ingredient-name":"json-file-name"} given a json 
directory

Relates each ingredient to the json file containing information on the ingredient 
(flavor profiles, molecules, etc.)

ex: {'egg': '0 Egg.json', 'bakery products': '1 Bakery Products.json',..}
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
Returns a set of all unique flavors within the directory/dataset
Determines the unique flavors from all the ingredients within the dataset
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
Returns a dictionary of the format {flavor_name: flavor_occurence} given an
ingredient's json file
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
Returns a dictionary of the format {flavor_name: flavor_occurence} given a 
list of ingredient's json files
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
Returns a dictionary of the format {flavor_name: flavor_occurence} such that the size/
number of items in the dictionary is equal to the total number of unique flavors 

dict_x is a dictionary of the format {flavor_name: flavor_occurence} for a 
single dish such that the size/number of items in the dictionary may differ
from that another dish since not all flavors may have been accounted/detected

This function standardizes the size of the dictionaries used to represent each dish's
flavor profile (equal to the total number of unique flavors).

The values of the dictionary is the 'flavor vector' of the dish. (Each value 
represents the occurrence of the respective flavor in the dish's flavor profile)
"""
def compare_dict_with_flavor_profiles(dict_X, all_flavor_profiles):
    flavor_profile_counts = dict.fromkeys(all_flavor_profiles, 0)
    for key, value in dict_X.items():
        if key in flavor_profile_counts:
            flavor_profile_counts[key] += value
    return flavor_profile_counts


"""
Returns a tuple of the format (dish_name, dish_id, ingredients), each of which is a list
given a recipes file (containing multiple recipes)

For each list in the tuple (dish_name, dish_id, and ingredients), the items with the same 
index are from the same recipe 

ex: dish_name[0] has an id of dish_id[0] with ingredients ingredients[0]
"""
def dish_id_ingr(recipes):
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
    return (dishes, id, ingr)


"""
Saves the matrix of all the dishes against the latent dimensions (flavors) 
[dish_latentflavors] and the matrix of the all the flavors against 
the latent dimensions (flavors) [latentflavor_flavors_trans.T] generated by 
apply SVD on the matrix of all dishes against all the flavors
"""
def flavor_matrix_svd(ndishes, nflavors, name_ing_data, json_dict, all_flavor_profiles):
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
    #dish_latentflavors, importance, latentflavor_flavors_trans = svds(matrix, k = 500)
    #np.save((os.path.join(base_dir, "data","dish-latent-flavors-matrix.npy")), dish_latentflavors)
    #np.save((os.path.join(base_dir, "data","latent-flavors-flavors-matrix.npy")), latentflavor_flavors_trans.T)
    return(matrix)


"""
Returns the stored user's inputted dish along with the dish's 'flavor vector.'

The stored user's input refers the the user's final selection of a dish from the drop 
down menu. To ensure that the user's input is within our dataset, we have the user  
select a dish from a drop down menu. The dishes listed in the drop down menu will be
order based on edit distance where most similar dish to the user's original input is 
listed first.
"""
def load_user_input(filename='input_vector.txt'):
    os.chdir("backend")
    with open(filename, 'r') as file:
        content = file.read()
        input_tuple = ast.literal_eval(content)
    user_input_string = input_tuple[0]
    return user_input_string


"""
Returns the top ten most similar dish to the user's input, along with their 
respective name, ID, description, and recipe instructions. 
"""
#EDIT BASED ON TA FEEDBACK

def top_ten(query_sim, name_ing_data, dish_latentflavors, recipes):
    index = name_ing_data[0].index(query_sim.lower())
    vect = dish_latentflavors[index,:]

    laplace = np.copy(dish_latentflavors) + 1
    pairs = np.size(laplace, 0)
    totals = np.sum(dish_latentflavors, axis = 0) + pairs
    smoothed = np.divide(laplace,totals)

    dish_sim = []
    for row in smoothed:
        dish_sim.append(np.dot(vect, row) / (LA.norm(vect) * LA.norm(row)))
    dish_cossim = np.array(dish_sim)
    top = np.argsort(dish_cossim)[-11:]
    ordered = top[::-1]
    #final = np.delete(ordered, np.where(ordered == index))
    #if np.size(final) != 10:
        #final = final[:10]  
    info = []
    with open(recipes, 'r', encoding='utf-8') as f:
        data = json.load(f)
        #for indx in final:
        for indx in ordered:
            name = data[indx]["Name"]
            #id = data[indx]["RecipeId"]
            #desc = data[indx]["Description"]
            #recipe = data[indx]["RecipeInstructions"]
            #info.append([name, id, desc, recipe])
            info.append((name, dish_sim[indx]))
    return(info)

#######################################################################################

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, "data", "flavors")
recipes_file = os.path.join(base_dir, "data", "reduced-recipe.json")

# Collect all unique flavor profiles from JSONs in the current directory
all_flavor_profiles = collect_flavor_profiles_from_directory(data_dir)

# Contains (dish_name, dish_id, ingredients)
name_ing_data = dish_id_ingr(recipes_file)

# Total Number of Dishes
ndishes = len(name_ing_data[0])

# Total Number of Flavors
nflavors = len(all_flavor_profiles)

json_dict = create_dict_from_directory(data_dir)
matrix = flavor_matrix_svd(ndishes, nflavors, name_ing_data, json_dict, all_flavor_profiles)

# U in SVD (dish against latent dimensions)
dish_latentflavors_path = os.path.join(base_dir, "data", "dish-latent-flavors-matrix.npy")
dish_latentflavors = np.load(dish_latentflavors_path)

userInput = load_user_input(filename='input_vector.txt')

final_output1 = top_ten("pulled pork", name_ing_data, dish_latentflavors, recipes_file)
for result in final_output1:
    print(result)

print("+++++++++++++++++++++++++")

final_output = top_ten("pulled pork", name_ing_data, matrix, recipes_file)
for result in final_output:
    print(result)


