from flask import Flask, request, jsonify
import sqlite3, logging, ssl
from datetime import datetime, timedelta
from flask_sslify import SSLify
from IPing_f import *
import pyodbc
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pyodbc
from datetime import datetime

#
server = "x"
database = 'x'
username = 'x'
password = 'x'
driver = '{SQL Server}'
#
# Użycie funkcji do wysłania e-maila
sender_email = 'x'
smtp_server0 = 'x'
smtp_username0 = 'x'
smtp_password0 = 'x'

###########################################
##### merge z host_data_bufo do host
def remove_invalid_data_from_host_data_bufor():
    try:
        conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
        cursor = conn.cursor()
        ### agregujemy dane do tabeli hosts i kasujemy najstarsze wpisy
        sql_query = """
        MERGE INTO Host AS target
        USING (
        SELECT ip, port, app_guid, guid, MAX(description) AS description, MAX(custom1) AS custom1,
        MAX(data_log) AS data_log, MAX(alert_mail_address) AS alert_mail_address,
        MAX(client_description) AS client_description
        FROM Host_data_bufor
        GROUP BY ip, port, app_guid, guid
        ) AS source
        ON (target.ip = source.ip AND target.port = source.port AND target.app_guid = source.app_guid)
        WHEN MATCHED THEN
        UPDATE SET target.description = source.description,
               target.app_guid = source.app_guid,
               target.guid = source.guid,
               target.custom1 = source.custom1,
               target.data_log = source.data_log,
               target.alert_mail_address = source.alert_mail_address,
               target.client_description = source.client_description
        WHEN NOT MATCHED BY TARGET THEN
        INSERT (ip, port, description, app_guid, guid, custom1, data_log, alert_mail_address, client_description)
        VALUES (source.ip, source.port, source.description, source.app_guid, source.guid, source.custom1, source.data_log, source.alert_mail_address, source.client_description)
        WHEN NOT MATCHED BY SOURCE THEN
        DELETE;
        """
        print("Agregacja do tabeli host");
        cursor.execute(sql_query)
        conn.commit()
        print("Zakończenie agregacji");

    except pyodbc.Error as e:
        print("Wystąpił błąd podczas łączenia z bazą danych:", str(e)) 
        #cursor.execute("DELETE FROM host_data_bufor")
        #wyslij mail / sms do mnie z taka informacja
        conn.commit()
    finally:
        conn.close()

remove_invalid_data_from_host_data_bufor()

###########################################
print("Aktualizacja pola alert_now w zależności od wartości percent_available i app_reachable")
conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
cursor = conn.cursor()

# Aktualizacja wartości pola alert_now na 1, jeśli percent_available jest mniejszy niż 65 i app_reachable wynosi 1
cursor.execute("""
UPDATE Host
SET alert_now = 1
WHERE (percent_available < 65 AND (app_reachable = 1 OR app_reachable IS NULL))
  AND  alert_now != 1
""")


# Aktualizacja wartości pola alert_now na 0, jeśli percent_available wynosi co najmniej 65 lub app_reachable wynosi 0
cursor.execute("""
    UPDATE Host
    SET alert_now = 0
    WHERE (percent_available >= 65 AND alert_now != 0) OR (app_reachable = 0 AND alert_now != 0)
""")

conn.commit()
conn.close()
###########################################
print("Sprawdzanie, czy główna aplikacja kliencka jest niedostępna")
conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
cursor = conn.cursor()

# Pobranie rekordów z tabeli app_lic, dla których alert_now wynosi 1 lub 0
cursor.execute("""
    SELECT *
    FROM app_lic
    WHERE alert_now IN (0, 1)
""")
rows = cursor.fetchall()
#print('Rekordy - agenty z niedostępną aplikacją kliencką:', rows)

# Pobranie nazw kolumn z wyniku zapytania
column_names = [column[0] for column in cursor.description]

for row in rows:
    # Utworzenie słownika dla wiersza, gdzie kluczami są nazwy kolumn
    row_dict = {column_names[i]: row[i] for i in range(len(column_names))}
    app_guid = row_dict['app_guid']  # Pobranie app_guid z wiersza
    alert_now = row_dict['alert_now']  # Pobranie alert_now z wiersza

    if alert_now == 1:
        # Aktualizacja pola app_reachable dla danego app_guid na 0, gdy alert_now wynosi 1
        cursor.execute("""
            UPDATE Host
            SET app_reachable = 0
            WHERE app_guid = ? AND app_reachable = 1
        """, (app_guid,))
    else:
        # Aktualizacja pola app_reachable dla danego app_guid na 1, gdy alert_now wynosi 0
        cursor.execute("""
            UPDATE Host
            SET app_reachable = 1
            WHERE app_guid = ? AND app_reachable = 0
        """, (app_guid,))
    conn.commit()
conn.close()
###########################################

# mail alert

def send_email(recipient, subject, message):
    # Konfiguracja serwera SMTP
    smtp_server = smtp_server0
    smtp_port = 587
    smtp_username = smtp_username0
    smtp_password = smtp_password0

    # Tworzenie wiadomości email
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    # Wysyłka wiadomości email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, recipient, msg.as_string())
        server.quit()
        #print('Wiadomość email została wysłana do', recipient)
        return True
    except Exception as e:
        print('Błąd podczas wysyłania wiadomości email:', str(e))
        return False

def process_alert_emails():
    print('process_alert_emails');
    try:
        conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ip, port, alert_mail_address, description
            FROM Host
            WHERE alert_now = 1 AND alert_notify_mail_send = 0
        """)
        rows = cursor.fetchall()

        for row in rows:
            ip, port, recipient, description = row

            print('Wysłanie wiadomości email')
            subject = f'Alert: Host niedostępny - {description}'
            message = f'Host o adresie {ip}:{port} {description} jest niedostępny.'
            if send_email(recipient, subject, message):
                print(' Aktualizacja informacji o wysłaniu alertu mailowego')
                cursor.execute("""
                    UPDATE Host
                    SET alert_notify_mail_send = 1
                    WHERE ip = ? AND port = ? AND alert_notify_mail_send != 1
                """, (ip, port))
                conn.commit()
    except Exception as e:
        print('Błąd podczas przetwarzania alertów emailowych:', str(e))
    finally:
        conn.close()


process_alert_emails()

def process_host_availability():
    print('process_host_availability');
    try:
        conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
        cursor = conn.cursor()

        print(' Pobranie rekordów z tabeli Host, które zmieniły stan na dostępny (alert_now = 0)')
        cursor.execute("""
               SELECT ip, port, alert_now, alert_notify_mail_send, alert_mail_address, description, percent_available
    FROM Host
    WHERE alert_notify_mail_send = 1
    AND alert_now = 0 AND app_reachable = 1  
        """)

        rows = cursor.fetchall()
        print('rows ', rows)

        for row in rows:
            ip, port, alert_now, alert_notify_mail_send, recipient, description, percent_available = row
            print('row', row);
            print('Ustawienie alert_notify_mail_send na 0, jeśli alert_now jest równy 0 i percent_available=100');
            if alert_now == 0 and percent_available == 100:
            
                subject = f'Alert: Host dostępny - {description}'
                message = f'Host o adresie {ip}:{port} {description}jest ponownie dostępny.'
                send_email(recipient, subject, message)            
            
                cursor.execute("""
                    UPDATE Host
                    SET alert_notify_mail_send = 0
                    WHERE ip = ? AND port = ? AND alert_notify_mail_send != 0
                """, (ip, port))
                conn.commit()

                
    except Exception as e:
        print('Błąd podczas przetwarzania dostępności hostów:', str(e))
    finally:
        conn.close()

process_host_availability()
#############################

#host_data_bufor
def kasuj_stare_wpisy():
    print('kasuj stare wpisy');
    try:
        conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
        cursor = conn.cursor()
        
        # Usunięcie wpisów starszych niż 10 minut
        cursor.execute("""DELETE FROM Host_data_bufor
                  WHERE data_log < DATEADD(MINUTE, -10, GETDATE())                    
                  """)
        conn.commit()
        conn.close()
        print("Stare wpisy zostały usunięte pomyślnie.")
    except Exception as e:
        print("Wystąpił błąd podczas usuwania starych wpisów:", str(e))
        
kasuj_stare_wpisy();
########################################################################
def oblicz_dostepnosc_hosta():
    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
    print('Obliczanie procentu dostępności hosta (percent_available')
    try:
        cursor.execute("""
        UPDATE Host
        SET percent_available = (
        SELECT FORMAT(
        CAST(SUM(CASE WHEN reachable = 1 THEN 1 ELSE 0 END) AS DECIMAL) / COUNT(*) * 100, 
        'N2')
        FROM Host_data_bufor
        WHERE app_guid = Host.app_guid AND ip = Host.ip AND port = Host.port
        )
        WHERE EXISTS (
        SELECT 1 
        FROM Host_data_bufor 
        WHERE app_guid = Host.app_guid AND ip = Host.ip AND port = Host.port)
        AND (
        percent_available != (
        SELECT FORMAT(
            CAST(SUM(CASE WHEN reachable = 1 THEN 1 ELSE 0 END) AS DECIMAL) / COUNT(*) * 100, 
            'N2')
        FROM Host_data_bufor
        WHERE app_guid = Host.app_guid AND ip = Host.ip AND port = Host.port
        )
        OR percent_available IS NULL
        )
                                                  """)
        conn.commit()
        if cursor.rowcount > 0:
            print("Zaktualizowano procent dostępności hosta.")
        else:
            print("Nie było potrzeby aktualizacji.")
    except Exception as e:
        print("Wystąpił błąd podczas aktualizacji dostępności hosta:", str(e))
    finally:
        conn.close()

oblicz_dostepnosc_hosta()