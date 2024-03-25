from sklearn.metrics.pairwise import cosine_similarity
import numpy as np



def calculate_cosine_similarities(target_vector, other_vectors):
    # Concatenate target_vector (1 vector) with other_vectors (all other vectors) for simultaneous calculation
    all_vectors = np.vstack([target_vector, other_vectors])
    
    # Calculate cosine similarity
    cosine_sim_matrix = cosine_similarity(all_vectors)
    
    # The first row corresponds to the similarity of the target vector with all vectors (including itself at index 0)
    target_similarities = cosine_sim_matrix[0, 1:]

    # Sort the similarities from highest to lowest
    sorted_indices = np.argsort(-target_similarities)  # The minus sign is used to sort in descending order
    sorted_similarities = target_similarities[sorted_indices]

    return sorted_similarities

dish_flavors_mat = np.load("dish-ingredient-matrix.npy")
all_dish_cos_sim_matrix = cosine_similarity(dish_flavors_mat, dish_flavors_mat)
print(all_dish_cos_sim_matrix)
# print(all_dish_cos_sim_matrix.shape)