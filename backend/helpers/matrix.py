import os
import json
from collections import Counter
import re
import numpy as np
import ast
from scipy.sparse.linalg import svds
from numpy import linalg as LA
from reviews import rating_count_weight


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
    input_file_path = os.path.join(base_dir,"data", "dish_id_ingr.txt")
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
    """
    lat = 15
    for (lat > 60):
        dish_latentflavors, importance, latentflavor_flavors_trans = svds(matrix, k = lat)
        np.save((os.path.join(base_dir, "data",str(k))), dish_latentflavors)
        lat = lat+5
    """
    #print(latentflavor_flavors_trans.T)
    #np.save((os.path.join(base_dir, "data","flavors-matrix.npy")), matrix)
    return(matrix)


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

# Contains (dish_name, dish_id, ingredients)
#dish_id_ingr(recipes_file, base_dir)

with open(dish_id_ingr_path, 'r') as file:
    content = file.read()
    input = ast.literal_eval(content)
name_ing_data = input

#Testing Purposes:
# Collect all unique flavor profiles from JSONs in the current directory
all_flavor_profiles = collect_flavor_profiles_from_directory(data_dir)
"""
flavor_dict = {}
for i, name in enumerate(all_flavor_profiles):
  flavor_dict[name] = i
print(flavor_dict)
"""


# Total Number of Dishes
ndishes = len(name_ing_data[0])

# Total Number of Flavors
nflavors = len(all_flavor_profiles)
"""
json_dict = create_dict_from_directory(data_dir)
matrix = flavor_matrix(ndishes, nflavors, name_ing_data, json_dict, all_flavor_profiles)
print("matrix_done")

lat = 15
while (lat < 105):
    dish_latentflavors, importance, latentflavor_flavors_trans = svds(matrix, k = lat)
    np.save((os.path.join(base_dir, "data",str(lat))), dish_latentflavors)
    np.save((os.path.join(base_dir, "data",str(lat)+"v")), latentflavor_flavors_trans.T)
    lat = lat+5
    print(lat)
print("done")
"""

"""
lat = 80
#while (lat < 105):
print(lat)
#U in SVD (dish against latent dimensions)
dish_latentflavors_path = os.path.join(base_dir, "data", str(lat)+".npy")
dish_latentflavors = np.load(dish_latentflavors_path)


#Test Purposes:
final_output1 = top_ten("Cottage Cheese Banana Sundae", name_ing_data, dish_latentflavors, recipes_file, rating_count_weight)

for each in final_output1:
    print("name ", each[0])
    #print("id ", each[3])
    print("cosine "  , each[1])
    #print("ranking " , each[2])
    #print("rating " , each[6])
    #print("count ", each[7])
    print("++++++++++++")
lat = lat+5
"""

lat = 80
#while (lat < 105):
print(lat)
#U in SVD (dish against latent dimensions)
dish_latentflavors_path = os.path.join(base_dir, "data", str(lat)+"v.npy")
v = np.load(dish_latentflavors_path)

word_to_index = {'absolute': 0, 'acacia': 1, 'acetic': 2, 'acetoin': 3, 'acetone': 4, 
                 'acetophenone': 5, 'acid': 6, 'acidic': 7, 'acrid': 8, 'acrylate': 9, 
                 'acrylic': 10, 'alcohol': 11, 'alcoholic': 12, 'aldehydic': 13, 'alkaline': 14, 
                 'alkane': 15, 'alliaceous': 16, 'allspice': 17, 'almond': 18, 'almond shell': 19,
                 'amber': 20, 'ambergris': 21, 'amine': 22, 'ammonia': 23, 'ammoniacal': 24, 
                 'angelica': 25, 'animal': 26, 'anise': 27, 'aniseed': 28, 'anisic': 29, 'apple': 30, 
                 'apple peel': 31, 'apple skin': 32, 'apricot': 33, 'aromatic': 34, 'arrack': 35, 
                 'asprin': 36, 'bacon': 37, 'baked': 38, 'balsam': 39, 'balsamic': 40, 'banana': 41, 
                 'banana peel': 42, 'barley': 43, 'basil': 44, 'bay oil': 45, 'bean': 46, 'beany': 47, 
                 'beef': 48, 'beefy': 49, 'beer': 50, 'beet': 51, 'bell': 52, 'benzaldehyde': 53, 
                 'benzyl acetate': 54, 'benzyl propionate': 55, 'bergamot': 56, 'berry': 57, 'biscuit': 58, 
                 'bitter': 59, 'bitter almond': 60, 'black currant': 61, 'black tea': 62, 'blackberry': 63, 
                 'blackcurrant': 64, 'bland': 65, 'bloody': 66, 'blossom': 67, 'blueberry': 68, 'boiled shrimp': 69, 
                 'boiled vegetable': 70, 'bois de rose': 71, 'borneol': 72, 'bouillon': 73, 'box tree': 74, 'brandy': 75, 
                 'bread': 76, 'bread crust': 77, 'bready': 78, 'broccoli': 79, 'broom': 80, 'brown': 81, 'buchu': 82, 
                 'burnt': 83, 'burnt almonds': 84, 'burnt sugar': 85, 'butter': 86, 'butterscotch': 87, 'buttery': 88, 
                 'butyric': 89, 'cabbage': 90, 'cadaverous': 91, 'camomile': 92, 'camphor': 93, 'camphoraceous': 94, 
                 'camphoreous': 95, 'cananga': 96, 'candy': 97, 'cantaloupe': 98, 'caramel': 99, 'caramellic': 100, 
                 'caraway': 101, 'cardboard': 102, 'carnation': 103, 'carrot': 104, 'cashew': 105, 'cassia': 106, 
                 'cassie': 107, 'castoreum': 108, 'cat': 109, 'cat-urine': 110, 'catty': 111, 'cauliflower': 112, 
                 'cedar': 113, 'cedarleaf': 114, 'cedarwood': 115, 'celery': 116, 'cereal': 117, 'chamomile': 118, 
                 'cheese': 119, 'cheesy': 120, 'chemical': 121, 'cherry': 122, 'chicken': 123, 'chip': 124, 'chocolate': 125,
                 'chrysanthemum': 126, 'cinnamic': 127, 'cinnamon': 128, 'cinnamyl': 129, 'cistus': 130, 'citral': 131, 
                 'citric': 132, 'citrus': 133, 'citrus peel': 134, 'civet': 135, 'clam': 136, 'clary': 137, 'clean': 138, 
                 'clean cloth': 139, 'clean clothes': 140, 'clove': 141, 'clover': 142, 'cocoa': 143, 'coconut': 144, 
                 'coffee': 145, 'cognac': 146, 'cooked': 147, 'cooked beef juice': 148, 'cooked potato': 149, 'cool': 150, 
                 'cooling': 151, 'coriander': 152, 'corn': 153, 'cortex': 154, 'cotton': 155, 'cotton candy': 156, 
                 'coumarin': 157, 'coumarinic': 158, 'cranberry': 159, 'cream': 160, 'creamy': 161, 'creosote': 162, 
                 'cresol': 163, 'crushed bug': 164, 'cucumber': 165, 'cucumber skin': 166, 'cultured dairy': 167, 
                 'cumin': 168, 'cuminseed': 169, 'curry': 170, 'cut grass': 171, 'cut privet': 172, 'cyclamen': 173, 
                 'dairy': 174, 'damascone': 175, 'decomposing cabbage': 176, 'deep': 177, 'delicate': 178, 'dewy': 179, 
                 'dill': 180, 'diphenyl oxide': 181, 'dirty': 182, 'diterpene': 183, 'dried berry': 184, 'dried raspberry': 185, 
                 'dry': 186, 'dust': 187, 'dusty': 188, 'earth': 189, 'earthy': 190, 'egg': 191, 'ester': 192, 'estery': 193, 
                 'ether': 194, 'ethereal': 195, 'ethyl benzoate': 196, 'eucalyptus': 197, 'eugenol': 198, 'extremely sweet': 199, 
                 'faint': 200, 'fat': 201, 'fatty': 202, 'fecal': 203, 'feet': 204, 'fenchyl': 205, 'fennel': 206, 'fenugreek': 207, 
                 'fermented': 208, 'filbert': 209, 'fir': 210, 'fir needle': 211, 'fish': 212, 'fishy': 213, 'flat': 214, 'floral': 215, 
                 'flower': 216, 'foliage': 217, 'formyl': 218, 'fragrant': 219, 'fresh': 220, 'fresh air': 221, 'fried': 222, 'fruit': 223, 
                 'fruity': 224, 'fungal': 225, 'furfural': 226, 'fusel': 227, 'galbanum': 228, 'gardenia': 229, 'garlic': 230, 'gasoline': 231, 
                 'gassy': 232, 'genet': 233, 'geranium': 234, 'ginger': 235, 'glue': 236, 'gooseberry': 237, 'grain': 238, 'grape': 239, 
                 'grape skin': 240, 'grapefruit': 241, 'grapefruit peel': 242, 'grass': 243, 'grassy': 244, 'gravy': 245, 'greasy': 246, 
                 'green': 247, 'green bean': 248, 'green pepper': 249, 'green tea': 250, 'guaiacol': 251, 'guaiacwood': 252, 'ham': 253, 
                 'harsh': 254, 'hawthorn': 255, 'hawthorne': 256, 'hay': 257, 'hazelnut': 258, 'heather': 259, 'heavy': 260, 'heliotrope': 261, 
                 'heliotropin': 262, 'herb': 263, 'herbaceous': 264, 'herbal': 265, 'honey': 266, 'honeydew': 267, 'honeysuckle': 268, 
                 'hop_oil': 269, 'horseradish': 270, 'hot milk': 271, 'hummus': 272, 'hyacinth': 273, 'incense': 274, 'indole': 275, 
                 'intensely': 276, 'ionone': 277, 'iris': 278, 'jam': 279, 'jammy': 280, 'jasmin': 281, 'jasmine': 282, 'juicy': 283, 
                 'ketonic': 284, 'kiwi': 285, 'labdanum': 286, 'lactonic': 287, 'lamb': 288, 'lard': 289, 'laundered cloths': 290, 
                 'laundry': 291, 'lavender': 292, 'leaf': 293, 'leafy': 294, 'leather': 295, 'leathery': 296, 'leaves': 297, 
                 'leek': 298, 'lemon': 299, 'lemon peel': 300, 'lemongrass': 301, 'lettuce': 302, 'licorice': 303, 'light': 304, 
                 'lilac': 305, 'lily': 306, 'lime': 307, 'linalool': 308, 'linden': 309, 'logenberry': 310, 'lovage': 311, 
                 'low': 312, 'magnolia': 313, 'mahogany': 314, 'malt': 315, 'malty': 316, 'mandarin': 317, 'mango': 318, 
                 'maple': 319, 'maple syrup': 320, 'marigold': 321, 'marshmallow': 322, 'matches': 323, 'meat': 324, 'meat broth': 325, 
                 'meaty': 326, 'medical': 327, 'medicinal': 328, 'medicine': 329, 'melon': 330, 'melon rind': 331, 'menthol': 332, 
                 'mentholic': 333, 'mesquite': 334, 'metal': 335, 'metallic': 336, 'mignonette': 337, 'mild': 338, 'mildew': 339, 
                 'milk': 340, 'milky': 341, 'mimosa': 342, 'mint': 343, 'minty': 344, 'molasses': 345, 'mold': 346, 'moldy': 347, 
                 'moss': 348, 'mossy': 349, 'moth ball': 350, 'mothball': 351, 'mouldy': 352, 'mousy': 353, 'muguet': 354, 
                 'mushroom': 355, 'musk': 356, 'musky': 357, 'must': 358, 'mustard': 359, 'musty': 360, 'myrcene': 361, 
                 'myrrh': 362, 'naphthalic': 363, 'naphthelene': 364, 'naphthyl': 365, 'narcissus': 366, 'natural': 367,
                 'neroli': 368, 'new mown hay': 369, 'nitrile': 370, 'nut': 371, 'nut skin': 372, 'nutmeg': 373, 'nutty': 374, 
                 'oakmoss': 375, 'ocimene': 376, 'odorless': 377, 'oil': 378, 'oily': 379, 'old paper': 380, 'old wood': 381, 
                 'onion': 382, 'opoponax': 383, 'orange': 384, 'orange blossom': 385, 'orange flower': 386, 'orange peel': 387, 
                 'orchid': 388, 'oriental': 389, 'orris': 390, 'others': 391, 'outdoor': 392, 'overripe fruit': 393, 'ozone': 394, 
                 'paint': 395, 'painty': 396, 'papaya': 397, 'paper': 398, 'parsley': 399, 'passion fruit': 400, 'pastry': 401, 
                 'patchouli': 402, 'pea': 403, 'peach': 404, 'peanut': 405, 'peanut butter': 406, 'pear': 407, 'pear skin': 408,
                 'peely': 409, 'penetrating': 410, 'peony': 411, 'pepper': 412, 'peppermint': 413, 'peppery': 414, 'petal': 415,
                 'petitgrain': 416, 'phenol': 417, 'phenolic': 418, 'pine': 419, 'pine needle': 420, 'pineapple': 421, 
                 'pistachio': 422, 'plant': 423, 'plastic': 424, 'pleasant': 425, 'plum': 426, 'popcorn': 427, 'pork': 428, 
                 'potato': 429, 'powdery': 430, 'powerful': 431, 'privet': 432, 'prune': 433, 'pulpy': 434, 'pumpkin': 435, 
                 'pungent': 436, 'putrid': 437, 'pyridine': 438, 'radish': 439, 'rancid': 440, 'raspberry': 441, 'raw': 442,
                 'red fruit': 443, 'red hots': 444, 'red rose': 445, 'repulsive': 446, 'resin': 447, 'resinous': 448, 
                 'rhubarb': 449, 'ripe': 450, 'ripe apricot': 451, 'roast': 452, 'roast beef': 453, 'roasted': 454, 
                 'roasted meat': 455, 'roasted nut': 456, 'roasted nuts': 457, 'roasted peanuts': 458, 'root': 459, 
                 'rooty': 460, 'roquefort cheese': 461, 'rose': 462, 'rose acetate': 463, 'rose bud': 464, 
                 'rose dried': 465, 'rose flower': 466, 'rose oxide': 467, 'rose water': 468, 'rosemary': 469,
                 'rosy': 470, 'rotten': 471, 'rotting': 472, 'rubber': 473, 'rubbery': 474, 'rum': 475, 'rummy': 476, 
                 'saffron': 477, 'sandalwood': 478, 'sappy': 479, 'sarsaparilla': 480, 'sassafrass': 481, 'sausage': 482, 
                 'savory': 483, 'scallion': 484, 'seaweed': 485, 'seedy': 486, 'sharp': 487, 'shellfish': 488, 'shrimp': 489, 
                 'sickening': 490, 'skunky': 491, 'slightly fruity': 492, 'slightly rose': 493, 'slightly waxy': 494, 
                 'smoke': 495, 'smoked': 496, 'smoky': 497, 'soap': 498, 'soapy': 499, 'soft': 500, 'soil': 501, 
                 'solvent': 502, 'soup': 503, 'sour': 504, 'soy': 505, 'soybean': 506, 'spearmint': 507, 'spice': 508, 
                 'spicy': 509, 'stem': 510, 'stinky': 511, 'storax': 512, 'straw': 513, 'strawberry': 514, 'strong': 515, 
                 'styrax': 516, 'styrene': 517, 'sugar': 518, 'sulfur': 519, 'sulfurous': 520, 'sulfury': 521, 'sweat': 522, 
                 'sweaty': 523, 'sweet': 524, 'sweet corn': 525, 'sweet-like': 526, 'syrup': 527, 'taco': 528, 'tallow': 529, 
                 'tangy': 530, 'tar': 531, 'tarragon': 532, 'tarry': 533, 'tart': 534, 'tea': 535, 'terpene': 536, 'terpenic': 537, 
                 'terpentine': 538, 'terpineol': 539, 'thuja': 540, 'thujone': 541, 'thyme': 542, 'thymol': 543, 'toasted': 544, 
                 'tobacco': 545, 'toffee': 546, 'toluene': 547, 'tomato': 548, 'tomato leaf': 549, 'tonka': 550, 'tropica': 551, 
                 'tropical': 552, 'truffle': 553, 'tuberose': 554, 'turnup': 555, 'turpentine': 556, 'tutti frutti': 557, 
                 'unpleasant': 558, 'unripe banana': 559, 'unripe fruit': 560, 'unripe plum': 561, 'urine': 562, 'valerian': 563,
                 'vanilla': 564, 'vanillin': 565, 'vegetable': 566, 'very mild': 567, 'very slight': 568, 'very strong': 569, 
                 'vinegar': 570, 'vinous': 571, 'violet': 572, 'violet-leaf': 573, 'walnut': 574, 'warm': 575, 'wasabi': 576, 
                 'watercress': 577, 'watermelon': 578, 'watery': 579, 'wax': 580, 'waxy': 581, 'weak': 582, 'weak spice': 583, 
                 'weedy': 584, 'wet': 585, 'whiskey': 586, 'wild': 587, 'wine': 588, 'wine-lee': 589, 'wine_like': 590, 
                 'winey': 591, 'wintergreen': 592, 'wood': 593, 'woody': 594, 'yeast': 595, 'yeasty': 596, 'ylang': 597};
index_to_word = {i:t for t,i in word_to_index.items()}
words_compressed = v
k=80
for i in range(k):
    print("Top words in dimension", i)
    dimension_col = words_compressed[:,i].squeeze()
    asort = np.argsort(-dimension_col)
    print([index_to_word[i] for i in asort[:10]])
    print()
