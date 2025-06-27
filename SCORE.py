import socket
from pythonosc import osc_server, udp_client, dispatcher

# --- 1. Global Configuration ---
# การตั้งค่าสำหรับ Socket Communication (กับโปรแกรมอื่นบนเครื่องเดียวกัน โปรแกรมเล่นเกมปุ่มกดของ FVS)
OTHER_PROGRAM_SOCKET_HOST = '127.0.0.1' # โปรแกรมอยู่บนเครื่องเดียวกัน
OTHER_PROGRAM_SOCKET_PORT = 12345        # Port ที่โปรแกรมเล่นเกมปุ่มกดฟังอยู่
SOCKET_COMMAND_TO_START = "START_CALCULATION" # คำสั่งสำหรับให้โปรแกรมอื่นเริ่มทำงาน

# การตั้งค่าสำหรับ OSC Communication (กับโปรแกรม UI บนเครื่องอื่น ของทีมปิกนิค)
# OSC Server (Python Script จะรับคำสั่งจาก UI ที่ Port นี้)
OSC_LISTEN_IP = '127.0.0.1' # ฟังการเชื่อมต่อจากทุก UI Program โปรแกรมอยู่บนเครื่องเดียวกัน 
OSC_LISTEN_PORT = 5555    # Port ที่ Python script จะรับ OSC เข้ามา เป็น PORT ของสคริปนี้

# OSC Client (Python Script จะส่งผลลัพธ์ไปที่ UI Program บนเครื่องอื่น ของทีมปิกนิค)
UI_PROGRAM_IP = '127.0.0.1' # !!! แก้ไขเป็น IP ของเครื่อง UI Program โปรแกรมอยู่บนเครื่องเดียวกัน !!!
UI_PROGRAM_OSC_PORT = 5556      # Port ที่ UI Program ฟัง OSC อยู่

# OSC Address Pattern ที่ใช้สื่อสาร
OSC_ADDRESS_START_PROCESS = "/profile_id" # UI จะส่งคำสั่งมาที่ address นี้
OSC_ADDRESS_RESULT = "/start_process"   # Python script จะส่งผลลัพธ์กลับไปที่ address นี้

# --- 2. Function for Socket Communication (กับโปรแกรมเกมปุ่มกดของ FVS) ---
def communicate_with_other_program(command):
    """
    เชื่อมต่อไปยังโปรแกรมอื่นผ่าน Socket, ส่งคำสั่ง, และรับค่ากลับมา
    """
    print(f"\n[Socket] กำลังเชื่อมต่อไปยังโปรแกรมอื่นที่ {OTHER_PROGRAM_SOCKET_HOST}:{OTHER_PROGRAM_SOCKET_PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((OTHER_PROGRAM_SOCKET_HOST, OTHER_PROGRAM_SOCKET_PORT))
            print("[Socket] เชื่อมต่อสำเร็จ")

            # ส่งคำสั่ง
            client_socket.sendall(command.encode('utf-8'))
            print(f"[Socket] ส่งคำสั่ง: '{command}'")

            # รับข้อมูลที่ส่งกลับมา
            received_data = b""
            while True:
                chunk = client_socket.recv(4096)
                if not chunk: # Server ปิดการเชื่อมต่อ
                    break
                received_data += chunk
            
            decoded_data = received_data.decode('utf-8').strip()
            print(f"[Socket] ได้รับข้อมูล: '{decoded_data}'")
            return decoded_data

        except ConnectionRefusedError:
            print(f"[Socket ERROR] ไม่สามารถเชื่อมต่อได้: Server ที่ {OTHER_PROGRAM_SOCKET_HOST}:{OTHER_PROGRAM_SOCKET_PORT} ไม่ทำงาน")
            return None
        except Exception as e:
            print(f"[Socket ERROR] เกิดข้อผิดพลาดในการสื่อสาร Socket: {e}")
            return None

# --- 3. Function for Data Calculation ---
def perform_calculation(data_string):
    
    #รับข้อมูลสตริงมาคำนวณและส่งคืนผลลัพธ์
    #จะต้องปรับแก้ส่วนนี้ให้เหมาะสมกับรูปแบบข้อมูลที่ได้รับ
    
    print(f"\n[Calculation] กำลังประมวลผลข้อมูล: '{data_string}'")
              
    A1 = 5.0 # สัมประสิทธิ์สำหรับ correct_hits_1
    A2 = 4.0 # สัมประสิทธิ์สำหรับ correct_hits_2
    A3 = 3.0 # สัมประสิทธิ์สำหรับ correct_hits_3
    incorrect_hits_1 = 4 # ตัวอย่างค่าที่ได้จากโปรแกรมเกม รอเชคจาก FVS
    stage_duration_sec_1 = 10.0 # ตัวอย่างค่าที่ได้จากโปรแกรมเกม รอเชคจาก FVS
    incorrect_hits_2 = 2 # ตัวอย่างค่าที่ได้จากโปรแกรมเกม รอเชคจาก FVS
    stage_duration_sec_2 = 5.0 # ตัวอย่างค่าที่ได้จากโปรแกรมเกม รอเชคจาก FVS
    incorrect_hits_3 = 1 # ตัวอย่างค่าที่ได้จากโปรแกรมเกม รอเชคจาก FVS
    stage_duration_sec_3 = 3.0 # ตัวอย่างค่าที่ได้จากโปรแกรมเกม รอเชคจาก FVS
    # คำนวณผลลัพธ์ตามสูตรที่กำหนด
    """        
    incorrect_hits_1 = raw_data.get("incorrect_hits_1", 0)
    stage_duration_sec_1 = raw_data.get("stage_duration_sec_1", 0.0)

    incorrect_hits_2 = raw_data.get("incorrect_hits_2", 0)
    stage_duration_sec_2 = raw_data.get("stage_duration_sec_2", 0.0)

    incorrect_hits_3 = raw_data.get("incorrect_hits_3", 0)
    stage_duration_sec_3 = raw_data.get("stage_duration_sec_3", 0.0)
    """

    score_1 = incorrect_hits_1*A1 + stage_duration_sec_1
    score_2 = incorrect_hits_2*A2 + stage_duration_sec_2
    score_3 = incorrect_hits_3*A3 + stage_duration_sec_3


    score = score_1 + score_2 + score_3
    total_time = stage_duration_sec_1 + stage_duration_sec_2 + stage_duration_sec_3
    
    calculated_result_score = score # ตัวอย่างการคำนวณคะแนน
    calculated_result_time = total_time  # ตัวอย่างการคำนวณเวลา 
    print(f"[Calculation] ผลลัพธ์: {calculated_result_score,calculated_result_time }")
    # ส่งคืนผลลัพธ์เป็นสตริงเดียว เช่น "3.0,18.0"
    result_str = f"{calculated_result_score},{calculated_result_time}"
    return result_str  # ส่งคืนผลลัพธ์ที่คำนวณได้เป็นสตริง
    

# --- 4. Function for OSC Communication (ส่งผลลัพธ์กลับ UI) ---
def send_osc_result(result):
    """
    ส่งผลลัพธ์ที่คำนวณได้กลับไปยัง UI Program ผ่าน OSC
    """
    try:
        osc_client = udp_client.SimpleUDPClient(UI_PROGRAM_IP, UI_PROGRAM_OSC_PORT)
        osc_client.send_message(OSC_ADDRESS_RESULT, result)
        print(f"\n[OSC Client] ส่งผลลัพธ์ (string) '{result}' ไปยัง UI ที่ {UI_PROGRAM_IP}:{UI_PROGRAM_OSC_PORT} ผ่าน address '{OSC_ADDRESS_RESULT}'")
    except Exception as e:
        print(f"[OSC Client ERROR] ไม่สามารถส่งข้อความ OSC ได้: {e}")

# --- 5. OSC Server Handler (รับคำสั่งจาก UI) ---
def handle_start_process(address, *args):
    """
    ฟังก์ชันนี้จะถูกเรียกเมื่อได้รับข้อความ OSC ที่ /start_process
    """
    print(f"\n[OSC Server] ได้รับคำสั่ง OSC จาก UI ที่ {address} พร้อม args: {args}")

    # 1. สั่งโปรแกรมอื่นทำงานและรับค่า
    received_data_from_other_program = communicate_with_other_program(SOCKET_COMMAND_TO_START)

    if received_data_from_other_program is not None:
        # 2. นำค่าที่ได้มาคำนวณต่อ
        final_calculated_value = perform_calculation(received_data_from_other_program)

        if final_calculated_value is not None:
            # 3. ส่งผลลัพธ์กลับไปยัง UI
            send_osc_result(final_calculated_value)
        else:
            print("[Main Flow] การคำนวณล้มเหลว ไม่สามารถส่งผลลัพธ์ได้")
    else:
        print("[Main Flow] ไม่ได้รับข้อมูลจากโปรแกรมอื่น ไม่สามารถดำเนินการต่อได้")

# --- Main Execution Block ---
if __name__ == "__main__":
    # ตั้งค่า OSC Dispatcher (กำหนดว่า OSC address ไหนจะเรียกฟังก์ชันอะไร)
    dispatcher_obj = dispatcher.Dispatcher()
    dispatcher_obj.map(OSC_ADDRESS_START_PROCESS, handle_start_process)

    # สร้าง OSC Server
    server = osc_server.ThreadingOSCUDPServer((OSC_LISTEN_IP, OSC_LISTEN_PORT), dispatcher_obj)
    print(f"กำลังเริ่มต้น OSC Server ที่ {OSC_LISTEN_IP}:{OSC_LISTEN_PORT}")
    print(f"รอรับคำสั่ง OSC จาก UI ที่ address: '{OSC_ADDRESS_START_PROCESS}'")
    print("กด Ctrl+C เพื่อหยุด Server\n")

    try:
        server.serve_forever() # เริ่มต้น Server และรอรับการเชื่อมต่อตลอดไป
    except KeyboardInterrupt:
        print("\nOSC Server กำลังหยุดทำงาน...")
        server.shutdown()
        print("OSC Server หยุดทำงานแล้ว")











"""
# --- กำหนดค่าคงที่ (Constants) ---ส่วนคิดคะแนน
SCORE_FILE_PATH = "C:\\Users\\SGVT\\OneDrive\\เดสก์ท็อป\\LightGame2\\LightGame2\\raw_score.json"

try:

    if not os.path.exists(SCORE_FILE_PATH):
        print(f"Error: File not found at {SCORE_FILE_PATH}")
        exit()

    with open(SCORE_FILE_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
except Exception as e:
    print(f"An error occurred: {e}")
    exit()

A1 = 5.0 # สัมประสิทธิ์สำหรับ correct_hits_1
A2 = 4.0 # สัมประสิทธิ์สำหรับ correct_hits_2
A3 = 3.0 # สัมประสิทธิ์สำหรับ correct_hits_3



incorrect_hits_1 = raw_data.get("incorrect_hits_1", 0)
stage_duration_sec_1 = raw_data.get("stage_duration_sec_1", 0.0)

incorrect_hits_2 = raw_data.get("incorrect_hits_2", 0)
stage_duration_sec_2 = raw_data.get("stage_duration_sec_2", 0.0)

incorrect_hits_3 = raw_data.get("incorrect_hits_3", 0)
stage_duration_sec_3 = raw_data.get("stage_duration_sec_3", 0.0)

score_1 = incorrect_hits_1*A1 + stage_duration_sec_1
score_2 = incorrect_hits_2*A2 + stage_duration_sec_2
score_3 = incorrect_hits_3*A3 + stage_duration_sec_3

score = score_1 + score_2 + score_3
print(score)

"""
