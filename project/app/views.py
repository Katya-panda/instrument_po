from django.shortcuts import render
import json
import os

# главная страница
def home(request):
    return render(request, 'app/home.html')

# о магазине
def about(request):
    return render(request, 'app/about.html')

# об авторе
def author(request):
    return render(request, 'app/author.html')

# загрузка квалификаций
def load_specs():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'dump.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# список квалификаций
def spec_list(request):
    data = load_specs()
    specs = []
    for item in data:
        if item['model'] == 'data.skill':
            spec_data = {
                'id': item['pk'],
                'name': item['fields']['title'],
                'code': item['fields']['code'],
                'desc': item['fields']['desc'] if item['fields']['desc'] else 'Нет описания'
            }
            specs.append(spec_data)
    return render(request, 'app/list.html', {'specs': specs})

# квалификация (подробнее)
def spec_detail(request, id):
    data = load_specs()
    for item in data:
        if item['model'] == 'data.skill' and item['pk'] == id:
            spec = {
                'id': item['pk'],
                'name': item['fields']['title'],
                'code': item['fields']['code'],
                'desc': item['fields']['desc'] if item['fields']['desc'] else 'Нет описания',
                'all_data': item['fields'] 
            }
            return render(request, 'app/detail.html', {'spec': spec})
    return render(request, 'app/404.html')

# ошибка
def error_404(request):
    return render(request, 'app/404.html')
