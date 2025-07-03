import socket
import time
from pythonosc import osc_server, udp_client, dispatcher
import re
import threading

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
GAME_SERVER_IP = '192.168.8.94'  # Replace with actual game server IP
GAME_SERVER_PORT = 8234

# Global socket variable for persistent connection
game_socket = None

# Event to signal the game data listener to start processing a new game session
start_new_game_event = threading.Event()

# --- 2. Function to Listen for Game Data Continuously ---
def listen_for_game_data_continuously():
    global game_socket
    full_data_stream = ""
    termination_keywords = ["Game Over", "You are winer", "Game Stop"]
    session_id = 0

    while True:
        # Wait for the signal to start a new game session
        start_new_game_event.wait()
        start_new_game_event.clear() # Clear the event for the next signal

        session_id += 1
        print(f"\n[Game Client] เริ่มดักฟังข้อมูลสำหรับเกมรอบที่ {session_id}...")
        full_data_stream = "" # Reset data for new session
        game_in_progress = False # State to track if we're accumulating data for a game

        try:
            while True:
                # Use a short timeout to allow checking the event, but still receive data
                game_socket.settimeout(0.1) 
                try:
                    data_chunk = game_socket.recv(1024).decode('utf-8', errors='ignore')
                except socket.timeout:
                    # If no data for a short period, check if we should stop this session
                    if not game_in_progress and not start_new_game_event.is_set():
                        # If no game is in progress and no new game signal, continue waiting for data
                        continue
                    elif start_new_game_event.is_set():
                        # If a new game signal is set, break from this inner loop to restart session
                        break
                    else:
                        # If game is in progress, continue waiting for data
                        continue

                if not data_chunk:
                    print("[Game Client] การเชื่อมต่อถูกปิดโดยเกม (Socket Closed)")
                    # Attempt to re-establish connection if closed
                    connect_to_game_server()
                    break # Break from inner loop to restart session listening
                
                print(f"[Game Client] ได้รับ: {data_chunk.strip()}")

                # Accumulate all data received
                full_data_stream += data_chunk + "\n"
                game_in_progress = True # Once data starts flowing, assume game is in progress

                # Check if the game session has ended
                if any(keyword in full_data_stream for keyword in termination_keywords):
                    print(f"[Game Client] ตรวจพบสัญญาณจบเกมสำหรับรอบที่ {session_id}!")
                    # Process the collected data
                    final_calculated_value = perform_calculation(full_data_stream.strip())
                    send_osc_result(final_calculated_value)
                    print(f"\n[Game Client] จบการดักฟังข้อมูลสำหรับรอบที่ {session_id}. รอคำสั่ง OSC ถัดไป...")
                    break # Break from inner loop to wait for next game signal

        except Exception as e:
            print(f"[Game Client ERROR] เกิดข้อผิดพลาดระหว่างดักฟังข้อมูล: {e}")
            # Attempt to re-establish connection if an error occurs
            connect_to_game_server()

# --- Function to Connect to Game Server (Persistent) ---
def connect_to_game_server():
    global game_socket
    if game_socket:
        try:
            game_socket.close()
            print("[Game Client] ปิดการเชื่อมต่อเก่าแล้ว")
        except Exception as e:
            print(f"[Game Client ERROR] ไม่สามารถปิด socket เก่าได้: {e}")

    while True:
        try:
            print(f"\n[Game Client] พยายามเชื่อมต่อกับเกมที่ {GAME_SERVER_IP}:{GAME_SERVER_PORT}...")
            game_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            game_socket.settimeout(15)  # Timeout for initial connection
            game_socket.connect((GAME_SERVER_IP, GAME_SERVER_PORT))
            print("[Game Client] เชื่อมต่อสำเร็จ!\n")
            game_socket.settimeout(None) # Remove timeout for continuous listening
            break
        except socket.timeout:
            print(f"[Game Client ERROR] การเชื่อมต่อหมดเวลา (ไม่สามารถเชื่อมต่อได้ภายใน 15 วินาที). ลองใหม่ใน 5 วินาที...")
            time.sleep(5)
        except ConnectionRefusedError:
            print("[Game Client ERROR] การเชื่อมต่อถูกปฏิเสธ (ตรวจสอบว่าเกมโหมด Server ทำงานอยู่). ลองใหม่ใน 5 วินาที...")
            time.sleep(5)
        except Exception as e:
            print(f"[Game Client ERROR] เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}. ลองใหม่ใน 5 วินาที...")
            time.sleep(5)

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
    result_str = f"{calculated_result_score},{total_time:.2f}"
    return result_str

# --- 4. Function for OSC Communication (Send result to UI) ---
def send_osc_result(result):
    """
    Sends the calculated result string back to the UI program via OSC.
    """
    try:
        osc_client = udp_client.SimpleUDPClient(UI_PROGRAM_IP, UI_PROGRAM_OSC_PORT)
        # ส่งผลลัพธ์เป็น String ตามที่ UI ต้องการ (เหมือนใน SCORE_test.py)
        osc_client.send_message(OSC_ADDRESS_RESULT, result)
        print(f"\n[OSC Client] ส่งผลลัพธ์ '{result}' ไปยัง UI ที่ {UI_PROGRAM_IP}:{UI_PROGRAM_OSC_PORT}")
    except Exception as e:
        print(f"[OSC Client ERROR] ไม่สามารถส่งข้อความ OSC ได้: {e}")

# --- 5. OSC Server Handler (Receives command from UI) ---
def handle_start_process(address, *args):
    """
    This function is the main trigger, called by an OSC message from the UI.
    It signals the game data listener to start processing a new game session.
    """
    print(f"\n[OSC Server] ได้รับคำสั่งจาก UI ที่ {address} พร้อม args: {args}")
    print("[Main] ส่งสัญญาณให้เริ่มกระบวนการดึงข้อมูลจากเกมรอบใหม่...")
    start_new_game_event.set() # Signal the listener thread to start

# --- Main Execution Block ---
if __name__ == "__main__":
    # 1. Connect to the game server persistently
    connect_to_game_server()

    # 2. Start a separate thread to continuously listen for game data
    game_listener_thread = threading.Thread(target=listen_for_game_data_continuously, daemon=True)
    game_listener_thread.start()

    # 3. Setup OSC server to listen for UI commands
    dispatcher_obj = dispatcher.Dispatcher()
    dispatcher_obj.map(OSC_ADDRESS_START_PROCESS, handle_start_process)
    
    server = osc_server.ThreadingOSCUDPServer((OSC_LISTEN_IP, OSC_LISTEN_PORT), dispatcher_obj)
    
    print(f"--- SCORE Processor v4 (Client Mode with Persistent Connection) ---")
    print(f"กำลังเริ่มต้น OSC Server ที่ {OSC_LISTEN_IP}:{OSC_LISTEN_PORT}")
    print(f"รอรับคำสั่ง OSC จาก UI ที่ address: '{OSC_ADDRESS_START_PROCESS}'")
    print("เมื่อได้รับคำสั่ง จะเริ่มดักฟังข้อมูลเกมสำหรับรอบใหม่")
    print("กด Ctrl+C เพื่อหยุด Server\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nOSC Server กำลังหยุดทำงาน...")
        server.shutdown()
        print("OSC Server หยุดทำงานแล้ว")
    finally:
        if game_socket:
            game_socket.close()
            print("ปิดการเชื่อมต่อเกมแล้ว")
