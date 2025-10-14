"""
Team 3 — Car Parts Catalog (Django mini project)
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
# Browse a catalog of parts associated with car models. Users maintain their own parts.

# =============================
# DATA MODEL (suggested)
# =============================
# TODO[A] MODELS
# class CarModel(models.Model):
#     name
#     year_start
#     year_end
#     def __str__(self):
#         return f"{self.name} ({self.year_start}–{self.year_end or '…'})"
#
# class Part(models.Model):
#     owner
#     name
#     code
#     car_model
#     price
#     in_stock
#     created_at
#     def __str__(self): return f"{self.name} ({self.code})"
# admin.py: register both with filters (car_model, in_stock), search (name, code)

# =============================
# REQUIRED PAGES / URLS
# =============================
# '/'               → Parts list with dropdown filter by car model (?model=<id>) and in_stock checkbox
# '/parts/create/'  → Create part
# '/parts/<id>/'    → Detail (edit/delete links)
# '/parts/<id>/update/', '/parts/<id>/delete/'
# '/models/'        → (optional) list/create CarModel entries

# =============================
# STEP-BY-STEP CHECKLIST
# =============================
# TODO[A] MODELS & ADMIN
# - Implement CarModel, Part. Run migrations.
# - Admin: search_fields, list_filter including car_model, in_stock, created_at
#
# TODO[B] VIEWS & URLCONF
# - app/urls.py for list/detail/create/update/delete (+ optional models list/create)
# - ListView.get_queryset(): owner-scoped; filter by ?model and ?in_stock=1
# - Create/Update CBVs: set owner in form_valid; protect with LoginRequiredMixin
#
# TODO[C] TEMPLATES & UX
# - base.html with nav: Parts | Add Part | Models | Login/Logout
# - parts_list.html with select of car models + in-stock checkbox
# - part_detail.html, part_form.html, part_confirm_delete.html
# - Optional: format price

# =============================
# ACCEPTANCE CRITERIA
# =============================
# - Owner scoping everywhere
# - Filter by car model works; in-stock toggle works
# - CRUD works

# =============================
# STRETCH
# =============================
# - Price range filter (?min=?&max=?)
# - Bulk seed a few CarModel rows via admin
