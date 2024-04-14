import json
import csv
from collections import defaultdict

def construct_reviews(recipe_data, review_data):
    """
    Links all 'RecipeId's from a JSON object to their corresponding averaged reviews and returns them in a dict

    Arguments
    ========
        recipe_data: JSON of recipes that need a corresponding average review score
        review_data: review data in a CSV

    Returns:
        big_dict: Dict of RecipeId:average review score format
    """
    # load recipe data from JSON
    recipes = json.loads(recipe_data)
    
    # init a default dict to hold sum and count of ratings for each RecipeId
    ratings_dict = defaultdict(lambda: {'sum': 0, 'count': 0})
    
    # read review data from CSV and aggregate ratings
    with open(review_data, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            recipe_id = int(row['RecipeId'])
            rating = float(row['Rating'])
            ratings_dict[recipe_id]['sum'] += rating
            ratings_dict[recipe_id]['count'] += 1
    
    # calc average rating and create the big_dict
    big_dict = {}
    for recipe in recipes:
        recipe_id = recipe['RecipeId']
        if ratings_dict[recipe_id]['count'] > 0:
            average_rating = ratings_dict[recipe_id]['sum'] / ratings_dict[recipe_id]['count']
            big_dict[recipe_id] = average_rating
        else:
            big_dict[recipe_id] = None  # or any other default value, maybe 0?
    
    return big_dict


#Step 1: link all recipeids from random-recipe to average reviews; returns a dict

#Step 2: figure out some weighting system for the reviews, update the dict values to that weighing

#Step 3: given a ranked list of recipes, apply our weighting of reviews onto it

construct_reviews('backend\\data\\random-recipe.json','C:\\Users\\Kevin\\Documents\\CS4300\\finalproj\\jsonstorage\\rev.csv')

