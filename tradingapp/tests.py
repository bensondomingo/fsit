from django.contrib.auth.models import User

from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED
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
        """ Create test Traders and Stocks """
        usera = User.objects.create(**USERA)
        usera.profile.balance = 1000
        usera.profile.save()
        userb = User.objects.create(**USERB)
        userb.profile.balance = 500
        userb.profile.save()
        Stock.objects.create(
            **{'name': 'StockA', 'price': 9.5, 'quantity': 100})
        Stock.objects.create(
            **{'name': 'StockB', 'price': 5.7, 'quantity': 70})

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

    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        self.logout_user()
        super().tearDown()

    def place_order(self, stock, quantity, order_type, trader):
        stock = Stock.objects.get(name=stock)
        balance_before_order = trader.balance
        quantity_before_order = stock.quantity

        endpoint = reverse(self.endpoint_order_list)
        data = {
            'order_type': order_type,
            'stock': stock.id,
            'quantity': quantity
        }
        resp = self.client.post(endpoint, data)

        trader.refresh_from_db()
        stock.refresh_from_db()

        return {
            'resp': resp,
            'balance_before_order': balance_before_order,
            'quantity_before_order': quantity_before_order,
            'balance_after_order': trader.balance,
            'quantity_after_order': stock.quantity
        }

    def test_create_order_no_auth(self):
        """
        Perform POST without logging in. Should result to 401 Unauthorized
        """
        endpoint = reverse(self.endpoint_order_list)
        resp = self.client.post(endpoint, {})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_place_buy_orders(self):
        """ Ensure we can place buy order """
        stock_name = 'StockA'
        order_quantity = 10
        order_type = 'buy'
        trader = self.login_user(username=USERA.get('username')).profile
        d = self.place_order(
            stock_name, order_quantity, order_type, trader)

        resp = d.get('resp')
        order_amount = resp.json().get('amount')
        order_quantity = resp.json().get('quantity')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Ensure trader's balance and stock quantity were updated
        self.assertEqual(d.get('balance_after_order') +
                         order_amount, d.get('balance_before_order'))
        self.assertEqual(d.get('quantity_after_order') +
                         order_quantity, d.get('quantity_before_order'))

    def test_place_multiple_orders(self):
        """
        Ensure we can place multiple orders from multiple traders. Place order
        from USERA and USERB. Make sure trader balance and stock quantity got
        updated accordingly.
        """
        # USERA
        # Buy 10 stock shares (95)
        stock_name = 'StockA'
        order_quantity = 10
        order_type = 'buy'
        trader = self.login_user(username=USERA.get('username')).profile
        d = self.place_order(
            stock_name, order_quantity, order_type, trader)

        resp = d.get('resp')
        order_amount = resp.json().get('amount')
        balance_before_order = d.get('balance_before_order')
        balance_after_order = d.get('balance_after_order')
        quantity_before_order = d.get('quantity_before_order')
        quantity_after_order = d.get('quantity_after_order')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Ensure trader's balance and stock quantity were updated
        self.assertEqual(balance_after_order +
                         order_amount, balance_before_order)
        self.assertEqual(quantity_after_order + order_quantity,
                         quantity_before_order)

        # Buy another 20 shares (190)
        order_quantity = 20
        d = self.place_order(
            stock_name, order_quantity, order_type, trader)
        resp = d.get('resp')
        order_amount = resp.json().get('amount')
        balance_before_order = d.get('balance_before_order')
        balance_after_order = d.get('balance_after_order')
        quantity_before_order = d.get('quantity_before_order')
        quantity_after_order = d.get('quantity_after_order')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Ensure trader's balance and stock quantity were updated
        self.assertEqual(balance_after_order +
                         order_amount, balance_before_order)
        self.assertEqual(quantity_after_order + order_quantity,
                         quantity_before_order)
        self.logout_user()

        # USERB
        # Buy 5 stock shares (47.5)
        stock_name = 'StockA'
        order_quantity = 5
        trader = self.login_user(username=USERB.get('username')).profile
        d = self.place_order(
            stock_name, order_quantity, order_type, trader)

        resp = d.get('resp')
        order_amount = resp.json().get('amount')
        order_quantity = resp.json().get('quantity')
        balance_before_order = d.get('balance_before_order')
        balance_after_order = d.get('balance_after_order')
        quantity_before_order = d.get('quantity_before_order')
        quantity_after_order = d.get('quantity_after_order')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Ensure trader's balance and stock quantity were updated
        self.assertEqual(balance_after_order +
                         order_amount, balance_before_order)
        self.assertEqual(quantity_after_order + order_quantity,
                         quantity_before_order)

    def test_place_buy_order_not_enough_balance(self):
        """
        Ensure endpoint will prevent trader from buying order he can't afford.
        """
        stock_name = 'StockA'
        order_quantity = 100
        order_type = 'buy'
        trader = self.login_user(username=USERB.get('username')).profile
        d = self.place_order(
            stock_name, order_quantity, order_type, trader)

        resp = d.get('resp')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # Ensure trader's balance and stock quantity didn't changed
        self.assertEqual(d.get('balance_after_order'),
                         d.get('balance_before_order'))
        self.assertEqual(d.get('quantity_after_order'),
                         d.get('quantity_before_order'))

    def test_place_buy_order_not_enough_stock(self):
        """
        Ensure endpoint will prevent trader placing order when stock quantity
        is not enough
        """
        stock_name = 'StockB'
        order_quantity = 100
        order_type = 'buy'
        trader = self.login_user(username=USERA.get('username')).profile
        d = self.place_order(
            stock_name, order_quantity, order_type, trader)

        resp = d.get('resp')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # Ensure trader's balance and stock quantity were kept
        self.assertEqual(d.get('balance_after_order'),
                         d.get('balance_before_order'))
        self.assertEqual(d.get('quantity_after_order'),
                         d.get('quantity_before_order'))

    def test_order_projected_gain(self):
        """
        Ensure changes on the stock price will reflect on the order's
        projected_gain
        """
        stock_name = 'StockA'
        order_quantity = 50
        order_type = 'buy'
        trader = self.login_user(username=USERB.get('username')).profile
        d = self.place_order(
            stock_name, order_quantity, order_type, trader)
        resp = d.get('resp')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # At some point in time the stock price will change. Through this
        # change in stock price the profit / loss can be calculated
        change_in_stock_price = 4.8
        stocka = Stock.objects.get(name='StockA')
        stocka.price += change_in_stock_price  # Incease stock price
        stocka.save()

        order = trader.orders.get(id=resp.json().get('id'))
        self.assertEqual(order.projected_gain,
                         order_quantity * change_in_stock_price)

    def test_place_sell_order(self):
        """
        Ensure we can place sell orders.
        """
        # First create intial orders
        trader = self.login_user(username=USERA.get('username')).profile
        d = self.place_order('StockA', 20, 'buy', trader)
        self.assertEqual(d.get('resp').status_code, HTTP_201_CREATED)
        d = self.place_order('StockB', 30, 'buy', trader)
        self.assertEqual(d.get('resp').status_code, HTTP_201_CREATED)

        # Sell 10 shares from StockA
        d = self.place_order('StockA', 10, 'sell', trader)
        resp = d.get('resp')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        sold_amount = float(resp.json().get('amount'))
        balance_before_order = d.get('balance_before_order')
        balance_after_order = d.get('balance_after_order')
        quantity_before_order = d.get('quantity_before_order')
        quantity_after_order = d.get('quantity_after_order')
        self.assertEqual(balance_before_order +
                         sold_amount, balance_after_order)
        self.assertEqual(quantity_before_order + 10, quantity_after_order)

    def test_place_sell_order_not_enough_shares(self):
        """
        Ensure only available shares can be sold by a trader
        """
        # First buy 20 shares
        trader = self.login_user(username=USERA.get('username')).profile
        d = self.place_order('StockA', 20, 'buy', trader)
        self.assertEqual(d.get('resp').status_code, HTTP_201_CREATED)

        # Try to sell 30. Endpoint should respond 400 Bad Request status
        d = self.place_order('StockA', 30, 'sell', trader)
        resp = d.get('resp')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        balance_before_order = d.get('balance_before_order')
        balance_after_order = d.get('balance_after_order')
        quantity_before_order = d.get('quantity_before_order')
        quantity_after_order = d.get('quantity_after_order')
        self.assertEqual(balance_before_order, balance_after_order)
        self.assertEqual(quantity_before_order, quantity_after_order)


class StockEndpointTestCase(TradingAppEndpointTestCase):
    pass
