from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating, ProductGallery
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct
from django.http import Http404


# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True).order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()


    context = {
        'products' : paged_products,
        'product_count' : product_count,
    }

    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product__id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None


    reviews = ReviewRating.objects.filter(product__id=single_product.id, status=True)

    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    # Productos relacionados: misma categoría, excluyendo el producto actual
    related_products = Product.objects.filter(
        category=single_product.category, is_available=True
    ).exclude(id=single_product.id)[:4]


    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'product_gallery': product_gallery,
        'related_products': related_products,
    }

    return render(request, 'store/product_detail.html', context)


def guia_talles(request):
    """Sección nueva: guía de talles para kimonos y rashguards."""
    return render(request, 'store/guia_talles.html')


INFO_PAGES = {
    'quienes-somos': {
        'title': '¿Quiénes somos?',
        'body': """
25 BJJ nace de la pasión por el Jiu-Jitsu Brasileño. Somos una tienda pensada
por y para practicantes: sabemos lo que se necesita arriba y abajo del tatami,
por eso seleccionamos kimonos, cinturones, rashguards y suplementos pensando
en el entrenamiento real, no solo en la vidriera.

Trabajamos para que consigas equipo de calidad sin vueltas, con la info clara
de talles, materiales y cuidados, para que puedas enfocarte en lo que importa:
entrenar sin límites.
""",
    },
    'pagos': {
        'title': 'Pagos',
        'body': """
Aceptamos los siguientes medios de pago:

- Tarjetas de crédito y débito (Visa, Mastercard) en hasta 3 cuotas sin interés.
- Transferencia bancaria (con 10% de descuento).
- Mercado Pago.
- Efectivo, retirando en punto de encuentro a coordinar.

Todos los pagos se procesan de forma segura. Si tenés dudas sobre alguna
promoción vigente, escribinos antes de confirmar tu compra.
""",
    },
    'retiros-envios': {
        'title': 'Retiros - Envíos',
        'body': """
Hacemos envíos a todo el país a través de correo y transportes a domicilio.
El tiempo estimado de entrega es de 3 a 7 días hábiles según la localidad,
y te vamos a pasar el número de seguimiento apenas despachemos tu pedido.

También podés coordinar el retiro sin cargo en punto de encuentro dentro
de la ciudad, previa coordinación por WhatsApp o email.

El costo de envío se calcula según el destino y se muestra antes de
confirmar la compra.
""",
    },
    'cambios-devoluciones': {
        'title': 'Cambios y Devoluciones',
        'body': """
Tenés hasta 10 días corridos desde que recibís tu pedido para solicitar un
cambio o devolución, siempre que el producto esté sin uso, con las etiquetas
originales y en su empaque.

Para iniciar un cambio o devolución, escribinos a info@25bjj.com con tu
número de pedido y el motivo. Los costos de envío del cambio corren por
cuenta del comprador, salvo que se trate de un producto con falla de
fabricación.
""",
    },
}


def info(request, slug):
    """Páginas informativas: quiénes somos, pagos, envíos, cambios y devoluciones."""
    page = INFO_PAGES.get(slug)
    if page is None:
        raise Http404("Página no encontrada")
    return render(request, 'store/info_page.html', {'page': page})


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {
        'products': products,
        'product_count': product_count,
    }

    return render(request, 'store/store.html', context)


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Muchas gracias!, tu comentario ha sido actualizado.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Muchas gracias!, tu comentario ha sido publicado.')
                return redirect(url)
