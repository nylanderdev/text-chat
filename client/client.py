from tkinter import *
from connection import Connection
import socket

def chat_client(soc):
    root = Tk()
    root.title('tk')
    root.geometry('600x600')

    connection = Connection(soc)

    def send():
        msg = message_box.get(1.0, END)
        message_box.delete(1.0, END)
        connection.send_plaintext(msg)

    def receive():
        msg_rec = connection.recv_plaintext()
        if msg_rec is not None:
            print(msg_rec)
            text_rectangle.configure(state=NORMAL)
            text_rectangle.insert(1.0, msg_rec)
            text_rectangle.yview(END)
            text_rectangle.configure(state=DISABLED)

    def listen():
        receive()
        root.after(50,listen)
    # add a welcome label
    welcome_label = Label(root, bg="#17202A", fg="white", text="Welcome to this chatroom!",
                          font=("Ostrich Sans", 16, "bold"), pady=10, width=600)
    welcome_label.pack()
    # add a divider
    label = Label(root, bg="black", pady=1, width=600)
    label.place(relheight=0.01, rely=0.08)
    # add text rectangle (space where you display the text)
    text_rectangle = Text(root, width=600, height=16, font=("Helvetica", 14), bg="#17202A", fg="white")
    text_rectangle.pack(pady=3)
    text_rectangle.configure(state=DISABLED)

    # add message label
    message_label = Label(root, text="Write your message below:", font=("Helvetica", 12), anchor='w', bg="#EAECEE").pack(
        fill='both')

    # add message box and send button
    message_box = Text(root, width=450, height=5, font=("Helvetica", 14), bg="#2C3E50", fg="white")
    message_box.pack(pady=1)
    send_button = Button(root, text="send", bg="#5D92B1", fg="white", width=600, height=100, command=send)
    send_button.pack(pady=1)

    listen()
    root.mainloop()

test_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('socket opened')

host = "localhost"
port = 9913
ADDR = (host, port)
test_soc.connect(ADDR)
print('connected')
chat_client(test_soc)