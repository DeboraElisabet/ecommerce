"""
Comando de management para reemplazar el catálogo de ByteShop
por el catálogo de 25 BJJ (kimonos, cinturones, rashguards, suplementos).

Uso:
    python manage.py seed_25bjj

No toca usuarios ni cuentas: solo borra las categorías/productos
viejos y crea los nuevos.
"""
from django.core.management.base import BaseCommand
from category.models import Category
from store.models import Product, Variation


CATEGORIES = [
    {
        "category_name": "Kimonos",
        "slug": "kimonos",
        "description": "Kimonos (Gi) de Jiu-Jitsu Brasileño para entrenamiento y competencia.",
        "cat_image": "photos/categories/kimonos.png",
    },
    {
        "category_name": "Cinturones",
        "slug": "cinturones",
        "description": "Cinturones de BJJ de todos los grados, trenzados y reforzados.",
        "cat_image": "photos/categories/cinturones.png",
    },
    {
        "category_name": "Rashguards",
        "slug": "rashguards",
        "description": "Rashguards y spats para entrenar No-Gi con compresión y durabilidad.",
        "cat_image": "photos/categories/rashguards.png",
    },
    {
        "category_name": "Suplementos",
        "slug": "suplementos",
        "description": "Suplementos deportivos para rendimiento y recuperación.",
        "cat_image": "photos/categories/suplementos.png",
    },
]

PRODUCTS = [
    # Kimonos (2 tipos, cada uno con talle y color a elegir por combo)
    dict(product_name="Kimono BJJ Tramado Grueso", slug="kimono-bjj-tramado-grueso",
         category="kimonos", price=130000, stock=15,
         images="photos/products/kimono-tramado-grueso.png",
         description="Kimono de tramado grueso (pearl weave), el más resistente y durable. "
                      "Ideal para entrenamiento diario intenso.",
         colors=["Negro", "Azul", "Blanco"], tallas=["A0", "A1", "A2", "A3", "A4"]),
    dict(product_name="Kimono BJJ Tramado Ultra Liviano", slug="kimono-bjj-tramado-ultra-liviano",
         category="kimonos", price=165000, stock=10,
         images="photos/products/kimono-tramado-ultra-liviano.png",
         description="Kimono de tramado ultra liviano (350 gsm), aprobado para competencia. "
                      "Pretina reforzada, costuras dobles y secado rápido.",
         colors=["Azul", "Blanco", "Negro"], tallas=["A0", "A1", "A2", "A3", "A4"]),

    # Cinturones (precio según color/grado)
    dict(product_name="Cinturón BJJ Blanco", slug="cinturon-bjj-blanco",
         category="cinturones", price=40000, stock=40,
         images="photos/products/cinturon-blanco.png",
         description="Cinturón de algodón grado A, ideal para empezar en el Jiu-Jitsu Brasileño.",
         tallas=["A0", "A1", "A2", "A3", "A4"]),
    dict(product_name="Cinturón BJJ Azul", slug="cinturon-bjj-azul",
         category="cinturones", price=55000, stock=35,
         images="photos/products/cinturon-azul.png",
         description="Cinturón de algodón grado A, reforzado en las puntas para mayor durabilidad.",
         tallas=["A0", "A1", "A2", "A3", "A4"]),
    dict(product_name="Cinturón BJJ Negro Trenzado", slug="cinturon-bjj-negro-trenzado",
         category="cinturones", price=70000, stock=12,
         images="photos/products/cinturon-negro-trenzado.png",
         description="Cinturón negro trenzado de competencia, con costuras reforzadas y "
                      "espacio para barras de grado.",
         tallas=["A0", "A1", "A2", "A3", "A4"]),

    # Rashguards
    dict(product_name="Rashguard Manga Larga Compresión", slug="rashguard-manga-larga-compresion",
         category="rashguards", price=35000, stock=25,
         images="photos/products/rashguard-manga-larga.png",
         description="Rashguard de compresión manga larga, tela transpirable de secado rápido "
                      "ideal para entrenar No-Gi.",
         colors=["Negro", "Rojo"], tallas=["S", "M", "L", "XL"]),
    dict(product_name="Rashguard Manga Corta Estampado", slug="rashguard-manga-corta-estampado",
         category="rashguards", price=30000, stock=25,
         images="photos/products/rashguard-manga-corta.png",
         description="Rashguard manga corta con estampado sublimado, costuras planas anti-roce.",
         colors=["Negro", "Rojo"], tallas=["S", "M", "L", "XL"]),
    dict(product_name="Spats de Compresión", slug="spats-de-compresion",
         category="rashguards", price=38000, stock=18,
         images="photos/products/rashguard-spats.png",
         description="Calza (spats) de compresión con tela de cuadriculado antideslizante en las rodillas.",
         tallas=["S", "M", "L", "XL"]),

    # Suplementos
    dict(product_name="Proteína Whey 1kg", slug="proteina-whey-1kg",
         category="suplementos", price=45000, stock=30,
         images="photos/products/proteina-whey.png",
         description="Proteína de suero de leche para recuperación muscular post-entrenamiento."),
    dict(product_name="Creatina Monohidratada 300g", slug="creatina-monohidratada-300g",
         category="suplementos", price=25000, stock=30,
         images="photos/products/creatina.png",
         description="Creatina monohidratada pura, para fuerza y rendimiento en entrenamientos exigentes."),
    dict(product_name="Pre-Entreno Combat", slug="pre-entreno-combat",
         category="suplementos", price=32000, stock=20,
         images="photos/products/pre-entreno.png",
         description="Pre-entreno formulado para deportes de combate: energía y foco sin bajón posterior."),
]


class Command(BaseCommand):
    help = "Reemplaza el catálogo de ByteShop por el catálogo de 25 BJJ"

    def handle(self, *args, **options):
        self.stdout.write("Borrando catálogo anterior (productos y categorías)...")
        Product.objects.all().delete()
        Category.objects.all().delete()

        self.stdout.write("Creando categorías de 25 BJJ...")
        cat_map = {}
        for c in CATEGORIES:
            cat = Category.objects.create(
                category_name=c["category_name"],
                slug=c["slug"],
                description=c["description"],
                cat_image=c["cat_image"],
            )
            cat_map[c["slug"]] = cat
            self.stdout.write(f"  + {cat.category_name}")

        self.stdout.write("Creando productos de 25 BJJ...")
        for p in PRODUCTS:
            product = Product.objects.create(
                product_name=p["product_name"],
                slug=p["slug"],
                description=p["description"],
                price=p["price"],
                images=p["images"],
                stock=p["stock"],
                is_available=True,
                category=cat_map[p["category"]],
            )

            for color in p.get("colors", []):
                Variation.objects.create(
                    product=product, variation_category="color",
                    variation_value=color, is_active=True,
                )
            for talla in p.get("tallas", []):
                Variation.objects.create(
                    product=product, variation_category="talla",
                    variation_value=talla, is_active=True,
                )

            self.stdout.write(f"  + {p['product_name']}")

        self.stdout.write(self.style.SUCCESS(
            f"Listo: {len(CATEGORIES)} categorías y {len(PRODUCTS)} productos de 25 BJJ."
        ))
