from tkinter import *

root = Tk()
root.title('tk')
root.geometry('600x600')


def send():
    msg = message_box.get(1.0, END)
    print(msg)
    message_box.delete(1.0, END)
    text_rectangle.configure(state=NORMAL)
    text_rectangle.insert(1.0, msg)
    text_rectangle.yview(END)
    text_rectangle.configure(state=DISABLED)


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

root.mainloop()
