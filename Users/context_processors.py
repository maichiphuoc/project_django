from .models import Cart


def cart_count(request):

    count = 0

    if request.user.is_authenticated:

        cart = Cart.objects.filter(
            user=request.user
        ).first()

        if cart:
            count = sum(
                item.quantity
                for item in cart.items.all()
            )

    return {
        'cart_count': count
    }