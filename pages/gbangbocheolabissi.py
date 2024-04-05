import math
import streamlit as st

from typing import Callable, Optional

import pandas as pd
import csv
import io

# Type aliases
UserRatings = list[Optional[int]]
Dataset = list[UserRatings]


# Functions
def ratings_avg(ratings: UserRatings) -> float:
    elements_sum = 0
    elements_counter = 0

    for rating in ratings:
        if rating is not None:
            elements_sum += rating
            elements_counter += 1

    return elements_sum / elements_counter


def same_dimensions(r1: UserRatings, r2: UserRatings) -> bool:
    for i in range(0, len(r1)):
        if r1[i] is None and r2[i] is not None:
            return False

        if r1[i] is not None and r2[i] is None:
            return False

    return True


def format_user(idx: int) -> str:
    return f"User n° {idx + 1}"


def convert_to_dataframe(dataset: Dataset):
    return pd.DataFrame(
        dataset,
        index=[f"User n° {i + 1}" for i in range(len(dataset))],
        columns=[f"Movie n° {j + 1}" for j in range(len(dataset[0]))]
    )


def clean_dataset(dataset: Dataset) -> Dataset:
    return [[None if r is None or r != r else int(r) for r in user_ratings] for user_ratings in dataset]


def join_readable(to_join) -> str:
    if len(to_join) == 0:
        return ''

    if len(to_join) == 1:
        return str(to_join[0])

    all_but_last_joined = ', '.join([str(x) for x in to_join][:-1])
    last = str(to_join[-1])
    return ' and '.join([all_but_last_joined, last])


def load_dataset_from_csv(file) -> Dataset:
    uploaded_string = io.StringIO(file.getvalue().decode("utf-8"))
    csv_reader = csv.reader(uploaded_string)
    data = []
    for row in csv_reader:
        new_row = []
        for col in row:
            if col == '':
                new_row.append(None)
            else:
                new_row.append(int(col))
        data.append(new_row)

    return data


def norm(ratings: UserRatings) -> float:
    total = 0

    for rating in ratings:
        if rating is not None:
            total += rating ** 2
    return math.sqrt(total)


def dot(r1: UserRatings, r2: UserRatings) -> int:
    total = 0
    for i in range(0, len(r1)):
        if r1[i] is not None and r2[i] is not None:
            total += r1[i] * r2[i]

    return total


def adjusted_cosine_similarity(r1: UserRatings, r2: UserRatings) -> float:
    r1_avg = ratings_avg(r1)
    r2_avg = ratings_avg(r2)
    diff_for_common_elements = 0
    r1_sum_squared = 0
    r2_sum_squared = 0

    for i in range(1, len(r1)):
        if r1[i] is not None and r2[i] is not None:
            diff_for_common_elements += (r1[i] - r1_avg) * (r2[i] - r2_avg)
            r1_sum_squared += (r1[i] - r1_avg) ** 2
            r2_sum_squared += (r2[i] - r2_avg) ** 2

    product_of_squared_differences = math.sqrt(r1_sum_squared) * math.sqrt(r2_sum_squared)

    if product_of_squared_differences == 0:
        product_of_squared_differences = 1

    return diff_for_common_elements / product_of_squared_differences


def cosine_similarity(r1: UserRatings, r2: UserRatings) -> float:
    return dot(r1, r2) / (norm(r1) * norm(r2))


def minkowski_distance(p: int, r1: UserRatings, r2: UserRatings) -> float:
    total = 0

    for i in range(0, len(r1)):
        if r1[i] is not None and r2[i] is not None:
            total += math.fabs(r1[i] - r2[i]) ** p

    return total ** (1 / p)


def manhattan_distance(r1: UserRatings, r2: UserRatings) -> float:
    return minkowski_distance(1, r1, r2)


def euclidian_distance(r1: UserRatings, r2: UserRatings) -> float:
    return minkowski_distance(2, r1, r2)


def jaccard_similarity(r1: UserRatings, r2: UserRatings) -> float:
    set1 = set(r1)
    set2 = set(r2)
    inter = set1.intersection(set2)
    union = set1.union(set2)
    return len(inter) / len(union)


def map_similarities(dataset: Dataset, index: int, func: Callable[[UserRatings, UserRatings], float]) -> list[float]:
    to_compare = dataset[index]
    return [func(to_compare, x) for x in dataset]


def get_top_indexes(n: int, similarities: list[float], exclude_index: int) -> list[int]:
    indexes = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)
    return [i for i in indexes if i != exclude_index][:n]


def estimate_ratings(dataset: Dataset, top_indexes: list[int], similarities: list[float]) -> list[float]:
    # For each similar user, for each item multiply by the similarity at index, add to a list
    # for each column, sum and divide by the sum of similarities at these top_indexes

    results = [0] * len(dataset[0])
    total_similarities = 0

    for index in top_indexes:
        total_similarities += similarities[index]

    for i in range(len(dataset)):
        if i in top_indexes:
            for j in range(len(dataset[i])):
                if dataset[i][j] is not None:
                    results[j] += dataset[i][j] * similarities[i]

    for i in range(len(results)):
        if total_similarities == 0:
            results[i] = 0
        else:
            results[i] = round(results[i] / total_similarities, 2)

    return results


# Constants

ADJUSTED_COSINE_SIMILARITY = 'ADJUSTED COSINE SIMILARITY'
COSINE_SIMILARITY = 'COSINE_SIMILARITY'
MANHATTAN_DISTANCE = 'MANHATTAN_DISTANCE'
EUCLIDIAN_DISTANCE = 'EUCLIDIAN_DISTANCE'
JACCARD_SIMILARITY = 'JACCARD_SIMILARITY'

# Labels for the select
ADJUSTED_COSINE_SIMILARITY_LABEL = ('Adjusted cosine similarity (may not perform well when the data is sparse or when '
                                    'there are many missing values)')
COSINE_SIMILARITY_LABEL = 'Cosine similarity (may not be appropriate when some values are missing)'
MANHATTAN_DISTANCE_LABEL = 'Manhattan distance (may not be appropriate when some values are missing)'
EUCLIDIAN_DISTANCE_LABEL = 'Euclidian distance (may not be appropriate when some values are missing)'
JACCARD_SIMILARITY_LABEL = 'Jaccard similarity (more appropriate when there is not a numeric scale for ratings)'

# Descriptions of the given similarities
ADJUSTED_COSINE_SIMILARITY_DESCRIPTION = ("Adjusted cosine similarity is a method used in recommendation systems to"
                                          "determine the similarity between two users or items. It adjusts for the fact"
                                          "that users may rate items on different scales by subtracting each user's "
                                          "average rating from their ratings before computing similarity")
COSINE_SIMILARITY_DESCRIPTION = ('Measures the cosine of the angle between two non-zero vectors. It is a measure of '
                                 'similarity between two vectors in a multidimensional space and is often used in '
                                 'collaborative filtering to recommend items based on user preferences.')
MANHATTAN_DISTANCE_DESCRIPTION = ('Also known as city block distance or L1 norm, it calculates the distance between '
                                  'two points in a grid based on the sum of the absolute differences of their '
                                  'coordinates. In collaborative filtering, it can be used to measure similarity '
                                  'between users or items')
EUCLIDIAN_DISTANCE_DESCRIPTION = ('Represents the length of the shortest path between two points in a Euclidean space. '
                                  'It is the most straightforward way of representing the distance between two points '
                                  'and is commonly used in collaborative filtering to measure similarity')
JACCARD_SIMILARITY_DESCRIPTION = ('Measures the similarity between two sets by comparing their intersection to their '
                                  'union. It is often used in collaborative filtering to measure similarity between '
                                  'sets of items or users based on their preferences')

SIMILARITIES = [
    ADJUSTED_COSINE_SIMILARITY,
    COSINE_SIMILARITY,
    MANHATTAN_DISTANCE,
    EUCLIDIAN_DISTANCE,
    JACCARD_SIMILARITY
]

LABELS_MAPPED = {
    ADJUSTED_COSINE_SIMILARITY: ADJUSTED_COSINE_SIMILARITY_LABEL,
    COSINE_SIMILARITY: COSINE_SIMILARITY_LABEL,
    MANHATTAN_DISTANCE: MANHATTAN_DISTANCE_LABEL,
    EUCLIDIAN_DISTANCE: EUCLIDIAN_DISTANCE_LABEL,
    JACCARD_SIMILARITY: JACCARD_SIMILARITY_LABEL
}

DESCRIPTIONS_MAPPED = {
    ADJUSTED_COSINE_SIMILARITY: ADJUSTED_COSINE_SIMILARITY_DESCRIPTION,
    COSINE_SIMILARITY: COSINE_SIMILARITY_DESCRIPTION,
    MANHATTAN_DISTANCE: MANHATTAN_DISTANCE_DESCRIPTION,
    EUCLIDIAN_DISTANCE: EUCLIDIAN_DISTANCE_DESCRIPTION,
    JACCARD_SIMILARITY: JACCARD_SIMILARITY_DESCRIPTION
}

FUNCTIONS_MAPPED = {
    ADJUSTED_COSINE_SIMILARITY: adjusted_cosine_similarity,
    COSINE_SIMILARITY: cosine_similarity,
    MANHATTAN_DISTANCE: manhattan_distance,
    EUCLIDIAN_DISTANCE: euclidian_distance,
    JACCARD_SIMILARITY: jaccard_similarity
}

GLOBAL_DESCRIPTION = ("Collaborative filtering is a technique used in recommendation systems to predict a user's "
                      "preferences based on the preferences of other users. It works by analyzing past user behavior, "
                      "such as items they have liked or interacted with, and finding similar users or items. There "
                      "are two main types of collaborative filtering: user-based and item-based. User-based "
                      "collaborative filtering recommends items that similar users have liked in the past, "
                      "while item-based collaborative filtering recommends items that are similar to ones the user "
                      "has liked before. Here, we will implement user based collaborative filtering by using "
                      "different methods to compute the similarity between our users.")

st.set_page_config(page_title="Collaborative filtering")
st.title('User-Based Collaborative filtering playground')

st.info('You can either upload a csv file containing the data or enter manually the number of users and the number of '
        'movies. In both cases, you will be able to modify the ratings and request the recommendations for a specific '
        'user', icon="ℹ️")

with st.expander("What is collaborative filtering ?"):
    st.markdown(f'<div style="text-align: justify;"> {GLOBAL_DESCRIPTION} </div>', unsafe_allow_html=True)

st.divider()

uploaded_file = st.file_uploader("Upload a csv file", type="csv")


def main():
    if 'dataset' not in st.session_state:
        st.session_state.dataset = []

    if uploaded_file is not None:
        st.session_state.dataset = load_dataset_from_csv(uploaded_file)
        st.session_state.nb_users = len(st.session_state.dataset)
        st.session_state.nb_movies = len(st.session_state.dataset[0])

    col1, col2 = st.columns(2)

    with col1:
        nb_users = st.number_input('Or, enter the number of users', min_value=1, key="nb_users",
                                   disabled=uploaded_file is not None)

    with col2:
        nb_movies = st.number_input('Enter the number of movies', min_value=1, key="nb_movies",
                                    disabled=uploaded_file is not None)

    if uploaded_file is None:
        if not st.session_state.dataset:
            st.session_state.dataset = [[None for _ in range(nb_movies)] for _ in range(nb_users)]

        else:
            if nb_users < len(st.session_state.dataset):
                st.session_state.dataset = st.session_state.dataset[:nb_users]

            for i in range(len(st.session_state.dataset)):
                if nb_movies < len(st.session_state.dataset[i]):
                    st.session_state.dataset[i] = st.session_state.dataset[i][:nb_movies]
                elif nb_movies > len(st.session_state.dataset[i]):
                    st.session_state.dataset[i] += [None] * (nb_movies - len(st.session_state.dataset[i]))

            if nb_users > len(st.session_state.dataset):
                st.session_state.dataset += [[None] * nb_movies for _ in
                                             range(nb_users - len(st.session_state.dataset))]

    edited_df = st.data_editor(convert_to_dataframe(st.session_state.dataset), use_container_width=True)

    if edited_df is not None:
        updated_dataset = edited_df.values.tolist()
        st.session_state.dataset = updated_dataset

    similarity_function_to_use = st.selectbox(
        "Similarity computation method that will be used",
        SIMILARITIES,
        index=None,
        placeholder="Select a similarity computation method",
        format_func=lambda x: LABELS_MAPPED[x]
    )

    if similarity_function_to_use is not None:
        st.caption(DESCRIPTIONS_MAPPED[similarity_function_to_use])

    users_indexes = range(nb_users)

    selected_user = st.selectbox(
        "User to whom recommendations will be made",
        users_indexes,
        index=None,
        placeholder="Select a user",
        format_func=format_user
    )

    if similarity_function_to_use is not None and selected_user is not None:
        clicked = st.button("Let's go !", type="primary", use_container_width=True)

        if clicked:
            try:
                with st.spinner('Doing computations...'):
                    dataset_cleaned = clean_dataset(st.session_state.dataset)
                    similarities = map_similarities(
                        dataset_cleaned,
                        selected_user,
                        FUNCTIONS_MAPPED[similarity_function_to_use]
                    )

                    top_n = max(1, min(3, nb_users // 4))
                    top_indexes = get_top_indexes(top_n, similarities, selected_user)
                    ratings = estimate_ratings(dataset_cleaned, top_indexes, similarities)

                if top_n == 1:
                    message = (f'The user that is most similar to the {format_user(selected_user)} is the '
                               f'{format_user(top_indexes[0])} with a '
                               f'similarity of {round(similarities[top_indexes[0]], 2)}')
                else:
                    indexes = [x + 1 for x in top_indexes]
                    message = (f'The users that are most similar to the {format_user(selected_user)} are in order : '
                               f' Users n° {join_readable(indexes)}')

                st.divider()
                st.write(message)

                st.write(f"The ratings the {format_user(selected_user)} might give to "
                         f"the movies are {join_readable(ratings)}")
                actual_ratings = dataset_cleaned[selected_user]

                # Show the movie that should be recommended to the user
                predicted = {}

                for i in range(len(actual_ratings)):
                    if actual_ratings[i] is None:
                        predicted[i] = ratings[i]

                if len(predicted) >= 1:
                    index_highest_rated_movie, rating_highest_rated_movie = max(predicted.items(), key=lambda x: x[1])
                    st.write(
                        f"The recommended movie would be the movie n°{index_highest_rated_movie + 1} "
                        f"since the estimated rating is {rating_highest_rated_movie} which is the highest"
                        f"estimated rating for a movie not yet rated by the {format_user(selected_user)}")
            except:
                st.error('An error occurred, make sure all the users have given at least one rating')


if __name__ == "__main__":
    main()
