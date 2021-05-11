# Textchat project in Python 

## Introduction 
The purpose of this project is to create a functioning group-chatting platform where users have the ability to communicate over the internet. 

## Description and technologies 
The project builds on a server that broadcasts messages to all its clients. Sockets are used as endpoints for sending and receiving data across the network. We have created our own chat protocol (TCP) that generates headers based on the length of individual messages, as well as supports sending and receiving plain text.

We have added a graphical user interface (GUI) using Tkinter in order to make the platform more user friendly. When joining the server the user will have to login with a username and password, after entering the credentials correctly they will then be redirected to the chatroom. At this stage in the project we only have support for one channel/chatroom but by the end of the project the user will be able to choose amongst several chatrooms. 

Users will also be able to send files. This is accomplished using a Huffman coding compression algorithm, which is a lossless data compression algorithm. 
