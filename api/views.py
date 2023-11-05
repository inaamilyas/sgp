from django.shortcuts import render
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from StudyGuidelinePortal.models import *
from StudyGuidelinePortal.serializers import *
from StudyGuidelinePortal.recomm4 import LRS

# All Api Views
RECOMM_SYS = LRS()
@api_view(['GET'])
@renderer_classes([JSONRenderer])
def lesson_list(request):
    if request.method == 'GET':
        lessons = Lesson.objects.all()[:1]
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)
    

# Latest Lessons 
@api_view(['GET'])
@renderer_classes([JSONRenderer])
def latestLessons(request):
    if request.method == 'GET':
        latest_lessons = Lesson.objects.all().order_by('-time')[:10]
        serializer = LessonSerializer(latest_lessons, many=True)
        return Response(serializer.data)
    
# Popular Lessons  
@api_view(['GET'])
@renderer_classes([JSONRenderer])
def popularLessons(request):
    if request.method == 'GET':
        popular_lessons_ids = RECOMM_SYS.popular_recomm()[:10]

        serializer = LessonSerializer(get_lesson_by_ids(popular_lessons_ids), many=True)
        return Response(serializer.data)
    

# Recommended Lessons (user-user)
@api_view(['GET'])
@renderer_classes([JSONRenderer])
def userUserRecomm(request, user_id):
    if request.method == 'GET':
        recomm_lessons_ids = RECOMM_SYS.user_user_based_recomm(user_id)
        if(len(recomm_lessons_ids) > 0):
            serializer = LessonSerializer(get_lesson_by_ids(recomm_lessons_ids), many=True)
            return Response(serializer.data)
        else:
            return Response("No data found")
        

# Recommended Lessons (user-lesson)
@api_view(['GET'])
@renderer_classes([JSONRenderer])
def userLessonRecomm(request, user_id):
    if request.method == 'GET':
        recomm_lessons_ids = RECOMM_SYS.user_user_based_recomm(user_id)
        if(len(recomm_lessons_ids) > 0):
            serializer = LessonSerializer(get_lesson_by_ids(recomm_lessons_ids), many=True)
            return Response(serializer.data)
        else:
            return Response("No data found")
        

# Feature Courses 
@api_view(['GET'])
@renderer_classes([JSONRenderer])
def featuredCourses(request):
    if request.method == 'GET':
        featured_courses = Course.objects.all()[:10]
        serializer = CourseSerializer(featured_courses, many=True)
        return Response(serializer.data)
 

# All Courses
@api_view(['GET'])
@renderer_classes([JSONRenderer])
def allCourses(request):
    if request.method == 'GET':
        all_courses = Course.objects.all()
        serializer = CourseSerializer(all_courses, many=True)
        return Response(serializer.data)


# Lesson details
@api_view(['GET'])
@renderer_classes([JSONRenderer])
def lessonDetails(request, lesson_slug):
    if request.method == 'GET':
        lesson = Lesson.objects.filter(lesson_slug=lesson_slug).first()
        serializer = LessonDetailsSerializer(lesson)
        return Response(serializer.data)
    
 
# Similar lessons 
@api_view(['GET'])
@renderer_classes([JSONRenderer])
def similarLessons(request, lesson_id):
    if request.method == 'GET':
        similar_lessons_ids = RECOMM_SYS.similarity_recomm(lesson_id)

        serializer = LessonSerializer(get_lesson_by_ids(similar_lessons_ids), many=True)
        return Response(serializer.data)


# Department wise courses 







# =============================================================
# Calculating Average Rating
def avgRating(lesson):
    lesson_reviews = LessonReview.objects.filter(lesson=lesson)
    total_ratings = 0
    avg_rating = 0
    for review in lesson_reviews:
        total_ratings = total_ratings+review.rate

    if total_ratings > 0:
        avg_rating = total_ratings/len(lesson_reviews)
    else:
        avg_rating = total_ratings
    return avg_rating


# Sorting Nested List
def sortListDesc(neslist, index):
    return sorted(neslist, key=lambda v: (-v[index]))


# Mapping lesson with Ratings
def map_lesson_details(lessons):
    lesson_details = []
    for lesson in lessons:
        avg_rating = avgRating(lesson)
        # Appending to the list
        lesson_details.append([lesson, avg_rating])
    return lesson_details

    course_details = []
    for course in courses:
        first_lesson = None
        no_of_lessons = 0
        lessons = Lesson.objects.filter(course=course)
        if lessons:
            first_lesson = lessons[0].lesson_slug
            no_of_lessons = lessons.count()

        course_details.append({
            "course_id":course.course_id,
            "course_name":course.course_name,
            "course_pic":course.course_pic,
            "course_slug":course.course_slug,
            "department":course.department.all(),
            'first_lesson': first_lesson,
            'no_of_lessons': no_of_lessons,
            })

    return course_details

def get_lesson_by_ids(lesson_ids):
    lessons=[]
    for lesson_id in lesson_ids:
        lesson = Lesson.objects.filter(lesson_id=lesson_id).first()
        if lesson:
            lessons.append(lesson)
    return lessons