# Python Coding Test

Please build a simple trading system as a pure REST API with the endpoints outlined below. We want to allow authenticated users the ability to place orders to buy and sell stocks and track the overall value of their investments. Stocks will have an id, name, and price.

- Create an endpoint to let users place trades. When an order is placed we need to record the quantity of the stock the user wants to buy or sell.

- Create an endpoint to retrieve the total value invested in a single stock by a user. To calculate this - we need to sum all the value of all orders placed by the user for a single stock. Order value is calculated by multiplying quantity and stock price.

- Create an endpoint to retrieve the total value invested in a single stock by a user.

## Assumptions

- There are already existing Stocks that traders can buy or sell. (Stock objects can be created through the Django admin panel or through the stock create endpoint.)

## Required Endpoints

- /tradingapp/api/orders/ `(POST)`: Let users place a buy or sell trades.

  - `stock: int` - ID of Stock to trade
  - `order_type: str` - Type of transaction either `buy` or `sell`
  - `quantity: int` - Number of shares to buy or sell

  ### Sample POST data:

  ```
  {
    "stock": 1,
    "order_type": "buy",
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
    "stock": 1
  }
  ```

- /tradingapp/api/stocks/`stock_id`/ (GET): Retrieve the stock details and the total value invested by a user

  - `stock_id` - ID of Stock to retrieve

  ### Sample Response

  ```
  {
    "id": 1,
    "invested": {
        "buy": {
            "amount": 100.0,
            "shares": 10
        },
        "sell": {
            "amount": 52.5,
            "shares": 5
        },
        "net_invested": 47.5,
        "net_shares": 5
    },
    "name": "MCHP",
    "price": 10.5,
    "quantity": 90,
    "created_at": "2020-08-26T08:08:13.893353+08:00",
    "updated_at": "2020-08-26T23:34:18.974257+08:00"
  }
  ```

  > Note: `invested` field will be `null` if authenticated user has no investment on this Stock

## Aditional Endpoints

### User Registration and Authentication

- /rest-auth/registration/ `(POST)`: User registration

  - `username`
  - `email` (optional)
  - `password1`
  - `password2`

- /rest-auth/login/ `(POST)`: Authenticate user

  - `username`
  - `password`

- /rest-auth/logout/ `(POST)`: Logout user

### Additional order endpoints

- /tradingapp/api/orders/ `(GET)`: List all orders created by an authenticated user

- /tradingapp/api/orders/`order_id`/ `(GET)`: Retrive order details
  - `order_id` - ID of order to retrieve

### Additional stock endpoints

- /tradingapp/api/stocks/ `(POST)`: Create a new Stock object

  - `name`
  - `price`
  - `quantity` - Available shares that users can buy. This got updated everytime a user places a buy order on this stock.

- /tradingapp/api/stocks/ `(GET)`: List all Stock objects
