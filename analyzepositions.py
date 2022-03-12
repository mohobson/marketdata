#!/usr/local/bin

# Analyze open option positions

# get all open positions in account
# return greeks and other info
# inform if it should be closed or held

from robin_stocks import robinhood as rs

# Modules
import functions
import SMA


def analyze_stock_positions():
    stock_positions = rs.account.get_open_stock_positions(info=None)
    return_data = []
    for stock in stock_positions:
        d = {}
        url = stock['instrument']
        symbol = rs.stocks.get_symbol_by_url(url)
        average_buy_price = stock['average_buy_price']
        price = rs.stocks.get_latest_price(symbol, priceType=None, includeExtendedHours=True)
        quantity = stock['quantity']
        equity = round(float(price[0]) * float(quantity), 2)
        profit_loss = round(equity - float(average_buy_price) * float(quantity), 2)
        profit_loss_percent = round(100 * profit_loss / (float(average_buy_price) * float(quantity)), 2)
        earnings = functions.get_upcoming_earnings(symbol)
        
        d['symbol'] = symbol
        d['average_buy_price'] = average_buy_price
        d['price'] = price[0]
        d['quantity'] = quantity
        d['equity'] = float(price[0]) * float(quantity)
        d['profit_loss'] = profit_loss
        d['profit_loss_percent'] = profit_loss_percent
        #d['earnings'] = earnings

        return_data.append(d)

    #print(return_data)
    return return_data


def analyze_option_positions():
    option_positions = rs.options.get_open_option_positions(info=None)
    return_data = []
    for option in option_positions:
        d = {}
        option_id = option['option_id']
        get_option_data = rs.options.get_option_instrument_data_by_id(option_id,info=None)
        d['chain_symbol'] = option['chain_symbol']
        d['short_or_long'] = option['type']
        d['quantity'] = option['quantity']
        d['expiration_date'] = get_option_data['expiration_date']
        d['strike_price'] = get_option_data['strike_price']
        return_data.append(d)
    return return_data


#analyze_stock_positions()
#analyze_option_positions()
