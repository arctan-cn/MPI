import threading
import socket
import yaml
import json
import uuid
import time
class InterfaceError(Exception): #自定义接口异常
    def __init__(self, message="", code=0):
        self.code = code
        super().__init__(message)
class Cursor(): #定义指针类
    def __init__(self):
        self.config = None #加载配置
        with open("config.yml", mode="r") as f:
            self.config = yaml.load(f, Loader=yaml.SafeLoader)
        self.socket = socket.socket() #生成socket实例
        self.uuid = uuid.uuid4()
        self.createTime = time.time()
        self.stack = []
        self.connected = False
    def setTimeout(self, timeout:float=10): self.socket.settimeout(timeout) #设置socket超时
    def connect(self): self.__enter__() #连接到Java服务端
    def close(self): self.__exit__(None, None, None) #关闭socket连接
    def __enter__(self): 
        self.socket.connect((self.config["server"]["address"], self.config["server"]["port"])) #连接到Java服务端
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
    def send(self, requestType:str, message:dict={}, login=False) -> uuid.UUID:
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
    def request(self, requestType:str, message:dict={}, asyncMode:bool=False, callback=None, login=False):
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
                                raise InterfaceError("Invalid response code:%s" % code, code)
                        if received_data.get("uuid") == responseUUID.__str__():  
                            if callback: callback(received_data)
                            return received_data
                    except json.decoder.JSONDecodeError as e:
                        print("Invalid JSON response:", data, e)
        if asyncMode:
            listenerThread = threading.Thread(target=tempResponseWaiter, args=(self.socket, requestUUID, callback))
            listenerThread.start()
            return listenerThread
        else:
            return tempResponseWaiter(self.socket, requestUUID, callback)
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.send("disconnect")
        self.socket.close()

if __name__=="__main__":
    mc = Cursor()
    mc.connect()
    mc.setTimeout(10)
    response = mc.request("debug", {"name": None})
    print(response)
    mc.close()