from django.urls import path
from .views import (
    PersonListView, PersonCreateView, EventCreateView, EventDetailView,
    ClientRegisterView, ClientLoginView, CustomLogoutView, ProfileView, TagDeleteView, CalendarView
)

urlpatterns = [
    path('register/', ClientRegisterView.as_view(), name='client_register'),
    path('login/', ClientLoginView.as_view(), name='client_login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    path('person/register/', PersonCreateView.as_view(), name='register_person'),
    path('people/', PersonListView.as_view(), name='person_list'),

    path('event/create/', EventCreateView.as_view(), name='create_event'),
    path('event/<int:pk>/', EventDetailView.as_view(), name='event_detail'),

    path('profile/', ProfileView.as_view(), name='profile'),
    path('tags/<int:pk>/delete/', TagDeleteView.as_view(), name='tag_delete'),

    path('calendar/', CalendarView.as_view(), name='calendar'),

]