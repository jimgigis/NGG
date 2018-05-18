import socket
import ssl
# admin client
adminsocket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
connstream = ssl.wrap_socket(adminsocket,
                             certfile = "Certs/7.crt",
                             keyfile =  "Certs/7.key",
                             ca_certs = "Certs/rootCA.crt",
                             cert_reqs = ssl.CERT_REQUIRED)
                             
connstream.connect(("127.0.0.1",4001))

Hello = "Hello"


connstream.send(bytes(Hello+"\r\n","utf-8"))
r = connstream.recv(1024).decode("utf-8")
connstream.send(bytes("Who\r\n","utf-8"))
print("The players currently playing are: ")
while r :
    r = connstream.recv(1024).decode("utf-8")    
    print(r)
connstream.close()
    
