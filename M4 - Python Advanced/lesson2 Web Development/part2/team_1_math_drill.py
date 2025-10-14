"""
Team 1 — Math Drill (Django mini project)
NOTE: This file is guidance only — copy steps into your repo and implement.
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
# Users practice basic arithmetic ( +, -, * small numbers ). Each submission is saved
# and marked correct/incorrect. A dashboard shows quick stats. A history page lists attempts.

# =============================
# DATA MODEL (suggested)
# =============================
# app/models.py — create Problem model
# TODO[A]: implement
# class Problem(models.Model):
#     owner
#     question =  # e.g. "7 + 5"
#     expected
#     submitted
#     was_correct
#     created_at
#     def __str__(self): return f"{self.question} = {self.submitted} ({'✓' if self.was_correct else '✗'})"
# Register in admin.py with list_display, list_filter=("was_correct", "created_at")

# =============================
# REQUIRED PAGES / URLS
# =============================
# '/'            → Dashboard: counts (total, correct, wrong), link to Practice
# '/practice/'   → One problem form (GET shows random problem; POST saves result)
# '/history/'    → Paginated attempts; filter ?result=correct|wrong

# =============================
# STEP-BY-STEP CHECKLIST
# =============================
# TODO[A] MODELS & ADMIN
# - Create Problem model as above
# - python manage.py makemigrations && python manage.py migrate
# - admin.py: register Problem; add list_display, search by question
#
# TODO[B] VIEWS & URLCONF
# - app/urls.py:
#     path('', views.DashboardView.as_view(), name='dashboard')
#     path('practice/', views.practice_view, name='practice')
#     path('history/', views.HistoryView.as_view(), name='history')
# - views:
#   DashboardView(LoginRequired): compute counts via queryset filters
#   practice_view(LoginRequired):
#       GET → generate a,b,op; store expected in hidden field or session; render form
#       POST → read submitted; compute was_correct; create Problem(owner=..., ...); redirect to history
#   HistoryView(LoginRequired, ListView): filter by owner; optional filter by ?result=
# - Protect all with LoginRequiredMixin/decorator
#
# TODO[C] TEMPLATES & UX
# - base.html with nav: Home | Practice | History | Login/Logout (logout as POST form)
# - dashboard.html: show counts + recent 5 attempts
# - practice.html: show the generated question and an input box; include {% csrf_token %}
# - history.html: table with question, submitted, expected, was_correct badge; add filters
# - Optional: flash messages after submissions

# =============================
# ACCEPTANCE CRITERIA
# =============================
# - Auth required for all three pages
# - Practice generates varied questions; submissions persist
# - Dashboard shows correct counts for current user
# - History is scoped to current user; basic filtering works
# - No server errors (run flake if available)

# =============================
# STRETCH (only if time remains)
# =============================
# - Difficulty select (easy/med → number ranges)
# - Operation filter (+, -, *)
# - Show streak on dashboard
