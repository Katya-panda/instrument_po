from django.shortcuts import render, get_object_or_404, redirect
import json
import os
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Product, Cart, CartItem, Order, OrderItem
from django.core.mail import EmailMessage
from openpyxl import Workbook
from io import BytesIO
from django.conf import settings

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

# отображение списка товаров с возможностью фильтрации и поиска
def product_list(request):
    products = Product.objects.all()
    category = request.GET.get("category")
    manufacturer = request.GET.get("manufacturer")
    search = request.GET.get("search")
    
    if category:
        products = products.filter(category__name=category)
    if manufacturer:
        products = products.filter(manufacturer__name=manufacturer)
    if search:
        products = products.filter(Q(name__icontains=search) | Q(description__icontains=search))
    
    return render(request, "app/product_list.html", {"products": products})

# отображение детальной информации о конкретном товаре
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "app/product_detail.html", {"product": product})

# добавление товара в корзину пользователя
@login_required  
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect("cart_view")

# обновление количества товара в корзине
@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    if request.method == 'POST':
        quantity = int(request.POST.get("quantity", 1))
        if quantity > 0 and quantity <= cart_item.product.stock_quantity:
            cart_item.quantity = quantity
            cart_item.save()
    return redirect("cart_view")

# удаление товара из корзины
@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect("cart_view")

# отображение содержимого карзины пользователя
@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cartitem_set.select_related('product').all()
    total = cart.total_price()
    return render(request, "app/cart.html", {
        "cart_items": cart_items,
        "total": total
    })

# обработка оформления заказа
@login_required
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.cartitem_set.all()
    
    if not cart_items.exists():
        return redirect('cart_view')
    
    if request.method == 'POST':
        try:
            # создание заказа
            order = Order.objects.create(
                user=request.user,
                total=cart.total_price(),
                address=request.POST.get('address'),
                email=request.POST.get('email', request.user.email),
                phone=request.POST.get('phone')
            )
            
            # добавление товаров в заказ
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
            
            # генерация Excel-чека
            wb = Workbook()
            ws = wb.active
            ws.title = "Чек заказа"
            ws.append(['Товар', 'Количество', 'Цена', 'Сумма'])
            for item in order.items.all():
                ws.append([item.product.name, item.quantity, item.price, item.total_price])
            ws.append(['', '', 'Итого:', order.total])
            
            excel_file = BytesIO()
            wb.save(excel_file)
            excel_file.seek(0)
            
            # отправка письма
            email = EmailMessage(
                f'Заказ №{order.id}',
                f'Спасибо за покупку! Адрес доставки: {order.address}',
                settings.DEFAULT_FROM_EMAIL,
                [order.email],
                attachments=[
                    (f'order_{order.id}.xlsx', excel_file.getvalue(), 
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                ]
            )
            email.send()
            
            # очистка корзины
            cart_items.delete()
            
            return render(request, 'app/order_success.html', {'order': order})
            
        except Exception as e:
            return render(request, 'app/checkout.html', {
                'error': f'Ошибка: {str(e)}',
                'cart_items': cart_items,
                'total': cart.total_price()
            })
    
    return render(request, 'app/checkout.html', {
        'cart_items': cart_items,
        'total': cart.total_price()
    })