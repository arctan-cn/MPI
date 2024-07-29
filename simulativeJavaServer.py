import socket  
import threading  
import time  
import random  
import json  
  
def handle_client(conn, addr):  
    print(f"[NEW CONNECTION] {addr} connected.")  
    connected = True  
    verified = False
    clientStack = []
    def sendback(data, code, message={}):
        reply = {
            "uuid": data['uuid'],
            "code": code,
            "message": message
            }
        replyJSON = json.dumps(reply)
        conn.sendall(replyJSON.encode("utf-8"))
    while connected:
        msg = conn.recv(1024).decode("utf-8")  
        try:  
            data = json.loads(msg)
            #uuid = data["uuid"]
            if len(clientStack) < 1 and not verified:
                if "password" in data["message"] and data["message"]["password"] == "ikun520":
                    verified = True
                    sendback(data, 200, "allowed")
                else:
                    sendback(data, 403, "denied")
                    break
            if data["type"]=="disconnect":
                connected = False
                break
            elif data["type"]=="ping":
                sendback(data, 200, {"text":"pong"})
            else:
                sendback(data, 200, {"text":"received at %s" % time.time()})

        except KeyError:  
            conn.sendall(("Error: 'uuid' key not found in JSON.\nRequest: %s" % msg).encode("utf-8"))  
        except json.JSONDecodeError:  
            conn.sendall("Error: Invalid JSON format.".encode("utf-8"))  
        except Exception as e:
            sendback(data, 500, {"exception":str(e)})
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