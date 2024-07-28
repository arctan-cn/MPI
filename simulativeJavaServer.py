import socket  
import threading  
import time  
import random  
import json  
  
def handle_client(conn, addr):  
    print(f"[NEW CONNECTION] {addr} connected.")  
    connected = True  
    while connected:  
        msg = conn.recv(1024).decode("utf-8")  
        try:  
            data = json.loads(msg)  # 解析JSON字符串  
            uuid = data["uuid"]  # 获取uuid键对应的值  
            reply = {"uuid": uuid, "code":200, "message": {"message": "Reveived."}}  # 构造回复的JSON数据  
            reply_msg = json.dumps(reply)  # 将回复数据转换为JSON字符串  
            # time.sleep(random.random())
            conn.sendall(reply_msg.encode("utf-8"))  # 发送回复  
            if data["type"]=="disconnect": connected = False
        except KeyError:  
            conn.sendall("Error: 'uuid' key not found in JSON.".encode("utf-8"))  
        except json.JSONDecodeError:  
            conn.sendall("Error: Invalid JSON format.".encode("utf-8"))  
        # 如果需要，可以在这里添加随机等待时间  
        # time.sleep(random.random() * 5)  
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