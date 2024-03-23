import os
import json
from collections import Counter
import re
import numpy as np

dir = "backend/data/flavors"
recipes = "backend/data/random-recipe.json"


"""
takes the json directory, and gives a list of all the jsons in a dict, in the form
of {"ingredient-name":"json-file-name"} ex: {"eggs":"0 eggs.json"}
"""
def create_dict_from_directory(directory):
    dict_files = {}
    contents = os.listdir(directory)
    for item in contents:
        if item.endswith('.json'):
            key = (item.split(' ', 1)[1].rsplit('.', 1)[0]).lower()
            dict_files[key] = item
    return dict_files



def get_flavor_profiles(json_file):
    # Initialize an empty set to store the flavor profiles
    flavor_profiles = set()

    # Open and load the JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Iterate over the 'molecules' list in the data
    for molecule in data['molecules']:
        # If 'fooddb_flavor_profile' key exists in the molecule
        if 'flavor_profile' in molecule:
            # Split the flavor profiles by '@' and add them to the set
            flavor_profiles.update(molecule['flavor_profile'].split('@'))

    # Remove the empty string if it exists
    flavor_profiles.discard('')

    # Return the set of flavor profiles
    return flavor_profiles



"""
takes a directory of json files, and combines it all into one set of all the flavors
"""
def collect_flavor_profiles_from_directory(directory):
    # Initialize an empty set to store all unique flavor profiles
    all_flavor_profiles = set()

    contents = os.listdir(directory)
    for item in contents:
        if item.endswith('.json'):
            # Get the flavor profiles from the current JSON file
            flavor_profiles = get_flavor_profiles(os.path.join(directory, item))
            # Add them to the set of all flavor profiles
            all_flavor_profiles.update(flavor_profiles)

    # Convert the set to a list, remove the empty string, and sort it alphabetically
    all_flavor_profiles = sorted([fp for fp in all_flavor_profiles if fp])

    return all_flavor_profiles

# Example usage: Collect all unique flavor profiles from JSONs in the current directory
all_flavor_profiles = collect_flavor_profiles_from_directory(dir)

# print(all_flavor_profiles)



def extract_keywords(json_file):
    keyword_counts = {}

    with open(json_file, 'r') as f:
        data = json.load(f)
        for molecule in data['molecules']:
            if 'flavor_profile' in molecule:
                keywords = molecule['flavor_profile'].split('@')
                for keyword in keywords:
                    if keyword: # ignore empty str
                        if keyword in keyword_counts:
                            keyword_counts[keyword] += 1
                        else:
                            keyword_counts[keyword] = 1

    return dict(sorted(keyword_counts.items(), key=lambda item: item[1], reverse=True))

"""
creato the flavor dict where the key is the flavor and the value is the count of the flavors
returns dict
"""
def merge_counts(json_files):
    
    merged_keyword_counts = Counter()

    for json_file in json_files:
        keyword_counts = extract_keywords("backend/data/flavors/"+str(json_file))
        merged_keyword_counts.update(keyword_counts)

    merged_keyword_counts = dict(sorted(merged_keyword_counts.items(), key=lambda item: item[1], reverse=True))
    return merged_keyword_counts


def compare_dict_with_flavor_profiles(dict_X, all_flavor_profiles):
    # Initialize a dictionary with all flavor profiles as keys and 0 as values
    flavor_profile_counts = dict.fromkeys(all_flavor_profiles, 0)

    # Iterate over the items in dict_X
    for key, value in dict_X.items():
        # If the key exists in the flavor profiles
        if key in flavor_profile_counts:
            # Update the count in the flavor profiles dictionary
            flavor_profile_counts[key] += value

    return flavor_profile_counts

# Example usage:
#print(compare_dict_with_flavor_profiles(bbq, all_flavor_profiles))

def dish_id_ingr (recipes):
  dish_id = []
  ingr = []
  with open(recipes, 'r',encoding='utf-8') as f:
    data = json.load(f)
    for dish in data:
      entry = (dish["Name"], dish["RecipeId"])
      dish_id.append(entry)
      ingr.append(((re.findall(r'"(.*?)"', dish["RecipeIngredientParts"].casefold()))))
  return (dish_id, ingr)

name_ing_data = dish_id_ingr(recipes)


ndishes = len(name_ing_data[0])
nflavors = len(all_flavor_profiles)
json_dict = create_dict_from_directory(dir)
matrix = np.zeros((ndishes,nflavors),dtype=int)

row = 0

print(nflavors)
print(ndishes)
# print(json_dict.keys())
# print("Egg" in json_dict.keys())
for ingredient_list in name_ing_data[1]:
  acc = []
  for ingredient in ingredient_list:
    
    if ingredient.lower() in json_dict.keys():
      
      acc.append(json_dict[ingredient.lower()])
  flavors = merge_counts(acc)

  for flavor in flavors.keys():
    ind = all_flavor_profiles.index(flavor)
    val = flavors[flavor]
    matrix[row][ind] = val
  row +=1

np.save("dish-ingredient-matrix.npy",matrix)
print(matrix)