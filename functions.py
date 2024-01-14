#!/usr/bin/python3

from robin_stocks import robinhood as rs
import time
import smtplib
import os
import sys
import pandas as pd
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# # if I need to use Postmark
# from postmarker.core import PostmarkClient

def get_third_friday(): # modified to two fridays from next
    today = datetime.date.today()
    third_friday = today + datetime.timedelta((4-today.weekday()) % 7) + datetime.timedelta(7) + datetime.timedelta(7)
    return third_friday

def get_upcoming_earnings(ticker):
    earnings = rs.stocks.get_earnings(ticker, info=None) # gather earnings data
    try:
        earning = earnings[-1]
        report = earning['report']
        date = report['date']
        earnings_coming_up = date
    except IndexError:
        d = {}
        di = {}
        d['report'] = 'N/A'
        earnings_coming_up = d
    return earnings_coming_up

def get_watchlist_tickers(name):
    watchlist_tickers = []
    watchlists = rs.account.get_watchlist_by_name(name=name, info=None)
    results = watchlists['results']
    for result in results:
        watchlist_tickers.append(result['symbol'])
    return watchlist_tickers

def get_tickers():
    tickers = (rs.markets.get_top_100(info='symbol')) # gathers top 100 tickers on Robinhood
    tickers = tickers + get_watchlist_tickers('weed stocks')
    tickers = tickers + get_watchlist_tickers('watchlist')
    tickers = ticker_cleanup(tickers)
    return tickers

def ticker_cleanup(tickers):
    clean_tickers = []
    for ticker in tickers:
        if ticker not in clean_tickers:
            clean_tickers.append(ticker)
    return clean_tickers

def create_dataframe(d):
    #print(d)
    columns = []
    df_list = []
    count = 0
    for item in d:
        temp_list = []
        if item != None:
            for key, value in item.items():
                try:
                    value = round(float(value), 3)
                except:
                    pass
                if count == 0:
                    columns.append(str(key))
                temp_list.append(value)
            count+=1
            df_list.append(temp_list)
    df = pd.DataFrame(df_list, columns=columns)
    #print(df)
    return df
    



def sendgrid_email_with_attachment(toaddr, fromaddr, subject, filename, filepath):
    # using SendGrid's Python Library
    # https://github.com/sendgrid/sendgrid-python

    # MAY NEED TO ADD THESE TO DOCKERFILE: 
    # pip install certifi
    # /Applications/Python\ 3.9/Install\ Certificates.command

    import base64
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)
    
    from dotenv import load_dotenv
    load_dotenv()

    message = Mail(
        to_emails=toaddr,
        subject=subject,
        from_email=fromaddr,
        html_content='<strong>Robinhood report, see attached. You may be interested in the charts below.</strong>'
    )

    with open(filename, 'rb') as f:
        data=f.read()
        f.close()
    encoded_file = base64.b64encode(data).decode()

    attachedFile = Attachment(
        FileContent(encoded_file),
        FileName(filename),
        FileType('application/xlsx'),
        Disposition('attachment')
    )
    
    import os

    a_list = [attachedFile]
    
    for file in os.listdir('.'):
        if file.endswith('.png'):
            with open(file, 'rb') as f:
                data=f.read()
                f.close()
            encoded_chart = base64.b64encode(data).decode()
            attach_chart = Attachment(
                FileContent(encoded_chart),
                FileName(file),
                FileType('image/png'),
                Disposition('attachment')
            )
            a_list.append(attach_chart)


    message.attachment = a_list
    
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print('/nEMAIL NOT SENT')
        print(e.message)

# ## Basic Layout for using Postmark if needed 

# # Send an email with the Postmark Python library
# # Learn more -> https://postmarkapp.com/send-email/python

# def send_postmark_email(toaddr, fromaddr, subject, filename, filepath):
#     from dotenv import load_dotenv
#     load_dotenv()

#     # Create an instance of the Postmark client
#     postmark = PostmarkClient(server_token=os.getenv('POSTMARK_SERVER_API_TOKEN'))

#     # Send an email
#     postmark.emails.send(
#     From=fromaddr,
#     To=toaddr,
#     Subject=subject,
#     HtmlBody='Hello'
#     )

# send_postmark_email('mthobson@ncsu.edu', 'mthobson@ncsu.edu', 'subject', 'filename', 'filepath')

def send_email_with_attachment(toaddr, subject, filename, filepath):
    from dotenv import load_dotenv
    load_dotenv()
    EMAIL_PASS = os.getenv('EMAIL_PASS')
    fromaddr = "insert_email@email.com"

    msg = MIMEMultipart()

    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject

    body = "Robinhood Report. See attached."

    msg.attach(MIMEText(body, 'plain'))

    try:
        attachment = open(filepath, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

        msg.attach(part)
    except:
        print('SOMETHING WENT WRONG ATTACHING FILE')

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    try:
        server.login(fromaddr, EMAIL_PASS)
    except smtplib.SMTPAuthenticationError:
        print('SMTP AuthenticationError')
    text = msg.as_string()
    try:
        server.sendmail(fromaddr, toaddr, text)
    except smtplib.SMTPSenderRefused:
        print('SMTP SenderRefused')
    server.quit()

#send_email_with_attachment('insert_email@email.com', 'test', None, None)

# this is a way to write a log file where exceptions are raised. exception is currently hard coded.
# import traceback
# try:
#     raise Exception('This is an error message.')
# except:
#     errorFile = open('errorInfo.txt', 'w')
#     errorFile.write(traceback.format_exc())
#     errorFile.close()
#     print('The traceback info was written to errorInfo.txt.')