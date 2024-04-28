import json

with open('../data/reduced-recipe.json', 'r') as file:
    recipes = json.load(file)

transformed_data = {"recipes": [], "reviews": []}

for recipe in recipes:
    recipe_info = {
        "RecipeId": recipe["RecipeId"],
        "Name": recipe["Name"],
        "AuthorName": recipe["AuthorName"],
        "Description": recipe["Description"],
        "RecipeInstructions": recipe["RecipeInstructions"],
    }
    review_info = {
        "RecipeId": recipe["RecipeId"],
        "AggregatedRating": recipe["AggregatedRating"],
    }

    transformed_data["recipes"].append(recipe_info)
    transformed_data["reviews"].append(review_info)

with open('../init.json', 'w') as outfile:
    json.dump(transformed_data, outfile, indent=4)

print("Transformation complete. The data is saved in 'transformed_recipes.json'.")
