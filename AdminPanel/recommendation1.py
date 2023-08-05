

'''
def reloadRecommendation1():
    print("inside recommendation model")
    # Connect to Database 
    mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="study_guideline_portal",
    )
    mycursor=mydb.cursor()

    # Fetching data from database
    mycursor.execute('SELECT studyguidelineportal_lesson.lesson_id, studyguidelineportal_lesson.lesson_title, studyguidelineportal_lesson.lesson_tags, studyguidelineportal_lesson.lesson_summary, studyguidelineportal_course.course_name, studyguidelineportal_department.dep_name FROM ( (studyguidelineportal_lesson left join studyguidelineportal_course on studyguidelineportal_lesson.course_id = studyguidelineportal_course.course_id) left join studyguidelineportal_department on studyguidelineportal_course.department_id = studyguidelineportal_department.dep_id);')
    data = mycursor.fetchall()

    # Converting data to pandas dataframe
    lesson_id=[]
    lesson_title=[]
    lesson_tags=[]
    lesson_summary=[]
    course_name=[]
    dep_name=[]

    for i in data:
        lesson_id.append(i[0])
        lesson_title.append(i[1])
        lesson_tags.append(i[2])
        lesson_summary.append(i[3])
        course_name.append(i[4])
        dep_name.append(i[5])

    mydict={
        'lesson_id':lesson_id,
        'lesson_title':lesson_title,
        'lesson_tags':lesson_tags,
        'lesson_summary':lesson_summary,
        'course_name':course_name,
        'dep_name':dep_name
        }
    lessons = pd.DataFrame(mydict) #creating dataframe throught dictionary

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
    lessons['tags'][0]

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
'''

"""
# Converting major into list
# def toList(str):
#     return str.split(',')

# def reloadRecomm():
#     print('inside relaod Recommendation')
#     lessons = pd.read_csv('csv_files/lessons.csv')
#     lessons.isnull().sum()
#     lessons.duplicated().sum()
#     lessons = lessons[['Title', 'course', 'Major']]
#     lessons_orig = lessons.copy()
#     lessons['Major']=lessons['Major'].apply(toList)
#     lessons['Title']=lessons['Title'].apply(lambda x:x.split())
#     # # Removing spaces from Course
#     lessons['course']=lessons['course'].apply(lambda x:x.replace(" ", ""))
#     # Converiting to list.
#     lessons['course']=lessons['course'].apply(toList)
#     lessons['tags']= lessons['Title']+lessons['course']+lessons['Major']
    
#     new_df = lessons[['Title','tags']]
#     # Converting back to String 
#     new_df['tags'] = new_df['tags'].apply(lambda x:" ".join(x))
#     # Converting to Lowercase
#     new_df['tags'] = new_df['tags'].apply(lambda x:x.lower())
#     new_df['tags']
#     cv = CountVectorizer(max_features=2000, stop_words='english')
#     vectors = cv.fit_transform(new_df['tags']).toarray()
#     similarity=cosine_similarity(vectors)

#     print('dumping files')
#     pickle.dump(lessons_orig, open('pkl_files/lessons.pkl', 'wb'))
#     pickle.dump(similarity, open('pkl_files/similarity.pkl', 'wb'))

"""


