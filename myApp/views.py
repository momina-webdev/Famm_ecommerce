from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Contact, Product, CartItem, Order, OrderItem


# =========================
# Home / Dashboard
# =========================
@login_required(login_url='login')
def index(request):
    products = Product.objects.all()
    items = CartItem.objects.filter(user=request.user)
    total_cost = sum(item.total_price() for item in items)
    cart_count = items.count()

    return render(request, 'index.html', {
        'products': products,
        'items': items,
        'total_cost': total_cost,
        'cart_count': cart_count,
    })


# =========================
# Contact
# =========================
def contact_view(request):
    if request.method == 'POST':
        Contact.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            subject=request.POST.get('subject'),
            message=request.POST.get('message')
        )
        messages.success(request, "Your message has been sent successfully!")
        return redirect('contact')  # reload with success message
    return render(request, 'contact.html')



# def contact_view(request):
#     return render(request, 'contact.html')


# =========================
# Authentication
# =========================
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered")
            return redirect('register')

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully")
        return redirect('login')

    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user:
            auth_login(request, user)
            return redirect('index')
        messages.error(request, "Invalid username or password")
        return redirect('login')

    return render(request, 'login.html')


def logout_view(request):
    auth_logout(request)
    return redirect('login')


# =========================
# Product Views
# =========================
def product_view(request):
    products = Product.objects.all()
    items = CartItem.objects.filter(user=request.user) if request.user.is_authenticated else []
    total_cost = sum(item.total_price() for item in items)
    cart_count = items.count() if request.user.is_authenticated else 0

    # Filters
    selected_categories = request.GET.getlist('category')
    if selected_categories:
        products = products.filter(category__in=selected_categories)

    max_price = request.GET.get('max_price')
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    sort = request.GET.get('sort')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')

    return render(request, 'product.html', {
        'products': products,
        'selected_categories': selected_categories,
        'max_price': max_price or '1000',
        'sort': sort,
        'items': items,
        'total_cost': total_cost,
        'cart_count': cart_count,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    items = CartItem.objects.filter(user=request.user) if request.user.is_authenticated else []
    total_cost = sum(item.total_price() for item in items)
    cart_count = items.count() if request.user.is_authenticated else 0

    return render(request, 'product_detail.html', {
        'product': product,
        'items': items,
        'total_cost': total_cost,
        'cart_count': cart_count,
    })


# =========================
# Cart Management
# =========================
@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=product_id)
        size = request.POST.get('size')
        quantity = request.POST.get('quantity')

        if not size or not quantity:
            return redirect('product_detail', pk=product.pk)

        try:
            quantity = int(quantity)
        except ValueError:
            return redirect('product_detail', pk=product.pk)

        image_url = getattr(product.image_main, 'url', '') if hasattr(product, 'image_main') else ''

        CartItem.objects.create(
            user=request.user,
            product_name=product.name,
            size=size,
            quantity=quantity,
            price=product.price,
            image_url=image_url,
        )
        return redirect('index')

    return redirect('product_detail', pk=product_id)


@login_required
def cart_modal_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.total_price() for item in cart_items)
    return render(request, 'your_template.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })


@login_required
def remove_cart_item(request, item_id):
    CartItem.objects.filter(id=item_id, user=request.user).delete()
    return redirect(request.META.get('HTTP_REFERER', 'view_cart'))


# =========================
# Checkout & Orders
# =========================
@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.total_price() for item in cart_items)

    if request.method == "POST":
        required_fields = ['full_name', 'email', 'phone', 'country', 'city', 'state', 'zip_code', 'address']
        for field in required_fields:
            if not request.POST.get(field):
                messages.error(request, f"{field.replace('_', ' ').title()} is required.")
                return render(request, 'checkout.html', {
                    'cart_items': cart_items,
                    'total_price': total_price,
                    'user_country': 'Pakistan'
                })

        order = Order.objects.create(
            user=request.user,
            full_name=request.POST.get('full_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            country=request.POST.get('country'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            zip_code=request.POST.get('zip_code'),
            address=request.POST.get('address'),
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product_name=item.product_name,
                size=item.size,
                quantity=item.quantity,
                price=item.price,
                image_url=item.image_url,
            )

        cart_items.delete()
        messages.success(request, "Your order has been placed successfully!")
        return render(request, 'index.html', {'order': order})

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'user_country': 'Pakistan'
    })


@login_required(login_url='login')
def Account(request):
    items = CartItem.objects.filter(user=request.user)
    total_cost = sum(item.total_price() for item in items)
    cart_count = items.count()
    orders = Order.objects.filter(user=request.user).order_by('-created_at').prefetch_related('items')

    return render(request, 'Account.html', {
        'user': request.user,
        'orders': orders,
        'items': items,
        'total_cost': total_cost,
        'cart_count': cart_count,
    })
