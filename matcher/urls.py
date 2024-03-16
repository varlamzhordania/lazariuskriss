from django.urls import path
from .views import MatcherView

app_name = 'matcher'

urlpatterns = [
    path('matcher/', MatcherView.as_view(),name="matcher")
]
