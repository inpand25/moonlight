from django.http import JsonResponse
from django.shortcuts import redirect, render
from shop.form import CustomUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
import json
from django.core.mail import send_mail
from django.conf import settings
from .models import Cart, Order, OrderItem, Favourite, Product, Catagory

def home(request):
    products = Product.objects.filter(trending=1)
    return render(request, 'shop/index.html', {'products': products})

def favviewpage(request):
    if request.user.is_authenticated:
        fav = Favourite.objects.filter(user=request.user)
        return render(request, "shop/fav.html", {"fav": fav})
    else:
        return redirect("/")

def remove_fav(request, fid):
    item = Favourite.objects.get(id=fid)
    item.delete()
    return redirect("/favviewpage")

def cart_page(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        return render(request, "shop/cart.html", {"cart": cart})
    else:
        return redirect("/")

def remove_cart(request, cid):
    cartitem = Cart.objects.get(id=cid)
    cartitem.delete()
    return redirect("/cart")

def fav_page(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            data = json.load(request)
            product_id = data['pid']
            product_status = Product.objects.get(id=product_id)
            if product_status:
                if Favourite.objects.filter(user=request.user.id, product_id=product_id):
                    return JsonResponse({'status': 'Product Already in Favourite'}, status=200)
                else:
                    Favourite.objects.create(user=request.user, product_id=product_id)
                    return JsonResponse({'status': 'Product Added to Favourite'}, status=200)
        else:
            return JsonResponse({'status': 'Login to Add Favourite'}, status=200)
    else:
        return JsonResponse({'status': 'Invalid Access'}, status=200)

def add_to_cart(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            data = json.load(request)
            product_qty = data['product_qty']
            product_id = data['pid']
            product_status = Product.objects.get(id=product_id)
            if product_status:
                if Cart.objects.filter(user=request.user.id, product_id=product_id):
                    return JsonResponse({'status': 'Product Already in Cart'}, status=200)
                else:
                    if product_status.quantity >= product_qty:
                        Cart.objects.create(user=request.user, product_id=product_id, product_qty=product_qty)
                        return JsonResponse({'status': 'Product Added to Cart'}, status=200)
                    else:
                        return JsonResponse({'status': 'Product Stock Not Available'}, status=200)
        else:
            return JsonResponse({'status': 'Login to Add Cart'}, status=200)
    else:
        return JsonResponse({'status': 'Invalid Access'}, status=200)

def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Logged out Successfully")
    return redirect("/")

def login_page(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == 'POST':
            name = request.POST.get('username')
            pwd = request.POST.get('password')
            user = authenticate(request, username=name, password=pwd)
            if user is not None:
                login(request, user)
                messages.success(request, "Logged in Successfully")
                return redirect("/")
            else:
                messages.error(request, "Invalid User Name or Password")
                return redirect("/login")
        return render(request, "shop/login.html")

def register(request):
    form = CustomUserForm()
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration Success You can Login Now..!")
            return redirect('/login')
    return render(request, "shop/register.html", {'form': form})

def collections(request):
    catagory = Catagory.objects.filter(status=0)
    return render(request, "shop/collections.html", {"catagory": catagory})

def collectionsview(request, name):
    if Catagory.objects.filter(name=name, status=0):
        products = Product.objects.filter(category__name=name)
        return render(request, "shop/products/index.html", {
            "products": products,
            "category_name": name,
        })
    else:
        messages.warning(request, "No Such Category Found")
        return redirect('collections')

def product_details(request, cname, pname):
    if Catagory.objects.filter(name=cname, status=0):
        if Product.objects.filter(name=pname, status=0):
            products = Product.objects.filter(name=pname, status=0).first()
            return render(request, "shop/products/product_details.html", {"products": products})
        else:
            messages.error(request, "No Such Product Found")
            return redirect('collections')
    else:
        messages.error(request, "No Such Category Found")
        return redirect('collections')

def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items:
        return redirect('/cart')

    total_price = sum(item.product.selling_price * item.product_qty for item in cart_items)

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            email=email,
            address=address,
            phone=phone,
            total_price=total_price,
            payment_mode='Cash on Delivery'
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product.name,
                price=item.product.selling_price,
                quantity=item.product_qty
            )

        message = f"New Order Placed by {full_name}:\n\n"
        for item in cart_items:
            message += f"{item.product.name} - Qty: {item.product_qty}, Price: {item.product.selling_price}\n"
        message += f"\nTotal: Rs.{total_price}\n\nDelivery Address:\n{address}\nPhone: {phone}"

        send_mail(
            subject="New Order Placed",
            message=message,
            from_email=None,
            recipient_list=["moonlightenterprises298@gmail.com"],
        )

        cart_items.delete()

        return render(request, 'shop/order_success.html')

    return render(request, 'shop/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

def placeorder(request):
    if request.method == 'POST':
        full_name = request.POST.get('fname') + ' ' + request.POST.get('lname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        cart_items = Cart.objects.filter(user=request.user)
        total_price = sum(item.product.selling_price * item.product_qty for item in cart_items)

        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            email=email,
            address=address,
            phone=phone,
            total_price=total_price,
            payment_mode='Cash on Delivery',
            status='Successful'
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.selling_price,
                quantity=item.product_qty
            )

        message = f"🛒 New Order Placed by {full_name}\n\n📦 Ordered Items:\n"
        for item in cart_items:
            message += f"- {item.product.name} (Qty: {item.product_qty}) - ₹{item.product.selling_price}\n"
        message += f"\n💰 Total Amount: ₹{total_price}\n📍 Address: {address}\n📞 Phone: {phone}\n📧 Email: {email}"

        send_mail(
            subject="🧾 New Order Placed",
            message=message,
            from_email='moonlightenterprises298@gmail.com',
            recipient_list=['eswariinpand@gmail.com'],
            fail_silently=False,
        )

        cart_items.delete()

        return render(request, 'shop/placeorder.html')

    return redirect('checkout')
