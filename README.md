# Python Coding Test

Please build a simple trading system as a pure REST API with the endpoints outlined below. We want to allow authenticated users the ability to place orders to buy and sell stocks and track the overall value of their investments. Stocks will have an id, name, and price.

* Create an endpoint to let users place trades. When an order is placed we need to record the quantity of the stock the user wants to buy or sell.

* Create an endpoint to retrieve the total value invested in a single stock by a user. To calculate this - we need to sum all the value of all orders placed by the user for a single stock. Order value is calculated by multiplying quantity and stock price.

* Create an endpoint to retrieve the total value invested in a single stock by a user.

## Required Endpoints

* /tradingapp/api/orders/ `(POST)`: Let users place a buy or sell trades.
  * `stock: int` - Stock ID to buy or sell
  * `order_type: str` - Type of transaction either `buy` or `sell`
  * `quantity: int` - Number of shares to buy or sell
### Sample POST data:
  ```
  {
    "stock": 1,
    "order_type": "sell",
    "quantity": 5
  }
  ```
### Sample Response
  ```
  {
    "id": 1,
    "quantity": 5.0,
    "price_per_share": 10.5,
    "order_type": "buy",
    "amount": 52.5,
    "status": "success",
    "remarks": null,
    "created_at": "2020-08-26T23:34:18.990588+08:00",
    "updated_at": "2020-08-26T23:34:18.990624+08:00",
    "trader": "benson",
    "stock": "MCHP"
  }
  ```
  
* /tradingapp/api/stocks/`stock_id`/ (GET): Retrieve the stock details and the total value invested by a user
