import ast
import os
import json
from collections import defaultdict

########## PATHS ##########
current_script_dir = os.path.dirname(os.path.abspath(__file__))
    
# Construct the paths to the data files
recipe_path = os.path.normpath(os.path.join(current_script_dir, '..', 'data', 'random-recipe.json'))
reviews_path = os.path.normpath(os.path.join(current_script_dir, '..', 'data', 'reviews.json'))
dish_id_ingr_path = os.path.normpath(os.path.join(current_script_dir, '..', 'data', 'dish_id_ingr.txt'))

def better_reviews(recipe_data):
    """
    Links all 'RecipeId's from a JSON object to their corresponding averaged reviews, then
    weighs the reviews, and updates the dict values to that weighing value

    Arguments
    ========
        recipe_data (str): The path to the JSON file containing the recipes data.

    Returns:
        final_dict: Dict of dict in RecipeId:{average rating, review count, weight} format
    """
    final_dict = {}
    # read recipe and review data from json and aggregate ratings
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
            
            if rating is None:
                weight = 0.25 * count + 1 # set value of 1.25*count for recipes with no reviews
            elif rating < 3:
                weight = (0.5 + (rating - 1) * 0.25) * count + 1 # linear interpolation between 1.5 and 1.75 times count
            else:
                weight = (1.0 + (rating - 3) * 0.25) * count + 1 # linear interpolation between 2.0 and 2.5 times count

            final_dict[recipe_id] = {'average_rating': rating, 'review_count': count, 'weight': weight}

    return final_dict

testweight = better_reviews(recipe_path)
print(testweight)

#Step 1: link all recipeids from random-recipe to average reviews; returns a dict

def construct_reviews(recipe_data, review_data):
    """
    Links all 'RecipeId's from a JSON object to their corresponding averaged reviews and returns them in a dict

    Arguments
    ========
        recipe_data (str): The path to the JSON file containing the recipes data.
        review_data (str): The path to the JSON file containing the review data.

    Returns:
        big_dict: Dict of dict in RecipeId:{average review score, number of reviews} format
    """
    # load recipe data from JSON
    #recipes = json.loads(recipe_data)

    # load recipe data from JSON path
    with open(recipe_data, 'r', encoding='utf-8') as f:
        recipes = json.load(f)
    
    # init a default dict to hold sum and count of ratings for each RecipeId
    ratings_dict = defaultdict(lambda: {'sum': 0, 'count': 0})
    
    # read review data from json and aggregate ratings
    with open(review_data, 'r', encoding='utf-8') as jsonfile:
        reviews = json.load(jsonfile)
        for review in reviews.values():
            recipe_id = int(review['RecipeId'])
            rating = float(review['Rating'])
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
#ditct = construct_reviews('backend\\data\\random-recipe.json','backend\\data\\reviews.json')
#print(ditct)

#def checkEqual(L1, L2):
#    return len(L1) == len(L2) and sorted(L1) == sorted(L2)

#print(len(list(ditct.keys())))
#print(len(matrix.name_ing_data[1]))
#print(checkEqual(list(ditct.keys()), matrix.name_ing_data[1]))
#print(ditct.keys())
#print(matrix.name_ing_data[1])

#Step 2: figure out some weighting system for the reviews, update the dict values to that weighing

def weigh_reviews(linked_data):
    """
    A weighting system for the reviews, updates the dict values to that weighing value

    Arguments
    ========
        linked_data: dict of recipes from construct_reviews() that have their respective average review rating as values

    Returns:
        another_big_dict: Dict of dict in RecipeId:{average rating, review count, weight} format
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
rating_count_weight = rerank(weighgedede,name_ing_data[1])

id = name_ing_data[1].index(184953)
print(name_ing_data[0][id])
print(name_ing_data[1][id])
print(weighgedede[184953])

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
    
    # sort the list by the weighted similarity in descending order
    weighted.sort(key=lambda x: x[1], reverse=True)
    
    return weighted
    