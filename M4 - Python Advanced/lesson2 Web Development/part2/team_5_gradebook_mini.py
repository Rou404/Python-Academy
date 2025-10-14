"""
Team 5 — Gradebook Mini (Django mini project)
"""

# =============================
# 0) COMMON BOOT-UP RECIPE
# =============================
# 1) Create project & app
#    python -m venv .venv && source .venv/bin/activate
#    pip install "django==5.0.*"
#    django-admin startproject proj
#    cd proj
#    python manage.py startapp app
#
# 2) Wire app & auth
#    settings.py: add 'app' to INSTALLED_APPS
#    urls.py (project):
#       from django.contrib import admin
#       from django.urls import path, include
#       urlpatterns = [
#         path('admin/', admin.site.urls),
#         path('accounts/', include('django.contrib.auth.urls')),
#         path('', include('app.urls')),
#       ]
#    settings.py: LOGIN_URL='/accounts/login/', LOGIN_REDIRECT_URL='/', LOGOUT_REDIRECT_URL='/'
#    templates/registration/login.html: basic login form (Django will render defaults if omitted)
#
# 3) DB & superuser
#    python manage.py makemigrations
#    python manage.py migrate
#    python manage.py createsuperuser
#
# 4) Run
#    python manage.py runserver

# =============================
# PROJECT SUMMARY
# =============================
# Record assignments and grades for students, then show a simple average per student.

# =============================
# DATA MODEL (suggested)
# =============================
# TODO[A] MODELS
# class Student(models.Model):
#     owner
#     name
#     def __str__(self): return self.name
#
# class Assignment(models.Model):
#     owner
#     title
#     max_points
#     def __str__(self): return self.title
#
# class Grade(models.Model):
#     owner
#     student
#     assignment
#     points
#     class Meta:
#         unique_together = ("student","assignment")
#     def __str__(self): return f"{self.student} - {self.assignment}: {self.points}"
# admin.py: register all three; add search and filters

# =============================
# REQUIRED PAGES / URLS
# =============================
# '/'                 → Dashboard: select student (?student=<id>) → table of grades + average (sum(points)/sum(max_points))
# '/students/'        → List + Create student
# '/assignments/'     → List + Create assignment
# '/grades/create/'   → Create grade (student, assignment, points)

# =============================
# STEP-BY-STEP CHECKLIST
# =============================
# TODO[A] MODELS & ADMIN
# - Implement 3 models, run migrations, admin registration
#
# TODO[B] VIEWS & URLCONF
# - app/urls.py: routes for dashboard, students list/create, assignments list/create, grades create
# - Dashboard(LoginRequired):
#     - if ?student=<id>, filter grades by that student & owner
#     - compute average = sum(points)/sum(max_points) where max_points from related assignment
# - CreateViews for Student/Assignment/Grade; set owner in form_valid
# - Owner scoping everywhere
#
# TODO[C] TEMPLATES & UX
# - base.html nav: Dashboard | Students | Assignments | Add Grade | Login/Logout
# - dashboard.html: select student (dropdown) + table of grades + computed average
# - students.html & assignments.html: list + small create form
# - grade_form.html: create grade form

# =============================
# ACCEPTANCE CRITERIA
# =============================
# - Owner scoping enforced
# - Average calculation correct for the selected student
# - Simple CRUD flows with minimal UI

# =============================
# STRETCH
# =============================
# - Class average across all students
# - Sort grades by assignment title or points
