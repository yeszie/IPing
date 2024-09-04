import requests
import os
from datetime import datetime
import subprocess
import time

def update():
    def get_remote_file_last_modified(url):
        response = requests.head(url)  # Wyślij zapytanie typu HEAD, aby uzyskać tylko nagłówki
        last_modified = response.headers.get('Last-Modified')
        return last_modified

    def download_file(url, local_path):
        response = requests.get(url)
        with open(local_path, 'wb') as f:
            f.write(response.content)

    def is_remote_file_newer(url, local_path):
        remote_last_modified = get_remote_file_last_modified(url)
        if not remote_last_modified:
            return False  # Jeśli nie można uzyskać daty modyfikacji pliku z serwera, zakładamy, że plik jest nieaktualny

        remote_last_modified_date = datetime.strptime(remote_last_modified, '%a, %d %b %Y %H:%M:%S %Z')
        local_last_modified_date = datetime.fromtimestamp(os.path.getmtime(local_path))

        return remote_last_modified_date > local_last_modified_date

    # Przykładowe użycie
    remote_urls = {
        "remote_url1": "https://www.iping.pl/cacert.pem",
        "remote_url2": "https://www.iping.pl/IPing_license.exe",
        "remote_url3": "https://www.iping.pl/client.exe"
    }
    local_file_paths = {
        "remote_url1": "cacert.pem",
        "remote_url2": "IPing_license.exe",
        "remote_url3": "client.exe"
    }

    for key, url in remote_urls.items():
        local_path = local_file_paths.get(key, "default_value")
        if os.path.exists(local_path):
            if is_remote_file_newer(url, local_path):
                print(f"Pobieranie nowszej wersji pliku {local_path}...")
                download_file(url, local_path)
            else:
                print(f"Lokalny plik {local_path} jest aktualny.")
        else:
            print(f"Pobieranie pliku {local_path}...")
            download_file(url, local_path)

while True:
    try:
        #print("Uruchamiam update...")
        update(); 

        #print("Uruchamiam klienta...")
        subprocess.run(['client.exe'])

        #print("Oczekiwanie 5 sekund przed ponownym uruchomieniem klienta...")
        time.sleep(5)  # Oczekiwanie 5 sekund

    except Exception as e:
        print(f"Wystąpił błąd podczas uruchamiania klienta: {e}")
        #print("Próba ponownego uruchomienia klienta za 5 sekund...")
        time.sleep(5)  # Oczekiwanie 5 sekund przed ponowną próbą uruchomienia
