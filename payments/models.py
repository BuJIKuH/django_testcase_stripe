import os
import re
import stripe

from datetime import datetime
from django.db import models
from django.core.exceptions import ValidationError


class Item(models.Model):
    """Модель товара."""
    name = models.CharField(max_length=55)
    description = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return self.name


class Order(models.Model):
    """Модель заказа."""
    name = models.CharField(max_length=55, null=True)
    total = models.DecimalField(max_digits=40, decimal_places=2, default=0)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name}'

    @staticmethod
    def create(request):
        order = Order()
        order.name = f'Заказ {request.user} ' \
                     f'от {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        order.save()
        return order

    @staticmethod
    def get_active_order(request):
        """Привязка заказа к сессии или возвращение уже привязанного."""
        if 'order' not in request.session.keys():
            order = Order.create(request)
            request.session['order'] = order.id
        return Order.objects.get(pk=request.session['order'])

    @staticmethod
    def deactivate_order(request):
        """Отвязка заказа от сессии."""
        del request.session['order']

    @staticmethod
    def get_total(request):
        """Получение суммы по заказу."""
        active_order = Order().get_active_order(request)
        checkout_items = OrderItem.objects.filter(order=active_order)
        total = 0
        for item in checkout_items:
            total += item.get_amount()
        return total


class OrderItem(models.Model):
    """Товар в заказе."""
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.item.name}'

    def checkout_view(self):
        """Вид позиции при оформлении заказа."""
        return f'{self.item.name}, ' \
               f'количество: {self.quantity}, ' \
               f'на сумму: {self.get_amount()} RUB'

    def get_amount(self):
        """Сумма заказанных товаров в позиции."""
        return self.item.price * self.quantity


class Discount(models.Model):
    """Скидка работающая через промокод Stripify.
    Управляется через панель администратора."""
    name = models.CharField(max_length=55, blank=False)
    stripe_id = models.CharField(max_length=55,
                                 default='Automatically assigned')
    promocode = models.CharField(max_length=55, blank=False)
    percent_off = models.IntegerField(blank=False, )
    active = models.BooleanField(default=True)
    visible = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name}'

    def clean(self):
        self.percent_off = abs(self.percent_off)
        if self.percent_off == 0:
            raise ValidationError('Поле percent_off должно быть больше 0.')
        self.promocode = re.sub('[^a-zA-Z]+', '', self.promocode)
        if Discount.objects.filter(promocode=self.promocode):
            raise ValidationError('Такой промокод уже есть.')

    def save(self, *args, **kwargs):
        """Связка скидки в БД и скидки Stripify"""
        self.stripify()
        super(Discount, self).save(*args, **kwargs)

    def stripify(self):
        """Создание скидки в Stripify."""
        stripe.api_key = os.environ.get('STRIPE_API_KEY')
        coupon = stripe.Coupon.create(name=self.name,
                                      percent_off=self.percent_off, )
        stripe.PromotionCode.create(coupon=coupon.id, code=self.promocode)
        self.stripe_id = coupon.id
        return coupon

    @staticmethod
    def visible_in_checkout():
        """Возвращает последнюю созданную скидку с активным
        параметром 'Показывать в оформлении заказа'."""
        visible_discount = Discount.objects.filter(
            active=True,
            visible=True).last()
        return visible_discount
