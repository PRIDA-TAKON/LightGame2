import socket
import time

# Configuration
LISTEN_IP = '192.168.1.7' # The IP the game is hardcoded to connect to
LISTEN_PORT = 8234

print(f"--- Advanced Socket Listener ---")
print(f"กำลังรอรับการเชื่อมต่อที่ IP: {LISTEN_IP} (ทุก Network Interface) Port: {LISTEN_PORT}")
print("สคริปต์นี้จะทำงานไปเรื่อยๆ และแสดงข้อมูลทั้งหมดที่ได้รับ")
print("กด Ctrl+C เพื่อหยุดการทำงาน")

# Create and bind the socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((LISTEN_IP, LISTEN_PORT))
server_socket.listen(1)

try:
    while True: # Main loop to accept connections indefinitely
        print("\n--------------------------------------------------")
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] รอรับการเชื่อมต่อจากเกม...")
        
        connection, client_address = server_socket.accept()
        with connection:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ได้รับการเชื่อมต่อจาก: {client_address}")
            print("--- เริ่มการดักฟังข้อมูล ---")
            
            try:
                while True: # Loop to receive all data from this connection
                    # Receive data in chunks
                    data_chunk = connection.recv(1024)
                    if not data_chunk:
                        # Empty data means the client closed the connection
                        print("\n--- Client ปิดการเชื่อมต่อ ---")
                        break

                    decoded_chunk = data_chunk.decode('utf-8', errors='ignore').strip()
                    if decoded_chunk:
                        print(f"ได้รับ: {decoded_chunk}")
            
            except ConnectionResetError:
                print("\n[ERROR] Client ตัดการเชื่อมต่ออย่างกระทันหัน (Connection Reset)")
            except Exception as e:
                print(f"\n[ERROR] เกิดข้อผิดพลาดระหว่างรับข้อมูล: {e}")

except KeyboardInterrupt:
    print("\n\nกำลังปิด Socket Listener...")
finally:
    server_socket.close()
    print("Socket Listener หยุดทำงานแล้ว")