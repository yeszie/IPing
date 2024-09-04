import requests
import socket
import time
import json
#import yaml
import platform
import os

#from colorama import Fore, Style


def load_config(filename):
    with open(filename, 'r') as config_file:
        config = json.load(config_file)
    return config
   
def is_valid_port(port):
    #print('is_valid_port')
    try:
        port = int(port)
        #print('port', port)
        if port < 1 or port > 65535:
            #print('False')
            return False
        #print('True')
        return True
    except ValueError:
        print('False - wrong port number')
        return False
        
def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org')
        if response.status_code == 200:
            return response.text
        else:
            #print("Nie udało się pobrać adresu IP. Status odpowiedzi:", response.status_code)
            return None
    except Exception as e:
        #print("Wystąpił błąd podczas pobierania adresu IP:", str(e))
        return None
        
def get_computer_name():
    try:
        return socket.gethostname()
    except Exception as e:
        #print("Wystąpił błąd podczas pobierania nazwy komputera:", str(e))
        return None
              
def get_os_info():
    try:
        return platform.platform()
    except Exception as e:
        #print("Wystąpił błąd podczas pobierania informacji o systemie operacyjnym:", str(e))
        return None
          
def get_current_user():
    try:
        return os.getlogin()
    except Exception as e:
        #print("Wystąpił błąd podczas pobierania nazwy zalogowanego użytkownika:", str(e))
        return None
             
from colorama import init, Fore, Style


def print_c(color, *args):
    init()  # Inicjalizacja biblioteki Colorama
    colors = {
        'red': Fore.RED,
        'green': Fore.GREEN,
        'blue': Fore.BLUE,
        'yellow': Fore.YELLOW,
        'magenta': Fore.MAGENTA,
        'cyan': Fore.CYAN
    }

    color_code = colors.get(color.lower())
    if color_code:
        print(color_code + ' '.join(map(str, args)) + Style.RESET_ALL)
    else:
        print("Unsupported color:", color)



def check_hosts_txt():            
    file_path = 'hosts.txt'
    if not os.path.exists(file_path):
        print("Nie znaleziono pliku z hostami", file_path)
        with open(file_path, 'w') as file:
            print("Tworzę nowy plik z przykładową zawartością", file_path)
            file.write('#host           0=icmp      description         custom_description\n')
            print('#host           0=icmp      description         custom_description\n')
            file.write('1.1.1.1         0           DNS                 Cloudflare\n')
            print('1.1.1.1         0           DNS                 Cloudflare\n')
            file.write('IPing.pl        443         IPing               Monitoring\n')
            print('IPing.pl        443         IPing               Monitoring\n')