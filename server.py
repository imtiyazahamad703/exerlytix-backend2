from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import signal
import sys

app = Flask(__name__)
CORS(app)  # Enable CORS

# 🔹 Store processes by exercise type
processes = {}
current_user_id = 1  # default

@app.route('/set_user', methods=['POST'])
def set_user():
    global current_user_id
    try:
        data = request.get_json(force=True)
        current_user_id = int(data.get('user_id', 1))  # fallback to 1
        print(f"✅ Active user set to: {current_user_id}")
        return jsonify({"message": "User ID set successfully", "user_id": current_user_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/run-python', methods=['POST'])
def run_python():
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 415

        data = request.get_json()
        exercise_type = data.get('exercise_type', 'pull-up')

        # If already running, stop it first
        if exercise_type in processes and processes[exercise_type]:
            try:
                os.kill(processes[exercise_type].pid, signal.SIGTERM)
            except Exception:
                pass
            processes[exercise_type] = None

        #start new process by passing current_user_id to main
        proc = subprocess.Popen(
        [sys.executable, 'main.py', '-t', exercise_type, '-u', str(current_user_id)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
         )

        """# Start new process
        proc = subprocess.Popen(
            [sys.executable, 'main.py', '-t', exercise_type],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )"""
        processes[exercise_type] = proc

        return jsonify({'message': f'{exercise_type} started', 'pid': proc.pid})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stop-python', methods=['POST'])
def stop_python():
    try:
        stopped = []
        for exercise, proc in list(processes.items()):
            if proc and proc.poll() is None:  # still running
                # 🧩 Step 1: Read final count from file
                try:
                    with open("exercise_counter.txt", "r") as f:
                        count = int(f.read().strip())
                except Exception:
                    count = 0

                # 🧩 Step 2: Calculate duration (rough)
                duration = 60  # ya tum start_time store karke bhi nikal sakte ho

                # 🧩 Step 3: Send final payload to backend
                payload = {
                    "userId": current_user_id,
                    "exercise": exercise,
                    "count": count,
                    "duration": duration
                }
                print(f"📤 Sending final data: {payload}")

                import requests
                try:
                    requests.post("https://exerlytix-backend1.onrender.com/api/exercise/update", json=payload, timeout=5)
                    print("✅ Data sent successfully to backend!")
                except Exception as e:
                    print(f"❌ Backend update failed: {e}")

                # 🧩 Step 4: Stop process
                proc.terminate()
                processes[exercise] = None
                stopped.append(exercise)

        if stopped:
            return jsonify({'message': f"Stopped & data saved for: {', '.join(stopped)}"})
        else:
            return jsonify({'message': 'No script running'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/exercise-count', methods=['GET'])
def get_exercise_count():
    try:
        with open('exercise_counter.txt', 'r') as f:
            count = int(f.read().strip())
        return jsonify({"completed": count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
