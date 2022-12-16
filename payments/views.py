import os
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Order, Item, OrderItem, Discount
from .forms import CatalogForm, DetailForm
import stripe


class Catalog(View):
    """Возвращает список всех товаров."""
    def get(self, request):
        context = {'items': Item.objects.all(),
                   'form': CatalogForm,
                   }
        return render(request, template_name='payments/catalog.html',
                      context=context,)


class ItemView(View):
    """Информация о выбранном товаре."""
    def get(self, request, item_id):
        context = {'item': Item.objects.get(pk=item_id),
                   'form': DetailForm}
        return render(request,
                      template_name="payments/detail.html",
                      context=context,)


class CheckoutView(View):
    """Оформление заказа."""
    def get(self, request):
        active_order = Order().get_active_order(request)
        total = active_order.get_total(request)
        checkout_items = OrderItem.objects.filter(order=active_order)
        discount = Discount.visible_in_checkout()
        return render(request,
                      context={'checkout_items': checkout_items,
                               'total': total,
                               'active_order': active_order,
                               'discount': discount
                               },
                      template_name='payments/checkout.html')


def create_checkout_session(request):
    """Выход на Stripe Checkout."""
    stripe.api_key = os.environ.get('STRIPE_API_KEY')
    order_name = request.POST.get('active_order')
    total = request.POST.get('total')
    session = stripe.checkout.Session.create(
        line_items=[{'price_data': {
            'product_data': {'name': order_name},
            "unit_amount": int(float(total))*100,
            "currency": 'RUB'},
            "quantity": 1,
        }],
        mode='payment',
        allow_promotion_codes=True,
        success_url='http://127.0.0.1:8000/success',
        cancel_url='http://127.0.0.1:8000/cancel',
    )
    return redirect(session.url, code=303)


def payment_successful(request):
    """Stripe Checkout Session - успешен,
     статус заказа - оплачен, заказ отвязан от сессии."""
    active_order = Order.get_active_order(request)
    active_order.paid = True
    active_order.total = active_order.get_total(request)
    active_order.save()
    Order.deactivate_order(request)
    return render(request,
                  template_name='payments/success.html',
                  context={'text': 'Заказ успешно оформлен.'})


def payment_cancelled(request):
    """Stripe Checkout Session - отменен,
    заказ остается приязанным к сессии."""
    return render(request,
                  template_name='payments/redirect_after_transaction.html',
                  context={'text': 'Платеж отменен.'})


def add_to_cart(request):
    """Пополнение заказа. Если позиция уже есть в заказе,
     то количество увеличивается на выбранное значение."""
    quantity = int(request.POST.get('quantity'))
    item = get_object_or_404(Item, pk=request.POST.get(f'added-item-id'))
    active_order = Order.get_active_order(request)
    order_item, created = OrderItem.objects.get_or_create(item=item,
                                                          order=active_order)
    if created:
        order_item.quantity = quantity
    else:
        order_item.quantity += quantity
    order_item.save()
    return redirect('catalog')


def cancel_order(request):
    """Сброс заказа."""
    Order.deactivate_order(request)
    return redirect('catalog')
