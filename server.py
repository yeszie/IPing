from flask import Flask, request, jsonify
import sqlite3, logging, ssl
from datetime import datetime, timedelta
from flask_sslify import SSLify
from IPing_f import *
import pyodbc
from colorama import Fore, Style

#
server = "xxxxxxxxxxxxxxxxxxx"
database = 'IPPL'
username = 'xxxxxxxxxxxxxxxxxxxx'
password = 'xxxxxxxxxxxxxxxxxxxx'
driver = '{SQL Server}'
#

#host_data_bufor, App_lic 
def dodaj(ip, port, description, reachable, client_description, guid, app_ver, custom1, app_guid, alert_mail_address):
    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""INSERT INTO Host_data_bufor 
            (ip, port, description, reachable, client_description, guid, app_ver, custom1, app_guid, data_log, alert_mail_address)  
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), ?)""", 
            (ip, port, description, reachable, client_description, guid, app_ver, custom1, app_guid, alert_mail_address))

        cursor.execute("""UPDATE App_lic 
                        SET last_seen = GETDATE(), last_seen_alert = DATEADD(MINUTE, 2, GETDATE())
                        WHERE app_guid = ? AND last_seen < DATEADD(SECOND, -60, GETDATE())""", (app_guid,))
        
        conn.commit()
    except pyodbc.Error as e:
        print_red("Wystąpił błąd podczas wykonywania zapytań:", str(e))
        conn.rollback()  # Cofnij transakcję w przypadku błędu
    finally:
        conn.close()

    
def aktualizuj_opisy1(app_ver, public_ip, hostname, os_info, current_user_c, app_guid):  
    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
    
    print('Aktualizacja tabeli App_lic');
    cursor.execute("""UPDATE App_lic
                   SET app_ver = ?, public_ip = ?, hostname = ?, os_info = ?, current_user_c = ?,
                   last_seen = GETDATE(), last_seen_alert = DATEADD(MINUTE, 2, GETDATE())
                   WHERE app_guid = ?
                   """, (app_ver, public_ip, hostname, os_info, current_user_c, app_guid))
    conn.commit()               
    conn.close()

   
app = Flask(__name__)
sslify = SSLify(app, permanent=True)  #TEST bez WSGI


def aktualizuj_reachable(app_guid):
    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()

    print('Aktualizacja tabeli host');
    cursor.execute("""UPDATE host
                   SET app_reachable = 1
                   WHERE (app_guid = ? AND app_reachable != 1) OR (app_guid = ? AND app_reachable IS NULL)
                   """, (app_guid, app_guid))
    conn.commit()
    conn.close()

 

@app.route('/app_exe', methods=['POST'])   #app_lic, hosty
def app_exe():
    data = request.json
    print('data from client: ', data)

    if data and 'app_guid' in data:
        app_guid = data['app_guid']
        app_ver = data.get('app_ver')
        public_ip = data.get('public_ip')
        hostname = data.get('hostname')
        os_info = data.get('os_info')
        current_user_c = data.get('current_user_c')

        # Aktualizacja danych aplikacji
        aktualizuj_opisy1(app_ver, public_ip, hostname, os_info, current_user_c, app_guid)

        # Pobranie adresu e-mail i informacji o licencji z tabeli App_lic
        conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
        cursor = conn.cursor()
        cursor.execute("""SELECT alert_mail_address, app_activated_license, SMS_alerting, SMS_alert_number, repeat_count, repeat_delay, ping_repeat FROM App_lic WHERE app_guid = ?""", (app_guid,))
        row = cursor.fetchone()
        conn.close()

        if row:
            alert_mail_address, app_activated_license, SMS_alerting, SMS_alert_number, repeat_count, repeat_delay, ping_repeat = row
            response_data = {
                "status": "success",
                "alert_mail_address": alert_mail_address,
                "app_activated_license": app_activated_license,
                "SMS_alerting": SMS_alerting, 
                "SMS_alert_number": SMS_alert_number,
                "repeat_count":repeat_count,
                "repeat_delay":repeat_delay,
                "ping_repeat":ping_repeat
            }
            print('response data', response_data)
            return jsonify(response_data)
        else:
            return jsonify({"status": "error", "message": "No data found for the provided app_guid"}), 404

    else:
        return jsonify({"status": "error", "message": "Invalid data format"}), 400


@app.route('/', methods=['POST'])    #host_data_bufor
def ping():
    data = request.json
    print('data from client: ', data);
    if data and 'ip' in data and 'port' in data and 'alert_mail_address' in data:
        ip = data['ip']
        port = data['port']
        description = data['description']
        reachable = data['reachable']
        client_description = data['client_description']
        guid = data['guid']
        app_ver = data['app_ver']
        custom1 = data['custom1']
        app_guid = data['app_guid']
        expiry_date = data['expiry_date']
        alert_mail_address = data['alert_mail_address']
        dodaj(ip, port, description, reachable, client_description, guid, app_ver, custom1, app_guid, alert_mail_address);
        aktualizuj_reachable(app_guid);        
        return jsonify({"status": "success"})  #200
    else:          
        return jsonify({"status": "error", "message": "Invalid data format"}), 400
     
 
@app.route('/lic', methods=['POST'])    
def lic():
    data = request.json
    print('data - endpoint lic: ', data)
    if data and 'guid' in data:
        guid = data['guid']
        app_guid = data.get('app_guid')  # Dodane pobieranie app_guid z danych wejściowych
         
        conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
        cursor = conn.cursor()
        cursor.execute('''SELECT active, klt_name, expiry_date, klt_mail, app_endpoint, ping_endpoint FROM Licenses WHERE guid = ?''', (guid,))
        result = cursor.fetchone()
        print('result', result) 
        if result:
            active, klt_name, expiry_date, klt_mail, app_endpoint, ping_endpoint = result
            # Pobranie client_description z tabeli App_lic
            cursor.execute('''SELECT client_description FROM App_lic WHERE guid = ? AND app_guid = ?''', (guid, app_guid))
            app_lic_result = cursor.fetchone()
            if app_lic_result:
                client_description = app_lic_result[0]
            else:
                client_description = None

            conn.close()

            if active:
                response_data = {
                    "status":             "success",
                    "active":             True,
                    "expiry_date":        expiry_date,
                    "customer":           klt_name,
                    "klt_mail":           klt_mail,
                    "client_description": client_description,
                    "app_endpoint":       app_endpoint, 
                    "ping_endpoint" :     ping_endpoint
                }  
                return jsonify(response_data)
            else:
                return jsonify({"status": "error", "message": "License inactive"}), 403
        else:
            return jsonify({"status": "error", "message": "License not found"}), 404
    else:
        return jsonify({"status": "error", "message": "Invalid data format"}), 400


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=18188, debug=True)