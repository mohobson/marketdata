#!/usr/local/bin

# CSP

import functions
import SMA
import datetime

from robin_stocks import robinhood as rs


def cash_secured_put(tickers):
    cheap_tickers = []
    put_data = []
    price_dict = {}
    expiration_date = str(functions.get_third_friday())
    for ticker in tickers: #iterate thru top 100 tickers on Robinhood
        price = rs.stocks.get_latest_price(ticker,priceType=None,includeExtendedHours=True) # get the latest price for each ticker
        if float(price[0]) < 15.0: # if the latest price is less than $15, add it to my list
            cheap_tickers.append(ticker)
            price_dict[str(ticker)] = price
    for cheap_ticker in cheap_tickers: # iterate thru list of <$15 tickers, pass if no option chain
        try:
            put_options = rs.options.find_options_by_specific_profitability(cheap_ticker, expirationDate=expiration_date, strikePrice=None, optionType='put', typeProfit='chance_of_profit_short', profitFloor=0.0, profitCeiling=1.0, info=None) # get options data for ticker. returns a list of dictionaries of kay/value pairs for all stock option market data
            for put in put_options: # iterate thru dictionaries
                d = {}
                pass_or_fail = 'pass' # set a parameter for filtering out the put options i dont care to see
                chain_symbol = put['chain_symbol']
                chance_of_profit_short = put['chance_of_profit_short']
                if float(chance_of_profit_short) < 0.50:
                    pass_or_fail = 'fail'
                elif float(chance_of_profit_short) > 0.90:
                    pass_or_fail = 'fail'
                open_interest = put['open_interest']
                volume = put['volume']
                if float(open_interest) < 100.0:
                    pass_or_fail = 'fail'
                if float(volume==0.0):
                    pass_or_fail = 'fail'

                d['chain_symbol'] = put['chain_symbol']
                d['price'] = price_dict[put['chain_symbol']][0]
                d['expiration_date'] = put['expiration_date']
                d['earnings_coming_up'] = functions.get_upcoming_earnings(chain_symbol)
                d['volume'] = volume
                d['open_interest'] = open_interest
                d['strike_price'] = put['strike_price']
                d['type_'] = put['type']
                d['chance_of_profit_short'] = put['chance_of_profit_short']
                d['implied_volatility'] = put['implied_volatility']
                d['break_even_price'] = put['break_even_price']
                d['ask_price'] = put['ask_price']
                d['bid_price'] = put['bid_price']
                d['mark_price'] = put['mark_price']
                d['last_trade_price'] = put['last_trade_price']
                d['delta'] = put['delta']
                d['gamma'] = put['gamma']
                d['rho'] = put['rho']
                d['theta'] = put['theta']
                d['vega'] = put['vega']
                

                if pass_or_fail == 'pass': # if the put option passes my filters, append to list
                    # print('\n......................................')
                    put_data.append(d)
        except:
            pass
    return put_data

