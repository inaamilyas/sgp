from django.urls import path
from .views import *

urlpatterns = [
    path('', dashboard, name='Dashboard'),
    path('adminlogin/', handleAdminLogin, name='AdminLogin'),
    path('adminlogout/', handleLogout, name='AdminLogout'),

    path('search/', handleMainSearch, name='HandleMainSearch'),

    # Users
    path('users/', users, name='Users'),
    path('user-details/<id>', userDetails, name='UserDetails'),
    path('update-user/<id>', updateUser, name='UpdateUser'),
    path('delete-user/<id>', deleteUser, name='DeleteUser'),

    # Department
    path('departments/', departments, name='Departments'),
    path('add-department/',
         addDepartment, name='AddDepartment'),
    path('department-details/<slug:department_slug>',
         departmentDetails, name='DepartmentDetails'),
    path('update-department/<slug:department_slug>',
         updateDepartment, name='UpdateDepartment'),
    path('delete-department/<slug:department_slug>',
         deleteDepartment, name='DeleteDepartment'),

    # Courses
    path('courses/', courses, name='Courses'),
    path('add-course/',
         addCourse, name='AddCourse'),
    path('course-details/<slug:course_slug>',
         courseDetails, name='CourseDetails'),
    path('update-course/<slug:course_slug>',
         updateCourse, name='UpdateCourse'),
    path('delete-course/<slug:course_slug>',
         deleteCourse, name='DeleteCourse'),

    # Lessons
    path('lessons/', lessons, name='Lessons'),
    path('lesson-details/<slug:lesson_slug>',
         lessonDetails, name='LessonDetails'),
    path('add-lesson/',
         addLesson, name='AddLesson'),
    path('update-lesson/<slug:lesson_slug>',
         updateLesson, name='UpdateLesson'),
    path('delete-lesson/<slug:lesson_slug>',
         deleteLesson, name='DeleteLesson'),


    # Queries
    path('queries/', queries, name='Queries'),
    path('query-details/<slug:query_slug>',
         queryDetails, name='QueryDetails'),
    path('add-query/',
         addQuery, name='AddQuery'),
    path('update-query/<slug:query_slug>',
         updateQuery, name='UpdateQuery'),
    path('delete-query/<slug:query_slug>',
         deleteQuery, name='DeleteQuery'),


    # Answers
    path('add-answer/<slug:query_slug>',addAnswer, name='AddAnswer'),
    path('update-answer/<int:answer_id>/',
         updateAnswer, name='UpdateAnswer'),
    path('delete-answer/<int:answer_id>/',
         deleteAnswer, name='DeleteAnswer'),


    # Links
    path('similar-links/', similarLinks, name='SimilarLinks'),
    path('add-link/', addLink, name='AddLink'),
    path('update-link/<int:link_id>',
         updateLink, name='UpdateLink'),
    path('delete-link/<int:link_id>',
         deleteLink, name='DeleteLink'),


    # Youtube Videos
#     path('add-youtube-videos/', addVideos, name='AddVideos'),
#     path('add-link/', addLink, name='AddLink'),
    
#     path('delete-link/<int:link_id>',
#          deleteLink, name='DeleteLink'),


#     path('generate-link/<slug:lesson_slug>',
#          generateLink, name='GenerateLink'),


    path('save-link-to-db/',
         saveLinkToDb, name='SaveLinkToDb'),
    path('save-video-to-db/',
         saveVideoToDb, name='SaveVideoToDb'),



]
