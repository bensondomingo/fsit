# Python Coding Test

Please build a simple trading system as a pure REST API with the endpoints outlined below. We want to allow authenticated users the ability to place orders to buy and sell stocks and track the overall value of their investments. Stocks will have an id, name, and price.

- Create an endpoint to let users place trades. When an order is placed we need to record the quantity of the stock the user wants to buy or sell.

- Create an endpoint to retrieve the total value invested in a single stock by a user. To calculate this - we need to sum all the value of all orders placed by the user for a single stock. Order value is calculated by multiplying quantity and stock price.

- Create an endpoint to retrieve the total value invested in a single stock by a user.

## Assumptions

- There are already existing Stocks that traders can buy or sell.

  > Stocks can be created through the `createstock` management command which accepts three postitional arguments `name`, `price`, and `quantity`. Example command: `python manage.py createstock MCHP 85.6 100` will store a new stock entry on the database.

- Endpoints requires authenticated access. Use the `/rest-auth/login/` endpoint to secure auth token then add it on the Authorization header. Example: `Authorization Token 9a49cf05c4be8e4c33c9d915808f180e44ae2452`
  > To register for an account use `/rest-auth/registration/`. More details below.

## How to install

- Install dependencies by `running pip install -r requirements.txt`.
- Run `python manage.py makemigrations` and `python manage.py migrate`.
- Create stocks using `createstock` management command.
- You can now play with the endpoints.

## Required Endpoints

- `/tradingapp/api/orders/ (POST)`: Let users place a buy or sell trades.

  - `stock: int` - ID of Stock to trade
  - `order_type: str` - Type of transaction either `buy` or `sell`
  - `quantity: int` - Number of shares to buy or sell

  ### Sample POST data:

  ```
  {
    "stock": "MCHP",
    "order_type": "buy",
    "quantity": 5
  }
  ```

  ### Sample Response

  ```
  {
    "id": 1,
    "quantity": 5.0,
    "price_per_share": 10.0,
    "order_type": "buy",
    "amount": 50.0,
    "status": "success",
    "remarks": null,
    "created_at": "2020-08-28T00:48:09.779324+08:00",
    "updated_at": "2020-08-28T00:48:09.779376+08:00",
    "trader": "benson",
    "stock": "MCHP"
  }
  ```

- `/tradingapp/api/stocks/stock_id/ (GET)`: Retrieve the stock details and the total value invested by a user

  - `stock_id` - ID of Stock to retrieve

  ### Sample Response

  ```
  {
    "name": "MCHP",
    "invested": {
        "buy": {
            "amount": 50.0,
            "shares": 5
        },
        "sell": {
            "amount": 20.0,
            "shares": 2
        },
        "net_invested": 30.0,
        "net_shares": 3
    },
    "price": 10.0,
    "quantity": 97,
    "created_at": "2020-08-28T00:40:31.822264+08:00",
    "updated_at": "2020-08-28T00:50:43.856990+08:00"
  }
  ```

  > Note: `invested` field will be `null` if authenticated user has no investment on this Stock

## Aditional Endpoints

### User Registration and Authentication

- `/rest-auth/registration/ (POST)`: User registration

  - `username`
  - `email` (optional)
  - `password1`
  - `password2`

- `/rest-auth/login/ (POST)`: Authenticate user

  - `username`
  - `password`

- `/rest-auth/logout/ (POST)`: Logout user

- `/profile/api/profiles/profile_id/ (GET)`: Retrieve user profile

  - Sample response

  ```
  {
    "id": 1,
    "user": {
        "username": "benson",
        "email": "benson@tradingapp.com",
        "last_login": "2020-08-28T00:42:09.681368+08:00"
    },
    "balance": 100.0,
    "created_at": "2020-08-28T00:42:09.624109+08:00",
    "updated_at": "2020-08-28T00:42:09.624162+08:00"
  }
  ```

### Additional order endpoints

- `/tradingapp/api/orders/ (GET)`: List all orders created by an authenticated user

  - Sample Response

    ```
    [
      {
          "id": 2,
          "quantity": 2.0,
          "price_per_share": 10.0,
          "order_type": "sell",
          "amount": 20.0,
          "status": "success",
          "remarks": null,
          "created_at": "2020-08-28T00:50:43.872315+08:00",
          "updated_at": "2020-08-28T00:50:43.872363+08:00",
          "trader": "benson",
          "stock": "MCHP"
      },
      {
          "id": 1,
          "quantity": 5.0,
          "price_per_share": 10.0,
          "order_type": "buy",
          "amount": 50.0,
          "status": "success",
          "remarks": null,
          "created_at": "2020-08-28T00:48:09.779324+08:00",
          "updated_at": "2020-08-28T00:48:09.779376+08:00",
          "trader": "benson",
          "stock": "MCHP"
      }
    ]
    ```

- `/tradingapp/api/orders/order_id/ (GET)`: Retrive order details
  - `order_id` - ID of order to retrieve
  - Sample response
    ```
    {
      "id": 2,
      "quantity": 2.0,
      "price_per_share": 10.0,
      "order_type": "sell",
      "amount": 20.0,
      "status": "success",
      "remarks": null,
      "created_at": "2020-08-28T00:50:43.872315+08:00",
      "updated_at": "2020-08-28T00:50:43.872363+08:00",
      "trader": "benson",
      "stock": "MCHP",
      "stock_name": "MCHP"
    }
    ```

### Additional stock endpoints

- `/tradingapp/api/stocks/ (GET)`: List all Stock objects
  - Sample respone
    ```
    [
      {
          "name": "ADI",
          "invested": null,
          "price": 20.0,
          "quantity": 100,
          "created_at": "2020-08-28T00:41:03.060893+08:00",
          "updated_at": "2020-08-28T00:41:03.060931+08:00"
      },
      {
          "name": "MCHP",
          "invested": {
              "buy": {
                  "amount": 50.0,
                  "shares": 5
              },
              "sell": {
                  "amount": 20.0,
                  "shares": 2
              },
              "net_invested": 30.0,
              "net_shares": 3
          },
          "price": 10.0,
          "quantity": 97,
          "created_at": "2020-08-28T00:40:31.822264+08:00",
          "updated_at": "2020-08-28T00:50:43.856990+08:00"
      },
      {
          "name": "MXIM",
          "invested": null,
          "price": 5.0,
          "quantity": 100,
          "created_at": "2020-08-28T00:40:49.185251+08:00",
          "updated_at": "2020-08-28T00:40:49.185289+08:00"
      }
    ]
    ```
