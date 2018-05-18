import socket
import select
import random
import ssl
import re




#defined communication string - messages to achieve proper behavour between server and player/admin clients
Greetings = "Greetings"
AdminGreetings = " Admin Greetings"
Far = "You are way off."
Near = "You are close!"
Correct = "You guessed correctly!"



#defined function to calculate wether a certain input is inside a range of the goal number
#it is also required to check that the value and goal inputs are not equal
def within(value,goal,n):
    if abs(value - goal ) <= n and value != goal :
        return True
    else :
        return False
#a Client class to store the data associated with each connected client
class Client:
    ip = ""
    port = 0
    number = 0
    numberOfGuesses = 0

#a list to hold the sockets connected to the server 
open_sockets = []
# a dictionary to hold the Client objects represeting the clients connected to the server
# it will use the port and ip numbers of each client as the key value
connected_clients = {}

#socket for players and admin are declared with port 4000 for players and port 4001 for admin
playersocket = socket.socket ( socket.AF_INET , socket.SOCK_STREAM)
adminsocket = socket.socket ( socket.AF_INET , socket.SOCK_STREAM)

playersocket.bind(("127.0.0.1", 4000))
adminsocket.bind(("127.0.0.1", 4001))

playersocket.listen(5)
adminsocket.listen(5)

#main server loop
while True:
    #initially when a socket is connected for the first time it needs to be appended to the open sockets list
    #it is also important to distinguish wether it is an admin socket or a player socket 
    #using the select module a reading list (rlist)is declared to store all the new sockets connecting to the server
    
    rlist,wlist,xlist = select.select([playersocket,adminsocket] + open_sockets , [] , [] )
    #next step is to check wether the new socket connected is a socket for admins or for players
    for socket in rlist:
        if socket is adminsocket:
            #if its an admin socket the server is designed to provide TLS protocol for security reasons
            new_adminsocket,address = adminsocket.accept()
            connstream  = ssl.wrap_socket(new_adminsocket,server_side = True,
                        certfile = "Certs/server.crt",
                        keyfile = "Certs/server.key",
                        ca_certs ="Certs/rootCA.crt",
                        cert_reqs =ssl.CERT_REQUIRED)
            #lastly the new socket is added to the list of open sockets connected to the server
            open_sockets.append(connstream)


        elif socket is playersocket:
            #if its a player socket  then a new Client object is instantiated and added to the connected_clients dictionary
            # a random number is assigned to each Client 
            new_playersocket , address = playersocket.accept()
            open_sockets.append(new_playersocket)
            if not (address[0] + "-" + str(address[1])) in connected_clients:
                connected_clients[address[0]+"-"+str(address[1])] = Client()
                connected_clients[address[0]+"-"+str(address[1])].ip = address[0]
                connected_clients[address[0]+"-"+str(address[1])].port = address[1]
                connected_clients[address[0]+"-"+str(address[1])].number = random.randrange(0,21,1)
                connected_clients[address[0]+"-"+str(address[1])].numberOfGuesses = 0
                
        #next step is to handle existing sockets        
        else:
            # if an existing socket's port is 4000 then it means its a player socket
            if socket.getsockname()[1] == 4000:
                # initially the server is expected to recieve a hello message from the client and respond with a similar greetings message.
                # an if statement is used to check wether the player is playing for the first time
                # if the numbers he has guessed is 0 that means he hasnt played the game yet
                if connected_clients[socket.getpeername()[0]+"-"+str(socket.getpeername()[1])].numberOfGuesses == 0:
                    data = socket.recv(1024).decode("utf-8")
                    if data == "Hello\r\n" :
                        socket.send(bytes(Greetings+ "\r\n","utf-8"))
                    connected_clients[socket.getpeername()[0]+"-"+str(socket.getpeername()[1])].numberOfGuesses +=  1
                    break
                data = socket.recv(1024).decode("utf-8")    
                if data == "":
                    del connected_clients[socket.getpeername()[0] + "-"+str(socket.getpeername()[1])]
                    socket.close()
                    open_sockets.remove(socket)
                    break
                #next step is the game logic
                else:
                    # a number input is received from the player
                    
                    number = re.findall(r'\d{1,2}',data)

                    guess= int(number[0])
                    #this if statement checks wether the input number given from the player is close to the correct number
                    # if it is, a message is sent to the client stating he is close to the target number and he is prompted to guess again
                    if (within(guess,connected_clients[socket.getpeername()[0]+"-"+str(socket.getpeername()[1])].number,3)):
                        socket.send(bytes(Near + "\r\n","utf-8"))
                        connected_clients[socket.getpeername()[0]+"-"+str(socket.getpeername()[1])].numberOfGuesses +=  1
                        break
                    #this if statement checks wether the input number from the player was correct
                    # if it is a message stating that he found the number is sent along with a message stating how many times he tried
                    # finally  the connection is closed and this player's socket is removed from the open sockets list
                    elif guess == connected_clients[socket.getpeername()[0]+"-"+str(socket.getpeername()[1])].number :
                        tries = connected_clients[socket.getpeername()[0]+"-"+str(socket.getpeername()[1])].numberOfGuesses
                        socket.send(bytes(Correct + "Your number of tries was " + str(tries) + "\r\n","utf-8"))
                        del connected_clients[socket.getpeername()[0]+"-"+str(socket.getpeername()[1])] 
                        open_sockets.remove(socket)
                        socket.close()
                        break
                    #if the above two if statements are false then the input number given from the player is far from the target number
                    # a message stating that he is far is send and he is prompted to guess again
                    else:
                        socket.send(bytes(Far + "\r\n","utf-8"))
                        connected_clients[socket.getpeername()[0]+"-"+str(socket.getpeername()[1])].numberOfGuesses +=  1
                        break
                        
                        
            # finally existing admin sockets are handled        
            elif socket.getsockname()[1] == 4001:
                #initally an Admin-Greetings message is sent and a similar message is expected from the admin 
                
                data = connstream.recv(1024).decode("utf-8")
                if data == "Hello\r\n" :
                    connstream.send(bytes(AdminGreetings+ "\r\n","utf-8"))
                #data = connstream.recv(1024).decode("utf-8")
                if data == "":
                    connstream.close()
                    open_sockets.remove(socket)
                #if "who" message is received then the server is expected to send a message containing the ip address and the port number of each connected client
                elif data == "Who\r\n":
                    for connectedClient in connected_clients :
                        totalConnectedClients = connected_clients[connectedClient].ip + " "+ str(connected_clients[connectedClient].port) + "\r\n"                        
                        connstream.send(bytes(totalConnectedClients,"utf-8"))
                    #finally after such message is sent the connection is closed
                    connstream.close()
                    open_sockets.remove(socket)
                     

                     

                                   
                 
             
    
