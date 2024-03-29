# urls.py

from django.urls import path
from .views import shadow_analysis, visualize_shadow_matrix, superimpose_shadow_matrix, generate_shadow_matrix

urlpatterns = [
    path('', generate_shadow_matrix, name='generate-shadow-matrix'),
    path('shadow-analysis/', shadow_analysis, name='shadow-analysis'),
    path('visualize-shadow-matrix/', visualize_shadow_matrix, name='visualize-shadow-matrix'),
    path('superimpose-shadow-matrix/', superimpose_shadow_matrix, name='superimpose-shadow-matrix'),
]
