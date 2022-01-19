# Textchat project in Python 

## Introduction 
The purpose of this project is to create a functioning group-chatting platform where users have the ability to communicate over the internet. 

## Description and technologies 
The project builds on a server that broadcasts messages to all its clients. Sockets are used as endpoints for sending and receiving data across the network. We have created our own chat protocol (on top of TCP) that generates headers based on the length of individual messages, as well as supports sending and receiving plain text.

We have added a graphical user interface (GUI) using Tkinter in order to make the platform more user friendly. When joining the server the user will have to login with a username and password, after entering the credentials correctly they will then be redirected to the chatroom.

In addition to text, users are also be able to send files. Images of supported formats are displayed in the client.

## How to run the program 
The program uses pipenv and python3.  

To run the server, use the command:

```pipenv run python -m server.main```

To run the graphical client and start using the program, use the command:

```pipenv run python -m client.main```



