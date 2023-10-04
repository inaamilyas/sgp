from django.views.decorators.cache import cache_control
from bs4 import BeautifulSoup
from django.shortcuts import render, redirect, HttpResponse
import requests
from StudyGuidelinePortal.models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import *
from django.contrib import messages
from .scraper import scraper
from django.http import JsonResponse

from .recommendation import reloadRecommendation
from googleapiclient.discovery import build

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


# @cache_control(no_cache=True, must_revalidate=True, no_store=True)


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
            'dashboard_is_active': True,
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
            'user_is_active': True,
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
            'user_is_active': True,
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
            'user_is_active': True,
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
            'department_is_active': True,
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
            'department_is_active': True,
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
            'department_is_active': True,
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
            'department': department,
            'depForm': depForm,
            'department_is_active': True,
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
            'course_is_active': True,
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
            'course_is_active': True,
        }
        return render(request, 'course/course-details.html', context)
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def addCourse(request):
    if not request.user.is_anonymous and request.user.is_superuser:
        if request.method == 'POST':
            form = CourseForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                reloadRecommendation()
                # Redirect to the course list view
                return redirect('/admin1/courses/')
        else:
            form = CourseForm()
        context = {
            'form': form,
            'course_is_active': True,
        }
        return render(request, 'course/add-course.html', context)
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def updateCourse(request, course_slug):
    if not request.user.is_anonymous and request.user.is_superuser:
        course = Course.objects.get(course_slug=course_slug)
        if request.method == 'POST':
            form = CourseForm(request.POST, request.FILES, instance=course)
            if form.is_valid():
                form.save()
                reloadRecommendation()
                # Redirect to the course list view
                return redirect('/admin1/courses/')
        else:
            form = CourseForm(instance=course)
        context = {
            'form': form,
            'course_is_active': True,
        }
        return render(request, 'course/edit-course.html', context)

    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def deleteCourse(request, course_slug):
    if not request.user.is_anonymous and request.user.is_superuser:
        course = Course.objects.get(course_slug=course_slug)
        course.delete()
        reloadRecommendation()
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
            'lesson_is_active': True,
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
            'lesson_reviews': LessonReview.objects.filter(lesson=lesson),
            'lesson_is_active': True,
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
                lesson_tags = lessonForm.cleaned_data['lesson_tags']
                lesson_summary = lessonForm.cleaned_data['lesson_summary']

                lesson.lesson_title = lesson_title
                lesson.lesson_desc = lesson_desc
                lesson.course = course
                lesson.lesson_summary = lesson_summary
                lesson.lesson_tags = lesson_tags

                lesson.save()
                # Lesson(lesson_id=lesson.lesson_id,lesson_title=lesson_title,
                #    lesson_desc=lesson_desc, course=course).save()
                reloadRecommendation()
                return redirect('Lessons')
        else:
            lessonForm = LesssonForm(instance=lesson)

        context = {
            'lessonForm': lessonForm,
            'lesson_is_active': True,
        }

        return render(request, 'lesson/edit-lesson.html', context)

    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def deleteLesson(request, lesson_slug):
    if not request.user.is_anonymous and request.user.is_superuser:
        lesson = Lesson.objects.get(lesson_slug=lesson_slug)
        lesson.delete()
        reloadRecommendation()
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
                lesson_summary = lessonForm.cleaned_data['lesson_summary']
                lesson_tags = lessonForm.cleaned_data['lesson_tags']

                Lesson(lesson_title=lesson_title,
                       lesson_desc=lesson_desc, course=course, lesson_summary=lesson_summary, lesson_tags=lesson_tags).save()

                newLesson = Lesson.objects.filter(
                    lesson_title=lesson_title).first()
                reloadRecommendation()
                links = scraper(newLesson.lesson_title)
                youtube_videos = get_youtube_videos(newLesson.lesson_title)

                context = {
                    "list_of_links": links,
                    'youtube_videos':youtube_videos,
                    'lesson': newLesson
                }
    
                return render(request, 'links/view-generated-link.html', context)
        else:
            lessonForm = LesssonForm()

        context = {
            'lessonForm': lessonForm,
            'lesson_is_active': True,
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
            'queries_is_active': True,
        }
        return render(request, 'queries/queries.html', context)
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def queryDetails(request, query_slug):
    if not request.user.is_anonymous and request.user.is_superuser:
        query = Query.objects.get(query_slug=query_slug)
        answers = Answer.objects.filter(query=query)
        ansForm = AnswerForm(request.POST)

        ans_like_count = []
        for answer in answers:
            total_likes = len(Like.objects.filter(answer=answer))
            ans_like_count.append([answer, total_likes])

        context = {
            'query': query,
            'queries_is_active': True,
            'ans_like_count':ans_like_count,
            'ansForm':ansForm,
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
            'queries_is_active': True,
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
            'queries_is_active': True,
        }
        return render(request, 'queries/add-query.html', context)
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


# Answers
def addAnswer(request, query_slug):
    if not request.user.is_anonymous and request.user.is_superuser:
        query = Query.objects.get(query_slug=query_slug)
        user = request.user
        if request.method == 'POST':
            ansForm = AnswerForm(request.POST)
            if ansForm.is_valid():
                ans_desc = ansForm.cleaned_data['ans_desc']
                Answer(ans_desc=ans_desc, query=query, user=user).save()
                print('answer is saved')
                return redirect(f'/admin1/query-details/{query_slug}')
        else:
            ansForm = AnswerForm()

        context = {
            'ansForm': ansForm,
            'queries_is_active': True,
        }
        return render(request, 'queries/add-answer.html', context)
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')
    

def updateAnswer(request, answer_id):
    if not request.user.is_anonymous and request.user.is_superuser:
        answer = Answer.objects.get(ans_id=answer_id)
        if request.method == 'POST':
            ansForm = AnswerForm(request.POST, instance=answer)
            if ansForm.is_valid():
                ans_desc = ansForm.cleaned_data['ans_desc']
                answer.ans_desc = ans_desc
                answer.save()
                return redirect(f'/admin1/query-details/{answer.query.query_slug}')
        else:
            ansForm = AnswerForm(instance=answer)

        context = {
            'ansForm': ansForm,
        }
        # Message success
        return render(request, 'queries/edit-answer.html', context)
       
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def deleteAnswer(request, answer_id):
    if not request.user.is_anonymous and request.user.is_superuser:
        answer = Answer.objects.get(ans_id=answer_id)
        query_slug = answer.query.query_slug

        answer.delete()
        # Message success
        return redirect(f'/admin1/query-details/{query_slug}')
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')



# Similar Links
def similarLinks(request):
    if not request.user.is_anonymous and request.user.is_superuser:
        links = SimilarLinks.objects.all()
        context = {
            'links': links,
            'link_is_active': True,
        }
        return render(request, 'links/links.html', context)
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def updateLink(request, link_id):
    if not request.user.is_anonymous and request.user.is_superuser:
        link = SimilarLinks.objects.get(link_id=link_id)
        if request.method == 'POST':
            link_title = request.POST.get('link_title')
            link_url = request.POST.get('link_url')

            link.link_title = link_title
            link.link_url = link_url
            link.save()
            messages.success(request, "Link updated successfully")
            return redirect('SimilarLinks')

        context = {
            'link': link,
            'queries_is_active': True,
        }

        return render(request, 'links/edit-link.html', context)

    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def deleteLink(request, link_id):
    if not request.user.is_anonymous and request.user.is_superuser:
        link = SimilarLinks.objects.get(link_id=link_id)
        link.delete()
        return redirect('SimilarLinks')
    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def addLink(request):
    if not request.user.is_anonymous and request.user.is_superuser:
        if request.method == 'POST':
            lesson_slug = request.POST.get('lesson_slug')
            lesson = Lesson.objects.filter(lesson_slug=lesson_slug).first()
            links = scraper(lesson.lesson_title)
            youtube_videos = get_youtube_videos(lesson.lesson_title)
            context = {
                "list_of_links": links, 
                'youtube_videos':youtube_videos,
                'lesson': lesson,
            }
            return render(request, 'links/view-generated-link.html', context)

        context = {
            'lesson_list': Lesson.objects.filter(),
            'queries_is_active': True,
        }

        return render(request, 'links/add-link.html', context)

    else:
        messages.error(request, 'Acess denied. Try again')
        return redirect('AdminLogin')


def saveLinkToDb(request):
    if request.method == "POST":
        form_data = request.POST
        link_title = form_data['link_title']
        link_url = form_data['link_url']
        lesson_slug = form_data['lesson_slug']
        lesson = Lesson.objects.filter(lesson_slug=lesson_slug).first()

        if not SimilarLinks.objects.filter(link_title=link_title, link_url=link_url, lesson=lesson):
            SimilarLinks(link_title=link_title, link_url=link_url, lesson=lesson).save()
            response_data = {"success": "form data received successfully"}
        else:
            response_data = {"error": "Something went wrong"}

        return JsonResponse(response_data)
    
def saveVideoToDb(request):
    if request.method == "POST":
        form_data = request.POST
        video_title = form_data['video_title']
        video_id = form_data['video_id']
        lesson_slug = form_data['lesson_slug']
        lesson = Lesson.objects.filter(lesson_slug=lesson_slug).first()
        print("inside video save")
        if not YoutubeVideos.objects.filter(video_id=video_id, lesson=lesson):
            YoutubeVideos(video_title=video_title, video_id=video_id, lesson=lesson).save()
            response_data = {"success": "form data received successfully"}
        else:
            response_data = {"error": "Something went wrong"}

        return JsonResponse(response_data)


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
                messages.error(
                    request, f"Can't show results for '{search_query}'")
            else:
                if search_for == 'department':
                    departments = Department.objects.filter(
                        dep_name__icontains=search_query)

                elif search_for == 'course':
                    courses = Course.objects.filter(
                        course_name__icontains=search_query)

                elif search_for == 'lesson':
                    lessons = Lesson.objects.filter(
                        lesson_title__icontains=search_query)

                elif search_for == 'query':
                    queries = Query.objects.filter(
                        query_title__icontains=search_query)

                elif search_for == 'answer':
                    answers = Answer.objects.filter(
                        ans_desc__icontains=search_query)

                else:
                    departments = Department.objects.filter(
                        dep_name__icontains=search_query)
                    courses = Course.objects.filter(
                        course_name__icontains=search_query)
                    lessons = Lesson.objects.filter(
                        lesson_title__icontains=search_query)
                    queries = Query.objects.filter(
                        query_title__icontains=search_query)
                    answers = Answer.objects.filter(
                        ans_desc__icontains=search_query)

        context = {
            'search_query': search_query,
            'departments': departments,
            'courses': courses,
            'lessons': lessons,
            'queries': queries,
            'answers': answers,
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


# Scraping Links
def fetchLinks(lesson_title):

    # Making url and search
    url = 'https://google.com/search?q=' + lesson_title
    request_result = requests.get(url)

    # Creating soup from the fetched request
    soup = BeautifulSoup(request_result.text, "html.parser")
    print(soup)
    # all major headings of our search result,
    heading_object = soup.find_all('h3')

    # Links relative to each heading
    link_object = soup.find_all('h3')

    # Getting href of link
    rawlinks = []
    for rawlink in link_object:
        link = rawlink.previous_element.previous_element.previous_element.get(
            'href')
        rawlinks.append(link)

    # Extracting the main url
    link_object = []
    for rawlink in rawlinks:
        if rawlink:
            link = ''
            for ch in rawlink:
                if ch == '&':
                    break
                else:
                    link = link+ch
            link_object.append(link[7:])

    # Mapping heading with links
    linksInfo = []
    for index in range(len(heading_object)):
        list = []
        list.append(heading_object[index].getText())
        list.append(link_object[index])

        linksInfo.append(list)

    return linksInfo


def get_youtube_videos(lesson_title):
    # Set up your YouTube API key
    api_key = 'AIzaSyDJI918prWCbljfoB6AvEpQEeLggLzmv4I'

    # Create a YouTube API client
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Perform a YouTube search
    search_response = youtube.search().list(
        q=lesson_title,
        type='video',
        part='id',
        maxResults=5  # Adjust the number of results as needed
    ).execute()

    # Extract video IDs from the search results
    video_ids = [item['id']['videoId'] for item in search_response['items']]

    # Retrieve video titles
    video_with_titles = []
    for video_id in video_ids:
        video_details = youtube.videos().list(
            part='snippet',
            id=video_id
        ).execute()
        video_with_titles.append([video_id,video_details['items'][0]['snippet']['title']])

    return video_with_titles