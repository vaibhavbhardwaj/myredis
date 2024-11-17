# Import socket module
import socket


def Main():
	# local host IP '127.0.0.1'
	host = '127.0.0.1'

	# Define the port on which you want to connect
	port = 6379

	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

	# connect to server on local computer
	s.connect((host,port))

	# message you send to server
	m1 = "*2\r\n$4\r\nECHO\r\n$3\r\norange\r\n"
	#m1 = '*1\r\n$4\r\nPING\r\n'
	message = "shaurya says geeksforgeeks"
    
	while True:
		

		# message sent to server
		s.send(m1.encode('ascii'))
        
		# message received from server
		data = s.recv(1024)

		# print the received message
		# here it would be a reverse of sent message
		print('Received from the server :',str(data.decode('ascii')))

		# ask the client whether he wants to continue
		ans = input('\nDo you want to continue(y/n) :')
		if ans == 'y':
			continue
		else:
			break
	# close the connection
	s.close()

if __name__ == '__main__':
	Main()
