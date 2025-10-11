from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Book
from .forms import BookForm

class BookListView(LoginRequiredMixin, ListView):
    model = Book
    paginate_by = 10

    def get_queryset(self):
        qs = Book.objects.filter(owner=self.request.user)
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(title__icontains=q)
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-created_at")

class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book

    def get_queryset(self):
        return Book.objects.filter(owner=self.request.user)

class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    success_url = reverse_lazy("book_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class BookUpdateView(LoginRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    success_url = reverse_lazy("book_list")

    def get_queryset(self):
        return Book.objects.filter(owner=self.request.user)

class BookDeleteView(LoginRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy("book_list")

    def get_queryset(self):
        return Book.objects.filter(owner=self.request.user)
