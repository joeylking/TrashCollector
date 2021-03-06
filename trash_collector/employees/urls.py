from django.urls import path

from . import views

# TODO: Determine what distinct pages are required for the user stories, add a path for each in urlpatterns

app_name = "employees"
urlpatterns = [
    path('', views.index, name="index"),
    path('new/', views.create, name="create"),
    path('edit_profile/', views.edit_profile, name="edit_profile"),
    path('routes/', views.routes, name="routes"),
    path('daily/<str:day>', views.daily, name="daily"),
    path('serviced/<int:customer_id>/', views.serviced, name="serviced"),
    # path('choose_route/', views.choose_route, name="choose_route"),
]