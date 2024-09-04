#pip install pip_system_certs python-certifi-win32 certifi pyopenssl pyyaml
# -*- coding: utf-8 -*-
print(" ")
import certifi, os, sys, ssl, platform, requests, socket, yaml, subprocess,  uuid 
from datetime import datetime, timedelta

cacert_file = "cacert.pem"
os.environ['REQUESTS_CA_BUNDLE'] = cacert_file

import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)
## 

from IPing_f import *

check_hosts_txt()

app_ver = 1
timeout = 2


def zapisz_zmienna_do_pliku(nazwa_zmiennej, your_variable, nazwa_pliku):
    try:
        with open(nazwa_pliku, 'r', encoding='utf-8') as file:
            existing_data = yaml.safe_load(file)
    except FileNotFoundError:
        existing_data = {}

    existing_data[nazwa_zmiennej] = your_variable

    with open(nazwa_pliku, 'w', encoding='utf-8') as file:
        yaml.dump(existing_data, file, allow_unicode=True)



def check_config_file():
    config_file = "IPing_client_config.yml"

    # Sprawdzenie istnienia pliku
    if not os.path.exists(config_file):
        print_c("red", "Plik IPing_client_config.yml nie istnieje.")
        return False

    # Odczytanie danych z pliku
    try:
        with open(config_file, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
    except FileNotFoundError:
        print_c("red", "Nie można otworzyć pliku IPing_client_config.yml.")
        return False
    
    # Sprawdzenie obecności kluczy
    if 'guid' not in data or 'app_guid' not in data:
        print_c("red","Plik IPing_client_config.yml nie zawiera poprawnych danych.")
        return False

    # Sprawdzenie poprawności wartości guid i app_guid
    guid = data['guid']
    app_guid = data['app_guid']
    try:
        uuid.UUID(guid, version=4)
        uuid.UUID(app_guid, version=4)
    except ValueError:
        print_c("red","Wartości GUID i App GUID w pliku IPing_client_config.yml nie są poprawne.")
        print_c("yellow","Usuwam błędne wartości. Wprowadź poprawne dane dotyczące licencjii.")
        zapisz_zmienna_do_pliku('app_guid', "", "IPing_client_config.yml");
        zapisz_zmienna_do_pliku('guid'    , "", "IPing_client_config.yml");
        return False

    # Zwrócenie True, jeśli wszystkie warunki zostały spełnione
    return True

# Przykład użycia funkcji
if check_config_file():
    print_c("green","Plik IPing_client_config.yml istnieje i zawiera poprawne dane.")
    # Kontynuuj działanie programu
else:
    print_c("red", "Proszę naprawić problemy z plikiem IPing_client_config.yml przed kontynuacją.")
    print_c("yellow", "Wprowadź dane licencji GUID oraz APP_GUID");
    try:
            #print_c("yellow", "Uruchamiam aplikację do wprowadzenia licencji");
            subprocess.run('IPing_license.exe')
    except FileNotFoundError:
            print_c("red", "Nie można znaleźć programu IPing_license.exe")
            time.sleep(10);
            exit();
    except Exception as e:
            print_c("red", f"Wystąpił błąd: {e}")
            time.sleep(10);
            exit();


def odczytaj_zmienna_z_yaml(nazwa_pliku, nazwa_zmiennej):
    with open(nazwa_pliku, 'r', encoding='utf-8') as plik:
        config = yaml.safe_load(plik)

    if nazwa_zmiennej in config:
        return config[nazwa_zmiennej]
    else:
        return None

public_ip = get_public_ip()
computer_name = get_computer_name()
os_info = get_os_info()
current_user_c = get_current_user()

def check_license(guid, app_guid):
    print_c('cyan','License checking..')
    url = "https://endpointsql.iping.pl/lic"
       
    data = {'guid': guid, 'app_guid': app_guid, 'public_ip': public_ip, 'computer_name': computer_name,  'app_ver': app_ver, 'current_user': current_user_c}
    
    #print('dane do api', data);
    response = requests.post(url, json=data)
    #print('response z api ', response);

    if response.status_code == 403 or response.status_code == 404:
        print_c('red', "Wykryto problem z licencją lub jej brak");
        time.sleep(10);
        exit();
    
    if response.status_code == 400:
        print_c('red', "Wykryto inny błąd");
        time.sleep(10);
        exit();

    if response.status_code == 200:
        result = response.json()
        #print('result', result);
        if result['status'] == 'success':
            active = result['active']
            expiry_date = result.get('expiry_date') 
            
            lic_test = odczytaj_zmienna_z_yaml('IPing_client_config.yml', 'license')
            if lic_test != expiry_date:
                zapisz_zmienna_do_pliku("license", expiry_date, "IPing_client_config.yml")
            customer = result.get('customer')  #.encode('utf-8') 
            expiry_date = datetime.strptime(expiry_date, '%a, %d %b %Y %H:%M:%S %Z')
            if active and expiry_date > datetime.now():
                print_c('green', "Licencja jest aktywna dla ", customer, "do ", expiry_date)
            else:
                print_c('red', "Licencja jest nieaktywna.")
                time.sleep(10);
                exit();
                
            email = odczytaj_zmienna_z_yaml('IPing_client_config.yml', 'email')
            if email != result['klt_mail']:
                print('Aktualizacja adresu email z serwera licencji na: ', result['klt_mail']);
                zapisz_zmienna_do_pliku("email", result['klt_mail'], "IPing_client_config.yml");

            customer_yml =  odczytaj_zmienna_z_yaml("IPing_client_config.yml", 'customer')
            
            if customer_yml != customer:
                zapisz_zmienna_do_pliku('customer', customer, "IPing_client_config.yml");
            
            if result['client_description'] != odczytaj_zmienna_z_yaml("IPing_client_config.yml", 'client_description'):
                zapisz_zmienna_do_pliku("client_description", result['client_description'], "IPing_client_config.yml");
                
            if result['app_endpoint'] != odczytaj_zmienna_z_yaml("IPing_client_config.yml", 'app_endpoint'):
                zapisz_zmienna_do_pliku("app_endpoint", result['app_endpoint'], "IPing_client_config.yml");    
            if result['ping_endpoint'] != odczytaj_zmienna_z_yaml("IPing_client_config.yml", 'ping_endpoint'):
                zapisz_zmienna_do_pliku("ping_endpoint", result['ping_endpoint'], "IPing_client_config.yml");    
                   
        else:
            print_c('red', f"Error: {result['message']}")
            print_c('red', 'Błąd komunikacji do serwera licencji, spróbuj ponownie później')
            time.sleep(10);
            exit();
    else:      
        print_c('red', f"Server error: {response.status_code}")
        print_c('red','Sprawdz czy masz łączność do serwera licencji: na porcie tcp/443   api.IPing.pl lub czy licencja jest aktywna')
        time.sleep(10);
        exit();


guid = odczytaj_zmienna_z_yaml('IPing_client_config.yml', 'guid')
app_guid = odczytaj_zmienna_z_yaml('IPing_client_config.yml', 'app_guid')
check_license(guid, app_guid)  


def zamelduj_aplikacje():
    print_c('cyan', 'Login app...'); 
    app_endpoint = odczytaj_zmienna_z_yaml("IPing_client_config.yml", 'app_endpoint')
    data = {'app_guid': app_guid, 'guid': guid, 'app_ver': app_ver, 'public_ip':public_ip, 'hostname': computer_name, 'os_info': os_info, 'current_user_c':current_user_c}
    response = requests.post(app_endpoint, json=data, verify=cacert_file)
    #response = requests.post(app_endpoint, json=data, verify=False)
    #print(response);
    if response.status_code == 200:
        result = response.json()
        #print('result', result);
        if result['status'] == 'success':
            #print('alert_mail_address: ', result['alert_mail_address'], 
            #'app_activated_license: ', result['app_activated_license'],
            #'SMS_alerting:', result['SMS_alerting'],   
            #'SMS_alert_number:',   result['SMS_alert_number']); 
                
            if result['app_activated_license'] != odczytaj_zmienna_z_yaml("IPing_client_config.yml", 'app_activated_license'):
                zapisz_zmienna_do_pliku("app_activated_license", result['app_activated_license'], "IPing_client_config.yml");
                
            if result['app_activated_license'] != True:
                print_c('red', 'Aplikacja klienta nie ma aktywnej licencji');
                time.sleep(60);
                exit();
                
            if result['alert_mail_address'] != odczytaj_zmienna_z_yaml("IPing_client_config.yml", 'alert_mail_address'):
                zapisz_zmienna_do_pliku("alert_mail_address", result['alert_mail_address'], "IPing_client_config.yml");               

            if result['SMS_alerting'] != odczytaj_zmienna_z_yaml("IPing_client_config.yml", 'SMS_alerting'):
                zapisz_zmienna_do_pliku("SMS_alerting", result['SMS_alerting'], "IPing_client_config.yml");            
            
            if result['SMS_alert_number'] != odczytaj_zmienna_z_yaml("IPing_client_config.yml", 'SMS_alert_number'):
                zapisz_zmienna_do_pliku("SMS_alert_number", result['SMS_alert_number'], "IPing_client_config.yml");               
            
            if result['repeat_count'] != odczytaj_zmienna_z_yaml("IPing_client_config.yml", 'repeat_count'):
                zapisz_zmienna_do_pliku("repeat_count", result['repeat_count'], "IPing_client_config.yml");
                
            if result['repeat_delay'] != odczytaj_zmienna_z_yaml("IPing_client_config.yml", 'repeat_delay'):
                zapisz_zmienna_do_pliku("repeat_delay", result['repeat_delay'], "IPing_client_config.yml");    
                
            if result['ping_repeat'] != odczytaj_zmienna_z_yaml("IPing_client_config.yml", 'ping_repeat'):
                zapisz_zmienna_do_pliku("ping_repeat", result['ping_repeat'], "IPing_client_config.yml"); 
                
        else:
            print_c('red', 'problem...')
            time.sleep(10);
            exit();
    else:
        print_c('red', 'problem z licencją aplikacji - należy podać właściwy app_guid w pliku konfiguracyjnym')
        time.sleep(10);
        exit();
        

zamelduj_aplikacje();


def is_port_open(host, port, timeout):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        s.close()
        return True
    except Exception as e:
        return False


ping_endpoint = odczytaj_zmienna_z_yaml("IPing_client_config.yml", 'ping_endpoint');


def send_ping(ip, description, server_url, unreachable_server_url, timeout):   
    try:
        ip = socket.gethostbyname(ip)  # Pobranie adresu IP na podstawie nazwy domenowej

        #print(isUp(ip))==True            

        if(isUp(ip)):
            print_c("green", '>')
            reachable = 1
        else:
            reachable = 0
            print_c("red", '>');
            notify_unreachable(ip, description, unreachable_server_url)

        data = {'ip': ip, 'port': 0, 'description': description, 'reachable': reachable, 'client_description': client_description, 'lic': lic, 'app_ver': app_ver, 'custom1': custom1, 'guid': guid, 'app_guid': app_guid, 'expiry_date': lic, 'alert_mail_address':alert_mail_address}
        #print('data - send_ping - line160', data)
        response = requests.post(server_url, json=data, verify=cacert_file)
        #print('guid - send_ping: ', data)
        if response.status_code == 200:
            #print(f"Success: Information sent to server for {description}")
            print_c("green","<");    
        else:
            print_c("red", f"Failure: Could not send information to server for {description}. Server returned status code {response.status_code}")
    except socket.gaierror as e:
        print_c("red", f"Error resolving hostname: {e}: ", ip, description)
        notify_unreachable(ip, description, unreachable_server_url)
    except requests.exceptions.RequestException as e:
        print_c("red", f"Request error: {e}")
    except Exception as e:
        print_c("red", f"An error occurred: {e}")


ping_repeat = odczytaj_zmienna_z_yaml("IPing_client_config.yml", 'ping_repeat');
def isUp(hostname, total_pings=ping_repeat):   ####delaye mozna dodac miedzy pingi w konfigu
    giveFeedback = True  # Ustawione na True dla wyświetlania informacji zwrotnej

    if platform.system() == "Windows":
        ping_cmd = "ping " + hostname + " -n " + str(1) + "-q -l 32 -w 1000  > NUL 2>&1" # Polecenie ping dla systemu Windows
    else:
        ping_cmd = "ping -c " + str(1) + " " + hostname  # Polecenie ping dla systemów Unix/Linux

    successful_pings = 0
    for i in range(total_pings):
        response = os.system(ping_cmd)
        if response == 0:
            successful_pings += 1
        
        # Wyświetlanie aktualnego pinga, ilości pozostałych pingów i wyniku procentowego
        if giveFeedback:
            remaining_pings = total_pings - (i + 1)
            success_rate = (successful_pings / (i + 1)) * 100
            print(f"Ping {i + 1}/{total_pings}, Remaining: {remaining_pings}, Success rate: {success_rate:.2f}%")

    success_rate = (successful_pings / total_pings) * 100  # Wynik procentowy sukcesu
    if giveFeedback:
        if success_rate >= 75:
            print_c("green", hostname, 'success rate:', success_rate)
        if success_rate == 0:
            print_c("red", hostname, 'success rate:', success_rate)

    return success_rate >= 75  # Zwróć True, jeśli wynik procentowy sukcesu wynosi co najmniej 75%




def notify_unreachable(ip, description, server_url=ping_endpoint):
    try:
        data = {'ip': ip, 'port': port, 'reachable':0,'description': description, 'client_description': client_description, 'lic': lic, 'app_ver': app_ver, 'custom1': custom1, 'guid':guid, 'app_guid': app_guid, 'expiry_date': lic, 'alert_mail_address':alert_mail_address}
        #print('data - notify_unreachable - linia208', data);
        response = requests.post(server_url, json=data, verify=cacert_file)
        if response.status_code == 200:
            #print(f"Success: Notification sent to server for {description}")
            print_c("red", "<");
        else:
            print_c("red", f"Failure: Could not send notification to server for {description}. Server returned status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print_c("red", f"Request error: {e}")


repeat_count = odczytaj_zmienna_z_yaml("IPing_client_config.yml", 'repeat_count')
repeat_delay = odczytaj_zmienna_z_yaml('IPing_client_config.yml', 'repeat_delay')
server_url = ping_endpoint
client_description = odczytaj_zmienna_z_yaml('IPing_client_config.yml', 'client_description')
lic = odczytaj_zmienna_z_yaml('IPing_client_config.yml', 'license')
guid_config = odczytaj_zmienna_z_yaml('IPing_client_config.yml', 'guid')
unreachable_server_url = ping_endpoint
timeout = odczytaj_zmienna_z_yaml('IPing_client_config.yml','timeout')
alert_mail_address = odczytaj_zmienna_z_yaml('IPing_client_config.yml','alert_mail_address')


if __name__ == "__main__":
    for _ in range(repeat_count):
        print_c("blue", "            repeat: ",_ ,'/',repeat_count)
        try:   
            with open('hosts.txt', 'r') as file:
                for line in file:
                    print_c("yellow", line)
                    if not line.strip().startswith("#"):
                        try:
                            ip, port, custom1, description = line.strip().split(maxsplit=3)
                            if port == "0":
                                send_ping(ip, description, server_url, unreachable_server_url, timeout)
                            elif is_valid_port(port):
                                port = int(port)
                                if is_port_open(ip, port, timeout):
                                    print_c("green", ">")
                                    reachable = 1
                                else:
                                    print_c("red", ">")
                                    reachable = 0
                                    notify_unreachable(ip, description, unreachable_server_url)
                                data = {'ip': ip, 'port': port, 'description': description, 'reachable': reachable,
                                        'client_description': client_description, 'lic': lic, 'app_ver': app_ver,
                                        'custom1': custom1, 'guid': guid, 'app_guid': app_guid, 'expiry_date': lic,
                                        'alert_mail_address': alert_mail_address}
                                response = requests.post(server_url, json=data)
                                if response.status_code == 200:
                                    print_c("green", "<");
                                else:
                                    print_c('red', f"Failure: Could not send information to server for {description}. "
                                                   f"Server returned status code {response.status_code}")
                            else:
                                print_c("red", f"Invalid port: {port}")
                        except ValueError as e:
                            print_c("magenta", f"Invalid line format in hosts.txt: {line.strip()}. Skipping...")
                        except socket.gaierror as e:
                            print_c("red", f"Error resolving hostname: {e}")
                            notify_unreachable(ip, description, unreachable_server_url)
                            print_c("red", f"Host {description} is unreachable. Notification sent to server.")
                        
                        time.sleep(repeat_delay)
        except FileNotFoundError:
            
            print_c("red", "Błąd: Nie znaleziono pliku z hostami.")
            
            time.sleep(repeat_delay)
            exit();
        except Exception as e:
            print_c("red", f"An error occurred: {e}")
            time.sleep(repeat_delay)
            exit();
            
