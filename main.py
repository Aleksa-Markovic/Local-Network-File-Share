import customtkinter
import tkinter
import requests
import wget
import json
import os
import sys
from bs4 import BeautifulSoup

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

class UI:

    SERVER_IP = None
    SERVER_PORT = None
    FULL_LINK = None
    SYSTEM = None

    SCROLLABLE_FRAME = None
    OPTIONS_WINDOW = None

    variable_list = []
    checkboxes = []
    checked_boxes = []
    links = []
    download_location = '.'

    new_ip_textbox = None
    new_port_textbox = None


    def __init__(self):
        super().__init__()

        self.ROOT = customtkinter.CTk()
        self.ROOT.title("Local Network File Sharing Client")
        self.ROOT.geometry("1000x600")
        self.ROOT.resizable(False, False)
        self.ROOT.protocol("WM_DELETE_WINDOW", self.safe_close)
        
        self.system_info()

        if os.path.exists('config'):
            self.load_configuration()
        else:
            self.write_default_configuration()

        self.create_widgets()

    def __repr__(self):
        try:
            return f"Local Network File Sharing Class:\n\tIP:{self.SERVER_IP}\n\tPORT:{self.SERVER_PORT}\n\tSYSTEM:{self.SYSTEM}"
        except:
            raise SystemError
        
    def write_default_configuration(self):
        with open('config', 'a+') as f:
            data = {
                "SERVER_IP": "192.168.0.26",
                "SERVER_PORT": 8080
            }
            json.dump(data, f)
        return

    def load_configuration(self):
        with open('config', 'r') as f:
            data = json.load(f)
            self.SERVER_IP = data['SERVER_IP']
            self.SERVER_PORT = data['SERVER_PORT']
        return

    def system_info(self):
        if sys.platform.startswith('linux'):
            self.SYSTEM = 'Lin'
        elif sys.platform.startswith('win32'):
            self.SYSTEM = 'Win'
        elif sys.platform.startswith('darwin'):
            self.SYSTEM = 'mOS'
        else:
            self.SYSTEM = None
            raise SystemExit

    def create_widgets(self):

        ip_label = customtkinter.CTkLabel(self.ROOT, text=f"Current Session IP: {self.SERVER_IP}")
        ip_label.place(relx=0.02, rely=0.05, anchor=customtkinter.W)

        port_label = customtkinter.CTkLabel(self.ROOT, text=f"Current Session PORT: {self.SERVER_PORT}")
        port_label.place(relx=0.02, rely=0.1, anchor=customtkinter.W)

        load_content_button = customtkinter.CTkButton(self.ROOT, width=200, text='Load Content', command=self.load_content)
        load_content_button.place(relx=0.02, rely=0.2, anchor=customtkinter.W)

        self.SCROLLABLE_FRAME = customtkinter.CTkScrollableFrame(self.ROOT, width=450, height=400)
        self.SCROLLABLE_FRAME.place(relx=0.5, rely=0.03, anchor=customtkinter.NW)

        download_button = customtkinter.CTkButton(self.ROOT, width=200, text='Download', command=self.download)
        download_button.place(relx=0.02, rely=0.3, anchor=customtkinter.W)

        location_button = customtkinter.CTkButton(self.ROOT, width=200, text='Set Download Location', command=self.set_download_location)
        location_button.place(relx=0.02, rely=0.4, anchor=customtkinter.W)

        options_button = customtkinter.CTkButton(self.ROOT, width=200, text='Options', command=self.options)
        options_button.place(relx=0.02, rely=0.5, anchor=customtkinter.W)

    def request_content(self):
        r = requests.get(self.FULL_LINK)
        if r.status_code == 200:
            return r.text
        else:
            raise Exception

    def load_content(self):
        self.clear_loaded_content()
        self.FULL_LINK = "http://"+str(self.SERVER_IP)+":"+str(self.SERVER_PORT)
        text = self.request_content()
        soup = BeautifulSoup(text, features='html.parser')
        links_list = soup.find_all('a')
        self.links = []
        for link in links_list:
            self.links.append(link.text)
        self.display_links()

    def display_links(self):
        for link in self.links:
            check_var = tkinter.IntVar()
            checkbox = customtkinter.CTkCheckBox(self.SCROLLABLE_FRAME, text=link, variable=check_var, onvalue=1, offvalue=0, command=self.update_checked)
            checkbox.pack(padx=5, pady=5)
            self.variable_list.append(check_var)
            self.checkboxes.append(checkbox)

    def clear_loaded_content(self):
        for checkbox,var in zip(self.checkboxes, self.variable_list):
            checkbox.destroy()
            del(var)
        self.checkboxes.clear()
        self.variable_list.clear()
        self.checked_boxes.clear()

    def update_checked(self):
        self.checked_boxes = []
        for var in self.variable_list:
            if var.get():
                index = self.variable_list.index(var)
                if self.links[index] not in self.checked_boxes:
                    self.checked_boxes.append(self.links[index])

    def set_download_location(self):
        new_location = customtkinter.filedialog.askdirectory(mustexist=True)
        if new_location != None and new_location != ():
            self.download_location = new_location

    def download(self):
        for checked_item in self.checked_boxes:
            item_link = self.FULL_LINK+'/'+checked_item
            wget.download(item_link, self.download_location)

    def options(self):
        self.OPTIONS_WINDOW = customtkinter.CTkToplevel(self.ROOT)
        self.OPTIONS_WINDOW.title("Options")
        self.OPTIONS_WINDOW.geometry("400x200")
        self.OPTIONS_WINDOW.resizable(False, False)

        new_ip_label = customtkinter.CTkLabel(self.OPTIONS_WINDOW, text="Enter the new IP Address:")
        new_ip_label.place(relx=0.02, rely=0.1, anchor=customtkinter.W)

        self.new_ip_textbox = customtkinter.CTkTextbox(self.OPTIONS_WINDOW, height=20, width=130)
        self.new_ip_textbox.place(relx=0.02, rely=0.25, anchor=customtkinter.W)
        self.new_ip_textbox.bind('<KeyRelease>', lambda event:self.limit_input(self.new_ip_textbox, type="IP"))

        new_port_label = customtkinter.CTkLabel(self.OPTIONS_WINDOW, text="Enter the new PORT:")
        new_port_label.place(relx=0.02, rely=0.4, anchor=customtkinter.W)

        self.new_port_textbox = customtkinter.CTkTextbox(self.OPTIONS_WINDOW, height=20, width=55)
        self.new_port_textbox.place(relx=0.02, rely=0.55, anchor=customtkinter.W)
        self.new_port_textbox.bind('<KeyRelease>', lambda event:self.limit_input(self.new_port_textbox, type='PORT'))

        options_button_update = customtkinter.CTkButton(self.OPTIONS_WINDOW, width=200, text="Update", command=self.update_source)
        options_button_update.place(relx=0.02, rely=0.8, anchor=customtkinter.W)

    def limit_input(self, textbox, type=None):
        if type == "PORT":
            if len(textbox.get('0.0', customtkinter.END)) > 5:
                textbox.delete('end-2c', 'end')
        elif type == "IP":
            if len(textbox.get('0.0', customtkinter.END)) > 16:
                textbox.delete('end-2c', 'end')

    def update_source(self):
        if len(self.new_ip_textbox.get('0.0', customtkinter.END).strip()) == 0:
            print("here")
        else:
            self.SERVER_IP = self.new_ip_textbox.get('0.0', customtkinter.END).strip()
            print(self.SERVER_IP)
            
    def safe_close(self):
        if self.OPTIONS_WINDOW != None:
            self.OPTIONS_WINDOW.destroy()
        self.ROOT.destroy()
        raise SystemExit

if __name__ == "__main__":
    defaultUI = UI()
    defaultUI.ROOT.mainloop()
