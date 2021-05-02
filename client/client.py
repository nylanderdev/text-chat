from tkinter import *

root = Tk()
root.title('Test')
root.geometry('800x640')

def send():
    textTmp = texten.get(1.0,END)
    print(textTmp)
    texten.delete(1.0,END)

texten = Text(root, width=80, height=20, font=("Helvetica", 14, "bold"))
texten.pack(pady=5)

button_frame = Frame(root)
button_frame.pack()
send_button = Button(button_frame, text="Send", command=send)
send_button.pack()

root.mainloop()