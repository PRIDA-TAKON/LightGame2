import time
from pythonosc import osc_server, udp_client, dispatcher
import threading

# --- Configuration (should match SCORE_test_v2.py) ---
# Config for sending the initial start command
SCORE_PROCESS_IP = '127.0.0.1'
SCORE_PROCESS_PORT = 5555 # Port where SCORE_test_v2.py is listening
OSC_ADDRESS_START_PROCESS = "/profile_id"

# Config for our local server to receive the final result
TEST_RUNNER_LISTEN_IP = '127.0.0.1'
# Port where SCORE_test_v2.py sends the result (must match UI_PROGRAM_OSC_PORT in the other script)
TEST_RUNNER_LISTEN_PORT = 5556 
OSC_ADDRESS_RESULT = "/start_process"

# --- OSC Handler to receive the final result ---
def handle_result(address, *args):
    """Receives the final calculated score from SCORE_test_v2.py"""
    print(f"\n--- ผลลัพธ์สุดท้ายที่ได้รับจาก SCORE_test_v2.py ---")
    print(f"OSC Address: {address}")
    if len(args) >= 3:
        print(f"Score (1=Win, 0=GameOver): {int(args[0])}")
        print(f"Total Time: {args[1]:.2f} วินาที")
        print(f"Average Time Difference: {args[2]:.2f} วินาที")
    else:
        print(f"ได้รับข้อมูลไม่ครบถ้วน: {args}")
    print("-------------------------------------------------")
    print("\nการทดสอบเสร็จสิ้น สามารถปิดสคริปต์นี้ได้ (Ctrl+C)")


# --- Function to send the start signal ---
def send_start_signal():
    """Sends the OSC message to kick off the process in SCORE_test_v2.py"""
    try:
        client = udp_client.SimpleUDPClient(SCORE_PROCESS_IP, SCORE_PROCESS_PORT)
        # Sending a dummy profile ID, as SCORE_test_v2.py expects it
        client.send_message(OSC_ADDRESS_START_PROCESS, 1)
        print(f"[Test Runner] ส่งคำสั่ง '{OSC_ADDRESS_START_PROCESS}' ไปยัง SCORE_test_v2.py ที่ {SCORE_PROCESS_IP}:{SCORE_PROCESS_PORT}")
        print("[Test Runner] SCORE_test_v2.py ควรจะเริ่มรอรับข้อมูลจากเกมที่ Socket port 8234 แล้ว")
    except Exception as e:
        print(f"[Test Runner ERROR] ไม่สามารถส่ง OSC ได้: {e}")
        print("กรุณาตรวจสอบว่า SCORE_test_v2.py กำลังทำงานอยู่")


# --- Main Execution Block ---
if __name__ == "__main__":
    # Setup OSC server to listen for the result
    dispatcher_obj = dispatcher.Dispatcher()
    dispatcher_obj.map(OSC_ADDRESS_RESULT, handle_result)

    server = osc_server.ThreadingOSCUDPServer((TEST_RUNNER_LISTEN_IP, TEST_RUNNER_LISTEN_PORT), dispatcher_obj)
    print(f"[Test Runner] เริ่ม OSC server เพื่อรอรับผลลัพธ์ที่ {TEST_RUNNER_LISTEN_IP}:{TEST_RUNNER_LISTEN_PORT}")
    print(f"[Test Runner] รอรับข้อมูลที่ OSC address: '{OSC_ADDRESS_RESULT}'")
    print("-" * 20)

    # Give the server a moment to start up in the background
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # Send the initial start signal
    time.sleep(1)
    send_start_signal()
    print("\n[Test Runner] ตอนนี้ให้รันตัวจำลองเกม 'light game port 8234' เพื่อส่งข้อมูล...")
    print("[Test Runner] สคริปต์นี้จะรอรับผลลัพธ์อยู่เบื้องหลัง กด Ctrl+C เพื่อออก")

    try:
        # Keep the main thread alive to allow the server thread to run
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Test Runner] กำลังปิดสคริปต์...")
        server.shutdown()
        print("[Test Runner] หยุดทำงานแล้ว")