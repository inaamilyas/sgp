from django.shortcuts import render, redirect
from StudyGuidelinePortal.models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import *
from django.contrib import messages

# Reload Recommendation System 
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle


# Converting major into list
def toList(str):
    return str.split(',')


def reloadRecomm():
    print('inside relaod Recommendation')
    lessons = pd.read_csv('csv_files/lessons.csv')
    lessons.isnull().sum()
    lessons.duplicated().sum()
    lessons = lessons[['Title', 'course', 'Major']]
    lessons_orig = lessons.copy()
    lessons['Major']=lessons['Major'].apply(toList)
    lessons['Title']=lessons['Title'].apply(lambda x:x.split())
    # # Removing spaces from Course
    lessons['course']=lessons['course'].apply(lambda x:x.replace(" ", ""))
    # Converiting to list.
    lessons['course']=lessons['course'].apply(toList)
    lessons['tags']= lessons['Title']+lessons['course']+lessons['Major']
    
    new_df = lessons[['Title','tags']]
    # Converting back to String 
    new_df['tags'] = new_df['tags'].apply(lambda x:" ".join(x))
    # Converting to Lowercase
    new_df['tags'] = new_df['tags'].apply(lambda x:x.lower())
    new_df['tags']
    cv = CountVectorizer(max_features=2000, stop_words='english')
    vectors = cv.fit_transform(new_df['tags']).toarray()
    similarity=cosine_similarity(vectors)

    print('dumping files')
    pickle.dump(lessons_orig, open('pkl_files/lessons.pkl', 'wb'))
    pickle.dump(similarity, open('pkl_files/similarity.pkl', 'wb'))


# Create your views here.

def handleAdminLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Checking user is exist or not
        user_obj = User.objects.filter(username=username).first()
        if user_obj is None:
            messages.error(request, 'Username not found...')
            return redirect('AdminLogin')

    #     # Authenticate user from database
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect('Dashboard')
            else:
                messages.error(request, "User is not an admin")
        else:
            messages.error(request, 'Wrong username or password. Try again')
            return redirect('AdminLogin')

    return render(request, 'adminlogin1.html')


def handleLogout(request):
    logout(request)
    return redirect('AdminLogin')


def dashboard(request):
    if not request.user.is_anonymous and request.user.is_superuser:
       
        total_course = len(Course.objects.all())
        total_lesson = len(Lesson.objects.all())
        total_questions = len(Query.objects.all())
        total_answers = len(Answer.objects.all())
        total_lessonReviews = len(LessonReview.objects.all())
        total_users = len(User.objects.filter(
            is_staff=False, is_superuser=False))

        context = {
            'total_users': total_users,
            'total_courses': total_course,
            'total_lesson': total_lesson,
            'total_questions': total_questions,
            'total_answers': total_answers,
            'total_lessonReviews': total_lessonReviews,
        }

        return render(request, 'dashboard.html', context)
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


# Users
def users(request):
    if not request.user.is_anonymous and request.user.is_superuser:
        users = User.objects.filter(is_staff=False, is_superuser=False)
        context = {
            'users': users,
        }
        return render(request, 'user/users.html', context)
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def userDetails(request, id):
    if not request.user.is_anonymous and request.user.is_superuser:
        user = User.objects.get(id=id)
        context = {
            'user': user,
        }
        return render(request, 'user/user-details.html', context)
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def updateUser(request, id):
    if not request.user.is_anonymous and request.user.is_superuser:
        if request.method == 'POST':
            first_name = request.POST.get('f_name')
            last_name = request.POST.get('l_name')
            username = request.POST.get('username')
            email = request.POST.get('email')
            update_user = User(id=id, email=email, username=username)
            update_user.first_name = first_name
            update_user.last_name = last_name

            update_user.save()
            # return redirect(f'/admin1/user-details/{id}')
            return redirect(f'/admin1/users/')

        user = User.objects.get(id=id)

        context = {
            'user': user,
        }
        return render(request, 'user/edit-user.html', context)
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def deleteUser(request, id):
    if not request.user.is_anonymous and request.user.is_superuser:
        user = User.objects.get(id=id)
        user.delete()
        return redirect('Users')
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


# Departments
def departments(request):
    if not request.user.is_anonymous and request.user.is_superuser:
        departments = Department.objects.all()
        context = {
            'departments': departments,
        }
        return render(request, 'department/departments.html', context)
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def departmentDetails(request, department_slug):
    if not request.user.is_anonymous and request.user.is_superuser:
        department = Department.objects.get(dep_slug=department_slug)
        context = {
            'department': department,
        }
        return render(request, 'department/department-details.html', context)
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def addDepartment(request):
    if not request.user.is_anonymous and request.user.is_superuser:
        
        if request.method == 'POST':
            depForm = DepartmentForm(request.POST)
            if depForm.is_valid():
                dep_name = depForm.cleaned_data['dep_name']

                Department(dep_name=dep_name).save()

                return redirect('Departments')
        else:
            depForm = DepartmentForm()

        context = {
            'depForm': depForm,
        }
        return render(request, 'department/add-department.html', context)
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def updateDepartment(request, department_slug):
    if not request.user.is_anonymous and request.user.is_superuser:
        department = Department.objects.get(dep_slug=department_slug)
        if request.method == 'POST':
            depForm = DepartmentForm(request.POST, instance=department)
            if depForm.is_valid():
                dep_name = depForm.cleaned_data['dep_name']

                Department(dep_id=department.dep_id, dep_name=dep_name).save()

                return redirect('Departments')
        else:
            depForm = DepartmentForm(instance=department)

        context = {
            'department':department,
            'depForm': depForm,
        }
        return render(request, 'department/edit-department.html', context)
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def deleteDepartment(request, department_slug):
    if not request.user.is_anonymous and request.user.is_superuser:
        department = Department.objects.get(dep_slug=department_slug)
        department.delete()
        return redirect('Departments')
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


# Courses
def courses(request):
    if not request.user.is_anonymous and request.user.is_superuser:
        courses = Course.objects.all()
        context = {
            'courses': courses,
        }
        return render(request, 'course/courses.html', context)
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def courseDetails(request, course_slug):
    if not request.user.is_anonymous and request.user.is_superuser:
        course = Course.objects.get(course_slug=course_slug)
        no_of_lessons = len(Lesson.objects.filter(course=course))
        context = {
            'course': course,
            'no_of_lessons': no_of_lessons,
        }
        return render(request, 'course/course-details.html', context)
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def addCourse(request):
    if not request.user.is_anonymous and request.user.is_superuser:
        departments = Department.objects.all()
        if request.method == 'POST':
            course_name = request.POST.get('course_name')
            if 'course_pic' in request.FILES:
                course_pic = request.FILES['course_pic']

            department_slug = request.POST.get('department')
            department = Department.objects.get(dep_slug=department_slug)

            newCourse = Course(course_name=course_name,
                               course_pic=course_pic, department=department)
            newCourse.save()
            return redirect('/admin1/courses/')

        context = {
            'departments': departments,
        }

        return render(request, 'course/add-course.html', context)
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def updateCourse(request, course_slug):
    if not request.user.is_anonymous and request.user.is_superuser:
        course = Course.objects.get(course_slug=course_slug)

        if request.method == 'POST':
            course_name = request.POST.get('course_name')
            if 'course_pic' in request.FILES:
                course_pic = request.FILES['course_pic']

            department_slug = request.POST.get('department')
            department = Department.objects.get(dep_slug=department_slug)

            updateCourse = Course(course_id=course.course_id, course_name=course_name,
                                  course_pic=course_pic, department=department)

            updateCourse.save()
            return redirect('Courses')

        departments = Department.objects.all()
        context = {
            'departments': departments,
            'course': course,
        }

        return render(request, 'course/edit-course.html', context)
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def deleteCourse(request, course_slug):
    if not request.user.is_anonymous and request.user.is_superuser:
        course = Course.objects.get(course_slug=course_slug)
        course.delete()
        return redirect('Courses')
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


# Lessons
def lessons(request):
    if not request.user.is_anonymous and request.user.is_superuser:
        lessons = Lesson.objects.all()
        context = {
            'lessons': lessons,
        }
        return render(request, 'lesson/lessons.html', context)
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def lessonDetails(request, lesson_slug):
    if not request.user.is_anonymous and request.user.is_superuser:
        lesson = Lesson.objects.get(lesson_slug=lesson_slug)

        # Getting Average rating for lesson
        lesson_ratings = avgRating(lesson)

        no_of_ratings = len(LessonReview.objects.filter(lesson=lesson))

        context = {
            'lesson': lesson,
            'lesson_ratings': lesson_ratings,
            'no_of_ratings': no_of_ratings,
        }
        return render(request, 'lesson/lesson-details.html', context)
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def updateLesson(request, lesson_slug):
    if not request.user.is_anonymous and request.user.is_superuser:
        lesson = Lesson.objects.get(lesson_slug=lesson_slug)
        if request.method == 'POST':
            lessonForm = LesssonForm(request.POST, instance=lesson)
            if lessonForm.is_valid():
                lesson_title = lessonForm.cleaned_data['lesson_title']
                lesson_desc = lessonForm.cleaned_data['lesson_desc']
                course = lessonForm.cleaned_data['course']
                course = Course.objects.filter(course_name=course).first()

                Lesson(lesson_id=lesson.lesson_id,lesson_title=lesson_title,
                       lesson_desc=lesson_desc, course=course).save()

                return redirect('Lessons')
        else:
            lessonForm = LesssonForm(instance=lesson)

        context = {
            'lessonForm': lessonForm,
        }

        return render(request, 'lesson/edit-lesson.html', context)

    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def deleteLesson(request, lesson_slug):
    if not request.user.is_anonymous and request.user.is_superuser:
        lesson = Lesson.objects.get(lesson_slug=lesson_slug)
        lesson.delete()
        return redirect('Lessons')
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def addLesson(request):
    if not request.user.is_anonymous and request.user.is_superuser:
        if request.method == 'POST':
            lessonForm = LesssonForm(request.POST)
            if lessonForm.is_valid():
                lesson_title = lessonForm.cleaned_data['lesson_title']
                lesson_desc = lessonForm.cleaned_data['lesson_desc']
                course = lessonForm.cleaned_data['course']
                course = Course.objects.filter(course_name=course).first()

                Lesson(lesson_title=lesson_title,
                       lesson_desc=lesson_desc, course=course).save()

                return redirect('Lessons')
        else:
            lessonForm = LesssonForm()

        context = {
            'lessonForm': lessonForm,
        }
        return render(request, 'lesson/add-lesson.html', context)
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')
    


# Queries
def queries(request):
    if not request.user.is_anonymous and request.user.is_superuser:
        queries = Query.objects.all()
        context = {
            'queries': queries,
        }
        return render(request, 'queries/queries.html', context)
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def queryDetails(request, query_slug):
    if not request.user.is_anonymous and request.user.is_superuser:
        query = Query.objects.get(query_slug=query_slug)

        context = {
            'query': query,
            
        }
        return render(request, 'queries/query-details.html', context)
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def updateQuery(request, query_slug):
    if not request.user.is_anonymous and request.user.is_superuser:
        query = Query.objects.get(query_slug=query_slug)
        if request.method == 'POST':
            queryForm = QueryForm(request.POST, instance=query)
            if queryForm.is_valid():
                query_title = queryForm.cleaned_data['query_title']
                query_desc = queryForm.cleaned_data['query_desc']
                course = queryForm.cleaned_data['course']
                course = Course.objects.filter(course_name=course).first()

                query.query_title = query_title
                query.query_desc = query_desc
                query.course = course
                query.save()
                # Query(query_id=query.query_id, query_title=query_title,
                #        query_desc=query_desc, course=course, user=request.user, created).save()

                return redirect('Queries')
        else:
            queryForm = QueryForm(instance=query)

        context = {
            'queryForm': queryForm,
        }

        return render(request, 'queries/edit-query.html', context)

    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def deleteQuery(request, query_slug):
    if not request.user.is_anonymous and request.user.is_superuser:
        query = Query.objects.get(query_slug=query_slug)
        query.delete()
        return redirect('Queries')
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def addQuery(request):
    if not request.user.is_anonymous and request.user.is_superuser:
        if request.method == 'POST':
            queryForm = QueryForm(request.POST)
            if queryForm.is_valid():
                query_title = queryForm.cleaned_data['query_title']
                query_desc = queryForm.cleaned_data['query_desc']
                course = queryForm.cleaned_data['course']
                course = Course.objects.filter(course_name=course).first()

                Query(query_title=query_title,
                       query_desc=query_desc, course=course, user=request.user).save()

                return redirect('Queries')
        else:
            queryForm = QueryForm()

        context = {
            'queryForm': queryForm,
        }
        return render(request, 'queries/add-query.html', context)
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


# Answers
def answers(request):
    if not request.user.is_anonymous and request.user.is_superuser:
        answers = Answer.objects.all()
        context = {
            'answers': answers,
        }
        return render(request, 'answers/answers.html', context)
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


# Search 
def handleMainSearch(request):
    if not request.user.is_anonymous and request.user.is_superuser:
        if request.method == 'GET':
            search_query = request.GET.get('search-query')
            search_for = request.GET.get('search-for')
            departments = []
            courses = []
            lessons = []
            queries = []
            answers = []

            if len(search_query) >= 30:
                messages.error(request, f"Can't show results for '{search_query}'" )
            else:
                if search_for == 'department':
                    departments = Department.objects.filter(dep_name__icontains=search_query)
                    
                elif search_for == 'course':
                    courses = Course.objects.filter(course_name__icontains=search_query)

                elif search_for == 'lesson':
                    lessons = Lesson.objects.filter(lesson_title__icontains=search_query)

                elif search_for == 'query':
                    queries = Query.objects.filter(query_title__icontains=search_query)

                elif search_for == 'answer':
                    answers = Answer.objects.filter(ans_desc__icontains=search_query)

                else :
                    departments = Department.objects.filter(dep_name__icontains=search_query)
                    courses = Course.objects.filter(course_name__icontains=search_query)
                    lessons = Lesson.objects.filter(lesson_title__icontains=search_query)
                    queries = Query.objects.filter(query_title__icontains=search_query)
                    answers = Answer.objects.filter(ans_desc__icontains=search_query)
               

        context={
            'search_query' : search_query,
            'departments':departments,
            'courses':courses,
            'lessons':lessons,
            'queries':queries,
            'answers':answers,
        }
        return render(request, 'search-main.html', context)
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')
    
# Just a template for new function
def Template(request):
    if not request.user.is_anonymous and request.user.is_superuser:
        
        return render(request, 'search-main.html')
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')
# ========================================


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
