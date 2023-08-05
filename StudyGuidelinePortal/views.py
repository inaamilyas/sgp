
from django.http import JsonResponse
import requests
from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib import messages
import uuid
from django.conf import settings
from django.core.mail import send_mail
from django.views.decorators.cache import cache_control
from .recomm3 import LRS
from urllib.parse import urlparse


# Create your views here.
# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home(request):

    rec_courses = set()
    rec_lessons = []
    latest_lessons = Lesson.objects.all().order_by('-time')

    # Recommendation code 
    rec_obj = LRS()
    if not request.user.is_anonymous:
        # make recommendations 
        for lesson_id in rec_obj.user_interest_recomm(request.user.id):
            lesson = Lesson.objects.filter(lesson_id=lesson_id).first()
            if lesson:
                rec_lessons.append(lesson)
                rec_courses.add(lesson.course)

    popular_lessons_ids=rec_obj.popular_recomm()
    popu_lessons = []
    for lesson_id in popular_lessons_ids:
            lesson = Lesson.objects.filter(lesson_id=lesson_id).first()
            if lesson:
                popu_lessons.append(lesson)

    # rec_lessons = Lesson.objects.all()
    # popu_lessons = Lesson.objects.all()
    # rec_courses = Course.objects.all()


    context = {
        'rec_lesson_details': map_lesson_details(rec_lessons),
        'latest_less_details': map_lesson_details(latest_lessons),
        'popu_lesson_details': map_lesson_details(popu_lessons),
        'rec_course_details': map_course_details(rec_courses),
    }
    return render(request, 'index.html', context)


def courses(request):
    all_courses = Course.objects.all()

    popu_courses = []
    for course in all_courses:
        first_lesson = None
        # if there is any lesson then get it
        no_of_lessons = len(Lesson.objects.filter(course=course))
        if (no_of_lessons > 0):
            first_lesson = Lesson.objects.filter(
                course=course).first().lesson_slug

        popu_courses.append([course, first_lesson])

    context = {
        'course_details': map_course_details(all_courses),
        'popu_courses': popu_courses,
    }
    return render(request, 'courses.html', context)


# Count lesson views
def countLessonViews(request, lesson_slug):
    lesson_details = Lesson.objects.get(lesson_slug=lesson_slug)
    # Counting views for lesson
    lesson_details.views = lesson_details.views+1
    lesson_details.save()

    context = {
        'lesson_views': lesson_details.views,
    }
    return JsonResponse(context)


def courseLesson(request, course_name, lesson_name):
    lesson_details = Lesson.objects.get(lesson_slug=lesson_name)
    course_lessons = Lesson.objects.filter(course=lesson_details.course)

    # Getting Average rating for lesson
    lesson_ratings = avgRating(lesson_details)

    # Number of Reviews
    review_count = len(LessonReview.objects.filter(lesson=lesson_details))

    # Getting specific user rating on the lesson
    try:
        user_rating = LessonReview.objects.get(
            user=request.user, lesson=lesson_details).rate
    except Exception as e:
        user_rating = 0

    # Finding Previous and Next Lesson
    prev_lesson = None
    next_lesson = None
    for i in range(0, len(course_lessons)):
        if course_lessons[i].lesson_id == lesson_details.lesson_id:
            if i > 0:
                prev_lesson = course_lessons[i-1]
            if i < len(course_lessons)-1:
                next_lesson = course_lessons[i+1]

    # Similar lessons
    # similar_lessons = Lesson.objects.all()
    similar_lessons = []
    lrs = LRS()
    lrs_simil = lrs.similarity_recomm(lesson_details.lesson_id)
    if lrs_simil:
        for lesson_id in lrs_simil:
            lesson = Lesson.objects.filter(lesson_id=lesson_id).first()
            if lesson:
                similar_lessons.append(lesson)


    # Latest lessons (- is used to reverse the order)
    latest_lessons = Lesson.objects.all().order_by('-time')[:6]

    # Links
    links = SimilarLinks.objects.filter(lesson=lesson_details.lesson_id)

    website_info = []
    if links:
        for link in links:
            web_name = extract_main_url(link.link_url)
            website_info.append([link, web_name])

    context = {
        'lesson_details': lesson_details,
        'lesson_slug': lesson_details.lesson_slug,
        'lesson_ratings': lesson_ratings,
        'review_count': review_count,
        'user_rating': user_rating,
        'course_lessons': course_lessons,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'similar_lessons_details': map_lesson_details(similar_lessons),
        'latest_lessons_details': latest_lessons,
        'website_info': website_info,
    }

    return render(request, 'all-lessons.html', context)


def queries(request):
    all_queries = Query.objects.all()
    total_queries = len(Query.objects.all())
    total_answers = len(Answer.objects.all())
    queries = []
    for query in all_queries:
        answer_count = len(Answer.objects.filter(query=query))
        queries.append([query, answer_count])

    context = {
        'queries': queries,
        'total_queries': total_queries,
        'total_answers': total_answers,
        'type': 'All',
    }
    return render(request, 'queries.html', context)


def latQueries(request):
    latest_queries = Query.objects.all().order_by('-created_at')

    total_queries = len(Query.objects.all())
    total_answers = len(Answer.objects.all())
    queries = []
    for query in latest_queries:
        answer_count = len(Answer.objects.filter(query=query))
        queries.append([query, answer_count])

    context = {
        'queries': queries,
        'total_queries': total_queries,
        'total_answers': total_answers,
        'type': 'Latest',
    }

    return render(request, 'queries.html', context)


def popuQueries(request):
    popular_queries = Query.objects.all()

    total_queries = len(Query.objects.all())
    total_answers = len(Answer.objects.all())

    queries = []
    for query in popular_queries:
        answer_count = len(Answer.objects.filter(query=query))
        queries.append([query, answer_count])

    context = {
        'queries': queries,
        'total_queries': total_queries,
        'total_answers': total_answers,
        'type': 'Popular',
    }

    return render(request, 'queries.html', context)


@login_required
def askQuery(request):
    if request.method == 'POST':
        queryForm = QueryForm(request.POST)
        if queryForm.is_valid():
            query_title = queryForm.cleaned_data['query_title']
            query_desc = queryForm.cleaned_data['query_desc']
            course = queryForm.cleaned_data['course']
            # query_slug = queryForm.cleaned_data['query_slug']
            user = request.user

            newQuery = Query(query_title=query_title, query_desc=query_desc,
                             course=course, user=user)
            newQuery.save()
            return redirect('/queries')

    else:
        queryForm = QueryForm()

    context = {
        'queryForm': queryForm,
    }
    return render(request, 'ask-query.html', context)


def queryDetails(request, query_slug):
    query = Query.objects.get(query_slug=query_slug)
    answers = Answer.objects.filter(query=query)

    total_queries = len(Query.objects.all())
    total_answers = len(Answer.objects.all())

    ans_like_count = []
    for answer in answers:
        total_likes = len(Like.objects.filter(answer=answer))

        # Checking user liked answer or not
        is_liked = False
        if (not request.user.is_anonymous):
            if Like.objects.filter(answer=answer, user=request.user).first():
                is_liked = True

        ans_like_count.append([answer, total_likes, is_liked])

    context = {
        'query': query,
        'answers': answers,
        'ans_like_count': ans_like_count,
        'total_queries': total_queries,
        'total_answers': total_answers,
        'ansForm': AnswerForm()
    }
    return render(request, 'answers.html', context)


# Count query views
def countQueryViews(request, query_slug):
    query = Query.objects.get(query_slug=query_slug)
    # Counting views for lesson
    query.views = query.views+1
    query.save()

    context = {
        'query_views': query.views,
    }
    return JsonResponse(context)


@login_required
def editQuery(request, query_slug):
    query = Query.objects.get(query_slug=query_slug)
    if request.method == 'POST':
        queryForm = QueryForm(request.POST, instance=query)
        if queryForm.is_valid():
            query_title = queryForm.cleaned_data['query_title']
            query_desc = queryForm.cleaned_data['query_desc']
            course = queryForm.cleaned_data['course']
            # user = request.user
            # Query(query_id=query.query_id, query_title=query_title, query_desc=query_desc,
            #       course=course, user=user, created_at=query.created_at).save()
            query.query_title = query_title
            query.query_desc = query_desc
            query.course = course
            query.save()
            return redirect(f'/query/{query_slug}/')
    else:
        queryForm = QueryForm(instance=query)
    context = {
        'queryForm': queryForm
    }

    return render(request, 'update-query.html', context)


@login_required
def delQuery(request, query_slug):
    query = Query.objects.get(query_slug=query_slug)

    query.delete()
    # Message success
    return redirect('/queries')


@login_required
def addAnswer(request, query_slug):
    query = Query.objects.get(query_slug=query_slug)
    user = request.user
    if request.method == 'POST':
        ansForm = AnswerForm(request.POST)
        if ansForm.is_valid():
            ans_desc = ansForm.cleaned_data['ans_desc']

            Answer(ans_desc=ans_desc, user=user, query=query).save()
            return redirect(f'/query/{query_slug}/')

    # Message success
    return redirect(f'/query/{query_slug}/')


@login_required
def editAnswer(request, answer_id):
    answer = Answer.objects.get(ans_id=answer_id)
    # user = request.user
    if request.method == 'POST':
        ansForm = AnswerForm(request.POST, instance=answer)
        if ansForm.is_valid():
            ans_desc = ansForm.cleaned_data['ans_desc']

            # Answer(ans_id=answer_id, ans_desc=ans_desc, user=user,
            #        query=answer.query, created_at=answer.created_at).save()
            answer.ans_desc = ans_desc
            answer.save()
            return redirect(f'/query/{answer.query.query_slug}/')
    else:
        ansForm = AnswerForm(instance=answer)

    context = {
        'ansForm': ansForm,
    }
    # Message success
    return render(request, 'update-ans.html', context)


@login_required
def delAnswer(request, answer_id):
    answer = Answer.objects.get(ans_id=answer_id)
    query_slug = answer.query.query_slug

    answer.delete()
    # Message success
    return redirect(f'/query/{query_slug}/')


@login_required
def ansLike(request):
    context={}
    if request.method == 'POST':
        ans_id = request.POST.get('ans-id')
        ans = Answer.objects.get(ans_id=ans_id)
        query = Query.objects.get(query_id=ans.query.query_id)
        user = request.user

        if len(Like.objects.filter(user=user, answer=ans)) > 0:
            # print('Already liked')
            Like.objects.get(user=user, answer=ans).delete()

            context = {
                'unliked':True,
            }
        else:
            Like(user=user, answer=ans).save()
            context = {
                'liked':True,
            }
            
    # return redirect(f'/query/{query.query_slug}/')
    return JsonResponse(context)


def sortAnswer(request):
    total_queries = len(Query.objects.all())
    total_answers = len(Answer.objects.all())
    query_slug = ''

    if request.method == 'POST':
        query_slug = request.POST.get('query-slug')
        query = Query.objects.get(query_slug=query_slug)
        sortby = request.POST.get('sortby')
        if sortby == 'likes':
            answers = Answer.objects.filter(query=query)

            ans_like_count = []
            for answer in answers:
                total_likes = len(Like.objects.filter(answer=answer))

                # Checking user liked answer or not
                is_liked = False
                if (not request.user.is_anonymous):
                    if Like.objects.filter(answer=answer, user=request.user).first():
                        is_liked = True

                ans_like_count.append([answer, total_likes, is_liked])

            # sorting list based on likes
            ans_like_count = sortListDesc(ans_like_count, 1)

        else:
            answers = Answer.objects.filter(
                query=query).order_by('-created_at')
            ans_like_count = []
            for answer in answers:
                total_likes = len(Like.objects.filter(answer=answer))

                # Checking user liked answer or not
                is_liked = False
                if (not request.user.is_anonymous):
                    if Like.objects.filter(answer=answer, user=request.user).first():
                        is_liked = True

                ans_like_count.append([answer, total_likes, is_liked])

    context = {
        'query': query,
        'answers': answers,
        'ans_like_count': ans_like_count,
        'total_queries': total_queries,
        'total_answers': total_answers,
        'ansForm': AnswerForm(),
    }
    return render(request, 'answers.html', context)


def handleCourseSearch(request):
    # all_courses = Course.objects.all()
    page_heading = "All Featured Courses"
    search_query = ""
    # Search
    course_details = []
    if request.method == 'GET':
        search_query = request.GET.get('search-query')
        print(search_query)
        if len(search_query) >= 30:
            course_details = []
        else:
            result = Course.objects.filter(course_name__icontains=search_query)
            course_details = []
            for course in result:
                first_lesson = None
                # if there is any lesson then get it
                no_of_lessons = len(Lesson.objects.filter(course=course))
                if (no_of_lessons > 0):
                    first_lesson = Lesson.objects.filter(
                        course_id=course.course_id).first().lesson_slug
                no_of_lessons = len(Lesson.objects.filter(
                    course_id=course.course_id))
                course_details.append([course, first_lesson, no_of_lessons])

        page_heading = "Your Search Results : "
        print(course_details)

    context = {
        'course_details': course_details,
        # 'popu_courses': popu_courses,
        'page_heading': page_heading,
        'search_query': search_query,
    }
    return render(request, 'searchcourse.html', context)


def handleSearch(request):
    if request.method == 'GET':
        search_query = request.GET.get('search-query')
        search_for = request.GET.get('search-for')
        departments = []
        courses = []
        lessons = []
        queries = []
        answers = []

        if len(search_query) >= 30:
            messages.error(request, f"Can't show results for '{search_query}'")
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

        if not lessons and not courses:
            messages.warning(request, 'No search results found')

        context = {
            'search_query': search_query,
            'departments': departments,
            'course_details': map_course_details(courses),
            'lesson_details': map_lesson_details(lessons),
            'queries': queries,
            'answers': answers,
        }

    return render(request, 'main_search.html', context)


def handleSignup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')

        # Checking username and email already exist or not
        if (User.objects.filter(username=username).first()):
            messages.error(request, 'Username is taken')
            return redirect('Signup')

        if (User.objects.filter(email=email).first()):
            messages.error(request, 'Email already exist')
            return redirect('Signup')

        if (password != confirm_password):
            messages.error(request, 'Password didnot match')
            return redirect('Signup')

        newUser = User.objects.create_user(username, email, password)
        newUser.first_name = fname
        newUser.last_name = lname
        newUser.save()

        auth_token = str(uuid.uuid4())
        user_profile = Profile(user=newUser, auth_token=auth_token)
        user_profile.save()

        # sendMailAfterVerification(email, auth_token)

        if sendMailAfterVerification(email, auth_token):
            messages.success(
                request, 'Check your mail and verify your account')
            return redirect('Login')

    return render(request, 'register.html')


def verifyEmail(request, auth_token):
    prof_obj = Profile.objects.filter(auth_token=auth_token).first()
    if prof_obj:
        if prof_obj.is_verified:
            messages.success(request, 'Account already verified')
            return redirect('Login')
        else:
            prof_obj.is_verified = True
            prof_obj.save()
            messages.success(request, 'Account has been verified')
            return redirect('Login')
    else:
        print("Porfile does not exist")


def forgetPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user is not None:
            user_profile = Profile.objects.filter(user=user).first()

            auth_token = str(uuid.uuid4())
            Profile(id=user_profile.id, user=user,
                    auth_token=auth_token).save()

            sendVerifiCodeMail(email, auth_token)
            messages.success(request, 'Please check your email')

            context = {
                'user': user,
            }
            return redirect('ChangePassword')
        else:
            messages.error(request, 'Email not found! Try another email')
    return render(request, 'forgetPassword.html')


def changePassword(request):
    if request.method == 'POST':
        # Get form data 
        email = request.POST.get('email')
        verifCode = request.POST.get('verif-code')
        password = request.POST.get('password')
        cpassword = request.POST.get('confirm-password')

        # Finding user against email 
        user = User.objects.filter(email=email).first()
        if user is not None:
            
            user_profile = Profile.objects.filter(
                user=user, auth_token=verifCode).first()
            if (user_profile is not None):

                # Change Password
                user.set_password(password)
                user.save()
                messages.success(request, 'Password changed successfully')
                return redirect('Login')
            else:
                messages.error(request, 'Verification Code is wrong!')
        else:
            messages.error(request, 'Email not found! Try another email')

    return render(request, 'changePassword.html')


def handleLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Checking user is exist or not
        user_obj = User.objects.filter(username=username).first()
        if user_obj is None:
            messages.error(request, 'Username not found...')
            return redirect('Login')

        # Checking user is verified or not
        prof_obj = Profile.objects.filter(user=user_obj).first()
        if not prof_obj.is_verified:
            messages.error(request, 'Account not verified. Check your mail!')
            return redirect('Login')

        # Authenticate user from database
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            next_page = request.GET.get('next')
            if next_page:
                return redirect(next_page)
            return redirect('Home')
        else:
            messages.error(request, 'Wrong username or password. Try again')
            return redirect('Login')

    return render(request, 'login.html')


@login_required
def handleLogout(request):
    logout(request)
    return redirect('Home')


@login_required
def handleLessonReviews(request):
    if request.method == 'GET':
        lesson_id = request.GET.get('lesson_id')
        lesson = Lesson.objects.get(lesson_id=lesson_id)
        rate = request.GET.get('rate')
        user = request.user

        if len(LessonReview.objects.filter(user=user, lesson=lesson)) > 0:
            # update the existing ratings
            existing_review = LessonReview.objects.get(
                user=user, lesson=lesson)
            existing_review.rate = rate 
            existing_review.save()
            # update_review = LessonReview(
            #     id=existing_review.id, user=user, lesson=lesson, rate=rate)
            # update_review.save()
            
            # Send Success Message
        else:
            # Add new ratings
            review = LessonReview(user=user, lesson=lesson, rate=rate)
            review.save()
            # Send Success Message

        course = Course.objects.get(course_id=lesson.course.course_id)
        return redirect(f'/{course.course_slug}/{lesson.lesson_slug}')


# Profile
@login_required
def profile(request):
    user = request.user

    if request.method == 'POST':
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')

        user.first_name = first_name
        user.last_name = last_name
        user.save()

        profile = Profile.objects.get(user=user)
        if 'profile-pic' in request.FILES:
            profile_pic = request.FILES['profile-pic']
            profile.profile_pic = profile_pic
            profile.save()
    profile_pic = Profile.objects.get(user=user).profile_pic
    context = {
        'user': user,
        'profile_pic': profile_pic,
    }
    return render(request, 'profile-page.html', context=context)


def calcLessonWatchTime(request, lesson_slug, watch_time):
    if not request.user.is_anonymous:
        lesson = Lesson.objects.filter(lesson_slug=lesson_slug).first()
        user = request.user
        lessonWatchtime = LessonWatchTime.objects.filter(
            user=user, lesson=lesson).first()

        if lessonWatchtime is not None:

            if (watch_time > int(lessonWatchtime.watch_time)):
                # Update the existing record
                LessonWatchTime(id=lessonWatchtime.id, user=user,
                                lesson=lesson, watch_time=watch_time).save()
                print('Watchtime is saved')
            else:
                print(
                    f'watchtime({watch_time}) is less than {lessonWatchtime.watch_time}')
        else:
            LessonWatchTime(user=user, lesson=lesson,
                            watch_time=watch_time).save()
            print('no previous watchtime found for this lesson and user')
        context = {
            'success':'success',
        }
        # return JsonResponse(context)
    else:
        print('user is not loggedin')
        context={
            'user':'user is not loggedin',
        }

    return JsonResponse(context)


# Handling 404 page error
def handle404Error(request, exception):
    return render(request, '404.html')

# ==============================================


# Scraping Links
def fetchLinks(lesson_title):

    # Making url and search
    url = 'https://google.com/search?q=' + lesson_title
    request_result = requests.get(url)

    # Creating soup from the fetched request
    soup = BeautifulSoup(request_result.text, "html.parser")

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


# Mapping course details
def map_course_details(courses):
    course_details = []
    for course in courses:
        first_lesson = None
        # if there is any lesson then get it
        if (len(Lesson.objects.filter(course=course)) > 0):
            first_lesson = Lesson.objects.filter(course=course)[0].lesson_slug
        no_of_lessons = len(Lesson.objects.filter(course=course))
        course_details.append([course, first_lesson, no_of_lessons])
    return course_details


# Send Mail After Registration
def sendMailAfterVerification(email, auth_token):
    try:
        subject = 'Your account needs to be verified'
        message = f'Hi, click the link to verify your account http://127.0.0.1:8000/verify/email/{auth_token}/'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail(subject, message, email_from, recipient_list)
        print('mail sent')
    except Exception as e:
        print(e)
        print('mail not sent')
    print(message)
    return True


def sendVerifiCodeMail(email, auth_token):
    try:
        subject = 'Password Change Request'
        message = f'Your verification code is : {auth_token}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail(subject, message, email_from, recipient_list)
        print('mail sent')
    except Exception as e:
        print(e)
        print('mail not sent')
    print(message)
    return True

# function to extact main url 
def extract_main_url(full_url):
        parsed_url = urlparse(full_url)
        main_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return main_url