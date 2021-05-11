from tkinter import *
from socket import *
from .client import chat_client


def menu_main():
    root = Tk()
    root.title("Connect to server")
    root.geometry("300x100")
    Label(root, text="Server:").pack()
    hostname_entry = Entry(root)
    hostname_entry.pack()

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
            hostname_entry.insert(0, "Connection failed!")
            pass

    send_button = Button(root, text="Connect", bg="#5D92B1", fg="white", width=600, height=100, command=connect)
    send_button.pack()
    root.mainloop()
    pass


if __name__ == "__main__":
    menu_main()
