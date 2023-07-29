import pandas as pd
import numpy as np
import mysql.connector
import pickle

class LRS:

    # Connect to Database
    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="study_guideline_portal",
    )
    mycursor = mydb.cursor()

    lessonsOrig_df = pd.DataFrame()
    ratings_df = pd.DataFrame()
    watchtime_df = pd.DataFrame()

    lessons_tags_df = ''
    similarity = ''

    def __init__(self):
        # Load the file 
        self.load_pkl_file()
        self.fetch_lessons()
        self.fetch_ratings()
        self.fetch_watchtime()


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

        self.lessonsOrig_df = pd.DataFrame(lessons)

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

        self.ratings_df = pd.DataFrame(lesson_rating_dict)

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

        self.watchtime_df = pd.DataFrame(lesson_watch_dict)  


    def user_interest_recomm(self, loggedin_user):
        lesson_watchtime_df= self.watchtime_df[[ 'lesson_watch_time','lesson_id','user_id']]
        lesson_df=self.lessonsOrig_df[['lesson_id', 'lesson_title']]
        lesson_ratings_df = self.ratings_df[['lesson_rating_id','lesson_rate','lesson_id', 'user_id']]
        
        def lesson_rated_by_user(user, list1):
            highest_rated_lesson = lesson_ratings_df[lesson_ratings_df['user_id'] == user].sort_values(
                'lesson_rate', ascending=False)[0:6]
            highest_rated_lesson = list(
                enumerate(highest_rated_lesson['lesson_id']))
            for i in highest_rated_lesson:
                list1.append(i[1])

        def lesson_watched_by_user(user, list1):
            most_watched_lesson = lesson_watchtime_df[lesson_watchtime_df['user_id'] == user].sort_values(
                'lesson_watch_time', ascending=False)[0:6]
            most_watched_lesson = list(enumerate(most_watched_lesson['lesson_id']))
            for i in most_watched_lesson:
                list1.append(i[1])

        def interest_based_recomm():
            user_history_lessons = []
            set_lessons = set()

            lesson_rated_by_user(loggedin_user, user_history_lessons)
            lesson_watched_by_user(loggedin_user, user_history_lessons)

            for id in user_history_lessons:
                title = list(enumerate(lesson_df[lesson_df['lesson_id'] == id]['lesson_title']))[0][1]
                for less in self.generate_recomm(title, 2):
                    set_lessons.add(less)

            return set_lessons

        return interest_based_recomm()

    def popular_recomm(self):
        lesson_views_df = self.lessonsOrig_df[['lesson_id', 'lesson_title', 'lesson_views']]
        lesson_watchtime_df=self.watchtime_df[['lesson_watch_time','lesson_id']]
        lesson_ratings_df=self.ratings_df[['lesson_rating_id','lesson_rate','lesson_id']]

        # Merging dataframes
        lesson_rating_views_df = lesson_ratings_df.merge(
            lesson_views_df, on='lesson_id')
        lesson_watchtime_views_df = lesson_watchtime_df.merge(
            lesson_views_df, on='lesson_id')

        # Calculating total watchtime on each lesson
        total_watchtime_df = lesson_watchtime_views_df.groupby(
            'lesson_title').sum()['lesson_watch_time'].reset_index()
        total_watchtime_df.rename(
            columns={'lesson_watch_time': 'total_watchtime'}, inplace=True)

        # Calculating number of watchtimes on each lesson
        num_watchtime_df = lesson_watchtime_views_df.groupby(
            'lesson_title').count()['lesson_watch_time'].reset_index()
        num_watchtime_df.rename(
            columns={'lesson_watch_time': 'num_watchtime'}, inplace=True)

        # Merging num_watch_df and total_watchtime_df
        final_watchtime_df = num_watchtime_df.merge(
            total_watchtime_df, on='lesson_title')

        # Merging views and watchtime dataframes
        lesson_views_df = lesson_views_df.merge(
            final_watchtime_df, on='lesson_title')

        # Number of ratings on each lesson
        num_rating_df = lesson_rating_views_df.groupby('lesson_title').count()[
            'lesson_rate'].reset_index()
        num_rating_df.rename(
            columns={'lesson_rate': 'num_ratings'}, inplace=True)

        # average rating on each lesson
        avg_rating_df = lesson_rating_views_df.groupby('lesson_title').mean()[
            'lesson_rate'].reset_index()
        avg_rating_df.rename(
            columns={'lesson_rate': 'avg_rating'}, inplace=True)

        # Merging avg_rating_df and num_rating_df
        final_rating_df = num_rating_df.merge(avg_rating_df, on='lesson_title')

        # Popular lessons based on ratings
        popular_rating_df = final_rating_df[final_rating_df['num_ratings'] >= 1].sort_values(
            'avg_rating', ascending=False)

        # Popular lessons based on watchtime and views
        popular_views_df = lesson_views_df[lesson_views_df['total_watchtime'] >= 10].sort_values(
            'lesson_views', ascending=False)

        print(popular_rating_df)
        print(popular_views_df)

        # converting dataframe into set 

    def similarity_recomm(self, lesson_title):
        return self.generate_recomm(lesson_title, 10)

    def generate_recomm(self, lesson_title, range):
        lesson_index = self.lessons_tags_df[self.lessons_tags_df['lesson_title'] == lesson_title].index[0]
        distances = self.similarity[lesson_index]
        lesson_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x:x[1])[1:range+1]
        list_of_titles=[]
        for i in lesson_list:
            list_of_titles.append(self.lessons_tags_df.iloc[i[0]].lesson_title)
        return list_of_titles