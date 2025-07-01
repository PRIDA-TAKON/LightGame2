import socket

# Configuration
LISTEN_IP = '192.168.1.7'
LISTEN_PORT = 8234

print(f"--- Socket Listener ---")
print(f"กำลังรอรับข้อมูลที่ {LISTEN_IP}:{LISTEN_PORT}")
print("กรุณารันตัวจำลองเกมของคุณเพื่อส่งข้อมูล...")
print("กด Ctrl+C เพื่อหยุดการทำงาน")

# Create and bind the socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((LISTEN_IP, LISTEN_PORT))
    server_socket.listen(1)

    try:
        # Wait for a connection
        connection, client_address = server_socket.accept()
        with connection:
            print(f"\nได้รับการเชื่อมต่อจาก: {client_address}")
            
            # Receive data
            received_data = connection.recv(4096).decode('utf-8', errors='ignore').strip()
            
            # Print the raw data
            print("--- ข้อมูลดิบที่ได้รับ ---")
            print(received_data)
            print("-------------------------")
            print("\nคัดลอกข้อมูลด้านบนทั้งหมด (ตั้งแต่ --- ข้อมูลดิบที่ได้รับ ---) แล้วส่งให้ Gemini ได้เลยครับ")

    except KeyboardInterrupt:
        print("\nกำลังปิด Socket Listener...")
    except Exception as e:
        print(f"\nเกิดข้อผิดพลาด: {e}")

print("Socket Listener หยุดทำงานแล้ว")
