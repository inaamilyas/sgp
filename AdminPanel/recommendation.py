# Reload Recommendation System 
from StudyGuidelinePortal.models import Lesson,Course,Department
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle



def reloadRecommendation():

    # Creating dataframe from lessons
    all_lessons = Lesson.objects.values('lesson_id', 'lesson_title', 'lesson_summary', 'lesson_tags', 'course')
    lessons_df=pd.DataFrame(all_lessons)
    lessons_df.rename(columns={'course': 'course_id'}, inplace=True)
    
    # Creating dataframe from courses 
    all_courses = Course.objects.values("course_id", 'course_name', 'department')
    courses_df = pd.DataFrame(all_courses)
    courses_df.rename(columns={'department': 'dep_id'}, inplace=True)
    
     # Creating dataframe from departments 
    dep = Department.objects.values('dep_id', 'dep_name')
    dep_df = pd.DataFrame(dep)

    # Merging all dfs into a single df 
    new_df = pd.merge(lessons_df, courses_df, on='course_id', how='left')
    lessons = pd.merge(new_df, dep_df, on='dep_id', how='left') #final dataframe
    

    # Converting to list 
    lessons['lesson_title'] =lessons['lesson_title'].apply(lambda x:x.split())
    lessons['lesson_summary'] =lessons['lesson_summary'].apply(lambda x:x.split())
    lessons['lesson_tags'] =lessons['lesson_tags'].apply(lambda x:x.split(","))
    lessons['course_name'] = lessons['course_name'].apply(lambda x: x.split(","))
    lessons['dep_name'] = lessons['dep_name'].apply(lambda x: x.split(","))

    # Removing spaces from course_name and dep_name
    lessons['dep_name']=lessons['dep_name'].apply(lambda x:[i.replace(" ", "") for i in x])
    lessons['course_name']=lessons['course_name'].apply(lambda x:[i.replace(" ", "") for i in x])

    # Creating new column 
    lessons['tags'] = lessons['lesson_title'] + lessons['lesson_tags'] + lessons['lesson_summary'] + lessons['course_name'] + lessons['dep_name']

    # Creating new dataframe 
    lessons_tags_df = lessons[['lesson_id','lesson_title','tags']]

    # Converting back to String 
    lessons_tags_df['tags'] = lessons_tags_df['tags'].apply(lambda x:" ".join(x))
    lessons_tags_df['lesson_title'] = lessons_tags_df['lesson_title'].apply(lambda x:" ".join(x))

    # Converting to Lowercase
    lessons_tags_df['tags'] =lessons_tags_df['tags'].apply(lambda x:x.lower())

    # Creating vectors 
    cv = CountVectorizer(max_features=2000, stop_words='english')
    vectors = cv.fit_transform(lessons_tags_df['tags']).toarray()
    # cv.get_feature_names()

    # calculating similarities 
    similarity=cosine_similarity(vectors)

    # Dumping files 
    print("dumpinig files")
    pickle.dump(lessons_tags_df, open('pkl_files/lessons_tags_df.pkl', 'wb'))
    pickle.dump(similarity, open('pkl_files/similarity.pkl', 'wb'))
