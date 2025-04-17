from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from .sitemap import StaticViewSitemap, ProductSitemap, CategorySitemap

sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
    'categories': CategorySitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('auth/', include('accounts.urls')),
    path('', include('home.urls')),
    path('products/', include('products.urls', namespace='products')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('checkout/', include('checkout.urls')),
    path('newsletter/', include('newsletter.urls')),
    path('profile/', include('profiles.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)