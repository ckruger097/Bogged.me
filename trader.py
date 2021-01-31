from pycoingecko import CoinGeckoAPI
from user_database import db
import user_database as udb

cg = CoinGeckoAPI()


def get_price(coin_id, currency):
    if not coin_id[0].isdigit():
        coin_id = coin_id.lower()
    currency = currency.lower()
    if coin_id == '':
        coin_id = "bitcoin"
    if currency == '':
        currency = "usd"
    price = cg.get_price(ids=coin_id, vs_currencies=currency)
    price = price.get(coin_id).get(currency)
    return price


def purchase(user, purchase, coin_amount, coin_id):
    balance = udb.get_user_balance(user)
    wallet = udb.get_user_wallet(user)
    id = udb.get_user_id(user)
    print("balance before:", balance)
    if balance < purchase:
        print("Error: Balance cannot be less than purchase")
        return False
    else:
        new_balance = balance - purchase
        if coin_id in wallet:
            wallet[coin_id] += coin_amount
        else:
            wallet[coin_id] = coin_amount

        # user_data_temp = udb.get_user(user)
        # user_data_temp["balance"] = balance
        # user_data_temp["wallet"] = wallet
        print("balance after: ", new_balance)
        udb.collection.update_one(
            {"_id": id},
            {
                "$set": {
                    "balance": new_balance,
                    "wallet": wallet
                }
            }
        )
        return True


def sell(user, purchase, coin_amount, coin_id):
    balance = db.get(user).get("balance")
    wallet = db.get(user).get("wallet")
    coin_balance = wallet.get(coin_id)
    if coin_amount > coin_balance:
        print("Error: Not enough coins")
        return False
    else:
        coin_balance -= coin_amount
        wallet[coin_id] = coin_balance
        balance += purchase

        user_data_temp = db.get(user)
        user_data_temp["balance"] = balance
        user_data_temp["wallet"] = wallet
        db.set(user, user_data_temp)
        # db.dump()
        return True


def calculate_profit(user):
    balance = udb.get_user_balance(user)
    print(f"balance in calculate profit: {balance}")
    currency = udb.get_user_currency(user).lower()
    starting_balance = udb.get_user_starting_balance(user)
    wallet = udb.get_user_wallet(user)
    coin_balance = 0
    for coin in wallet:
        temp_coin_balance = wallet[coin]
        temp_coin_balance *= cg.get_price(ids=coin, vs_currencies=currency).get(coin).get(currency)
        # print(temp_coin_balance)
        coin_balance += temp_coin_balance
    print(f"coin balance: {coin_balance}")
    balance += coin_balance
    percent_profit = balance / starting_balance
    return [balance, percent_profit]


def check_coin(coin_id):
    # if not coin_id[0].isdigit():
    # coin_id = coin_id.lower()
    try:

        data = cg.get_coin_by_id(coin_id)
        print("good coin")
        return True
    except ValueError:
        print('bad coin')
        return False
