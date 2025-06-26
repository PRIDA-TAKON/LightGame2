# LightGame2
เกมสำหรับใช้กับเครื่องเล่นปุ่มกด สำหรับโครงการฟิวเจอเรียม
สคริปทำงานเองเมื่อเปิดเครื่อง

+-------------------+                          +---------------------+
|    UI Program     |                          |   Other Program     |
|   (Remote Machine)| <--- OSC Message ------> |   (Local Machine)   |
|   (OSC Client)    |                          |   (Socket Server)   |
+-------------------+                          +----------^----------+
         |                                               |
         | (OSC Command)                                 | (Socket Data)
         V                                               |
+-----------------------------------------------------------------+
|                    Your Python Script                           |
|          (OSC Server & OSC Client & Socket Client)              |
|                                                                 |
| 1. Receives OSC Command from UI (e.g., "/start_process")        |
| 2. Connects to Other Program via Socket, sends command          |
| 3. Receives calculated values from Other Program via Socket     |
| 4. Performs further calculations                                |
| 5. Sends calculated result back to UI via OSC (e.g., "/result") |
+-----------------------------------------------------------------+

ตั้งค่าให้ SCORE.py ทำงานเมื่อเปิดเครื่องเสมอ หลังจาก copy สคริปมาวางแล้ว
ส่วนจำเป็นที่ต้องมีในเครื่อง
python ติดตั้งในเครื่องก่อน
socket 1.0.0 ติดตั้งผ่าน terminal คำสั่ง pip install sockets
pythonosc python-osc 1.9.3 ติดตั้งผ่าน terminal คำสั่ง pip install python-osc

1 เปิด Task Scheduler:
กดปุ่ม Windows + R พิมพ์ taskschd.msc แล้วกด Enter
หรือค้นหา "Task Scheduler" ใน Start Menu

2 สร้าง Basic Task:
ใน Task Scheduler, ที่ด้านขวาเลือก "Create Basic Task..."

3 ตั้งชื่อและคำอธิบาย:
Name: ตั้งชื่อที่เข้าใจง่าย เช่น RunMyPythonScriptOnStartup
Description: (ไม่บังคับ) ใส่คำอธิบายสั้นๆ

4 ตั้ง Trigger (เมื่อไหร่ที่ Task จะเริ่มทำงาน):
เลือก "When the computer starts" แล้วคลิก "Next"

5 ตั้ง Action (จะทำอะไรเมื่อ Trigger ทำงาน):
เลือก "Start a program" แล้วคลิก "Next"

6 กำหนด Program/script:
Program/script: นี่คือส่วนสำคัญ คุณจะต้องระบุพาธไปยัง python.exe ที่ใช้รัน script ของคุณ
ตัวอย่าง: C:\Users\YourUser\AppData\Local\Programs\Python\Python39\python.exe
(คุณสามารถหาพาธนี้ได้โดยเปิด Command Prompt พิมพ์ where python หรือ python -c "import sys; print(sys.executable)")
Add arguments (optional): ใส่พาธเต็มของ Python script ของคุณ (รวมชื่อไฟล์ .py ด้วย)
ตัวอย่าง: C:\path\to\your_script.py
Start in (optional): (ไม่บังคับ แต่แนะนำ) ใส่พาธของโฟลเดอร์ที่เก็บ script ของคุณ
ตัวอย่าง: C:\path\to\
ยืนยันและเสร็จสิ้น:

6 คลิก "Next" ตรวจสอบการตั้งค่า แล้วคลิก "Finish"
