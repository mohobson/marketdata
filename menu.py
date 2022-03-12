#!/usr/local/bin

# MENU

import time

def optional_tickers(ticker_list):
    y_or_n = input('\nWould you like to add tickers? (y/n): ')
    if y_or_n.lower() == 'y':
        add_tickers = input('\nSeparate tickers by spaces: ')
        add_tickers = list(add_tickers.split(" "))
        #print(add_tickers)
        for ticker in add_tickers:
            if ticker not in ticker_list:
                ticker_list.append(ticker)
    else:
        pass
    return ticker_list


def change_SMA(old_N1, old_N2):
    y_or_n = input('\nWould you like to change the SMAs from ' + str(old_N1) + ' and ' + str(old_N2) + ' to something new? (y/n): ')
    if y_or_n.lower() == 'y':
        new_N1 = input('\nEnter lower SMA: ')
        new_N2 = input('\nEnter upper SMA: ')
        new_SMAs = int(new_N1), int(new_N2)
    else:
        new_SMAs = int(old_N1), int(old_N2)
    return new_SMAs
  
