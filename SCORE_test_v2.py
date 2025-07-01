import socket
import time
from pythonosc import osc_server, udp_client, dispatcher
import re

# --- 1. Global Configuration ---
# OSC server to listen for commands from UI
OSC_LISTEN_IP = '127.0.0.1'
OSC_LISTEN_PORT = 5555
OSC_ADDRESS_START_PROCESS = "/profile_id"

# OSC client to send results back to UI
UI_PROGRAM_IP = '127.0.0.1'
UI_PROGRAM_OSC_PORT = 5556
OSC_ADDRESS_RESULT = "/start_process"

# Game (which is a Server) connection settings
GAME_SERVER_IP = '192.168.1.7'
GAME_SERVER_PORT = 8234

# --- 2. Function to Connect to Game and Get Data ---
def connect_and_get_game_data():
    """
    Connects to the game server, listens for the entire data stream until a
    termination keyword is found, and returns the full data.
    """
    print(f"\n[Game Client] พยายามเชื่อมต่อกับเกมที่ {GAME_SERVER_IP}:{GAME_SERVER_PORT}...")
    full_data_stream = ""
    termination_keywords = ["Game Over", "You are winer", "Game Stop"]

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(15)  # Timeout for initial connection
            sock.connect((GAME_SERVER_IP, GAME_SERVER_PORT))
            print("[Game Client] เชื่อมต่อสำเร็จ! เริ่มดักฟังข้อมูล...")
            sock.settimeout(None)  # No timeout while listening

            while True:
                data_chunk = sock.recv(1024).decode('utf-8', errors='ignore')
                if not data_chunk:
                    print("[Game Client] การเชื่อมต่อถูกปิดโดยเกม")
                    break
                
                print(f"[Game Client] ได้รับ: {data_chunk.strip()}")
                full_data_stream += data_chunk + "\n"

                # Check if the game session has ended
                if any(keyword in full_data_stream for keyword in termination_keywords):
                    print("[Game Client] ตรวจพบสัญญาณจบเกม!")
                    time.sleep(0.5) # Wait for any final data
                    try:
                        sock.settimeout(0.5)
                        final_chunk = sock.recv(1024).decode('utf-8', 'ignore')
                        full_data_stream += final_chunk + "\n"
                    except socket.timeout:
                        pass # No more data, which is fine
                    break
        
        print("\n[Game Client] รวบรวมข้อมูลทั้งหมดสำเร็จ")
        return full_data_stream.strip()

    except socket.timeout:
        print(f"[Game Client ERROR] ไม่สามารถเชื่อมต่อได้ภายใน 15 วินาที")
        return None
    except ConnectionRefusedError:
        print("[Game Client ERROR] การเชื่อมต่อถูกปฏิเสธ (ตรวจสอบว่าเกมโหมด Server ทำงานอยู่)")
        return None
    except Exception as e:
        print(f"[Game Client ERROR] เกิดข้อผิดพลาด: {e}")
        return None

# --- 3. Function for Data Calculation ---
def perform_calculation(data_string):
    """
    Parses the full data stream from the game and calculates the score.
    """
    print(f"\n[Calculation] กำลังประมวลผลข้อมูล...")
    
    # 1. Determine game status (Win/Loss)
    if "You are winer" in data_string:
        calculated_result_score = 1
    elif "Game Over" in data_string:
        calculated_result_score = 0
    else:
        calculated_result_score = -1  # Unknown status

    # 2. Extract Total Time
    total_time_match = re.search(r"Total Time = ([\d.]+)", data_string)
    total_time = float(total_time_match.group(1)) if total_time_match else 0.0

    # 3. Extract all button press times
    button_times = [float(t) for t in re.findall(r"Time=([\d.]+)", data_string)]
    
    # 4. Calculate the average of the time differences
    average_difference = 0.0
    if len(button_times) > 1:
        differences = [abs(button_times[i] - button_times[i-1]) for i in range(1, len(button_times))]
        if differences:
            average_difference = sum(differences) / len(differences)

    print(f"[Calculation] ผลลัพธ์: Score={calculated_result_score}, TotalTime={total_time:.2f}, AvgDifference={average_difference:.2f}")
    
    # Return the result as a comma-separated string
    result_str = f"{calculated_result_score},{total_time:.2f},{average_difference:.2f}"
    return result_str

# --- 4. Function for OSC Communication (Send result to UI) ---
def send_osc_result(result):
    """
    Sends the calculated result string back to the UI program via OSC.
    """
    try:
        osc_client = udp_client.SimpleUDPClient(UI_PROGRAM_IP, UI_PROGRAM_OSC_PORT)
        args_to_send = [float(x) for x in result.split(',')]
        osc_client.send_message(OSC_ADDRESS_RESULT, args_to_send)
        print(f"\n[OSC Client] ส่งผลลัพธ์ {args_to_send} ไปยัง UI ที่ {UI_PROGRAM_IP}:{UI_PROGRAM_OSC_PORT}")
    except Exception as e:
        print(f"[OSC Client ERROR] ไม่สามารถส่งข้อความ OSC ได้: {e}")

# --- 5. OSC Server Handler (Receives command from UI) ---
def handle_start_process(address, *args):
    """
    This function is the main trigger, called by an OSC message from the UI.
    """
    print(f"\n[OSC Server] ได้รับคำสั่งจาก UI ที่ {address} พร้อม args: {args}")
    print("[Main] เริ่มกระบวนการดึงข้อมูลจากเกม...")
    
    game_result_data = connect_and_get_game_data()
    
    if game_result_data:
        final_calculated_value = perform_calculation(game_result_data)
        send_osc_result(final_calculated_value)
    else:
        print("[Main] ไม่ได้รับข้อมูลจากเกม จะไม่ส่งข้อมูลไปที่ UI")

# --- Main Execution Block ---
if __name__ == "__main__":
    dispatcher_obj = dispatcher.Dispatcher()
    dispatcher_obj.map(OSC_ADDRESS_START_PROCESS, handle_start_process)
    
    server = osc_server.ThreadingOSCUDPServer((OSC_LISTEN_IP, OSC_LISTEN_PORT), dispatcher_obj)
    
    print(f"--- SCORE Processor v3 (Client Mode) ---")
    print(f"กำลังเริ่มต้น OSC Server ที่ {OSC_LISTEN_IP}:{OSC_LISTEN_PORT}")
    print(f"รอรับคำสั่ง OSC จาก UI ที่ address: '{OSC_ADDRESS_START_PROCESS}'")
    print("เมื่อได้รับคำสั่ง จะเชื่อมต่อกับเกมเพื่อดึงข้อมูลคะแนน")
    print("กด Ctrl+C เพื่อหยุด Server\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nOSC Server กำลังหยุดทำงาน...")
        server.shutdown()
        print("OSC Server หยุดทำงานแล้ว")