import pandas as pd
import numpy as np
import mysql.connector
import pickle
from .models import *

class LRS:

    # Connect to Database
    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="study_guideline_portal",
    )
    mycursor = mydb.cursor()

    lessonsOrig_df = ''
    ratings_df = ''
    watchtime_df = ''

    lessons_tags_df = ''
    similarity = ''


    def __init__(self):
        # Load the file 
        self.load_pkl_file()

        self.lessonsOrig_df = self.fetch_lessons()
        self.ratings_df= self.fetch_ratings()
        self.watchtime_df = self.fetch_watchtime()


    def load_pkl_file(self):
        self.lessons_tags_df = pickle.load(open('pkl_files/lessons_tags_df.pkl', 'rb'))
        self.similarity = pickle.load(open('pkl_files/similarity.pkl', 'rb'))

    def fetch_lessons(self):
        # Fetching lessons from database and creating dataframe
        self.mycursor.execute('SELECT lesson_id,lesson_title, views FROM studyguidelineportal_lesson;')
        lessonViews = self.mycursor.fetchall()

        lesson_id = []
        lesson_title=[]
        lesson_views = []

        for i in lessonViews:
            lesson_id.append(i[0])
            lesson_title.append(i[1])
            lesson_views.append(i[2])

            
        lessons = {
            'lesson_id':lesson_id,
            'lesson_title':lesson_title,
            'lesson_views':lesson_views,
        }

        # self.lessonsOrig_df = pd.DataFrame(lessons)
        return pd.DataFrame(lessons)

    def fetch_ratings(self):
        self.mycursor.execute('SELECT * FROM studyguidelineportal_lessonreview;')
        lessonRatings = self.mycursor.fetchall()

        lesson_rating_id = []
        lesson_rate = []
        lesson_id=[]
        user_id=[]

        for i in lessonRatings:
            lesson_rating_id.append(i[0])
            lesson_rate.append(i[1])
            lesson_id.append(i[2])
            user_id.append(i[3])
            
        lesson_rating_dict = {
            'lesson_rating_id':lesson_rating_id ,
            'lesson_rate':lesson_rate,
            'lesson_id':lesson_id,
            'user_id':user_id,
        }

        # self.ratings_df = pd.DataFrame(lesson_rating_dict)
        return pd.DataFrame(lesson_rating_dict)

    def fetch_watchtime(self):
        # Fetching lesson Watchtime from database and creating a dataframe
        self.mycursor.execute('SELECT * FROM studyguidelineportal_lessonwatchtime;')
        lessonWTime = self.mycursor.fetchall()

        # Creating dataframe
        watch_time_id = []
        lesson_watch_time = []
        user_id=[]
        lesson_id=[]

        for i in lessonWTime:
            watch_time_id.append(int(i[0]))
            lesson_watch_time.append(int(i[1]))
            lesson_id.append(i[3])
            user_id.append(i[4])
            
        lesson_watch_dict = {
            'watch_time_id':watch_time_id,
            'lesson_watch_time':lesson_watch_time,
            'lesson_id':lesson_id,
            'user_id':user_id,
        }

        # self.watchtime_df = pd.DataFrame(lesson_watch_dict)  
        return pd.DataFrame(lesson_watch_dict)  


    def user_interest_recomm(self, loggedin_user):
        lesson_watchtime_df= self.watchtime_df[[ 'lesson_watch_time','lesson_id','user_id']]
        lesson_ratings_df = self.ratings_df[['lesson_rating_id','lesson_rate','lesson_id', 'user_id']]
        
        def lesson_rated_by_user(user, lesson_set):
            highest_rated_lesson = lesson_ratings_df[lesson_ratings_df['user_id'] == user].sort_values('lesson_rate', ascending=False)[0:6]
            highest_rated_lesson = list(enumerate(highest_rated_lesson['lesson_id']))
            for i in highest_rated_lesson:
                lesson_set.add(i[1])

        def lesson_watched_by_user(user, lesson_set):
            most_watched_lesson = lesson_watchtime_df[(lesson_watchtime_df['user_id'] == user) & (lesson_watchtime_df['lesson_watch_time'] >30)].sort_values(
                'lesson_watch_time', ascending=False)[0:6]
            most_watched_lesson = list(enumerate(most_watched_lesson['lesson_id']))
            for i in most_watched_lesson:
                lesson_set.add(i[1])

        def interest_based_recomm():
            user_history_lessons = set()
            set_lessons = set()

            lesson_rated_by_user(loggedin_user, user_history_lessons)
            lesson_watched_by_user(loggedin_user, user_history_lessons)
            range=2
            if len(user_history_lessons) < 3: range=5
            for id in user_history_lessons:
                for less in self.generate_recomm(id, range):
                    set_lessons.add(less)
            return set_lessons
        return interest_based_recomm()

    def popular_recomm(self):
        lesson_views_df = self.lessonsOrig_df[['lesson_id', 'lesson_title', 'lesson_views']]
        lesson_watchtime_df=self.watchtime_df[['lesson_watch_time','lesson_id']]
        lesson_ratings_df=self.ratings_df[['lesson_rating_id','lesson_rate','lesson_id']]

        # average rating on each lesson
        avg_rating_df = lesson_ratings_df.groupby('lesson_id').mean()['lesson_rate'].reset_index()
        avg_rating_df.rename(columns={'lesson_rate': 'avg_rating'}, inplace=True)

         # number of ratings on each lesson
        num_rating_df = lesson_ratings_df.groupby('lesson_id').count()['lesson_rate'].reset_index()
        num_rating_df.rename(columns={'lesson_rate': 'num_rating'}, inplace=True)

        final_ratings_df = avg_rating_df.merge(num_rating_df, on='lesson_id')

        # total watchtime on each lesson
        total_watch_time_df = lesson_watchtime_df.groupby('lesson_id').sum()['lesson_watch_time'].reset_index()
        total_watch_time_df.rename(columns={'lesson_watch_time': 'total_watch_time'}, inplace=True)

        # Merging lessons with ratings df and watchtime df
        lesson_with_ratings = pd.merge(lesson_views_df, final_ratings_df, on='lesson_id', how='left')
        lesson_info_df = pd.merge(lesson_with_ratings, total_watch_time_df, on='lesson_id', how='left')
        lesson_info_df.fillna(0, inplace=True)

        def calculate_popularity_score(lesson_views, avg_rating, num_rating, total_watch_time, w1=1, w2=2, w3=1/60):
            return (w1 * lesson_views) + (w2 * avg_rating * num_rating) + (w3 * (total_watch_time))

        # Calculate popularity score for each lesson
        lesson_info_df['popularity_score'] = calculate_popularity_score(lesson_info_df['lesson_views'], lesson_info_df['avg_rating'], lesson_info_df['num_rating'], lesson_info_df['total_watch_time'])

        # Rank lessons based on popularity score
        lesson_info_df = lesson_info_df.sort_values(by='popularity_score', ascending=False)[0:10]

        # function to return popular lessons 
        def pupular_lessons():
            l=[]
            for item in list(enumerate(lesson_info_df['lesson_id'])):
                l.append(item[1])
            return l

        return pupular_lessons()

    def similarity_recomm(self, lesson_id):
        return self.generate_recomm(lesson_id, 10)

    def generate_recomm(self, lesson_id, range):
        lesson_index = self.lessons_tags_df[self.lessons_tags_df['lesson_id'] == lesson_id].index[0]
        distances = self.similarity[lesson_index]
        lesson_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x:x[1])[1:range+1]
        list_of_lessons=[]
        for i in lesson_list:
            list_of_lessons.append(self.lessons_tags_df.iloc[i[0]].lesson_id)
        return list_of_lessons