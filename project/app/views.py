from django.shortcuts import render

# главная страница
def home(request):
    return render(request, 'app/home.html')

# о магазине
def about(request):
    return render(request, 'app/about.html')

# об авторе
def author(request):
    return render(request, 'app/author.html')