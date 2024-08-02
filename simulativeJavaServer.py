import socket  
import threading  
import time  
import random  
import json  

PASSWORD = "ikun520"

def requestAnalyzerThread(client, request):
    def sendback(code, message={}):
        reply = {
            "uuid": request['uuid'],
            "code": code,
            "message": message
            }
        replyJSON = json.dumps(reply)
        client.sendall(replyJSON.encode("utf-8"))
    if type(request) != dict or not ("uuid", "type", "args", "kwargs" in request)[-1]: sendback(400, "Bad Request")
    if request['type'] == 'ping':
        sendback(200, "Pong at %s" % time.time())
    elif request['type'] == 'command':
        sendback(200, "Command executed")
    pass
def handle_client(conn, addr):  
    print(f"[NEW CONNECTION] {addr} connected.")  
    connected = True  
    verified = False
    clientStack = []
    def sendback(code, message={}, data=[]):
        if not data: data = [{"uuid":'ffffffff-ffff-ffff-ffff-ffffffffffff'}]
        reply = {
            "uuid": data[0]['uuid'],
            "code": code,
            "message": message
            }
        replyJSON = json.dumps(reply)
        conn.sendall(replyJSON.encode("utf-8"))
    while connected:
        try:
            msg = conn.recv(1024).decode("utf-8")  
        except Exception as e:
            print(e)
            break
        try:  
            data = json.loads(msg)
            print(data)
            if type(data) != list or len(data)==0:
                sendback(400, "Empty request")
                break
            elif len(data) == 1 and data[0]['type']=="disconnect":
                sendback(200, "Disconnected", data)
                break
            elif (not verified) and len(data) == 1 and data[0]['type']=="login":
                if data[0]['args'][0] == PASSWORD:
                    sendback(200, 'Connection verification successful', data)
                    verified = True
                    continue
                else:
                    sendback(403, 'Connection verification failed', data)
                    connected = False
                    break
            elif not verified:
                sendback(403, 'Connection not verified', data)
                break
            analyzingThreads = []
            for request in data: 
                analyzingThreads.append(threading.Thread(target=requestAnalyzerThread, args=(conn, request)))
                analyzingThreads[-1].start()
        except KeyError:  
            conn.sendall(("Error: 'uuid' key not found in JSON.\nRequest: %s" % msg).encode("utf-8"))  
        except json.JSONDecodeError:  
            conn.sendall("Error: Invalid JSON format.".encode("utf-8"))  
        except Exception as e:
            sendback(500, {"exception":str(e)})
            break
    conn.close()  
  
def start_server():  
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    server.bind(("127.0.0.1", 9201))  
    server.listen()  
    print("[LISTENING] Server is listening on 127.0.0.1 :9201")  
    while True:  
        conn, addr = server.accept()  
        thread = threading.Thread(target=handle_client, args=(conn, addr))  
        thread.start()  
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")  
print("Server is starting...")  
start_server()