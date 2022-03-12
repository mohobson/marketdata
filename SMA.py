#!/usr/local/bin

# This module accepts a ticker and two moving average periods and returns a chart and buy/sell signals based on crossing lines

# Imports
from robin_stocks import robinhood as rs
import requests
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import pyEX as p
import time
import os

# Modules
import functions


def within_percentage(n1, n2, percent):
    #convert n1 and n2 to float
    if percent==None:
        percent = 5
    percent = float(percent)
    n1 = float(n1)
    n2 = float(n2)
    yes_or_no = 0
    n2_upper = n2+n2*percent/100
    n2_lower = n2-n2*percent/100
    if n1 > n2_lower and n1 < n2_upper or n1 == n2_lower or n1 == n2_upper:
        yes_or_no = 1
    if yes_or_no == 0:
        print(str(n1) + ' is not within ' + str((percent)) + '% of ' + str(n2))
    else:
        print(str(n1) + ' is within ' + str((percent)) + '% of ' + str(n2))
    return yes_or_no

# This function will calculate SMAs from list of prices and two given periods
# Then it can plot it
def calcSMA(ticker, N1, N2):

    interval = 'day'
    span = 'year'

    # Robinhood functions that return lists of close dates and prices
    closeDate=rs.get_stock_historicals(ticker, interval=interval, span=span, bounds='regular', info='begins_at')
    closePrice=rs.get_stock_historicals(ticker, interval=interval, span=span, bounds='regular', info='close_price')

    latest_price = rs.get_latest_price(ticker, priceType=None, includeExtendedHours=True)

    # Add most recent price since get_stock_historicals ends yesterday
    closePrice += latest_price
    
    # Add today's date to closeDate to match length and index of closePrice
    today = datetime.today().strftime('%Y-%m-%d')
    closeDate += [today] # want to add it by using closeDate[-1] + 1day

    # Convert closePrice to float
    floatPrice=[]
    for price in closePrice:
        price = float(price)
        price = round(price, 2)
        floatPrice.append(price)

    # print(len(closeDate))
    # print(len(closePrice))
    # print(len(floatPrice))

    # Create dataframe from list
    structure_data=[]
    index=0
    for date in closeDate:
        try:
            structure_data.append([date, floatPrice[index]])
            index += 1
        except IndexError:
            print('IndexError: data may be delayed by a day')
            if index==0:
                index += 1
    df = pd.DataFrame(structure_data, columns=['ds', 'y'])

    # create lists
    cumsum, N1_moving_aves, N2_moving_aves = [0], [], []

    # use enumerate to track where i'm at in list
    # calc SMA for N1 and N2
    for i, x in enumerate(floatPrice, 1):
        cumsum.append(cumsum[i-1] + x)
        if i>=N1:
            moving_ave = (cumsum[i] - cumsum[i-N1])/N1
            moving_ave = round(moving_ave, 2)
            N1_moving_aves.append(moving_ave)
        else:
            N1_moving_aves.append(None)
    for i, x in enumerate(floatPrice, 1):
        cumsum.append(cumsum[i-1] + x)
        if i>=N2:
            moving_ave = (cumsum[i] - cumsum[i-N2])/N2
            moving_ave = round(moving_ave, 2)
            N2_moving_aves.append(moving_ave)
        else:
            N2_moving_aves.append(None)

    # add means to df so they can be plotted
    rolling_mean = pd.DataFrame(N1_moving_aves)
    rolling_mean2 = pd.DataFrame(N2_moving_aves)


    # print(rolling_mean)
    # print(rolling_mean2)

    ##################################

    # for plotting chart to excel (no need for this now...)

    # writer = pd.ExcelWriter('SMA_chart.xlsx', engine='xlsxwriter')

    # # Convert the dataframe to an XlsxWriter Excel object.
    # df.to_excel(writer, sheet_name='Sheet1')
    # rolling_mean.to_excel(writer, sheet_name='Sheet1', startcol=3)
    # rolling_mean2.to_excel(writer, sheet_name='Sheet1', startcol=5)

    # # Get the xlsxwriter objects from the dataframe writer object.
    # workbook  = writer.book
    # worksheet = writer.sheets['Sheet1']

    # # Create a chart object.
    # chart = workbook.add_chart({'type': 'line'})

    # # Configure the series of the chart from the dataframe data.
    # chart.add_series({'name': 'Price', 'values': '=Sheet1!$C$2:$C$253'})
    # chart.add_series({'name': 'SMA ' + str(N1), 'values': '=Sheet1!$E$2:$E$253'})
    # chart.add_series({'name': 'SMA ' + str(N2), 'values': '=Sheet1!$G$2:$G$253'})

    # chart.set_x_axis({'name': 'Time'})
    # chart.set_y_axis({'name': 'Price'})

    # # Insert the chart into the worksheet.
    # worksheet.insert_chart('J2', chart)

    # writer.save()


    list1 = crossover(ticker, floatPrice, N1_moving_aves, name1='price', name2='SMA ' + str(N1))
    list2 = crossover(ticker, floatPrice, N2_moving_aves, name1='price', name2='SMA ' + str(N2))
    list3 = crossover(ticker, N1_moving_aves, N2_moving_aves, name1='SMA ' + str(N1), name2='SMA ' + str(N2))

    # print(list1, list2, list3)

    list4 = []
    list4 += list1 + list2 + list3
    
    if len(list4) == 0:
        list4 = [None]
    
    # add in price to dictionary
    for l in list4:
        if list4 != [None]:
            l['price'] = floatPrice[-1]
    

    ##################################


    # for plotting and saving as .png
    plot_df = pd.DataFrame(structure_data, columns=['ds', 'y'])

    plot_rolling_mean = pd.DataFrame(N1_moving_aves, columns = ['y'])
    plot_rolling_mean2 = pd.DataFrame(N2_moving_aves, columns = ['y'])

    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)

    ax1.plot(plot_df['ds'], plot_df['y'], label = 'Price (' + str(floatPrice[-1]) + ')')
    ax1.plot(plot_rolling_mean['y'], label = 'SMA ' + str(N1) + ' (' + str(N1_moving_aves[-1]) + ')')
    ax1.plot(plot_rolling_mean2['y'], label = 'SMA ' + str(N2) + ' (' + str(N2_moving_aves[-1]) + ')')
    # ax1.set_xticks(np.arange(1, 10))
    plt.legend(loc = 'upper left')
    plt.title(str(ticker) + '\n (' + str(closeDate[-1]) + ')', loc='center')
    
    for d in list1:
        if d['signal'] == 'buy' or d['signal'] == 'mega buy':
            plt.savefig(str(ticker) + '_chart.png')

    for d in list2:
        if d['signal'] == 'buy' or d['signal'] == 'mega buy':
            plt.savefig(str(ticker) + '_chart.png')

    for d in list3:
        if d['signal'] == 'buy' or d['signal'] == 'mega buy':
            plt.savefig(str(ticker) + '_chart.png')

    plt.close('all')
    # plt.cla()

    # plt.show()

    ##################################

    return list4
    
def crossover(ticker, p1, p2, name1, name2):
    # only want to look at the last 5 days
    index = -5
    over_under_index = 0
    over_under = []
    signal = ''
    desc = 'no breakout'
    signalList = []
    while index <= -1:
        d = {}
        #close_one = within_percentage(p1[index], p2[index], percent=1)
        if p1[index] == p2[index]:
            over_under.append('equal')
            #print(str(ticker) + ' ' + name1 + ', ' + str(p1[index]) + ', is equal to ' + name2 + ', ' + str(p2[index]))
        if p1[index] > p2[index]:
            over_under.append('over')
            #print(str(ticker) + ' ' + name1 + ', ' + str(p1[index]) + ', is greater than ' + name2 + ', ' + str(p2[index]))
        if p1[index] < p2[index]:
            over_under.append('under')
            #print(str(ticker) + ' ' + name1 + ', ' + str(p1[index]) + ', is less than ' + name2 + ', ' + str(p2[index]))
        # skip first iteration
        if over_under_index > 0:
            # if the price switches above or below the moving average
            if over_under[over_under_index-1] != over_under[over_under_index]:
                # if the price moves above the moving average
                if p1[index] > p2[index]:
                    signal = 'buy'
                    desc = name1 + ' broke above ' + name2 + ' ' + str(index*-1) + ' days ago.'
                    if index*-1 == 1:
                        desc = name1 + ' broke above ' + name2 + ' ' + str(index*-1) + ' day ago.'
                    #print(desc)
                if p1[index] < p2[index]:
                # if the price moves below the moving average
                    signal = 'sell'
                    desc = name1 + ' went below ' + name2 + ' ' + str(index*-1) + ' days ago.'
                    if index*-1 == 1:
                        desc = name1 + ' went below ' + name2 + ' ' + str(index*-1) + ' day ago.'
                    #print(desc)
            else:
                #print('no breakout')
                pass
        if index == -1 and desc != 'no breakout':
            d['ticker'] = ticker
            # d['price'] = ? rs.get_latest_price(ticker, priceType=None, includeExtendedHours=True)
            # d['resistance'] = ?
            d['signal'] = signal
            d['desc'] = desc
            signalList.append(d)
        index += 1
        over_under_index += 1
    return signalList

# takes a list of tickers and runs calcSMA function for each one
def all_signals(tickers, SMA1, SMA2):
    return_signals = []
    for ticker in tickers:
        # return_signals.append(calcSMA(ticker, SMA1, SMA2))
        signals = calcSMA(ticker, SMA1, SMA2)
        for signal in signals:
            if signal != None:
                return_signals.append(signal)
    return return_signals

# calcSMA('GE', 50, 200)
# all_signals(['SNDL', 'GE', 'PLUG', 'ACB'], 50, 200)