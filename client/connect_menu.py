from tkinter import *
import tkinter.messagebox
from socket import *
from .client import chat_client


def menu_main():
    root = Tk()
    root.title("Connect to server")
    root.geometry("300x200")
    Label(root, text="Server:").pack()
    hostname_entry = Entry(root)
    hostname_entry.pack()
    Label(root, text="Username:").pack()
    username_entry = Entry(root)
    username_entry.pack()
    Label(root, text="Password:").pack()
    password_entry = Entry(root)
    password_entry.pack()
    
    def connect():
        hostname = hostname_entry.get()
        try:
            # Attempt connection at port 1337
            soc = socket(AF_INET, SOCK_STREAM)
            soc.connect((hostname, 1337))
            root.destroy()
            chat_client(soc)
        except:
            # Failed to connect
            hostname_entry.delete(0, END)
            tkinter.messagebox.showinfo('Oops', 'Connection failed!')
            pass

    send_button = Button(root, text="Connect", bg="#5D92B1", fg="white", width=600, height=100, command=connect)
    send_button.pack()
    root.mainloop()
    pass


if __name__ == "__main__":
    menu_main()
