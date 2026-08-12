from django.urls import path

from apps.hrms.views.user_view import (
    UserCreateView,
)


urlpatterns = [

    # User
    path(
        "/users/create/",
        UserCreateView.as_view(),
        name="user-create",
    ),

]