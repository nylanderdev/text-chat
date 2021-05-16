from tkinter import *
from tkinter import filedialog
from common.connection import Connection
from common.compression import *
import tkinter
import os
from PIL import Image, ImageTk


def chat_client(soc):
    HEIGHT = 800
    WIDTH = 800
    root = Tk()
    root.title('tk')
    connection = Connection(soc)

    def send():
        msg = message_box.get(1.0, END)
        message_box.delete(1.0, END)
        connection.send_plaintext(msg)

    #Event för om man trycker på enter
    def sende(event):
        send()

    #Funktion för att skicka bilder
    def send_img():
        global new_img
        file_img = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select Image", filetypes=(("JPG", "*.jpg"), ("All", "*.*")))
        img = Image.open(file_img)
        img.thumbnail((150,150))
        new_img = ImageTk.PhotoImage(img)

    def receive():
        msg_rec = connection.recv_plaintext()
        user = "Temp"
        if msg_rec is not None:
            print(msg_rec)
            text_label = Label(text_rectangle,font=("Helvetica", 12), bg="#17282A", fg="white" , bd=5, text=(user + ": " + msg_rec))
            text_labels.append(text_label)
            text_label.pack(side="top", fill="x", pady=1)
            # Update scrollbar
            canvas_scroll.update_idletasks()
            canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))
            canvas_scroll.yview_moveto(1)

    def listen():
        receive()
        root.after(50, listen)

    canvas = Canvas(root, height=HEIGHT, width=WIDTH)
    canvas.pack()

    # Welcome banner
    welcome_banner = Label(root, bd=5, bg="#17202A", fg="white", text="Welcome to this chatroom!",
                           font=("Ostrich Sans", 16, "bold"))
    welcome_banner.place(relx=0, rely=0, relwidth=1.0, relheight=0.1)

    #Upper left frame, Scrollbar is a bit hacky
    frame_upper_left = Frame(root, bd=5)
    frame_upper_left.place(relx=0, rely=0.1,relwidth=0.7,relheight=0.5)

    canvas_scroll = Canvas(frame_upper_left, bg="#17202A")
    canvas_scroll.pack(side=LEFT, fill="both", expand=1)
    scrollbar = Scrollbar(frame_upper_left,orient=VERTICAL, command=canvas_scroll.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    canvas_scroll.configure(yscrollcommand=scrollbar.set)
    canvas_scroll.bind("<Configure>", lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))

    text_rectangle = Frame(canvas_scroll, bg="#17202A")
    canvas_scroll.create_window((0,0), window=text_rectangle, anchor="nw", width=WIDTH*0.7)
    text_labels = []
    scrollbar.place(relx=0.95, rely=0, relwidth=0.05, relheight=1.0)

    # Chat room frame
    frame_upper_right = Frame(root, bd=5)
    frame_upper_right.place(relx=0.7, rely=0.1, relwidth=0.3, relheight=0.5)
    chat_room = Text(frame_upper_right, bd=1, font=("Helvetica", 14), bg="#17202A", fg="white")
    chat_room.place(relx=0, rely=0, relwidth=1.0, relheight=0.5)
    chat_room.configure(state=DISABLED)
    online_users_frame = Text(frame_upper_right, bd=1, font=("Helvetica", 14), bg="#17202A", fg="white")
    online_users_frame.place(relx=0, rely=0.5, relwidth=1.0, relheight=0.5)

    # Message label
    message_label = Label(root, bd=5, text="Write your message below:", font=("Helvetica", 12), bg="#EAECAE")
    message_label.place(relx=0, rely=0.6, relwidth=1.0, relheight=0.05)

    # Input Frame
    frame_middle = Frame(root, bd=5)
    frame_middle.place(relx=0, rely=0.65, relwidth=1.0, relheight=0.25)
    message_box = Text(frame_middle, font=("Helvetica", 14), bg="#2C3E50", fg="white")
    message_box.pack()
    message_box.bind("<Return>", sende)

    # Send buttons
    frame_lower = Frame(root, bd=5)
    frame_lower.place(relx=0, rely=0.9, relwidth=1.0, relheight=0.1)
    send_button = Button(frame_lower, text="send", bg="#5D92B1", fg="white", command=send, bd=5)
    send_button.place(relx=0.3, rely=0.1, relwidth=0.2, relheight=0.8)
    send_image = Button(frame_lower, text="send image", bg="#5D92B1", fg="white", command=send_img, bd=5)
    send_image.place(relx=0.5, rely=0.1, relwidth=0.2, relheight=0.8)

    listen()
    root.mainloop()
