import threading
import socket
import yaml
import json
import uuid
import time
import sys

VERSION = "0.0.2"

class InterfaceError(Exception):
    def __init__(self, message="", code=0):
        self.code = code
        super().__init__(message)
class Selector:
    def __init__(self, selector:str):
        if type(selector) != str:
            raise TypeError("Selector argument must be str (not %s)" % type(selector.__name__))
        if not selector:
            raise TypeError("Selector cannot be an empty string")
        self.__selector = selector
    @property
    def selector(self):
        return self.__selector
    def __repr__(self):
        return "Selector(%s)"%self.__selector
class Entity:
    def __init__(self, entityType:str, nbt:dict={"uuid":uuid.uuid4().__str__()}, world:str="world", position:list=[0, 0, 0]):
        self.__type = entityType
        self.__nbt = nbt
        self.__world = world
        self.__position = position
        if "uuid" in nbt:
            self.__uuid = nbt["uuid"]
        else:
            self.__uuid = uuid.uuid4().__str__()
    @property
    def type(self): return self.__type
    @property
    def nbt(self): return self.__nbt
    @property
    def world(self): return self.__world
    @property
    def position(self): return self.__position
    @property
    def uuid(self): return self.__uuid

class Interface:
    def __init__(self):
        self.config = None
        with open("config.yml", mode="r") as f:
            self.config = yaml.load(f, Loader=yaml.SafeLoader)
        self.socket = socket.socket()
        self.uuid = uuid.uuid4()
        self.createTime = time.time()
        self.stack = []
        self.connected = False
    def setTimeout(self, timeout:float=10): self.socket.settimeout(timeout)
    def connect(self): self.__enter__()
    def close(self): self.__exit__(None, None, None)
    def __enter__(self): 
        self.socket.connect((self.config["server"]["address"], self.config["server"]["port"]))
        try:
            response = self.request("login", {"password": self.config["server"]["password"]}, login=True)
            self.connected = True
        except InterfaceError as e:
            if e.code==403:
                self.socket.close()
                raise InterfaceError("Login failed")
            else:
                self.socket.close()
                raise e
        except Exception as e:
            self.socket.close()
            raise e
    def send(self, requestType:str, message:dict={}, login=False, throwExceptionalCode=True) -> uuid.UUID:
        if (not login) and (not self.connected): raise InterfaceError("Socket is not connected")
        messageUUID = uuid.uuid4()
        messageJson = {
            "uuid": messageUUID.__str__(),
            "time": time.time(),
            "type": requestType, 
            "message": message,
        }
        self.stack.append(messageJson)
        self.socket.send(json.dumps(messageJson).encode("utf-8"))
        return messageUUID
    def request(self, requestType:str, message:dict={}, asyncMode:bool=False, callback=None, login:bool=False, throwExceptionalCode:bool=False):
        requestUUID = self.send(requestType, message, login)
        def tempResponseWaiter(sock, responseUUID:uuid.UUID, callback) -> dict:
            while True:  
                data = sock.recv(1024).decode("utf-8")  
                if data:  
                    try:
                        received_data = json.loads(data)  
                        if received_data.get("code") != 200:
                            code = received_data.get("code")
                            if code == 700:
                                raise InterfaceError("Server closed", 700)
                            else:
                                if throwExceptionalCode: raise InterfaceError("Exceptional response code:%s\nMessage:%s" % (code, received_data), code)
                        if received_data.get("uuid") == responseUUID.__str__():  
                            if callback: callback(received_data)
                            return received_data
                    except json.decoder.JSONDecodeError as e:
                        raise InterfaceError("Invalid JSON response: %s\n%s" % (data, e))
        if asyncMode:
            listenerThread = threading.Thread(target=tempResponseWaiter, args=(self.socket, requestUUID, callback))
            listenerThread.start()
            return listenerThread
        else:
            return tempResponseWaiter(self.socket, requestUUID, callback)
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.send("disconnect")
        self.socket.close()

    def command(self, command:str):
        return self.request("command", {"command":command})

if __name__=="__main__":
    print("Copyright(c) OASIS")
    print("MPI Debugger Console alpha v0.1")
    mc = Interface()
    print("Connecting to the server...")
    mc.connect()
    print("\033[0;32mSuccessfully connected to the server.\033[0m")
    while True:
        try:
            sys.stdout.write("\033[0;36m")
            i = input("> ")
            l = i.split(" ")
            if len(l)<1: continue
            requestType = l[0]
            args = " ".join(l[1:len(l)])
            if not args:args = '{}'
            args = json.loads(args)
            if requestType == "break":
                sys.stdout.write("\033[0;0m")
                break
            response = mc.request(requestType, args)
            if response['code']==200:
                print("\033[0;0m%s"%str(response))
            else:
                print("\033[0;33m%s"%str(response))
            sys.stdout.write("\033[0;0m")
        except Exception as e:
            print("\033[0;31m",e,"\033[0m")
        except KeyboardInterrupt:
            break
    print("Disconnecting...")
    mc.close()
    print("\033[0;32mSuccessfully disconnected from the server.\033[0m")