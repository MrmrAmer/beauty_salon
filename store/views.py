from django.shortcuts import render, redirect
from .models import Product, Order, OrderItem
from users.models import User
from django.contrib import messages
from django.http import JsonResponse

def product_list(request):
    context = {
        'products': Product.objects.all()
    }
    return render(request, 'store/product_list.html', context)


def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        cart = request.session.get('cart', {})
        cart[product_id] = cart.get(product_id, 0) + 1
        request.session['cart'] = cart
        return JsonResponse({'status': 'ok', 'cart': cart})
    return JsonResponse({'status': 'error'}, status=400)

def get_cart_data(request):
    cart = request.session.get('cart', {})
    return JsonResponse({'cart': cart})

def view_cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=int(product_id))
        subtotal = product.price * quantity
        items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })
        total += subtotal

    context = {
        'items': items,
        'total': total
    }
    return render(request, 'store/cart.html', context)


def checkout(request):
    if 'user_id' not in request.session:
        return redirect('/login')

    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('/store/cart/')

    user = User.objects.get(id=request.session['user_id'])
    total = 0
    order = Order.objects.create(user=user, total_price=0)

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=int(product_id))
        subtotal = product.price * quantity
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            subtotal_price=subtotal
        )
        total += subtotal
        product.stock -= quantity
        product.save()

    order.total_price = total
    order.save()

    request.session['cart'] = {}
    messages.success(request, "Order placed successfully!")
    return redirect('/store/my_orders')

def delete_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
    return redirect('/store/cart/')

def clear_cart(request):
    if 'cart' in request.session:
        del request.session['cart']
    return redirect('/store/cart/')

def my_orders(request):
    if 'user_id' not in request.session:
        return redirect('/login/')

    user = User.objects.get(id=request.session['user_id'])
    user_orders = Order.objects.filter(user=user).order_by('-created_at')

    context = {
        'orders': user_orders
    }
    return render(request, 'store/my_orders.html', context)