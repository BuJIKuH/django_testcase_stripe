from django.urls import path
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    path('item/<int:item_id>', views.ItemView.as_view(), name='item'),
    path('catalog', views.Catalog.as_view(), name='catalog'),
    path('create-checkout-session', views.create_checkout_session),
    path('success', views.payment_successful),
    path('cancel', views.payment_cancelled),
    path('add-to-cart', views.add_to_cart, name='add-to-cart'),
    path('checkout', views.CheckoutView.as_view(), name='checkout'),
    path('cancel-order', views.cancel_order, name='cancel-order'),
    path('', RedirectView.as_view(url='catalog')),
    ]