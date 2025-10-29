import numpy as np
from body_part_angle import BodyPartAngle
from utils import *


class TypeOfExercise(BodyPartAngle):
    def __init__(self, landmarks):
        super().__init__(landmarks)
        
    def bicep_curl(self, counter, status):
        # Left arm angle (shoulder-elbow-wrist)
        left_shoulder = detection_body_part(self.landmarks, "LEFT_SHOULDER")
        left_elbow = detection_body_part(self.landmarks, "LEFT_ELBOW")
        left_wrist = detection_body_part(self.landmarks, "LEFT_WRIST")

        left_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)

        # Right arm angle (shoulder-elbow-wrist)
        right_shoulder = detection_body_part(self.landmarks, "RIGHT_SHOULDER")
        right_elbow = detection_body_part(self.landmarks, "RIGHT_ELBOW")
        right_wrist = detection_body_part(self.landmarks, "RIGHT_WRIST")

        right_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)

        # Take average of both arms
        avg_angle = (left_angle + right_angle) // 2

        # Curl logic
        if status:  # arm extended
            if avg_angle < 40:  # fully bent
                counter += 1
                status = False
        else:  # arm bent
            if avg_angle > 160:  # fully extended again
                status = True

        return [counter, status]

    def push_up(self, counter, status):
            left_arm_angle = self.angle_of_the_left_arm()
            right_arm_angle = self.angle_of_the_right_arm()
            avg_arm_angle = (left_arm_angle + right_arm_angle) // 2

            if status:
                if avg_arm_angle < 70:
                    counter += 1
                    status = False
            else:
                if avg_arm_angle > 160:
                    status = True

            return [counter, status]


    def pull_up(self, counter, status):
        nose = detection_body_part(self.landmarks, "NOSE")
        left_elbow = detection_body_part(self.landmarks, "LEFT_ELBOW")
        right_elbow = detection_body_part(self.landmarks, "RIGHT_ELBOW")
        avg_shoulder_y = (left_elbow[1] + right_elbow[1]) / 2

        if status:
            if nose[1] > avg_shoulder_y:
                counter += 1
                status = False

        else:
            if nose[1] < avg_shoulder_y:
                status = True

        return [counter, status]

    def squat(self, counter, status):
        left_leg_angle = self.angle_of_the_left_leg()
        right_leg_angle = self.angle_of_the_right_leg()
        avg_leg_angle = (left_leg_angle + right_leg_angle) // 2

        if status:
            if avg_leg_angle < 70:
                counter += 1
                status = False
        else:
            if avg_leg_angle > 160:
                status = True

        return [counter, status]

    def walk(self, counter, status):
        right_knee = detection_body_part(self.landmarks, "RIGHT_KNEE")
        left_knee = detection_body_part(self.landmarks, "LEFT_KNEE")

        if status:
            if left_knee[0] > right_knee[0]:
                counter += 1
                status = False

        else:
            if left_knee[0] < right_knee[0]:
                counter += 1
                status = True

        return [counter, status]

    def sit_up(self, counter, status):
        angle = self.angle_of_the_abdomen()
        if status:
            if angle < 55:
                counter += 1
                status = False
        else:
            if angle > 105:
                status = True

        return [counter, status]
    
    def shoulder_raise(self, counter, status):
        # Left arm (shoulder–elbow–hip)
        left_shoulder = detection_body_part(self.landmarks, "LEFT_SHOULDER")
        left_elbow = detection_body_part(self.landmarks, "LEFT_ELBOW")
        left_hip = detection_body_part(self.landmarks, "LEFT_HIP")

        left_angle = calculate_angle(left_elbow, left_shoulder, left_hip)

        # Right arm (shoulder–elbow–hip)
        right_shoulder = detection_body_part(self.landmarks, "RIGHT_SHOULDER")
        right_elbow = detection_body_part(self.landmarks, "RIGHT_ELBOW")
        right_hip = detection_body_part(self.landmarks, "RIGHT_HIP")

        right_angle = calculate_angle(right_elbow, right_shoulder, right_hip)

        # Average both arms
        avg_angle = (left_angle + right_angle) // 2

        # Debug print
        # print(f"Left: {left_angle:.2f}, Right: {right_angle:.2f}, Avg: {avg_angle:.2f}, Status: {status}, Count: {counter}")

        # Rep logic
        if status:  # arm down
            if avg_angle > 80:  # lifted
                counter += 1
                status = False
        else:  # arm up
            if avg_angle < 30:  # back down
                status = True

        return [counter, status]

    def shoulder_press(self, counter, status):
        # Get landmarks
        left_elbow_angle = self.angle_of_the_left_arm()
        right_elbow_angle = self.angle_of_the_right_arm()

        left_hand = detection_body_part(self.landmarks, "LEFT_WRIST")
        right_hand = detection_body_part(self.landmarks, "RIGHT_WRIST")
        left_shoulder = detection_body_part(self.landmarks, "LEFT_SHOULDER")
        right_shoulder = detection_body_part(self.landmarks, "RIGHT_SHOULDER")

        # Average elbow angle
        avg_elbow_angle = (left_elbow_angle + right_elbow_angle) // 2

        if status:  # Arms are down, waiting to press up
            if avg_elbow_angle > 160 and \
            left_hand[1] < left_shoulder[1] and \
            right_hand[1] < right_shoulder[1]:
                counter += 1
                status = False
        else:  # Arms are up, wait until they go down again
            if avg_elbow_angle < 100:  # back to start position
                status = True

        return [counter, status]
    
    def chest_fly(self, counter, status):
        # Landmarks
        left_wrist = detection_body_part(self.landmarks, "LEFT_WRIST")
        right_wrist = detection_body_part(self.landmarks, "RIGHT_WRIST")
        left_elbow = detection_body_part(self.landmarks, "LEFT_ELBOW")
        right_elbow = detection_body_part(self.landmarks, "RIGHT_ELBOW")
        left_shoulder = detection_body_part(self.landmarks, "LEFT_SHOULDER")
        right_shoulder = detection_body_part(self.landmarks, "RIGHT_SHOULDER")

        # Horizontal wrist distance (main movement)
        wrist_distance = abs(left_wrist[0] - right_wrist[0])

        # Reference shoulder width
        shoulder_distance = abs(left_shoulder[0] - right_shoulder[0])

        # Elbow angles (to check arms are extended, not pressing)
        left_elbow_angle = self.angle_of_the_left_arm()
        right_elbow_angle = self.angle_of_the_right_arm()

        # ---- THRESHOLDS ----
        OPEN_THRESHOLD = 2.3 * shoulder_distance   # arms wide
        CLOSE_THRESHOLD = 1.2 * shoulder_distance  # arms nearly together
        MIN_ELBOW_ANGLE = 150                      # arms straight

        # ✅ Logic
        if status:  # waiting for close
            if wrist_distance < CLOSE_THRESHOLD and \
            left_elbow_angle > MIN_ELBOW_ANGLE and \
            right_elbow_angle > MIN_ELBOW_ANGLE:
                counter += 1
                status = False
        else:  # waiting to open again
            if wrist_distance > OPEN_THRESHOLD:
                status = True

        return [counter, status]

    
    def lunge(self, counter, status):
        # Track RIGHT LEG (front leg)
        knee_angle = self.angle_of_joint("RIGHT_HIP", "RIGHT_KNEE", "RIGHT_ANKLE")

        # Down phase
        if knee_angle < 80 and status:
            status = False  # bottom reached

        # Up phase
        if knee_angle > 160 and not status:
            counter += 1
            status = True  # ready for next rep
            print(f"Lunge counted! Total: {counter}")

        return counter, status
    
    def calculate_exercise(self, exercise_type, counter, status):
        if exercise_type == "push-up":
            counter, status = TypeOfExercise(self.landmarks).push_up(
                counter, status)
        elif exercise_type == "pull-up":
            counter, status = TypeOfExercise(self.landmarks).pull_up(
                counter, status)
        elif exercise_type == "squat":
            counter, status = TypeOfExercise(self.landmarks).squat(
                counter, status)
        elif exercise_type == "walk":
            counter, status = TypeOfExercise(self.landmarks).walk(
                counter, status)
        elif exercise_type == "sit-up":
            counter, status = TypeOfExercise(self.landmarks).sit_up(
                counter, status)
        elif exercise_type == "bicep":
            counter, status = TypeOfExercise(self.landmarks).bicep_curl(counter, status)
        elif exercise_type == "shoulder-raise":
            counter, status = TypeOfExercise(self.landmarks).shoulder_raise(counter, status)
        elif exercise_type == "shoulder-press":
            counter, status = TypeOfExercise(self.landmarks).shoulder_press(counter, status)
            
        elif exercise_type == "chest-fly":
            counter, status = TypeOfExercise(self.landmarks).chest_fly(counter, status)
        
        elif exercise_type == "lunge":
            counter, status = TypeOfExercise(self.landmarks).lunge(counter, status)

        return [counter, status]