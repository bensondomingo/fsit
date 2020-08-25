from django.contrib.auth.models import User

from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from tradingapp.models import Stock

USERA = {'username': 'test_user_a', 'password': 'test1234'}
USERB = {'username': 'test_user_b', 'password': 'test1234'}


class TradingAppEndpointTestCase(APITestCase):

    endpoint_order_list = 'order-list'

    @classmethod
    def setUpClass(cls) -> None:
        """ Create test users """
        usera = User.objects.create(**USERA)
        userb = User.objects.create(**USERB)

        # Give them initial balance
        usera.profile.balance = 1000
        usera.profile.save()
        userb.profile.balance = 500
        userb.profile.save()

    @classmethod
    def tearDownClass(cls) -> None:
        pass

    def login_user(self, username):
        user = User.objects.get(username=username)
        token = Token.objects.get_or_create(user=user)[0]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        return user

    def logout_user(self):
        self.client.logout()


class OrderEndpointTestCase(TradingAppEndpointTestCase):

    @classmethod
    def setUpClass(cls) -> None:
        """ Create User and Stocks """
        super().setUpClass()

        Stock.objects.create(
            **{'name': 'StockA', 'price': 9.5, 'quantity': 100})

        Stock.objects.create(
            **{'name': 'StockB', 'price': 5.7, 'quantity': 70})

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()

    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        self.logout_user()
        super().tearDown()

    def test_create_order_no_auth(self):
        """
        Perform POST without logging in. Should result to 401 Unauthorized
        """
        endpoint = reverse(self.endpoint_order_list)
        resp = self.client.post(endpoint, {})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def place_buy_order(self, stock, quantity, trader):
        stock = Stock.objects.get(name=stock)
        balance_before_buy = trader.balance
        quantity_before_buy = stock.quantity

        endpoint = reverse(self.endpoint_order_list)
        data = {
            'order_type': 'buy',
            'stock': stock.id,
            'quantity': quantity
        }
        resp = self.client.post(endpoint, data)

        trader.refresh_from_db()
        stock.refresh_from_db()

        return {
            'resp': resp,
            'balance_before_buy': balance_before_buy,
            'quantity_before_buy': quantity_before_buy,
            'balance_after_buy': trader.balance,
            'quantity_after_buy': stock.quantity
        }

    def test_place_buy_order(self):
        """ Ensure we can place buy order """
        stock_name = 'StockA'
        order_quantity = 10
        trader = self.login_user(username=USERA.get('username')).profile
        d = self.place_buy_order(stock_name, order_quantity, trader)

        resp = d.get('resp')
        order_amount = resp.json().get('amount')
        order_quantity = resp.json().get('quantity')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Ensure trader's balance and stock quantity were updated
        self.assertEqual(d.get('balance_after_buy') +
                         order_amount, d.get('balance_before_buy'))
        self.assertEqual(d.get('quantity_after_buy') +
                         order_quantity, d.get('quantity_before_buy'))

    def test_place_buy_order_not_enough_balance(self):
        """
        Ensure endpoint will prevent trader from buying order he can't afford.
        """
        stock_name = 'StockA'
        order_quantity = 100
        trader = self.login_user(username=USERB.get('username')).profile
        d = self.place_buy_order(stock_name, order_quantity, trader)

        resp = d.get('resp')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # Ensure trader's balance and stock quantity were kept
        self.assertEqual(d.get('balance_after_buy'),
                         d.get('balance_before_buy'))
        self.assertEqual(d.get('quantity_after_buy'),
                         d.get('quantity_before_buy'))

    def test_place_buy_order_not_enough_stock(self):
        """
        Ensure endpoint will prevent selling not enough stock quantity.
        """
        stock_name = 'StockB'
        order_quantity = 100
        trader = self.login_user(username=USERA.get('username')).profile
        d = self.place_buy_order(stock_name, order_quantity, trader)

        resp = d.get('resp')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # Ensure trader's balance and stock quantity were kept
        self.assertEqual(d.get('balance_after_buy'),
                         d.get('balance_before_buy'))
        self.assertEqual(d.get('quantity_after_buy'),
                         d.get('quantity_before_buy'))


class StockEndpointTestCase(TradingAppEndpointTestCase):
    pass
