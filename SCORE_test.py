import socket
import time
from pythonosc import osc_server, udp_client, dispatcher
from random import randint
import re

# --- 1. Global Configuration ---
# การตั้งค่าสำหรับ Socket Server (สคริปต์นี้จะรอรับข้อมูลจากเกมที่ Port นี้)
SOCKET_LISTEN_IP = '192.168.8.94'  # รอรับการเชื่อมต่อจากตัวเกม
SOCKET_LISTEN_PORT = 8234       # Port ที่จะเปิดรอให้เกมเชื่อมต่อเข้ามา

# การตั้งค่าสำหรับ OSC Communication (กับโปรแกรม UI)
OSC_LISTEN_IP = '127.0.0.1'
OSC_LISTEN_PORT = 5555
UI_PROGRAM_IP = '127.0.0.1'
UI_PROGRAM_OSC_PORT = 5556
OSC_ADDRESS_START_PROCESS = "/profile_id"
OSC_ADDRESS_RESULT = "/start_process"

# --- 2. Function to Listen for Game Result via Socket ---
def listen_for_game_result():
    """
    เปิด Server Socket เพื่อรอรับการเชื่อมต่อและข้อมูลผลลัพธ์จากเกม
    """
    print(f"\n[Socket Server] เริ่มรอรับการเชื่อมต่อที่ {SOCKET_LISTEN_IP}:{SOCKET_LISTEN_PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((SOCKET_LISTEN_IP, SOCKET_LISTEN_PORT))
        server_socket.listen(1)
        print("[Socket Server] รอเกมเชื่อมต่อและส่งผลลัพธ์...")
        
        try:
            connection, client_address = server_socket.accept()
            with connection:
                print(f"[Socket Server] ได้รับการเชื่อมต่อจาก {client_address}")
                received_data = b""
                while True:
                    chunk = connection.recv(1024)
                    if not chunk:
                        break
                    received_data += chunk
                
                decoded_data = received_data.decode('utf-8').strip()
                print(f"[Socket Server] ได้รับข้อมูล: '{decoded_data}'")
                return decoded_data
        except Exception as e:
            print(f"[Socket Server ERROR] เกิดข้อผิดพลาด: {e}")
            return None

# --- 3. Function for Data Calculation ---
def perform_calculation(data_string):
    """
    ดึงข้อมูลเวลาจากสตริงและคำนวณคะแนน (ยังใช้ค่าสุ่มสำหรับคะแนน)
    """
    print(f"\n[Calculation] กำลังประมวลผลข้อมูล: '{data_string}'")
    match = re.search(r"Total Time:\s*(\d+\.\d+)", data_string)
    
    if match:
        calculated_result_time = float(match.group(1))
        calculated_result_score = randint(49, 100) # คะแนนยังคงเป็นการสุ่ม
    else:
        print(f"[Calculation ERROR] ไม่พบ 'Total Time: X.X' ในข้อมูล: '{data_string}'")
        calculated_result_score = 0
        calculated_result_time = 0.0
    
    print(f"[Calculation] ผลลัพธ์: Score={calculated_result_score}, Time={calculated_result_time}")
    result_str = f"{calculated_result_score},{calculated_result_time}"
    return result_str

# --- 4. Function for OSC Communication (ส่งผลลัพธ์กลับ UI) ---
def send_osc_result(result):
    """
    ส่งผลลัพธ์กลับไปยัง UI Program ผ่าน OSC
    """
    try:
        osc_client = udp_client.SimpleUDPClient(UI_PROGRAM_IP, UI_PROGRAM_OSC_PORT)
        osc_client.send_message(OSC_ADDRESS_RESULT, result)
        print(f"\n[OSC Client] ส่งผลลัพธ์ '{result}' ไปยัง UI ที่ {UI_PROGRAM_IP}:{UI_PROGRAM_OSC_PORT}")
    except Exception as e:
        print(f"[OSC Client ERROR] ไม่สามารถส่งข้อความ OSC ได้: {e}")

# --- 5. OSC Server Handler (รับคำสั่งจาก UI) ---
def handle_start_process(address, *args):
    """
    เมื่อได้รับคำสั่งจาก UI จะเริ่มรอรับข้อมูลจากเกม
    """
    print(f"\n[OSC Server] ได้รับคำสั่งจาก UI ที่ {address} พร้อม args: {args}")
    print("[Main] เริ่มรอรับข้อมูลผลลัพธ์จากเกมผ่าน Socket...")

    # 1. รอรับข้อมูลจากเกม
    game_result_data = listen_for_game_result()

    if game_result_data:
        # 2. คำนวณคะแนนจากข้อมูลที่ได้รับ
        final_calculated_value = perform_calculation(game_result_data)

        # 3. รอ 10 วินาที (ตามโค้ดเดิม)
        print("รอ 10 วินาทีก่อนส่งคะแนน...")
        time.sleep(10)

        # 4. ส่งผลลัพธ์กลับไปยัง UI
        send_osc_result(final_calculated_value)
    else:
        print("[Main] ไม่ได้รับข้อมูลจาก Socket จะไม่ส่งข้อมูลไปที่ UI")

# --- Main Execution Block ---
if __name__ == "__main__":
    dispatcher_obj = dispatcher.Dispatcher()
    dispatcher_obj.map(OSC_ADDRESS_START_PROCESS, handle_start_process)

    server = osc_server.ThreadingOSCUDPServer((OSC_LISTEN_IP, OSC_LISTEN_PORT), dispatcher_obj)
    print(f"กำลังเริ่มต้น OSC Server ที่ {OSC_LISTEN_IP}:{OSC_LISTEN_PORT}")
    print(f"รอรับคำสั่ง OSC จาก UI ที่ address: '{OSC_ADDRESS_START_PROCESS}'")
    print("กด Ctrl+C เพื่อหยุด Server\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nOSC Server กำลังหยุดทำงาน...")
        server.shutdown()
        print("OSC Server หยุดทำงานแล้ว")
