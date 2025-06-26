from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('register/', views.client_register, name='client_register'),
    path('login/', views.client_login, name='client_login'),
    path('logout/', views.custom_logout, name='logout'),

    path('person/register/', views.register_person, name='register_person'),
    path('people/', views.person_list, name='person_list'),
    path('people/<int:person_id>/', views.person_detail, name='person_detail'),

    path('event/create/', views.create_event, name='create_event'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),

    path('profile/', views.profile_view, name='profile'),
    path('tags/', views.tag_list, name='tag_list'),
    path('tags/create/', views.tag_create, name='tag_create'),
    path('tags/<int:tag_id>/edit/', views.tag_edit, name='tag_edit'),
    path('tags/<int:tag_id>/delete/', views.tag_delete, name='tag_delete'),


    path('notes/<int:client_id>/', views.client_notes, name='client_notes'),
    path('notes/<int:client_id>/add/', views.add_note, name='add_note'),
    path('calendar/', views.calendar_view, name='calendar'),
]