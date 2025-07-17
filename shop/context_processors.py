from .models import Cart, Favourite

def cart_and_fav_counts(request):
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).count()
        fav_count = Favourite.objects.filter(user=request.user).count()
    else:
        cart_count = 0
        fav_count = 0

    return {
        'cart_count': cart_count,
        'fav_count': fav_count,
    }
