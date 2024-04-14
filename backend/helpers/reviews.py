import json
import csv
from collections import defaultdict

#Step 1: link all recipeids from random-recipe to average reviews; returns a dict

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
    #recipes = json.loads(recipe_data)

    # load recipe data from JSON path
    with open(recipe_data, 'r', encoding='utf-8') as f:
        recipes = json.load(f)
    
    # init a default dict to hold sum and count of ratings for each RecipeId
    ratings_dict = defaultdict(lambda: {'sum': 0, 'count': 0})
    
    # read review data from CSV and aggregate ratings
    with open(review_data, newline='', encoding='utf-8', errors='replace') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
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
            big_dict[recipe_id] = {'average_rating': average_rating, 'review_count': ratings_dict[recipe_id]['count']}
        else:
            big_dict[recipe_id] = {'average_rating': None, 'review_count': 0}  # or any other default value, maybe 0?
    
    return big_dict

#ditct = construct_reviews('backend\\data\\random-recipe.json','C:\\Users\\Kevin\\Documents\\CS4300\\finalproj\\jsonstorage\\rev.csv')
#print(ditct)

#Step 2: figure out some weighting system for the reviews, update the dict values to that weighing

def weigh_reviews(linked_data):
    """
    A weighting system for the reviews, updates the dict values to that weighing value

    Arguments
    ========
        linked_data: dict of recipes from construct_reviews() that have their respective average review rating as values

    Returns:
        another_big_dict: Dict of RecipeId:weighting format
    """
    #some method of weighing reviews. maybe use 3 stars as 1.0? and closer we go to 5 stars the closer we get to 1.5.
    #and closer we go to 1, we go closer to 0.5 weighting. What should we do about 0 stars? I think just a set value of 0.25.
    another_big_dict = {}
    for recipe_id, data in linked_data.items():
        average_rating = data['average_rating']
        if average_rating is None:
            weight = 0.25  # set value for recipes with no reviews
        elif average_rating < 3:
            weight = 0.5 + (average_rating - 1) * 0.25  # linear interpolation between 0.5 and 0.75
        else:
            weight = 1.0 + (average_rating - 3) * 0.25  # linear interpolation between 1.0 and 1.5
        another_big_dict[recipe_id] = {'average_rating': average_rating, 'review_count': data['review_count'], 'weight': weight}
    
    return another_big_dict

#weighgedede = weigh_reviews(ditct)
#print(weighgedede)

#Step 3: given a ranked list of recipes, apply our weighting of reviews onto it

def rerank_review(ranked_orig, linked_data):
    """
    Applies our weighting of reviews onto ranked_orig, returning a weighted ranked list 

    Arguments
    ========
        ranked_orig: list of list? of recipes to be weighed (should be from top_ten)
        linked_data: dict of recipes from weigh_reviews() that have their respective average review rating as values

    Returns:
        weighted: list of list? of weighed recipes
    """
    weighted = []
    for recipe in ranked_orig:
        recipe_id = recipe[1]  # second element in the list is the RecipeId?
        if recipe_id in linked_data:
            weight = linked_data[recipe_id]['weight']
            cosine_similarity = recipe[1]
            weighted_similarity = cosine_similarity * weight
            weighted_recipe = recipe.copy()
            weighted_recipe[1] = weighted_similarity
            weighted.append(weighted_recipe)
        else:
            weighted.append(recipe)
    
    # sort the list by the weighted similarity in descending order
    weighted.sort(key=lambda x: x[1], reverse=True)
    
    return weighted
    