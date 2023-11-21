from rest_framework import serializers
from .models import *
from django.db.models import Avg
from bs4 import BeautifulSoup

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
    first_lesson_slug = serializers.SerializerMethodField()
    no_of_lessons = serializers.SerializerMethodField()
    department_info = serializers.SerializerMethodField()
    # course_pic = serializers.SerializerMethodField()

    def get_department_info(self, obj):
        # Retrieve the department information for the course
        departments = obj.department.all()
        return DepartmentSerializer(departments, many=True).data

    def get_first_lesson_slug(self, obj):
        firstLesson = Lesson.objects.filter(course=obj).first()
        if(firstLesson):
            return firstLesson.lesson_slug
        else:
            return None
    
    def get_no_of_lessons(self, obj):
        return Lesson.objects.filter(course=obj).count()
    
    # def get_course_pic(self, obj):
    #     request = self.context.get('request')
    #     if obj.course_pic:
    #         return request.build_absolute_uri(obj.course_pic.url)
    #     return None
    
    

class LessonSerializer(serializers.ModelSerializer):
    lesson_desc = serializers.SerializerMethodField()
    class Meta:
        model = Lesson
        fields = '__all__'

    lesson_avg_ratings = serializers.SerializerMethodField()
    course = CourseSerializer()


    def get_lesson_avg_ratings(self, lesson):
        avg_rating = LessonReview.objects.filter(lesson=lesson).aggregate(Avg('rate'))['rate__avg']
        return avg_rating if avg_rating is not None else 0
    
    def get_course(self, course):
        return Course.objects.filter(course=course).first()
    
    def get_lesson_desc(self, obj):
        # Parse the HTML description using BeautifulSoup
        soup = BeautifulSoup(obj.lesson_desc , 'html.parser')

        # Find the first two <p> tags and extract their text
        paragraphs = soup.find_all('p')[:2]
        lesson_desc = ' '.join(p.get_text() for p in paragraphs)
        return lesson_desc
    
class YoutubeVideosSerializer(serializers.ModelSerializer):
    class Meta:
        model = YoutubeVideos
        fields = '__all__'


class SimilarLinksSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimilarLinks
        fields = '__all__'



class LessonDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'

    lesson_avg_ratings = serializers.SerializerMethodField()
    similar_links = serializers.SerializerMethodField()
    youtube_videos = serializers.SerializerMethodField()


    def get_lesson_avg_ratings(self, lesson):
        avg_rating = LessonReview.objects.filter(lesson=lesson).aggregate(Avg('rate'))['rate__avg']
        return avg_rating if avg_rating is not None else 0
    
    def get_similar_links(self, lesson):
        similar_links = SimilarLinks.objects.filter(lesson=lesson)
        similar_links_data = SimilarLinksSerializer(similar_links, many=True).data
        return similar_links_data
    
    def get_youtube_videos(self, lesson):
        youtube_videos = YoutubeVideos.objects.filter(lesson=lesson)
        youtube_videos_data = YoutubeVideosSerializer(youtube_videos, many=True).data
        return youtube_videos_data
    
    


class LessonReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonReview
        fields = '__all__'

class LessonWatchTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonWatchTime
        fields = '__all__'
