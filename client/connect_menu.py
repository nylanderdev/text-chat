from tkinter import *
import tkinter.messagebox
from socket import *
from common.connection import Connection
from common.handler import ConnectionHandler
from .client import chat_client


def authenticate_connection(conn, username, password):
    connection_handler = ConnectionHandler()
    connection_handler.register(conn, 0)
    response_received = False
    auth_success = False

    def on_text(client, cid, text):
        print("[SERVER]", text)

    def on_accept(client, cid):
        nonlocal response_received, auth_success
        response_received = True
        auth_success = True

    def on_reject(client, cid, reason):
        nonlocal response_received
        print("[SERVER]", reason)
        response_received = True

    connection_handler.set_reject_handler(on_reject)
    connection_handler.set_accept_handler(on_accept)
    connection_handler.set_plaintext_handler(on_text)
    conn.send_registration(username, password)
    while not response_received:
        connection_handler.poll()
    return auth_success


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

    def login():
        hostname = hostname_entry.get()
        try:
            # Attempt connection at port 1337
            soc = socket(AF_INET, SOCK_STREAM)
            soc.connect((hostname, 1337))
            connection = Connection(soc)
            connection.send_login(username_entry.get(), password_entry.get())
            if authenticate_connection(connection, username_entry.get(), password_entry.get()):
                root.destroy()
                chat_client(connection)
            else:
                tkinter.messagebox.showinfo("Invalid login")
                soc.close()
        except Exception as e:
            print(e)
            # Failed to connect
            hostname_entry.delete(0, END)
            tkinter.messagebox.showinfo('Oops', 'Connection failed!')
            pass

    def register():
        hostname = hostname_entry.get()
        try:
            # Attempt connection at port 1337
            soc = socket(AF_INET, SOCK_STREAM)
            soc.connect((hostname, 1337))
            connection = Connection(soc)
            connection.send_registration(username_entry.get(), password_entry.get())
            if authenticate_connection(connection, username_entry.get(), password_entry.get()):
                root.destroy()
                chat_client(connection)
            else:
                tkinter.messagebox.showinfo("Registration failed")
                soc.close()
        except Exception as e:
            print(e)
            # Failed to connect
            hostname_entry.delete(0, END)
            tkinter.messagebox.showinfo('Oops', 'Connection failed!')
            pass


    divider = Label(root, width=600)
    divider.pack()
    login_button = Button(root, text="Sign in", bg="lightgray", fg="black", command=login)
    login_button.pack()
    or_label = Label(root, text="or", width=600, font=("Helvetica", 12))
    or_label.pack()
    register_button = Button(root, text="Sign up", bg="lightgray", fg="black", command=register)
    register_button.pack()

    root.mainloop()
    pass


if __name__ == "__main__":
    menu_main()
