from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os


def calculate_cosine_similarities(target_vector, other_vectors):
    all_vectors = np.vstack([target_vector, other_vectors])
    cosine_sim_matrix = cosine_similarity(all_vectors)
    target_similarities = cosine_sim_matrix[0, 1:]
    sorted_indices = np.argsort(-target_similarities)
    sorted_similarities = target_similarities[sorted_indices]
    return sorted_similarities

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dish_flavors_mat_path = os.path.join(base_dir, "data", "dish-ingredient-matrix.npy")
dish_flavors_mat = np.load(dish_flavors_mat_path)
all_dish_cos_sim_matrix = cosine_similarity(dish_flavors_mat, dish_flavors_mat)