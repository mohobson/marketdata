#!/usr/local/bin

# Libraries
#import robin_stocks as rs
from robin_stocks import robinhood as rs
import time
import smtplib
import os
import sys
import pandas as pd
import datetime
import openpyxl

# import dotenv and search for environment variables from either .env file or os environment
from dotenv import load_dotenv
load_dotenv()

# Modules
import menu
import functions
import CSP
import SMA
import analyzepositions
import pyotp

# load time-based one time password from .env file or os environment
TOTP = os.getenv('TOTP')

# authenticate with dual-factor app inside robinhood
totp = pyotp.TOTP(TOTP).now()

ROBINHOOD_USERNAME = os.getenv('ROBINHOOD_USERNAME')
ROBINHOOD_PASSWORD = os.getenv('ROBINHOOD_PASSWORD')

rs.login(username=ROBINHOOD_USERNAME,
         password=ROBINHOOD_PASSWORD,
         expiresIn=86400,
         by_sms=True,
         mfa_code=totp)

def main():
    # set default SMAs
    N1 = 50
    N2 = 200

    tickers = functions.get_tickers()
    
    # menu_option = input('Would you like additional options? (y/n): ')
    menu_option = 'n'
    if menu_option.lower() == 'y':
        tickers = menu.optional_tickers(tickers)
        N1, N2 = menu.change_SMA(N1, N2)
    else:
        pass
    
    # convert lists from other modules to dataframe using create_dataframe
    # in functions module so they can go to Excel


    put_df = functions.create_dataframe(CSP.cash_secured_put(tickers))
    signal_df = functions.create_dataframe(SMA.all_signals(tickers, N1, N2))
    option_positions_df = functions.create_dataframe(analyzepositions.analyze_option_positions())
    stock_positions_df = functions.create_dataframe(analyzepositions.analyze_stock_positions())

    # use ExcelWriter to write to different sheets
    filename = 'robinhood.xlsx'
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        option_positions_df.to_excel(writer, sheet_name='Option Positions')
        stock_positions_df.to_excel(writer, sheet_name='Stock Positions')
        signal_df.to_excel(writer, sheet_name='Buy or Sell Signals')
        put_df.to_excel(writer, sheet_name=str(functions.get_third_friday())+' CSP')

        # Get the xlsxwriter workbook and worksheet objects
        workbook = writer.book
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]

            # Iterate through each column and set the width based on the maximum content length
            for i, col in enumerate(worksheet.columns):
                max_len = 3
                column = col[0].column_letter  # Get the column name
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_len:
                            max_len = len(cell.value)
                    except:
                        pass
                adjusted_width = (max_len + 2)
                worksheet.column_dimensions[column].width = adjusted_width

        # Save the workbook to apply column width changes
        # writer.save() # .save() function was removed from library - change to .close()
        # writer.close()

    # send email with Excel file
    subject = 'Robinhood Report'
    filepath = os.getcwd() + '/' + filename
    toaddr = os.getenv('toaddr')
    fromaddr = os.getenv('fromaddr')
    
    try:
        functions.sendgrid_email_with_attachment(toaddr, fromaddr, subject, filename, filepath)
        # functions.send_postmark_email(toaddr2, fromaddr2, subject, filename, filepath)
        # functions.send_email_with_attachment(toaddr, subject, filename, filepath)
        print('\nEMAIL SENT\n')

    except:
        print('NO EMAIL SENT')

    print(put_df)

    # remove charts
    dir_name = os.getcwd()
    test = os.listdir(dir_name)

    for item in test:
        if item.endswith(".png"):
            os.remove(os.path.join(dir_name, item))

    rs.logout()

if __name__ == '__main__':
    main()
