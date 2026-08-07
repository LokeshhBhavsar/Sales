from django.urls import path

from apps.accounts.view.login_view import LoginView
from apps.accounts.view.refresh_token_view import RefreshTokenView
from apps.accounts.view.logout_view import LogoutView
from apps.accounts.view.permission_view import (
    PermissionView,
    PermissionListAPIView
)
from apps.accounts.view.role_view import (
    RoleCreateView,
    RoleListView,
    RoleDetailView,
)
from apps.accounts.view.role_permission_view import (
    RolePermissionView,
   
)

from apps.accounts.view.user_permission_view import (
    UserPermissionView,
)


from apps.accounts.view.role_view import RoleCreateView, RoleListView

app_name = "accounts"

urlpatterns = [
    path(
        "/login",
        LoginView.as_view(),
        name="login",
    ),
    path(
        "/refresh-token",
        RefreshTokenView.as_view(),
        name="refresh-token",
    ),
    path(
        "/logout",
        LogoutView.as_view(),
        name="logout"
    ),

    # =====================================================
    # Permission Management
    # =====================================================

    path(
        "/create-permissions/",
        PermissionView.as_view(),
        name="permission-list-create",
    ),

    path(
        "/permissions/",
        PermissionListAPIView.as_view(),
        name="permission-list",
    ),

    # =====================================================
    # Role Permission Management
    # =====================================================

    path(
        "/roles/permissions/",
        RolePermissionView.as_view(),
        name="role-permission-list-create",
    ),

    # =====================================================
    # User Permission Management
    # =====================================================

    path(
        "users/permissions/",
        UserPermissionView.as_view(),
        name="user-permission-list-create",
    ),
      path(
        "/roles",
        RoleCreateView.as_view(),
        name="role-create",
    ),

    # List Roles
    path(
        "/roles/list/",
        RoleListView.as_view(),
        name="role-list",
    ),

    # Get / Update / Delete Role
    path(
        "/roles/<uuid:role_id>/",
        RoleDetailView.as_view(),
        name="role-detail",
    ), 
]
