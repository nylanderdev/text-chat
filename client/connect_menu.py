from tkinter import *
import tkinter.messagebox
from socket import *
from common import handle_user_info
from .client import chat_client


def menu_main():
    root = Tk()
    root.title("Connect to server")
    root.geometry("300x300")
    Label(root, text="Server:").pack()
    hostname_entry = Entry(root)
    hostname_entry.pack()
    Label(root, text="Username:").pack()
    username_entry = Entry(root)
    username_entry.pack()
    Label(root, text="Password:").pack()
    password_entry = Entry(root)
    password_entry.pack()

    global login_check
    login_check = False
    global register_check
    register_check = False

    def connect():
        if login_check or register_check == True:

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
        else:
            tkinter.messagebox.showinfo('Oops', 'You must login or register first!')

    def authenticate_login():
        if handle_user_info.login(username_entry.get(), password_entry.get()):
            username_entry.delete(0, END)
            password_entry.delete(0, END)
            username_entry.insert(0,"success!")
            password_entry.insert(0, "success!")
            global login_check
            login_check = True
        else:
            username_entry.delete(0, END)
            password_entry.delete(0, END)

    def register():
        if handle_user_info.register(username_entry.get(), password_entry.get()):
            username_entry.delete(0, END)
            password_entry.delete(0, END)
            username_entry.insert(0, "success!")
            password_entry.insert(0, "success!")
            global register_check
            register_check = True
        else:
            username_entry.delete(0, END)
            password_entry.delete(0, END)


    divider = Label(root, width=600)
    divider.pack()
    login_button = Button(root, text="Login", bg="lightgray", fg="black", command=authenticate_login)
    login_button.pack()
    or_label = Label(root, text="or", width=600, font=("Helvetica", 12))
    or_label.pack()
    register_button = Button(root, text="register", bg="lightgray", fg="black", command=register)
    register_button.pack()
    divider = Label(root, width=600)
    divider.pack()
    send_button = Button(root, text="Connect", bg="#5D92B1", fg="white", width=600, height=200, command=connect)
    send_button.pack()

    root.mainloop()
    pass


if __name__ == "__main__":
    menu_main()
