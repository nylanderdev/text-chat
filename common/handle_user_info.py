import tkinter


def login(username, password):
    file = open("user_info.txt", "r")
    for i in file:
        usr, passwrd = i.split(",")
        passwrd = passwrd.strip()
        if usr == username and passwrd == password:
            return True
    file.close()
    return correct

def register(username, password):
    file = open("user_info.txt", "r")
    for i in file:
        usr, passwrd = i.split(",")
        passwrd = passwrd.strip()
        if usr == username and passwrd == password:
            tkinter.messagebox.showinfo('Oops', 'Username and password already registered!')
            return False
    file.close()

    file = open("user_info.txt", "a")
    file.write(username + "," + password + "\n")
    file.close()
    return True
