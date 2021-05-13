def login(username, password):
    correct = False
    file = open("user_info.txt", "r")
    for i in file:
        usr, passwrd = i.split(",")
        passwrd = passwrd.strip()
        if usr == username and passwrd == password:
            correct = True
            break
    file.close()
    if not correct:
        print("Incorrect username or password!")


def register(username, password):
    file = open("user_info.txt", "a")
    file.write(username + "," + password+"\n")
    file.close()

if __name__ == '__main__':
    register("hi","hey")