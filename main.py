import time
import cv2
import argparse
import requests
import signal
import sys
from utils import *
import mediapipe as mp
from body_part_angle import BodyPartAngle
from types_of_excercise import TypeOfExercise

# Argument setup
ap = argparse.ArgumentParser()
ap.add_argument("-t", "--exercise_type", type=str, required=True)
ap.add_argument("-vs", "--video_source", type=str, required=False)
ap.add_argument("-u", "--user_id", type=int, required=True)
args = vars(ap.parse_args())

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

exercise_type = args["exercise_type"]
user_id = args["user_id"]
backend_url = "http://localhost:8081/api/exercise"
cap = cv2.VideoCapture("Exercise Videos/" + args["video_source"]) if args["video_source"] else cv2.VideoCapture(0)

cap.set(3, 800)
cap.set(4, 480)

counter = 0
status = True
start_time = time.time()

# 🧩 Graceful exit function (called when stop button pressed)
def graceful_exit(signum, frame):
    duration = round(time.time() - start_time, 2)
    payload = {
        "userId": user_id,
        "exercise": exercise_type,
        "count": counter,
        "duration": duration
    }
    print(f"\n📤 Sending final data: {payload}")
    try:
        requests.post(backend_url, json=payload, timeout=5)
    except Exception as e:
        print(f"❌ Failed to send data: {e}")
    print("🛑 Exiting gracefully...")
    cap.release()
    cv2.destroyAllWindows()
    sys.exit(0)

# Register signal for stop
signal.signal(signal.SIGTERM, graceful_exit)
signal.signal(signal.SIGINT, graceful_exit)

# Main pose detection loop
with mp_pose.Pose(min_detection_confidence=0.5,
                  min_tracking_confidence=0.5) as pose:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (800, 480))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame.flags.writeable = False
        results = pose.process(frame)
        frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        try:
            landmarks = results.pose_landmarks.landmark
            counter, status = TypeOfExercise(landmarks).calculate_exercise(exercise_type, counter, status)
            # 🧾 Save counter to file (so Flask can read)
            with open("exercise_counter.txt", "w") as f:
                f.write(str(counter))
        except Exception:
            pass

        frame = score_table(exercise_type, frame, counter, status)
        mp_drawing.draw_landmarks(
            frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(174, 139, 45), thickness=2, circle_radius=2)
        )

        cv2.imshow('Video', frame)
        # ❌ No q required, stop handled by Flask
        if cv2.waitKey(10) & 0xFF == 27:  # just for manual testing with ESC
            graceful_exit(None, None)

cap.release()
cv2.destroyAllWindows()
