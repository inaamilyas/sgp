
from django.urls import path
from .views import *

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', home, name='Home'),
    path('courses/', courses, name='Courses'),
    path('<slug:course_name>/<slug:lesson_name>', courseLesson, name='CourseLesson'),
    path('count-lesson-views/<slug:lesson_slug>/', countLessonViews, name='CountLessonViews'),
    

    path('queries/', queries, name='Queries'),
    path('latest-queries/', latQueries, name='LatestQueries'),
    path('popular-queries/', popuQueries, name='PopularQueries'),
    path('query/<slug:query_slug>/', queryDetails, name='QueryDetails'),
    path('del-query/<slug:query_slug>/', delQuery, name='DelQuery'),
    path('edit-query/<slug:query_slug>/', editQuery, name='EditQuery'),
    path('ask-query/', askQuery, name='AskQuery'),
    path('count-query-views/<slug:query_slug>/', countQueryViews, name='CountQueryViews'),


    path('add-answer/<slug:query_slug>/', addAnswer, name='AddAnswer'),
    path('edit-answer/<int:answer_id>/', editAnswer, name='EditAnswer'),
    path('delete-answer/<int:answer_id>/', delAnswer, name='DelAnswer'),
    path('sort-answer/', sortAnswer, name='SortAnswer'),


    path('search/', handleSearch, name='Search'),
    path('search-course/', handleCourseSearch, name='SearchCourse'),

    path('login/', handleLogin, name='Login'),
    path('signup/', handleSignup, name='Signup'),
    path('verify/email/<slug:auth_token>/', verifyEmail, name='VerifyEmail'),
    # path('mail-verification-success/', verifyMailSuccess, name='VerifyMailSuccess'),
    # path('mail-verification-error/', verifyMailError, name='VerifyMailError'),
    path('forget-password/', forgetPassword, name='ForgetPassword'),
    path('change-password/', changePassword, name='ChangePassword'),
    path('logout/', handleLogout, name='Logout'),
    path('profile/', profile, name='Profile'),
    path('about/', about, name='About'),

    path('reviews/', handleLessonReviews, name='Reviews'),
    path('ans-like/', ansLike, name='AnsLike'),

    path('calc-lesson-watch-time/<slug:lesson_slug>/<int:watch_time>/', calcLessonWatchTime, name='CalcLessonWatchTime'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

