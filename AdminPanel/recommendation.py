# Reload Recommendation System 
from StudyGuidelinePortal.models import Lesson,Course
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
    
    # Creating dataframe from courses and department
    courses = Course.objects.all()
    data = []
    for course in courses:
        department_names = ', '.join([department.dep_name for department in course.department.all()])
        course_data = {
            'course_id': course.course_id,
            'course_name': course.course_name,
            'dep_name': department_names,
        }
        data.append(course_data)
    courses_df = pd.DataFrame(data)

    # Merging all dfs into a single df 
    lessons = pd.merge(lessons_df, courses_df, on='course_id', how='left')
    
    # Converting to list 
    lessons['lesson_title'] =lessons['lesson_title'].apply(lambda x:x.split())
    lessons['lesson_summary'] =lessons['lesson_summary'].apply(lambda x:x.split())
    lessons['lesson_tags'] =lessons['lesson_tags'].apply(lambda x:x.split(","))
    lessons['course_name'] = lessons['course_name'].apply(lambda x: x.split(","))
    # lessons['dep_name'] = lessons['dep_name'].apply(lambda x: x.split(","))

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
