from django.urls import path

from apps.hrms.views.user_view import (
    UserCreateView,
)

from apps.hrms.views.skill_view import (
    SkillListCreateView,
    SkillDetailView
)

from apps.hrms.views.department_skill_view import (
    DepartmentSkillListCreateView
)

from apps.hrms.views.employee_skill_view import (
    EmployeeSkillListCreateView,
    EmployeeSkillDetailView
)

from apps.hrms.views.skill_matrix_view import (
    EmployeeSkillMatrixView,
    DepartmentSkillMatrixView
)

urlpatterns = [

    # User
    path(
        "/users/create/",
        UserCreateView.as_view(),
        name="user-create",
    ),
    path(
        "skills/",
        SkillListCreateView.as_view(),
        name="skill-list-create"
    ),

    path(
        "skills/<uuid:skill_id>/",
        SkillDetailView.as_view(),
        name="skill-detail"
    ),

    # =====================================================
    # DEPARTMENT SKILLS
    # =====================================================

    path(
        "department-skills/",
        DepartmentSkillListCreateView.as_view(),
        name="department-skill-list-create"
    ),

    # =====================================================
    # EMPLOYEE SKILLS
    # =====================================================

    path(
        "employee-skills/",
        EmployeeSkillListCreateView.as_view(),
        name="employee-skill-list-create"
    ),

    path(
        "employee-skills/<uuid:skill_id>/",
        EmployeeSkillDetailView.as_view(),
        name="employee-skill-detail"
    ),

    # =====================================================
    # SKILL MATRIX
    # =====================================================

    path(
        "employees/<uuid:employee_id>/skill-matrix/",
        EmployeeSkillMatrixView.as_view(),
        name="employee-skill-matrix"
    ),

    path(
        "departments/<uuid:department_id>/skill-matrix/",
        DepartmentSkillMatrixView.as_view(),
        name="department-skill-matrix"
    ),

]