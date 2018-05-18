import socket
import re 
playersocket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
playersocket.connect(("127.0.0.1",4000))
# a hello message is defined as it is required for proper server-client communication
Hello = "Hello"

#initially the player sends the hello message to the server and awaits the the appropriate greetings message from the server
playersocket.send(bytes(Hello+"\r\n","utf-8"))
r = playersocket.recv(1024).decode("utf-8")
# the greetings message is printed on the user's screen
print("Welcome to guess the number game!")
while r :
    r = input("What is your guess: ")
    # a regular expression to extract the number from the r input string
    s = re.findall(r'\d{1,2}',r)
    # if statement to handle an index out of bounds exception for s list
    if len(s) > 0 :
        Guess = "Guess: " +  str(s[0]) + "\r\n"
        playersocket.send(bytes(Guess,"utf-8"))   
        r = playersocket.recv(1024).decode("utf-8")
        print(r)
        if (re.search("Your number of tries was ", r) is not None):
            break
    else:
        break
playersocket.close()
    
