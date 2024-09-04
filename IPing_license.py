import tkinter as tk
from tkinter import simpledialog, messagebox
import uuid
import os
import yaml
import time

class CustomDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None):
        self.guid = ""
        self.app_guid = ""
        super().__init__(parent, title=title)

    def body(self, master):
        tk.Label(master, text="GUID:").grid(row=0, sticky=tk.W)
        tk.Label(master, text="App GUID:").grid(row=1, sticky=tk.W)

        self.guid_entry = tk.Entry(master, width=36)
        self.app_guid_entry = tk.Entry(master, width=36)

        self.guid_entry.grid(row=0, column=1)
        self.app_guid_entry.grid(row=1, column=1)

        # Ograniczenie długości wprowadzanych danych
        self.guid_entry.config(validate="key", validatecommand=(self.register(self.validate_length), "%P"))
        self.app_guid_entry.config(validate="key", validatecommand=(self.register(self.validate_length), "%P"))

        return self.guid_entry

    def validate_length(self, new_value):
        return len(new_value) <= 36

    def validate_guid(self, guid):
        try:
            uuid.UUID(guid, version=4)
            return True
        except ValueError:
            return False

    def validate(self):
        guid = self.guid_entry.get()
        app_guid = self.app_guid_entry.get()

        if not guid or not app_guid:
            messagebox.showwarning("Błąd", "Proszę wprowadzić GUID i App GUID.")
            return False
        elif not self.validate_guid(guid) or not self.validate_guid(app_guid):
            messagebox.showwarning("Błąd", "Proszę wprowadzić poprawny format GUID (np. 123e4567-e89b-12d3-a456-426614174000).")
            return False
        elif guid == app_guid:
            messagebox.showwarning("Błąd", "Proszę wprowadzić różne wartości dla GUID i App GUID.")
            return False

        self.guid = guid
        self.app_guid = app_guid
        return True

    def apply(self):
        # Zamień wartości app_guid i guid przed zapisaniem do pliku
        self.result = (self.app_guid, self.guid)


def main():
    root = tk.Tk()
    root.withdraw()  # Ukrycie głównego okna

    config_file = "IPing_client_config.yml"

    if not os.path.exists(config_file):
        dialog = CustomDialog(root, title="Wprowadź dane licencji")
        result = dialog.result

        if result:
            data = {
                'app_guid': result[0],
                'guid': result[1]
            }
            print("Zapisane dane:", data)
            with open(config_file, "w", encoding="utf-8") as file:
                yaml.dump(data, file)
        else:
            print("Operacja anulowana.")
            return

    with open(config_file, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
        app_guid = data.get('app_guid')
        guid = data.get('guid')
        print("Odczytane dane:", data)

    if not app_guid or not guid:
        dialog = CustomDialog(root, title="Wprowadź dane licencji")
        result = dialog.result

        if result:
            app_guid, guid = result
            data['app_guid'] = app_guid
            data['guid'] = guid

            with open(config_file, "w", encoding="utf-8") as file:
                yaml.dump(data, file, allow_unicode=True)
            print("Zapisane dane:", data)
        else:
            print("Operacja anulowana.")
            return

    print("- - - - - - - - - - - - - - - - - - - - - - - - - - -");
    print("Wczytano dane z pliku IPing_client_config.yml:")
    print("GUID:", guid)
    print("App GUID:", app_guid)
    time.sleep(5);
    exit();

if __name__ == "__main__":
    main()
