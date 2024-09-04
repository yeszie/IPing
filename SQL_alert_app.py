from flask import Flask, request, jsonify
import sqlite3, logging, ssl
from datetime import datetime, timedelta
from flask_sslify import SSLify
from IPing_f import *
import pyodbc
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smsapi.client import SmsApiPlClient
from smsapi.client import Client
import requests
from datetime import datetime

#
server = "xxxxxxxxxxxxxxxxx"
database = 'xxxxxxxxxxxxxxx'
username = 'xxxxxxxxxxxxxxxxxxx'
password = 'xxxxxxxxxxxxxxxxxxxx'
driver = '{SQL Server}'
#
# Użycie funkcji do wysłania e-maila
sender_email = 'xxxxxxxxxxxxx'
smtp_server0 = 'xxxxxxxxxxxxx'
smtp_username0 = 'xxxxxxxxxxxx'
smtp_password0 = 'xxxxxxxxxxxxxxxx'
#

 
def check_for_alert():
    print('check_for_alert - client')
    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    print('conn', conn)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE App_lic
        SET alert_now = CASE 
            WHEN GETDATE() >= last_seen_alert THEN 1
            ELSE 0
        END;
    """)
    conn.commit()
    conn.close()

####################

check_for_alert();

import unicodedata
import re

def replace_dots_with_underscore(text):
    return text.replace('&', '_')
    #return text.replace('.', '_')

def remove_polish_characters(text):
    polish_characters = {'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
                         'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'}
    return ''.join(polish_characters.get(char, char) for char in text)

def convert_to_windows_1250(text):
    return text.encode('windows-1250', 'ignore').decode('windows-1250')

def send_sms_alert(SMS_alert_number, message):
    # Usunięcie polskich znaków
    message_without_polish = remove_polish_characters(message)
    
    # Zamiana kropek na podkreślenia w adresie IP
    message_with_underscore = replace_dots_with_underscore(message_without_polish)
    
    # Konwersja do kodowania Windows-1250
    message_windows_1250 = convert_to_windows_1250(message_with_underscore)
    
    # Wysłanie wiadomości za pomocą klienta SMSAPI
    client = Client("https://api.smsapi.pl/", access_token="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", details=1, normalize=1, flash=0, max_parts=1)
    send_results = client.sms.send(to=SMS_alert_number, message=message_windows_1250, from_="IPing.pl")
 
    # Wyświetlenie wyników wysyłania
    for result in send_results:
        print(result.id, result.points, result.error)


# Funkcja do wysyłania powiadomienia mailowego
def send_email_alert(host_info, alert_type):
    print('send_email_alert');
    try:
        # Dane do połączenia z serwerem SMTP
        smtp_server = smtp_server0
        smtp_port = 587
        smtp_username = smtp_username0
        smtp_password = smtp_password0

        # Adres nadawcy i odbiorcy
        from_addr = sender_email
        to_addr = host_info['alert_mail_address']

        # Treść wiadomości
        if alert_type == 'alert':
            print('alert_type', alert_type)
            subject = 'Alarm: Agent niedostępny'
            body = f"""\
            Witaj,

            Agent {host_info['hostname']} ({host_info['public_ip']}) jest obecnie niedostępny.

            Informacje o hoście:
            - System operacyjny: {host_info['os_info']}
            - Wersja aplikacji: {host_info['app_ver']}

            Pozdrawiamy,
            IPing.pl
            """          
        else:  # 'restore' - powiadomienie o przywróceniu dostępności
            subject = 'Powrót online: Agent dostępny'
            body = f"""\
            Witaj,

            Agent {host_info['hostname']} ({host_info['public_ip']}) jest ponownie dostępny.

            Informacje o hoście:
            - System operacyjny: {host_info['os_info']}
            - Wersja aplikacji: {host_info['app_ver']}

            Pozdrawiamy,
            IPing.pl
            """
        # Konfiguracja wiadomości e-mail
        msg = MIMEMultipart()
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Utworzenie połączenia SMTP i wysłanie wiadomości
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)

        print(f'Wysłano powiadomienie e-mail do: {to_addr}')
    except Exception as e:
        print(f'Błąd podczas wysyłania e-maila: {e}')

# Funkcja do aktualizacji pól dotyczących alertów w bazie danych
def update_alert_fields(app_guid, alert_type):
    try:
        # Połączenie z bazą danych
        conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
        cursor = conn.cursor()

        # Aktualizacja pola alert_notify_mail_send
        print('Aktualizacja pola alert_notify_mail_send')
        if alert_type == 'alert':
            print('alert_type', alert_type);
            cursor.execute("""
                UPDATE App_lic
                SET alert_notify_mail_send = 1
                WHERE app_guid = ? AND alert_now = 1 AND alert_notify_mail_send = 0
            """, app_guid)
        else:  # 'restore' - przywrócenie dostępności
            cursor.execute("""
                UPDATE App_lic
                SET alert_notify_mail_send = 0
                WHERE app_guid = ? AND alert_now = 0 AND alert_notify_mail_send = 1
            """, app_guid)

        conn.commit()
        conn.close()
    except Exception as e:
        print(f'Błąd podczas aktualizacji pól dotyczących alertów: {e}')

# Funkcja główna do obsługi powiadomień
def handle_alerts():
    print('handle_alerts')
    try:
        # Połączenie z bazą danych
        conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
        cursor = conn.cursor()

        # Pobranie rekordów z tabeli App_lic, dla których należy wysłać powiadomienie
        cursor.execute("""
            SELECT app_guid, hostname, public_ip, os_info, app_ver, alert_mail_address, alert_now, last_seen, app_activated_license, SMS_alerting, SMS_alert_number, client_description
            FROM App_lic
            WHERE (alert_now = 1 AND alert_notify_mail_send = 0)
                OR (alert_now = 0 AND alert_notify_mail_send = 1)
        """)
        rows = cursor.fetchall()

        for row in rows:
            app_guid, hostname, public_ip, os_info, app_ver, alert_mail_address, alert_now, last_seen, app_activated_license, SMS_alerting, SMS_alert_number, client_description  = row
            host_info = {
                'hostname': hostname,
                'public_ip': public_ip,
                'os_info': os_info,
                'app_ver': app_ver,
                'alert_mail_address': alert_mail_address,
                'last_seen' : last_seen,      
                'app_activated_license':app_activated_license, 
                'SMS_alerting':SMS_alerting, 
                'SMS_alert_number':SMS_alert_number,
                'client_description' : client_description
            }
            
            def round_to_second(time_obj):
                # Zaokrąglenie czasu do sekundy
                rounded_time_obj = time_obj.replace(microsecond=0)
                return rounded_time_obj
            
            rounded_last_seen = round_to_second(last_seen)



            if alert_now == 1:
                # Wysłanie powiadomienia o alarmie
                send_email_alert(host_info, 'alert')
                # Aktualizacja pól dotyczących alertów w bazie danych
                update_alert_fields(app_guid, 'alert')
            #SMS   
                if app_activated_license and SMS_alerting:
                    msg_ = "Agent nieosiagalny "  + client_description + " "  + hostname + " "  + str(rounded_last_seen)
                    message = str(msg_)
                    print('SMS', message)
                    response = send_sms_alert(SMS_alert_number, message);
                    print(response)

            else:
                # Wysłanie powiadomienia o przywróceniu dostępności
                send_email_alert(host_info, 'restore')
                # Aktualizacja pól dotyczących alertów w bazie danych
                update_alert_fields(app_guid, 'restore')
            #SMS    
                if app_activated_license and SMS_alerting:
                    msg_ = "Agent OK "             + client_description + " " + hostname + " " + str(rounded_last_seen)
                    message = str(msg_)
                    print('SMS', message)
                    response = send_sms_alert(SMS_alert_number, message);
                    print(response)

    except Exception as e:
        print(f'Błąd podczas obsługi powiadomień: {e}')
    finally:
        conn.close()

# Wywołanie funkcji obsługującej powiadomienia
handle_alerts()
