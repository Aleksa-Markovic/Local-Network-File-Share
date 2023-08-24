import customtkinter
import tkinter
import requests
from requests.exceptions import ConnectTimeout
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
    IP_LABEL = None
    PORT_LABEL = None
    SELECT_ALL_BUTTON = None
    BACK_BUTTON = None
    OPTIONS_WINDOW = None
    REQUEST_TIMEOUT = 1.0
    SELECTED_ALL = False
    NEW_FOLDER_LOADED = False
    DEFAULT_LINK = None

    variable_list = []
    checkboxes = []
    checked_boxes = []
    links = []
    download_location = '.'

    new_ip_textbox = None
    new_port_textbox = None
    request_time_limit_textbox = None

    def __init__(self):
        super().__init__()

        self.ROOT = customtkinter.CTk()
        self.ROOT.title("Local Network File Sharing Client")
        self.ROOT.geometry("1000x450")
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
                "SERVER_IP": "localhost",
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
            self.ROOT.after(501, lambda :self.ROOT.iconbitmap('Logo.ico'))
        elif sys.platform.startswith('darwin'):
            self.SYSTEM = 'mOS'
        elif hasattr(sys, 'getandroidapilevel'):
            self.SYSTEM = 'And'
        else:
            self.SYSTEM = None
            raise SystemExit

    def create_widgets(self):

        self.IP_LABEL = customtkinter.CTkLabel(self.ROOT, text=f"Current Session IP: {self.SERVER_IP}")
        self.IP_LABEL.place(relx=0.02, rely=0.05, anchor=customtkinter.W)

        self.PORT_LABEL = customtkinter.CTkLabel(self.ROOT, text=f"Current Session PORT: {self.SERVER_PORT}")
        self.PORT_LABEL.place(relx=0.02, rely=0.1, anchor=customtkinter.W)

        load_content_button = customtkinter.CTkButton(self.ROOT, width=200, text='Load Content', command=self.load_content)
        load_content_button.place(relx=0.02, rely=0.2, anchor=customtkinter.W)

        self.SCROLLABLE_FRAME = customtkinter.CTkScrollableFrame(self.ROOT, width=450, height=420)
        self.SCROLLABLE_FRAME.place(relx=0.5, rely=0.01, anchor=customtkinter.NW)

        download_button = customtkinter.CTkButton(self.ROOT, width=200, text='Download', command=self.download)
        download_button.place(relx=0.02, rely=0.3, anchor=customtkinter.W)

        location_button = customtkinter.CTkButton(self.ROOT, width=200, text='Set Download Location', command=self.set_download_location)
        location_button.place(relx=0.02, rely=0.4, anchor=customtkinter.W)

        self.SELECT_ALL_BUTTON = customtkinter.CTkButton(self.ROOT, width=200, text='Select All', command=self.select_all)
        self.SELECT_ALL_BUTTON.place(relx=0.02, rely=0.5, anchor=customtkinter.W)

        options_button = customtkinter.CTkButton(self.ROOT, width=200, text='Options', command=self.options)
        options_button.place(relx=0.02, rely=0.6, anchor=customtkinter.W)

        self.BACK_BUTTON = customtkinter.CTkButton(self.ROOT, width=200, text='Back', command=self.load_back)

    def request_content(self):
        try:
            r = requests.get(self.FULL_LINK, timeout=self.REQUEST_TIMEOUT)
            if r.status_code == 200:
                return r.text
            else:
                return None
        except ConnectTimeout:
            return None

    def load_content(self, suffix="", new_full_link=None):
        self.clear_loaded_content()
        if new_full_link == None:
            if self.DEFAULT_LINK == None:
                self.DEFAULT_LINK = "http://"+str(self.SERVER_IP)+":"+str(self.SERVER_PORT)
            self.FULL_LINK = "http://"+str(self.SERVER_IP)+":"+str(self.SERVER_PORT)+suffix
        else:
            if new_full_link[-1] == '/':
                new_full_link = new_full_link[:-1]
            self.FULL_LINK = new_full_link+suffix
            if self.FULL_LINK[-1] != '/':
                self.FULL_LINK = self.FULL_LINK+'/'
        text = self.request_content()
        if text == None:
            return
        soup = BeautifulSoup(text, features='html.parser')
        links_list = soup.find_all('a')
        self.links = []
        for link in links_list:
            self.links.append(link.text)
        self.display_links()

    def display_links(self):
        self.SCROLLABLE_FRAME = None
        self.SCROLLABLE_FRAME = customtkinter.CTkScrollableFrame(self.ROOT, width=450, height=420)
        for link in self.links:
            check_var = tkinter.IntVar()
            checkbox = customtkinter.CTkCheckBox(self.SCROLLABLE_FRAME, text=link, variable=check_var, onvalue=1, offvalue=0, command=self.folder_or_file)
            checkbox.pack(padx=5, pady=5)
            self.variable_list.append(check_var)
            self.checkboxes.append(checkbox)
        self.SCROLLABLE_FRAME.place(relx=0.5, rely=0.01, anchor=customtkinter.NW)

    def clear_loaded_content(self):
        for checkbox,var in zip(self.checkboxes, self.variable_list):
            checkbox.destroy()
            del(var)
        self.checkboxes.clear()
        self.variable_list.clear()
        self.checked_boxes.clear()

    def reload_new_link(self, link):
        self.links.clear()
        self.clear_loaded_content()
        self.SCROLLABLE_FRAME.place_forget()
        self.load_content(suffix='/'+link, new_full_link=self.FULL_LINK)
        self.NEW_FOLDER_LOADED = True
        self.back_button_show()

    def back_button_show(self):
        if self.NEW_FOLDER_LOADED == True:
            self.BACK_BUTTON.place(relx=0.02, rely=0.8, anchor=customtkinter.W)

    def folder_or_file(self):
        for var in self.variable_list:
            if var.get():
                index = self.variable_list.index(var)
                if self.links[index].endswith('/'):
                    self.reload_new_link(self.links[index])
                    return
                if self.links[index].endswith('@'):
                    self.reload_new_link(self.links[index].replace('@', ''))
                    return
        self.update_checked()

    def load_back(self):
        if self.NEW_FOLDER_LOADED == False:
            return
        else:
            if self.FULL_LINK == self.DEFAULT_LINK:
                self.NEW_FOLDER_LOADED = False
                return
            if self.FULL_LINK.endswith('/'):
                self.FULL_LINK = self.FULL_LINK[:-1].rsplit('/', 1)[0]
                if self.FULL_LINK == self.DEFAULT_LINK:
                    self.NEW_FOLDER_LOADED = False
                self.load_content(suffix='',new_full_link=self.FULL_LINK)

    def update_checked(self):
        self.checked_boxes = []
        for var in self.variable_list:
            if var.get():
                index = self.variable_list.index(var)
                if self.links[index] not in self.checked_boxes and not self.links[index].endswith('/'):
                    self.checked_boxes.append(self.links[index])

    def set_download_location(self):
        new_location = customtkinter.filedialog.askdirectory(mustexist=True)
        if new_location != None and new_location != ():
            self.download_location = new_location

    def download(self):
        for checked_item in self.checked_boxes:
            if checked_item.endswith('/'):
                continue
            item_link = self.FULL_LINK+'/'+checked_item
            wget.download(item_link, self.download_location)

    def select_all(self):
        if len(self.checkboxes) > 0:
            if self.SELECTED_ALL == False:
                for checkbox in self.checkboxes:
                    if not checkbox.cget('text').endswith('/'):
                        checkbox.select()
                self.SELECT_ALL_BUTTON.configure(text='Deselect All')
                self.SELECTED_ALL = True
                self.update_checked()
            else:
                for checkbox in self.checkboxes:
                    checkbox.deselect()
                self.SELECT_ALL_BUTTON.configure(text='Select All')
                self.SELECTED_ALL = False
                self.update_checked()

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

        request_time_limit_label = customtkinter.CTkLabel(self.OPTIONS_WINDOW, text="Request Time Limit (Default is 1)")
        request_time_limit_label.place(relx=0.4, rely=0.4, anchor=customtkinter.W)

        self.request_time_limit_textbox = customtkinter.CTkTextbox(self.OPTIONS_WINDOW, height=20, width=50)
        self.request_time_limit_textbox.place(relx=0.4, rely=0.55, anchor=customtkinter.W)
        self.request_time_limit_textbox.bind('<KeyRelease>', lambda event:self.limit_input(self.request_time_limit_textbox, type='RATE'))

    def limit_input(self, textbox, type=None):
        if type == "PORT":
            if len(textbox.get('0.0', customtkinter.END)) > 5:
                textbox.delete('end-2c', 'end')
        elif type == "IP":
            if len(textbox.get('0.0', customtkinter.END)) > 16:
                textbox.delete('end-2c', 'end')
        elif type == "RATE":
            if len(textbox.get('0.0', customtkinter.END)) > 4:
                textbox.delete('end-2c', 'end')

    def update_source(self):
        if len(self.new_ip_textbox.get('0.0', customtkinter.END).strip()) == 0:
            self.SERVER_IP = self.SERVER_IP
        else:
            self.SERVER_IP = self.new_ip_textbox.get('0.0', customtkinter.END).strip()
            self.update_labels()
        if len(self.new_port_textbox.get('0.0', customtkinter.END).strip()) == 0:
            self.SERVER_PORT = self.SERVER_PORT
        else:
            self.SERVER_PORT = self.new_port_textbox.get('0.0', customtkinter.END).strip()
            self.update_labels()
        if len(self.request_time_limit_textbox.get('0.0', customtkinter.END).strip()) == 0:
            self.REQUEST_TIMEOUT = self.REQUEST_TIMEOUT
        else:
            self.REQUEST_TIMEOUT = float(self.request_time_limit_textbox.get('0.0', customtkinter.END).strip())

    def update_labels(self):
        self.IP_LABEL.configure(text=f"Current Session IP: {self.SERVER_IP}")
        self.PORT_LABEL.configure(text=f"Current Session PORT: {self.SERVER_PORT}")

    def safe_close(self):
        if self.OPTIONS_WINDOW != None:
            self.OPTIONS_WINDOW.destroy()
        self.ROOT.destroy()
        raise SystemExit

if __name__ == "__main__":
    defaultUI = UI()
    defaultUI.ROOT.mainloop()