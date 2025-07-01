import socket
import time

# --- Configuration ---
GAME_SERVER_IP = '192.168.1.7'
GAME_SERVER_PORT = 8234
BUFFER_SIZE = 1024  # How much data to receive at a time

# Keywords that signal the end of a game session
TERMINATION_KEYWORDS = ["Game Over", "You are winer", "Game Stop", ":RY1Trig"]

print("--- Game Data Client (Continuous Listener) ---")
print(f"เป้าหมาย: IP {GAME_SERVER_IP} Port {GAME_SERVER_PORT}")
print("\nคำแนะนำ:")
print("1. เปิดเกมและตั้งค่าเป็นโหมด Server (IP 192.168.1.7, Port 8234)")
print("2. กดปุ่ม Connect/Start ในเกมเพื่อให้เกมเริ่มรอรับการเชื่อมต่อ")
print("3. รันสคริปต์นี้... มันจะเชื่อมต่อและเริ่มดักฟัง")
print("4. กลับไปเล่นเกมตั้งแต่ต้นจนจบ")
print("5. สคริปต์จะรวบรวมข้อมูลทั้งหมดและแสดงผลเมื่อเกมจบ")
print("-" * 30)

full_data_stream = ""

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(15) # Timeout for initial connection
        print("\nกำลังพยายามเชื่อมต่อกับเกม...")
        sock.connect((GAME_SERVER_IP, GAME_SERVER_PORT))
        print("เชื่อมต่อสำเร็จ! เริ่มโหมดดักฟังต่อเนื่อง...")
        print("กรุณาเริ่มเล่นเกมได้เลย")
        sock.settimeout(None) # Remove timeout for listening

        # Loop to continuously receive data
        while True:
            try:
                # Wait and receive a chunk of data
                data_chunk = sock.recv(BUFFER_SIZE).decode('utf-8', errors='ignore')
                
                if not data_chunk:
                    # Connection closed by the game server
                    print("\n[INFO] การเชื่อมต่อถูกปิดโดยเกม (อาจจะปิดโปรแกรมเกมไปแล้ว)")
                    break

                print(f"ได้รับข้อมูล: {data_chunk.strip()}")
                full_data_stream += data_chunk + "\n" # Append new data

                # Check if any termination keyword is in the received chunk
                if any(keyword in full_data_stream for keyword in TERMINATION_KEYWORDS):
                    print("\n[INFO] ตรวจพบสัญญาณจบเกม!")
                    # Wait a tiny moment to catch any final straggling data
                    time.sleep(0.5)
                    try:
                        # Try to receive one last time with a short timeout
                        sock.settimeout(0.5)
                        final_chunk = sock.recv(BUFFER_SIZE).decode('utf-8', errors='ignore')
                        if final_chunk:
                            print(f"ได้รับข้อมูลสุดท้าย: {final_chunk.strip()}")
                            full_data_stream += final_chunk + "\n"
                    except socket.timeout:
                        # This is expected if there's no more data
                        pass
                    break # Exit the listening loop

            except socket.timeout:
                print("\n[INFO] หยุดรอข้อมูลเนื่องจากไม่มีข้อมูลเข้ามาเลย")
                break
            except ConnectionResetError:
                print("\n[ERROR] การเชื่อมต่อถูกตัดโดยเกม (Connection Reset)")
                break

except socket.timeout:
    print(f"\n[ERROR] ไม่สามารถเชื่อมต่อกับเกมได้ภายใน 15 วินาที")
    print("  - ตรวจสอบว่าเกมทำงานในโหมด Server และกด Connect แล้ว")
except ConnectionRefusedError:
    print("\n[ERROR] การเชื่อมต่อถูกปฏิเสธ (Connection Refused)")
    print("  - ตรวจสอบให้แน่ใจว่าเกมทำงานในโหมด Server แล้วจริงๆ")
except Exception as e:
    print(f"\n[ERROR] เกิดข้อผิดพลาดที่ไม่คาดคิด: {e}")

finally:
    print("\n--- ข้อมูลทั้งหมดที่รวบรวมได้ ---")
    print(full_data_stream.strip())
    print("----------------------------------")
    print("สคริปต์ทำงานเสร็จสิ้น")
