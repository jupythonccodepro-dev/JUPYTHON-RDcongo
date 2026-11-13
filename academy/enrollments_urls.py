from django.urls import path
from .enrollments_api import (
    EnrollAPIView,
    EnrollmentProgressAPIView,
    LessonProgressAPIView,
    LessonPracticeSubmissionAPIView,
    ModuleQuizAPIView,
    MyEnrollmentsAPIView,
)

urlpatterns = [
    path('enroll/', EnrollAPIView.as_view()),
    path('my/', MyEnrollmentsAPIView.as_view()),
    path('<int:enrollment_id>/progress/', EnrollmentProgressAPIView.as_view()),
    path('lessons/<int:lesson_id>/progress/', LessonProgressAPIView.as_view()),
    path('lessons/<int:lesson_id>/practice/', LessonPracticeSubmissionAPIView.as_view()),
    path('modules/<int:module_id>/quiz/', ModuleQuizAPIView.as_view()),
]
