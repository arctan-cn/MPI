from mpigadgets import *
import subprocess
import threading
import socket
import yaml
import json
import uuid
import time
import tqdm
import sys
import os

VERSION = "0.0.4"
PATH = __file__
PARENT_PATH = "./.."
PROGRAM_PACKS_PATH = PARENT_PATH + "/programpacks"
MPI_VERSION = Version(VERSION)

def SHOW_VERSION(): print(f"\033[47;30m MPI Version \033[47;36m{VERSION}\033[47;30m \033[0m By Asyncio_ & JadeStyle")
class InterfaceError(Exception):
    def __init__(self, message="", code=0):
        self.code = code
        super().__init__(message)
class Link:
    def __init__(self, type:str, target:str):
        # {"type":"none","target":""}
        self.__link = {"type":type, "target":target}
        self.__type = type
        self.__target = target
    @property
    def type(self): return self.__type
    @property
    def target(self): return self.__target
    def __repr__(self):
        return f"Link({self.__type}->{self.__target})"
    def call(self, *args, **kwargs):
        arguments = {
            "type": "call",
            "args": args,
            "kwargs": kwargs
        }
        if self.__type == "script":
            arguments['type'] = "scriptCall"
            response = subprocess.run(["python", f"{PROGRAM_PACKS_PATH}/{self.__target}", json.dumps(arguments)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if response.returncode == 0:
                return response.stdout.decode("utf-8")
            else:
                raise InterfaceError(f"Exceptional return code: {response.returncode}\nstdout: {response.stdout}\nstderr: {response.stderr}")

class Pack:
    def __init__(self, namespace:str):
        self.__namespace = namespace
        self.__path = "./"
        self.configFiles = ["pack.yml", "register.yml"]
    @property
    def namespace(self): return self.__namespace
    @property
    def path(self): return self.__path
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
        with open("config.yml", mode="r", encoding="utf-8") as f:
            self.config = yaml.load(f, Loader=yaml.SafeLoader)
        self.socket = socket.socket()
        self.uuid = uuid.uuid4()
        self.createTime = time.time()
        self.stack = []
        self.connected = False
        self.socket.settimeout(10)
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
    @staticmethod
    def constructArguments(type:str="call", *args, **kwargs): return {"type":type, "args":args, "kwargs":kwargs}
    @staticmethod
    def executeScript(path, type:str="call", *args, **kwargs):
        response = subprocess.run(["python", path, json.dumps({"type":type, "args":args, "kwargs":kwargs})], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if response.returncode == 0:
            return response.stdout.decode("utf-8")
        else:
            raise InterfaceError(f"Exceptional return code: {response.returncode}\nstdout: {response.stdout}\nstderr: {response.stderr}")
    @staticmethod
    def yamlUpdate(path:str, updater=None):
        try:
            data = None
            with open(path, mode="r", encoding="utf-8") as f:
                data = yaml.load(f, Loader=yaml.SafeLoader)
            if updater:
                data = updater(data)
                with open(path, mode="w", encoding="utf-8") as f:
                    yaml.dump(data, f)
            return data
        except Exception as e:
            raise InterfaceError(f"Failed to update YAML File: {path}\nException:{e}")
        

def UIConsole():
    SHOW_VERSION()
    print("Debugger Console alpha v0.1")
    print("Copyright(c) OASIS")
    mc = Interface()
    print("Connecting to the server... %s:%s" % (mc.config['server']['address'], mc.config['server']['port']))
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

def launch():
    print(f"MPI v{VERSION}")
    print("加载程序包...")
    with open("packs.yml", mode="r", encoding="utf-8") as f:
        packs = yaml.load(f, Loader=yaml.SafeLoader)
        packs2 = {}
        for packname in packs:
            if packs[packname]: packs2[packname] = packs[packname]
        packs = packs2
    def isVersionInRange(version:Version, lr:list): return (lr[0] == "*" or version >= Version(lr[0])) and (lr[1] == "*" or version <= Version(lr[1]))
    def isVersionValid(packname:str, reqname:str, version:Version, lr:list):
        if not isVersionInRange(version, lr):
            ml = ""
            mr = ""
            text = ""
            if lr[0] != "*": ml = ">=" + lr[0]
            if lr[1] != "*": mr = "<=" + lr[1]
            if ml and mr: text = ml + "and" + mr
            elif not (ml and mr): text = "== Any"
            else: text = ml + mr
            raise InterfaceError(f"\"{packname}\" requires \"{reqname}\" (Version {text}), but \"{reqname}\"(Version=\"{version}\") was found.")
    if len(packs) > 0:
        loadedPacks = []
        counterPackLoader = Counter("successes", "failures")
        progressPackLoader = tqdm.tqdm(total=len(packs), desc="Loading Packs", unit="pack")
        for packname in packs:
            progressPackLoader.set_postfix({"Pack": packname})
            try:
                packInfo = Interface.yamlUpdate(f"{PROGRAM_PACKS_PATH}/{packname}/pack.yml")
                packRequirements = packInfo["requirements"]
                for req in packRequirements:
                    reqVersion = None
                    if req == "mpi": reqVersion = MPI_VERSION
                    reqpath = f"{PROGRAM_PACKS_PATH}/{req}/pack.yml"
                    if os.path.exists(reqpath) or req == "mpi":
                        if not reqVersion: reqVersion = Version(Interface.yamlUpdate(reqpath)["version"])
                        isVersionValid(packname, req, reqVersion, packRequirements[req])
                    else:
                        raise InterfaceError(f"\"{packname}\" requires \"{req}\", but \"{req}\" was not found.")
                Interface.yamlUpdate("cache/registeredLinks.yml", lambda data: {**data, **{packname: Interface.yamlUpdate(f"{PROGRAM_PACKS_PATH}/{packname}/links.yml")}})
                Interface.executeScript(f"{PROGRAM_PACKS_PATH}/{packname}/init.py", "init")
                Interface.yamlUpdate("cache/loadedPacks.yml", lambda data: data + [packname])
                loadedPacks.append(packname)
                counterPackLoader.successes += 1
            except Exception as e:
                print(f"\n\033[0;31m加载程序包失败 \"{packname}\":\n{e}\033[0m")
                counterPackLoader.failures += 1
            progressPackLoader.update(1)
        progressPackLoader.close()
        print(f"程序包加载完成 (总计 \033[0;36m%s\033[0m / 成功 \033[0;32m{counterPackLoader.successes}\033[0m / 失败 \033[0;31m{counterPackLoader.failures}\033[0m)" % len(packs))
    else:
        print("\033[0;33m未找到启用的程序包 已跳过程序包加载阶段\033[0m")
    Interface.yamlUpdate("cache/loadedPacks.yml", lambda data: loadedPacks)
    print("已更新 cache/loadedPacks.yml")
def UIClearcache():
    cacheFiles = {
        "loadedPacks": [],
        "registeredLinks": {},
    }
    pbar = tqdm.tqdm(total=len(cacheFiles), desc="Clearing Cache", unit="file")
    successes = 0
    for f in cacheFiles:
        pbar.set_postfix({"File":f})
        try:
            Interface.yamlUpdate(f"cache/{f}.yml", lambda data: cacheFiles[f])
            successes += 1
        except Exception as e:
            print(f"清除失败: {e}")
        pbar.update(1)
    pbar.close()
    print(f"缓存清除完成 ({successes}/%s)" % len(cacheFiles))

if __name__=="__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "--help" or sys.argv[1] == "-?":
        print("MPI %s Helps:" % VERSION)
        with open("config.yml", mode="r", encoding="utf-8") as f:
            for i in yaml.load(f, Loader=yaml.SafeLoader)["helps"]: print(i.replace("__file__", __file__).replace("\\t","\t"))
    elif sys.argv[1] == "--version" or sys.argv[1] == "-v":
        SHOW_VERSION()
    elif sys.argv[1] == "--start" or sys.argv[1] == "-s":
        launch()
    elif sys.argv[1] == "--console" or sys.argv[1] == "-c":
        UIConsole()
    elif sys.argv[1] == "--clearcache" or sys.argv[1] == "-cc":
        UIClearcache()