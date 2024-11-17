import socket  # noqa: F401
# import thread module
from _thread import *
import threading
from threading import Thread

print_lock = threading.Lock()
def threaded(c):
    while True:
        data = c.recv(1024)
        print("data",data.decode("utf-8"))
        if not data:
            print("Bye")
            #print_lock.release()
            break
        #data = data[::-1]
        
        request_string = decode_string(data.decode("utf-8"))
        print(request_string,"request_string")
        response_string = respone_data(request_string)
        print('response',response_string)
        c.send(response_string.encode('ascii'))
        #c.send(data)    
    c.close()
        # data received from client
        # data = c.recv(1024)
	    # if not data:
		# 	print('Bye')
			
		# 	# lock released on exit
		# 	print_lock.release()
		# 	break

		# reverse the given string from client
		#data = data[::-1]

		# send back reversed string to client
		

	# connection closed
def respone_data(data):
    print("inside response",data)
    length_data_array = len(data)
    #command_data = data.split(' ')[1]
    if data[0] == 'PING':
        return '+PONG\r\n'
    command_data = data[len(data)-1]
    #print(command_data)
    #print(f'${len(command_data)}\\r\\n{command_data}\\r\\n')
    return f'${len(command_data)}\r\n{command_data}\r\n'
    	
def decode_string(data):
    mark = data[0]
    match mark:
        case "+": return str(data[1:-2])
        case "-": return str(data[1:-2])
        case ":": return int(data[1:-2])
        case "$":
            parts = data[1:].split('\r\n')
            ln = int(parts[0])
            if ln == -1:
                return None
            elif ln == 0:
                return ''
            else:
                return str(parts[1])
        case '*':
            u = data.split('\r\n')
            u.remove('')
            chunk_character=[]
            chunk_data = []
            for i in range (1, len(u)):
                if i%2==0:
                    chunk_data.append(u[i])
                else:
                    chunk_character.append(u[i])
            items=[]
            for i in range(len(chunk_data)):
                print(decode_string(f'{chunk_character[i]}\r\n{chunk_data[i]}\r\n'))
                items.append(decode_string(f'{chunk_character[i]}\r\n{chunk_data[i]}\r\n'))
            return items
        case _:
            return 'oops'
def encode(data, simple_str=False):
    if isinstance(data, ValueError):
        print(1)
        return f'-{str(data)}\r\n'
    elif isinstance(data, str) and simple_str:
        print(2)
        return f'+{data}\r\n'
    elif isinstance(data, int):
        print(3)
        return f':{data}\r\n'
    elif isinstance(data, str):
        print(4,f'${len(data)}\\r\\n{data}\\r\\n')
        return f'${len(data)}\\r\\n{data}\\r\\n'
    elif isinstance(data, list) or isinstance(data, tuple):
        enc = f'*{len(data)}\r\n'
        for itm in data:
            enc += encode(itm)
        return enc

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here1!")

   # Uncomment this to pass the first stage
    #
    #server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    # server_socket = socket.create_server(("localhost", 6379))
    # client, address = server_socket.accept() # wait for client
    # #client.send(b"+PONG\r\n")
    # with client:
    #     client.recv(1024)
    #     client.send(b"+PONG\r\n")
    with socket.create_server(("localhost", 6379)) as server_socket:
        print(1)
        while True:
            print(2)
            server_socket.listen(0)
            client, address = server_socket.accept()
            #while client.recv(8000):
            #with client:
            #print_lock.acquire()
            print('Connected to :', address[0], ':', address[1])
            #print("thread")
                #start_new_thread(threaded, (client,))
            thread = threading.Thread(target=threaded,args=(client,))
            thread.start()
        thread.join()
                #client.send(b"+PONG\r\n")



    


if __name__ == "__main__":
    print ("here1")
    main()
