import pandas as pd
import pickle
from .models import *
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class LRS:
    lessonsOrig_df = pd.DataFrame()
    ratings_df = pd.DataFrame()
    watchtime_df = pd.DataFrame()

    def __init__(self):
        self.load_pkl_file()

        lessons = Lesson.objects.values('lesson_id', 'lesson_title', 'views')
        ratings = LessonReview.objects.values('id', 'user', 'lesson', 'rate')
        watchtime = LessonWatchTime.objects.values(
            'user', 'lesson', 'watch_time', 'updated_at')
        self.lessonsOrig_df = pd.DataFrame(list(lessons))
        self.ratings_df = pd.DataFrame(list(ratings))
        self.watchtime_df = pd.DataFrame(list(watchtime))
        # print(self.watchtime_df.sort_values(by='updated_at', ascending=False).head(3))
        self.rename_cols()

    def load_pkl_file(self):
        self.lessons_tags_df = pickle.load(
            open('pkl_files/lessons_tags_df.pkl', 'rb'))
        self.similarity = pickle.load(open('pkl_files/similarity.pkl', 'rb'))

    def rename_cols(self):
        self.lessonsOrig_df.rename(
            columns={'views': 'lesson_views'}, inplace=True)

        self.ratings_df.rename(columns={'id': 'lesson_rating_id', 'user': 'user_id',
                               'lesson': 'lesson_id', 'rate': 'lesson_rate'}, inplace=True)

        self.watchtime_df.rename(columns={
                                 'user': 'user_id', 'lesson': 'lesson_id', 'watch_time': 'lesson_watch_time'}, inplace=True)

        self.watchtime_df['lesson_watch_time'] = self.watchtime_df['lesson_watch_time'].astype(
            int)


    # Popularity Based Recommendations
    def popular_recomm(self):
        lesson_views_df = self.lessonsOrig_df[[
            'lesson_id', 'lesson_title', 'lesson_views']]
        lesson_watchtime_df = self.watchtime_df[[
            'lesson_watch_time', 'lesson_id']]
        lesson_ratings_df = self.ratings_df[[
            'lesson_rating_id', 'lesson_rate', 'lesson_id']]

        # average rating on each lesson
        avg_rating_df = lesson_ratings_df.groupby('lesson_id').mean()[
            'lesson_rate'].reset_index()
        avg_rating_df.rename(
            columns={'lesson_rate': 'avg_rating'}, inplace=True)

        # number of ratings on each lesson
        num_rating_df = lesson_ratings_df.groupby('lesson_id').count()[
            'lesson_rate'].reset_index()
        num_rating_df.rename(
            columns={'lesson_rate': 'num_rating'}, inplace=True)

        final_ratings_df = avg_rating_df.merge(num_rating_df, on='lesson_id')

        # total watchtime on each lesson
        total_watch_time_df = lesson_watchtime_df.groupby(
            'lesson_id').sum()['lesson_watch_time'].reset_index()
        total_watch_time_df.rename(
            columns={'lesson_watch_time': 'total_watch_time'}, inplace=True)

        # Merging lessons with ratings df and watchtime df
        lesson_with_ratings = pd.merge(
            lesson_views_df, final_ratings_df, on='lesson_id', how='left')
        lesson_info_df = pd.merge(
            lesson_with_ratings, total_watch_time_df, on='lesson_id', how='left')
        lesson_info_df.fillna(0, inplace=True)

        def calculate_popularity_score(lesson_views, avg_rating, num_rating, total_watch_time, w1=1, w2=2, w3=1/60):
            return (w1 * lesson_views) + (w2 * avg_rating * num_rating) + (w3 * total_watch_time)

        # Calculate popularity score for each lesson
        lesson_info_df['popularity_score'] = calculate_popularity_score(
            lesson_info_df['lesson_views'], lesson_info_df['avg_rating'], lesson_info_df['num_rating'], lesson_info_df['total_watch_time'])

        # Rank lessons based on popularity score
        lesson_info_df = lesson_info_df.sort_values(
            by='popularity_score', ascending=False)[0:10]

        # function to return popular lessons
        def pupular_lessons():
            l = []
            for item in list(enumerate(lesson_info_df['lesson_id'])):
                l.append(item[1])
            return l

        return pupular_lessons()

    # Content Based Recommendations
    def similarity_recomm(self, lesson_id):
        return self.generate_recomm(lesson_id, 10)

    def generate_recomm(self, lesson_id, range):
        lesson_index = self.lessons_tags_df[self.lessons_tags_df['lesson_id']
                                            == lesson_id].index[0]
        distances = self.similarity[lesson_index]
        lesson_list = sorted(list(enumerate(distances)),
                             reverse=True, key=lambda x: x[1])[1:range+1]
        list_of_lessons = []
        for i in lesson_list:
            list_of_lessons.append(self.lessons_tags_df.iloc[i[0]].lesson_id)
        return list_of_lessons


    # Recommend based on user personal interactions
    def user_item_based_recomm(self, user_id):
        # Merge watch time and ratings data
        merged_df = pd.merge(self.watchtime_df, self.ratings_df, on=[
                             'user_id', 'lesson_id'])
        # Filter out interactions where the user ID is not 1 and lessons are also highly watched and rated 
        filtered_merged_df = merged_df[(merged_df['user_id'] != user_id) & (
            merged_df['rating'] >= 3) & (merged_df['watchtime'] >= 3)]

        # Filter out interactions where the user ID is 1 and lessons are also highly watched and rated
        target_user_interactions_df = merged_df[(merged_df['user_id'] == user_id) & (
            merged_df['rating'] >= 3) & (merged_df['watchtime'] >= 3)]

        recommended_lessons_ids = set()
        for lesson_id in target_user_interactions_df['lesson_id'].tolist():
            # finding out similar lessons for user interactions
            list_of_lessons = self.generate_recomm(lesson_id, 5)

            for lesson_id in list_of_lessons:
                # checking recommeded lessons is exist in our dataframe
                if lesson_id in filtered_merged_df['lesson_id'].values:
                    recommended_lessons_ids.add(lesson_id)

        return recommended_lessons_ids  # returning the set of lessons for recommendations


    # Recommendations based on similar users
    def user_user_based_recomm(self, user_id):
        # Merge watch time and ratings data
        merged_df = pd.merge(self.watchtime_df, self.ratings_df, on=['user_id', 'lesson_id'])
        print(merged_df)
        
        # Filter out lessons based on average watchtime,no of views/watchtime, average ratings and number of ratings

        # Define a function to calculate a combined score
        def calculate_combined_score(row):
            # Normalize watch time and rating to [0, 1] range
            normalized_watchtime = row['lesson_watch_time'] / merged_df['lesson_watch_time'].max()
            # Assuming ratings are on a scale of 0-5
            normalized_rating = row['lesson_rate'] / 5

            # Calculate a combined score (average of normalized values)
            combined_score = (normalized_watchtime + normalized_rating) / 2
            return combined_score

        # Apply the function to calculate combined scores
        merged_df['combined_score'] = merged_df.apply(
            calculate_combined_score, axis=1)

        # Making item-user matrix
        pivot_matrix = merged_df.pivot_table(
            index='user_id', columns='lesson_id', values='combined_score').fillna(0)

        user_similarity = cosine_similarity(pivot_matrix)

        # Finding out similar users
        def find_similar_users(target_user_id):

            # Get user IDs from the pivot matrix
            user_ids = pivot_matrix.index

            target_user_index = user_ids.get_loc(target_user_id)

            # Get the similarity scores for the target user compared to all other users
            similarities_to_target = user_similarity[target_user_index]

            # Sort and get the indices of users with highest similarity (excluding the target user)
            similar_user_indices = similarities_to_target.argsort()[:-1][::-1]

            # Print the similar user IDs and their similarity scores
            for similar_user_index in similar_user_indices:
                similar_user_id = user_ids[similar_user_index]
                similarity_score = similarities_to_target[similar_user_index]
                print(
                    f"Similar User ID: {similar_user_id}, Similarity Score: {similarity_score}")

            return similar_user_indices

        # Recommended items according to the similar user
        def recommend_on_similar_users(target_user_id):
            similar_user_indices = find_similar_users(user_id)

            # Get the lessons rated highly by similar users
            # similar_users_rated_lessons = pivot_matrix.iloc[similar_user_indices].apply(lambda row: row >= 0.7)
            similar_users_rated_lessons = pivot_matrix.iloc[similar_user_indices].apply(lambda row: row >= 0.4)

            # Get the lessons rated by the target user
            # target_user_rated_lessons = pivot_matrix.loc[target_user_id] >= 0.7
            target_user_rated_lessons = pivot_matrix.loc[target_user_id] >= 0.4

            # Find lessons highly rated by similar users but not rated by the target user
            recommended_lessons = (similar_users_rated_lessons & ~target_user_rated_lessons).any()

            # Print recommended products
            recommended_lesson_ids = recommended_lessons[recommended_lessons].index.tolist(
            )
            print("Recommended Lesson IDs:", recommended_lesson_ids)
            return recommended_lesson_ids

        return recommend_on_similar_users(user_id)
