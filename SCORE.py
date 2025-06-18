import json
import os


# --- กำหนดค่าคงที่ (Constants) ---
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

profile_id = raw_data.get("player_id")

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

print(profile_id)
print(score)
