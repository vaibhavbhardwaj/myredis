import socket  # noqa: F401
# import thread module
from _thread import *
import threading
from threading import Thread
import time
from datetime import timedelta
import sys
import os


print_lock = threading.Lock()
db_dict = {}
CONFIG_DICT = {}
# print(CONFIG_DICT)

# print(sys.argv)
def set_config(data):
    CONFIG_DICT['config'] = {data[1].replace('--',''):data[2],data[3].replace('--',''):data[4]}
def get_config():
    print (CONFIG_DICT)
    return CONFIG_DICT
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
        command_output = redis_command(request_string)
        #response_string = respone_data(request_string)
        print('response',command_output)
        c.send(command_output.encode('ascii'))
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
def get_keys_from_dbfile():
    config_dict = get_config()
    if config_dict:
        print("db exists")
        db_file_name = config_dict['config'].get('dbfilename')
        db_file_path = config_dict['config'].get('dir')
        rdb_file_path = os.path.join(db_file_path,db_file_name)
        if os.path.exists(rdb_file_path):
            with open(rdb_file_path, "rb") as rdb_file:
                rdb_content = str(rdb_file.read())
                print(rdb_content)
                if rdb_content:
                    key = parse_redis_file_format(rdb_content)
                    return key
        else:
            return "*0\r\n"

def parse_redis_file_format(file_format: str):
    file_array = file_format.split("\\")
    print(file_array)
    # resizedb_index = file_array.index("xfb")
    # print(resizedb_index,"xfb")
    # key_index = resizedb_index + 4
    # value_index = key_index + 1
    # key_bytes = file_array[key_index]
    # value_bytes = file_array[value_index]
    # key = remove_bytes_caracteres(key_bytes)
    # value = remove_bytes_caracteres(value_bytes)
    #print("keyfunction",key)
    all_keys = get_all_keys(file_array)
    #return [key,value]
    return all_keys

def get_all_keys(file_list):
    all_keys_string = []
    all_keys = []
    all_values = []
    all_values_string = []
    # all_key_value_data =  file_list[file_list.index('xfb')+4:file_list.index('xff')]
    # all_key_value_data_removex00 = [i for i in all_key_value_data if (i != 'x00')]
    # all_keys = all_key_value_data_removex00[::2]
    for i in range(file_list.index('xfb')+3,len(file_list)):
        if file_list[i] == 'x00':
            all_keys.append(file_list[i+1])
            all_values.append(file_list[i+2])
            i = i+2
    for key in all_keys:
        all_keys_string.append(remove_bytes_caracteres(key))
    for value in all_values:
        all_values_string.append(remove_bytes_caracteres(value))
    return [all_keys_string,all_values_string]

def remove_bytes_caracteres(string: str):
    if string.startswith("x"):
        return string[3:]
    elif string.startswith("t"):
        return string[1:]
    elif string.startswith("n"):
        return string[1:] 



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

def redis_command(data):
    command = data[0]
    match command:
        case 'PING':
            return '+PONG\r\n'
        case 'ECHO':
            if len(data) == 2:
                return f'${len(data[1])}\r\n{data[1]}\r\n'
            else:
                return "unknown command"
        case 'SET':        
            if len(data) == 3:
                data_key = data[1]
                data_value = data[2]
                db_dict[data_key] = {'value':data_value,'createtime':time.time()}
                print(db_dict)
                return '+OK\r\n'
            elif len(data) == 5:
                data_key = data[1]
                data_value = data[2]
                data_expiry = data[4]
                db_dict[data_key] = {'value':data_value,'createtime':time.time(),'px':int(data_expiry)}
                print(db_dict)
                return '+OK\r\n'

            else:
                return "unknow command set"
        case 'GET':
            if len(data) == 2:
                print(data,db_dict,"duc datta")
                data_key = data[1]
                if data_key in db_dict:
                    data_value = db_dict[data_key].get('value')
                    data_createtime = db_dict[data_key].get('createtime')
                    print("expiry value",db_dict[data_key].get('px'))
                    if (db_dict[data_key].get('px')):
                        if (timedelta(seconds = time.time()-data_createtime ).total_seconds()*1000 > db_dict[data_key].get('px')):
                            return '$-1\r\n'
                    print (f'${len (data_value)} \r\n{data_value}\r\n') 
                    return f'${len (data_value)}\r\n{data_value}\r\n'
                else:
                #return "unknow command set"
                    print(data,"command data")
                    data_key = data[1]
                    keys_string = get_keys_from_dbfile()[0]
                    keys_value = get_keys_from_dbfile()[1]
                    print("getkey",keys_string,keys_value)
                    key_value = keys_value[keys_string.index(data_key)]
                    print(key_value,"keys")
                    return f'${len(key_value)}\r\n{key_value}\r\n'
        case 'CONFIG':
            config_command = data[1]
            config_parameter = data[2]
            config_data = CONFIG_DICT['config'].get(config_parameter)
            print (f'*2\r\n${len (config_parameter)}\r\n{config_parameter}\r\n${len (config_data)}\r\n{config_data}\r\n')
            return f'*2\r\n${len (config_parameter)}\r\n{config_parameter}\r\n${len (config_data)}\r\n{config_data}\r\n'
<<<<<<< HEAD
        case 'KEYS1':
            config_command = data[0]
            config_parameter = data[1]
            print("inside keys1",data)
            key = get_keys_from_dbfile()[0]
            return f'*1\r\n${len(key)}\r\n{key}\r\n'
        case 'KEYS':
            keys = get_keys_from_dbfile()[0]
            key_string = f'*{len(keys)}\r\n'
            for t in keys:
                key_string = key_string+f'${len(t)}\r\n{t}\r\n'
            return key_string
        case 'GET1':
            key = get_keys_from_dbfile()[1]
            print(key,"keys")
            return f'${len(key)}\r\n{key}\r\n'


=======
>>>>>>> 35678d6a51edd6aef839f86cfdf2caffd037a801




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
    if len(sys.argv) >= 5:
        set_config(sys.argv)
    get_config()
<<<<<<< HEAD
    get_keys_from_dbfile()
=======
>>>>>>> 35678d6a51edd6aef839f86cfdf2caffd037a801
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
