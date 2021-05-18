import io
from tkinter import *
from tkinter import filedialog
from common.handler import ConnectionHandler
from pathlib import Path
import os
from PIL import Image, ImageTk


def chat_client(connection):
    HEIGHT = 800
    WIDTH = 800
    root = Tk()
    root.title('tk')

    online_users = {}
    usernames_by_uid = {}
    channels = {}
    chatrooms_labels = []
    channel_text_rectangles = {}
    current_room = 0
    images = []
    files_by_fid = {}
    handler = ConnectionHandler()
    handler.register(connection, 0)
    pending_image_labels = {}

    def on_message(conn, cid, uid, text, channel_id):
        frame_create(usernames_by_uid[uid], channel_id, text)
        print("[DEBUG]", " <", str(uid), ">:", text)
        update_scrollbar()

    def on_upload(conn, cid, fid, chid, name, data):
        if fid in pending_image_labels:
            img = Image.open(io.BytesIO(bytes(data)))
            img.thumbnail((150, 150))
            new_img = ImageTk.PhotoImage(img)
            images.append(new_img)
            frame = pending_image_labels[fid]
            frame.configure(image=new_img, compound=RIGHT)
            update_scrollbar()
            del pending_image_labels[fid]
        else:
            # Oh god, it's a download prompt... TODO
            save_file = filedialog.asksaveasfile("wb", initialdir=str(os.path.join(Path.home(), "Downloads")),
                                                 initialfile=name)
            if save_file is not None:
                save_file.write(bytes(data))
                save_file.close()

    def on_join(conn, cid, username, uid):
        print("[SERVER] User", str(uid), "joined with name", username)
        usernames_by_uid[uid] = username
        online_users[uid] = True

    def on_left(conn, cid, uid):
        print("[SERVER] User", str(uid), "left")
        del online_users[uid]

    def on_channel(conn, cid, channel_name, channel_id):
        print("[SERVER] Channel", channel_id, "with name", channel_name)
        channels[channel_id] = channel_name
        if channel_id not in channel_text_rectangles:
            channel_text_rectangles[channel_id] = []
        change_rooms(current_room)

    def on_file(conn, cid, sender_uid, channel_id, fileid, filename, filelen, image):
        files_by_fid[fileid] = (filename, sender_uid, image, filelen)
        if image:
            conn.send_download(fileid, False)
            label = frame_create(usernames_by_uid[sender_uid], channel_id)
            label.bind("<Button 1>", lambda event, client=conn: conn.send_download(fileid, False))
            pending_image_labels[fileid] = label
        else:
            frame_create(usernames_by_uid[sender_uid], channel_id,
                         "<FILE> \"" + filename + "\" @ " + str(filelen/1000) + "KB <FILE>")\
                .bind("<Button 1>", lambda event, client=conn: conn.send_download(fileid, False))
        update_scrollbar()

    handler.set_message_handler(on_message)
    handler.set_upload_handler(on_upload)
    handler.set_join_handler(on_join)
    handler.set_left_handler(on_left)
    handler.set_channel_handler(on_channel)
    handler.set_file_event_handler(on_file)


    def send():
        msg = message_box.get(1.0, END)
        message_box.delete(1.0, END)
        connection.send_message(0, msg, current_room)

    # Event för om man trycker på enter
    def sende(event):
        send()

    # Funktion för att skicka bilder
    def send_img():
        file_img = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select Image",
                                              filetypes=(("JPG", "*.jpg"), ("All", "*.*")))
        data = open(file_img, "rb").read()
        file_name = file_img[file_img.rfind("/") + 1:]
        connection.send_upload(0, current_room, file_name, list(data))
        # display_image(file_img, "Image User")

    # Function that creates GUI frames for messages
    def frame_create(sender, channel_id, message=""):
        text_label = Label(text_rectangle, font=("Helvetica", 11), bg="#17282A", fg="white", bd=5,
                           text=sender + ": " + message, anchor=NW)
        channel_text_rectangles[channel_id].append(text_label)
        if channel_id == current_room:
            text_label.pack(side="top", fill="x", pady=1)
        return text_label

    # Function that displays image, needs img file location, needs sender
    # def display_image(file_img, sender):
    #     img = Image.open(file_img)
    #     img.thumbnail((150, 150))
    #     new_img = ImageTk.PhotoImage(img)
    #     images.append(new_img)
    #     tmp_frame = frame_create(sender, 0)
    #     tmp_frame.configure(image=new_img, compound=RIGHT)
    #     update_scrollbar()

    # Function to update scrollbar
    def update_scrollbar():
        canvas_scroll.update_idletasks()
        canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))
        canvas_scroll.yview_moveto(1)

    # Function for changing chatrooms, needs chatroom id
    def change_rooms(num):
        nonlocal current_room
        for label in channel_text_rectangles[current_room]:
            label.pack_forget()
        current_room = num
        for label in channel_text_rectangles[current_room]:
            label.pack(side="top", fill="x", pady=1)
        for label in chat_room.winfo_children():
            label.destroy()
        update_room_labels()

    def update_room_labels():
        for channel_id, channel_name in channels.items():
            room_label = None
            if channel_id == current_room:
                room_label = Label(chat_room, font=("Helvetica", 10), bg="#57282A", fg="white", bd=5,
                                   text=channel_name)
            else:
                room_label = Label(chat_room, font=("Helvetica", 10), bg="#17282A", fg="white", bd=5,
                               text=channel_name)
            chatrooms_labels.append(room_label)
            room_label.pack(side="top", fill="x", pady=1)
            room_label.bind("<Button 1>", lambda e, numb=channel_id: change_rooms(numb))

    def update_users():
        online_users_frame.configure(state=NORMAL)
        online_users_frame.delete(1.0, END)
        for uid, online in online_users.items():
            if online:
                online_users_frame.insert(END, usernames_by_uid[uid] + "\n")
        online_users_frame.configure(state=DISABLED)
        root.after(100, update_users)

    def listen():
        handler.poll()
        root.after(5, listen)

    def startup():
        update_users()
        root.after(5, listen)

    canvas = Canvas(root, height=HEIGHT, width=WIDTH)
    canvas.pack()

    # Welcome banner
    welcome_banner = Label(root, bd=5, bg="#17202A", fg="white", text="Welcome to this chatroom!",
                           font=("Ostrich Sans", 16, "bold"))
    welcome_banner.place(relx=0, rely=0, relwidth=1.0, relheight=0.1)

    # Upper left frame, Scrollbar is a bit hacky
    frame_upper_left = Frame(root, bd=5)
    frame_upper_left.place(relx=0, rely=0.1, relwidth=0.7, relheight=0.5)

    canvas_scroll = Canvas(frame_upper_left, bg="#17202A")
    canvas_scroll.pack(side=LEFT, fill="both", expand=1)
    scrollbar = Scrollbar(frame_upper_left, orient=VERTICAL, command=canvas_scroll.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    canvas_scroll.configure(yscrollcommand=scrollbar.set)
    canvas_scroll.bind("<Configure>", lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))

    text_rectangle = Frame(canvas_scroll, bg="#17202A")
    canvas_scroll.create_window((0, 0), window=text_rectangle, anchor="nw", width=WIDTH * 0.7)
    text_labels = []
    scrollbar.place(relx=0.95, rely=0, relwidth=0.05, relheight=1.0)

    # Chat room and user frames
    frame_upper_right = Frame(root, bd=5)
    frame_upper_right.place(relx=0.7, rely=0.1, relwidth=0.3, relheight=0.5)
    chat_room = Frame(frame_upper_right, bd=1, bg="#17202A")
    chat_room.place(relx=0, rely=0.05, relwidth=1.0, relheight=0.45)

    online_users_frame = Text(frame_upper_right, font=("Helvetica", 8), bd=1, bg="#17202A", fg="white")
    online_users_frame.place(relx=0, rely=0.55, relwidth=1.0, relheight=0.45)
    online_users_frame.configure(state=DISABLED)

    chat_room_label = Label(frame_upper_right, font=("Helvetica", 12), bd=1, bg="#17232A", fg="white", text="Chatrooms")
    online_users_label = Label(frame_upper_right, font=("Helvetica", 12), bd=1, bg="#17232A", fg="white",
                               text="Online Users")
    chat_room_label.place(relx=0, rely=0, relwidth=1.0, relheight=0.05)
    online_users_label.place(relx=0, rely=0.5, relwidth=1.0, relheight=0.05)

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

    startup()
    root.mainloop()
