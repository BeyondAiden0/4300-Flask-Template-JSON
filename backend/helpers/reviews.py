import ast
import os
import json
from collections import defaultdict

current_script_dir = os.path.dirname(os.path.abspath(__file__))
recipe_path = os.path.normpath(os.path.join(current_script_dir, '..', 'data', 'random-recipe.json'))
reviews_path = os.path.normpath(os.path.join(current_script_dir, '..', 'data', 'reviews.json'))
dish_id_ingr_path = os.path.normpath(os.path.join(current_script_dir, '..', 'data', 'dish_id_ingr.txt'))


"""
Links all 'RecipeId's from a JSON object to their corresponding averaged reviews, then
weighs the reviews, and updates the dict values to that weighing value

Parameter:
    recipe_data (str): The path to the JSON file containing the recipes data.

Returns:
    final_dict: Dict of dict in RecipeId:{average rating, review count, weight} format
"""

def better_reviews(recipe_data):
    final_dict = {}
    with open(recipe_data, 'r', encoding='utf-8') as jsonfile:
        reviews = json.load(jsonfile)

        for review in reviews:
            recipe_id = int(review['RecipeId'])

            if review['ReviewCount'] is None:
                rating = None
                count = 0
            else:
                rating = review['AggregatedRating']
                count = review['ReviewCount']

            if count == 0:
                count_weight = 0.005
            elif count <= 5:
                count_weight = 0.01
            elif count < 10:
                count_weight = 0.015
            else:
                count_weight = 0.02

            if rating is None:
                weight = 0.25 + count_weight + 1 
            elif rating < 3:
                weight = (0.5 + (rating - 1) * 0.25) + count_weight + 1  
            else:
                weight = (1.0 + (rating - 3) * 0.25) + count_weight + 1  

            final_dict[recipe_id] = {'average_rating': rating, 'review_count': count, 'weight': weight}

    return final_dict

testweight = better_reviews(recipe_path)


"""
Links all 'RecipeId's from a JSON object to their corresponding averaged reviews and returns 
them in a dict

Parameters:
    recipe_data (str): The path to the JSON file containing the recipes data.

    review_data (str): The path to the JSON file containing the review data.

Returns:
    big_dict: Dict of dict in RecipeId:{average review score, number of reviews} format
"""

def construct_reviews(recipe_data, review_data):
    with open(recipe_data, 'r', encoding='utf-8') as f:
        recipes = json.load(f)
    
    ratings_dict = defaultdict(lambda: {'sum': 0, 'count': 0})
    
    with open(review_data, 'r', encoding='utf-8') as jsonfile:
        reviews = json.load(jsonfile)
        for review in reviews.values():
            recipe_id = int(review['RecipeId'])
            rating = float(review['Rating'])
            ratings_dict[recipe_id]['sum'] += rating
            ratings_dict[recipe_id]['count'] += 1
    
    big_dict = {}
    for recipe in recipes:
        recipe_id = recipe['RecipeId']
        if ratings_dict[recipe_id]['count'] > 0:
            average_rating = ratings_dict[recipe_id]['sum'] / ratings_dict[recipe_id]['count']
            big_dict[recipe_id] = {'average_rating': average_rating, 'review_count': 
                                   ratings_dict[recipe_id]['count']}
        else:
            big_dict[recipe_id] = {'average_rating': None, 'review_count': 0}  
    
    return big_dict

ditct = construct_reviews(recipe_path,reviews_path)


"""
A weighting system for the reviews, updates the dict values to that weighing value

Parameter:
    linked_data: dict of recipes from construct_reviews() that have their respective average 
    review rating as values

Returns:
    another_big_dict: Dict of dict in RecipeId:{average rating, review count, weight} format
"""

def weigh_reviews(linked_data):
    another_big_dict = {}
    for recipe_id, data in linked_data.items():
        average_rating = data['average_rating']
        if average_rating is None:
            weight = 0.25  
        elif average_rating < 3:
            weight = 0.5 + (average_rating - 1) * 0.25 
        else:
            weight = 1.0 + (average_rating - 3) * 0.25 
        another_big_dict[recipe_id] = {'average_rating': average_rating, 'review_count': 
                                       data['review_count'], 'weight': weight}
    
    return another_big_dict


"""
Returns a list of list containing three sublists (ratings, counts, and weights), which are
ordered according to 'id_ordered'.

Parameters:
    id_rating_dict (dict): A dictionary where keys are dish ids and values are dictionaries
    containing 'average_rating', 'review_count', and 'weight'.

    id_ordered (list): A list of dish ids in the desired order.

Returns:
    rating_count_weight (list of lists): A list containing three sublists - ratings, counts, and weights -
    ordered according to 'id_ordered'.

"""

def rerank(id_rating_dict, id_ordered):
    rating_count_weight = []
    rating = []
    count = []
    weight = []
    for indx in id_ordered:
        rating.append(id_rating_dict[indx]["average_rating"])
        count.append(id_rating_dict[indx]["review_count"])
        weight.append(id_rating_dict[indx]["weight"])
    rating_count_weight.append(rating)
    rating_count_weight.append(count)
    rating_count_weight.append(weight)
    return(rating_count_weight)


with open(dish_id_ingr_path, 'r') as file:
    content = file.read()
    input = ast.literal_eval(content)
name_ing_data = input
rating_count_weight = rerank(testweight,name_ing_data[1])


"""
Applies our weighting of reviews onto ranked_orig, returning a weighted ranked list 

Parameter
    ranked_orig: list of list? of recipes to be weighed (should be from top_ten)

    linked_data: dict of recipes from weigh_reviews() that have their respective average 
    review rating as values

Returns:
    weighted: list of list? of weighed recipes
"""

def rerank_review(ranked_orig, linked_data):
    weighted = []
    for recipe in ranked_orig:
        recipe_id = recipe[2] 
        if recipe_id in linked_data:
            weight = linked_data[recipe_id]['weight']
            cosine_similarity = recipe[1]
            weighted_similarity = cosine_similarity * weight
            weighted_recipe = recipe.copy()
            weighted_recipe[1] = weighted_similarity
            weighted.append(weighted_recipe)
        else:
            weighted.append(recipe)
    
    weighted.sort(key=lambda x: x[1], reverse=True)
    
    return weighted
    