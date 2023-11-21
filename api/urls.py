from django.urls import path
from .views import *

urlpatterns = [
    path('lessons/', lesson_list,),

    path('get-latest-lessons/', latestLessons,),
    path('get-popular-lessons/', popularLessons,),
    path('get-user-user-recomm/<int:user_id>/', userUserRecomm,),
    path('get-user-lesson-recomm/<int:user_id>/', userLessonRecomm,),
    path('get-similar-lessons/<int:lesson_id>/', similarLessons,),

    path('get-feature-courses/', featuredCourses,),
    path('get-all-courses/', allCourses,),

    path('get-lesson-details/<int:lesson_id>/', lessonDetails,),
    
]