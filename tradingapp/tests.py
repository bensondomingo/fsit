from django.contrib.auth.models import User

from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from tradingapp.models import Stock

USERA = {'username': 'test_user_a', 'password': 'test1234'}
USERB = {'username': 'test_user_b', 'password': 'test1234'}

TEST_STOCK_A = {'name': 'TEST_STOCK_A', 'price': 9.5, 'quantity': 100}
TEST_STOCK_B = {'name': 'TEST_STOCK_B', 'price': 5.7, 'quantity': 70}


class TradingAppEndpointTestCase(APITestCase):

    endpoint_order_list = 'order-list'
    endpoint_order_detail = 'order-detail'
    endpoint_stock_list = 'stock-list'
    endpoint_stock_detail = 'stock-detail'

    @classmethod
    def setUpClass(cls) -> None:
        """ Create test traders """
        usera = User.objects.create(**USERA)
        usera.profile.balance = 1000
        usera.profile.save()
        userb = User.objects.create(**USERB)
        userb.profile.balance = 500
        userb.profile.save()

    @classmethod
    def tearDownClass(cls) -> None:
        User.objects.all().delete()

    def setUp(self) -> None:
        """
        Create test stock objects
        """
        TEST_STOCK_OBJ_A = Stock.objects.create(**TEST_STOCK_A)
        TEST_STOCK_OBJ_B = Stock.objects.create(**TEST_STOCK_B)
        self.TEST_STOCK_A = TEST_STOCK_OBJ_A.name
        self.TEST_STOCK_B = TEST_STOCK_OBJ_B.name

    def tearDown(self) -> None:
        Stock.objects.all().delete()
        super().tearDown()

    def login_user(self, username):
        user = User.objects.get(username=username)
        token = Token.objects.get_or_create(user=user)[0]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        return user

    def logout_user(self):
        self.client.logout()

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


class OrderEndpointTestCase(TradingAppEndpointTestCase):

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

    def test_place_buy_orders(self):
        """ Ensure we can place buy order """
        stock_name = self.TEST_STOCK_A
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
        stock_name = self.TEST_STOCK_A
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
        stock_name = self.TEST_STOCK_B
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
        stock_name = self.TEST_STOCK_A
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
        stock_name = self.TEST_STOCK_A
        order_quantity = 101
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
        stock_name = self.TEST_STOCK_A
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
        stocka = Stock.objects.get(name=self.TEST_STOCK_A)
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
        d = self.place_order(self.TEST_STOCK_A, 20, 'buy', trader)
        self.assertEqual(d.get('resp').status_code, HTTP_201_CREATED)
        d = self.place_order(self.TEST_STOCK_A, 30, 'buy', trader)
        self.assertEqual(d.get('resp').status_code, HTTP_201_CREATED)

        # Sell 10 shares from TEST_STOCK_A
        d = self.place_order(self.TEST_STOCK_A, 10, 'sell', trader)
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
        d = self.place_order(self.TEST_STOCK_A, 20, 'buy', trader)
        self.assertEqual(d.get('resp').status_code, HTTP_201_CREATED)

        # Try to sell 30. Endpoint should respond 400 Bad Request status
        d = self.place_order(self.TEST_STOCK_A, 30, 'sell', trader)
        resp = d.get('resp')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # Ensure trader's balance and stock quantity didn't changed
        balance_before_order = d.get('balance_before_order')
        balance_after_order = d.get('balance_after_order')
        quantity_before_order = d.get('quantity_before_order')
        quantity_after_order = d.get('quantity_after_order')
        self.assertEqual(balance_before_order, balance_after_order)
        self.assertEqual(quantity_before_order, quantity_after_order)


class StockEndpointTestCase(TradingAppEndpointTestCase):

    def test_access_no_auth(self):
        """
        Ensure unauthenticated users have no access
        """
        self.logout_user()
        endpoint = reverse(self.endpoint_stock_list)
        resp = self.client.get(endpoint)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        endpoint = reverse(self.endpoint_stock_detail, kwargs={'pk': 1})
        resp = self.client.get(endpoint)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_stock_list_endpoint(self):
        self.login_user(USERA.get('username'))
        endpoint = reverse(self.endpoint_stock_list)
        resp = self.client.get(endpoint)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp_data = resp.json()
        # Two stock objects were created by setUp method
        self.assertEqual(len(resp_data), 2)

    def test_stock_retrieve_endpoint(self):
        self.login_user(USERB.get('username'))

        # Retrieve TEST_STOCK_A
        endpoint = reverse(self.endpoint_stock_detail, kwargs={'pk': 1})
        resp = self.client.get(endpoint)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Retrieve TEST_STOCK_B
        endpoint = reverse(self.endpoint_stock_detail, kwargs={'pk': 2})
        resp = self.client.get(endpoint)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_stock_retrive_invested_field(self):
        """
        Ensure "invested" field on the response data is null if the
        authenticated trader has no investment on the stock. "invested"
        field should contain the investment details if the authenticated
        trader has investment on the stock
        """
        trader = self.login_user(USERA.get('username')).profile

        # 1. Not invested
        endpoint = reverse(self.endpoint_stock_detail, kwargs={'pk': 1})
        resp = self.client.get(endpoint)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp_data = resp.json()
        self.assertIn('invested', resp_data.keys())
        # Ensure "invested" field is null
        self.assertIsNone(resp_data['invested'])

        # 2.  Buy some shares
        stock_name = self.TEST_STOCK_A
        buy_quantity = 50
        d = self.place_order(stock_name, buy_quantity, 'buy', trader)
        resp = d.get('resp')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # 3. Repeat step 1, but now expect data on the "invested" field
        resp = self.client.get(endpoint)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp_data = resp.json()
        self.assertIn('invested', resp_data.keys())
        # Ensure "invested" field contains some data
        self.assertIsNotNone(resp_data['invested'])
        invested = resp_data.get('invested')

        # Inspect invested.buy
        buy_amount = invested.get('buy').get('amount')
        buy_shares = invested.get('buy').get('shares')
        # Ensure "shares" field is equal to the bought quantity
        self.assertEqual(buy_shares, buy_quantity)
        # Ensure "amount" field is equal to the actual stock price * quantity
        stock_price = TEST_STOCK_A.get('price')
        self.assertEqual(buy_amount, stock_price * buy_quantity)

        # inspect invested.sell. Expect 0 since not shares was sold yet
        sell_amount = invested.get('sell').get('amount')
        sell_shares = invested.get('sell').get('shares')
        self.assertEqual(sell_shares, 0)
        self.assertEqual(sell_amount, 0)

        # inspect invested.net_invested and invested.net_shares
        # invested.net_invested is the monetary difference of bought and
        # sold stocks
        # invested.net_shares is the quantity difference of bought and
        # sold stocks
        net_invested = invested.get('net_invested')
        net_shares = invested.get('net_shares')
        self.assertEqual(net_invested, stock_price * buy_quantity)
        self.assertEqual(net_shares, buy_quantity)

        # 4. Sell some shares then refetch enpoint and ensure "invested"
        # field is updated accordingly.
        sell_quantity = 20
        d = self.place_order(self.TEST_STOCK_A, sell_quantity, 'sell', trader)
        self.assertEqual(d.get('resp').status_code, status.HTTP_201_CREATED)

        resp = self.client.get(endpoint)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp_data = resp.json()
        invested = resp_data.get('invested')

        # makesure investment.buy didn't changed
        buy_amount = invested.get('buy').get('amount')
        buy_shares = invested.get('buy').get('shares')
        # Ensure "shares" field is still equal to the bought quantity
        self.assertEqual(buy_shares, buy_quantity)
        # Ensure "amount" field is still equal to the actual stock
        # price * quantity
        self.assertEqual(buy_amount, stock_price * buy_quantity)

        # Ensure investment.sell reflects the sold shares
        sell_amount = invested.get('sell').get('amount')
        sell_shares = invested.get('sell').get('shares')
        self.assertEqual(sell_amount, sell_quantity * stock_price)
        self.assertEqual(sell_shares, sell_quantity)

        # inspect net invested
        net_invested = invested.get('net_invested')
        net_shares = invested.get('net_shares')
        self.assertEqual(net_invested,
                         stock_price * (buy_quantity - sell_quantity))
        self.assertEqual(net_shares, (buy_quantity - sell_quantity))
