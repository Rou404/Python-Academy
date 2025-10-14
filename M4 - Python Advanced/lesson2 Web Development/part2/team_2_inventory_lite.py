"""
Team 2 — Inventory Lite (Django mini project)
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
# Track items (name, sku, quantity, location). Provide list/search/filter and CRUD.

# =============================
# DATA MODEL (suggested)
# =============================
# app/models.py — create Item
# TODO[A]: implement
# class Item(models.Model):
#     owner
#     name
#     sku
#     quantity
#     location
#     created_at
#     class Meta:
#         constraints = [models.UniqueConstraint(fields=["owner","sku"], name="uniq_owner_sku")]
#     def __str__(self): return f"{self.name} ({self.sku})"
# admin.py: register with list_display=(name,sku,quantity,location,owner,created_at), search, list_filter

# =============================
# REQUIRED PAGES / URLS
# =============================
# '/'                 → Item list with search (q on name/sku) & filter by location
# '/items/create/'    → Create item
# '/items/<id>/'      → Detail
# '/items/<id>/update/' '/items/<id>/delete/' → Update/Delete

# =============================
# STEP-BY-STEP CHECKLIST
# =============================
# TODO[A] MODELS & ADMIN
# - Create Item model, run migrations
# - Admin registration with search_fields=("name","sku"), list_filter=("location","created_at")
#
# TODO[B] VIEWS & URLCONF
# - app/urls.py routes for list/detail/create/update/delete (use CBVs)
# - ListView.get_queryset():
#       qs = Item.objects.filter(owner=request.user)
#       q = request.GET.get('q'); if q: qs = qs.filter(Q(name__icontains=q) | Q(sku__icontains=q))
#       loc = request.GET.get('location'); if loc: qs = qs.filter(location=loc)
#       return qs.order_by('-created_at')
# - Use LoginRequiredMixin on all CBVs
# - For CreateView.form_valid(), set form.instance.owner = request.user
#
# TODO[C] TEMPLATES & UX
# - base.html nav: List | Create | Login/Logout (logout via POST form)
# - item_list.html: search input + location select (unique locations from queryset)
# - item_detail.html: fields + edit/delete links
# - item_form.html, item_confirm_delete.html
# - messages after create/update/delete

# =============================
# ACCEPTANCE CRITERIA
# =============================
# - Only the owner’s items are listed and editable
# - Search by name/sku works; optional location filter works
# - CRUD works end-to-end without errors

# =============================
# STRETCH
# =============================
# - CSV export of filtered list
# - Low-stock badge when quantity < 3
