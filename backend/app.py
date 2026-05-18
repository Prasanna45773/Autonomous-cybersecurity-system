from flask import Flask, jsonify
from flask_cors import CORS
import threading
import time
from datetime import datetime
import queue

from dataset_handler import DatasetHandler
from detection_agent import DetectionAgent
from decision_agent import DecisionAgent
from response_agent import ResponseAgent
from monitoring_agent import MonitoringAgent
from learning_agent import LearningAgent
from crypto_manager import CryptoManager

# --------------------------------------------------
# Flask App
# --------------------------------------------------
app = Flask(__name__)
CORS(app)

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
DATASET_PATH = "../datasets/CIC-IDS-2018"

# --------------------------------------------------
# Initialize Crypto
# --------------------------------------------------
crypto_manager = CryptoManager()

# --------------------------------------------------
# Initialize Dataset & Agents
# --------------------------------------------------
dataset_handler = DatasetHandler(DATASET_PATH)
monitoring_agent = MonitoringAgent(DATASET_PATH)

detection_agent = DetectionAgent()
decision_agent = DecisionAgent()
response_agent = ResponseAgent(crypto_manager=crypto_manager)
learning_agent = LearningAgent(
    state_size=10,
    action_size=5,
    crypto_manager=crypto_manager
)

# --------------------------------------------------
# System State
# --------------------------------------------------
system_state = {
    "status": "initializing",
    "models_trained": False,
    "monitoring_active": False,
    "autonomous_loop_active": False,
    "total_threats_detected": 0,
    "total_actions_taken": 0,
    "false_positives": 0,
    "false_negatives": 0,
    "auto_learning_events": 0
}

training_complete = False
detection_queue = queue.Queue(maxsize=1000)

# --------------------------------------------------
# TRAINING
# --------------------------------------------------
def train_models():
    global training_complete

    try:
        print("\n" + "=" * 70)
        print("TRAINING DETECTION MODELS (DATASET-BASED)")
        print("=" * 70)

        X_train, X_test, y_train, y_test = dataset_handler.get_train_test_data()

        detection_agent.train(
            X_train,
            y_train,
            feature_names=dataset_handler.feature_names
        )

        metrics = detection_agent.evaluate(X_test, y_test)
        detection_agent.save_models()

        learning_agent.load_learning_state()

        system_state["models_trained"] = True
        system_state["status"] = "ready"
        system_state["model_metrics"] = metrics
        training_complete = True

        print("\nTRAINING COMPLETE")
        print(f"Accuracy : {metrics['accuracy']:.4f}")
        print(f"Precision: {metrics['precision']:.4f}")
        print(f"Recall   : {metrics['recall']:.4f}")
        print(f"F1-score : {metrics['f1_score']:.4f}")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"[ERROR] Training failed: {e}")
        system_state["status"] = "error"

# --------------------------------------------------
# AUTONOMOUS CLOSED LOOP
# --------------------------------------------------
def autonomous_loop():
    print("\n" + "=" * 70)
    print("AUTONOMOUS LOOP STARTED")
    print("Observe → Detect → Decide → Act → Learn")
    print("=" * 70 + "\n")

    cycle = 0

    while system_state["autonomous_loop_active"]:
        try:
            cycle += 1

            # ---------------- OBSERVE ----------------
            data_row = monitoring_agent.observe()
            if data_row is None:
                break

            # ---------------- DETECT ----------------
            prediction, confidence = detection_agent.detect(
                data_row,
                scaler=dataset_handler.scaler
            )

            # ---------------- STATE (RL) ----------------
            state = learning_agent._extract_state({
                "confidence": confidence,
                "risk_score": confidence if prediction == 1 else 0.2,
                "packet_count": data_row.get("Flow Pkts/s", 0),
                "byte_count": data_row.get("TotLen Fwd Pkts", 0),
                "blocked_ips": len(response_agent.blocked_ips),
                "cpu_usage": 0.5,
                "false_positive_rate": system_state["false_positives"] / max(cycle, 1),
                "false_negative_rate": system_state["false_negatives"] / max(cycle, 1),
                "recent_threats": system_state["total_threats_detected"],
                "peak_hours": False
            })

            # ---------------- DECIDE ----------------
            action_idx = learning_agent.choose_action(state)
            learned_action = learning_agent.actions[action_idx]

            decision = decision_agent.assess_threat(
                prediction,
                confidence,
                learned_action
            )

            # ---------------- ACT ----------------
            response_result = None
            actual_action = "allow"

            if decision["threat_detected"]:
                response_result = response_agent.execute_actions(
                    decision,
                    source_ip="dataset"
                )
                actual_action = decision["actions"][0]
                system_state["total_threats_detected"] += 1
                system_state["total_actions_taken"] += len(decision["actions"])

            # ---------------- LEARN ----------------
            ground_truth = prediction
            reward = learning_agent.calculate_reward(
                prediction,
                ground_truth,
                actual_action
            )

            next_state = state
            learning_agent.learn_from_experience(
                state,
                action_idx,
                reward,
                next_state,
                True
            )

            system_state["auto_learning_events"] += 1

            # ---------------- LOG ----------------
            detection_event = {
    "timestamp": datetime.now().isoformat(),

    # ✅ REQUIRED BY FRONTEND
    "traffic_data": {
        "src_ip": data_row.get("Src IP", "dataset-src"),
        "dst_ip": data_row.get("Dst IP", "dataset-dst"),
        "src_port": int(data_row.get("Src Port", 0)),
        "dst_port": int(data_row.get("Dst Port", 0)),
        "protocol": data_row.get("Protocol", "CIC-IDS-2018")
    },

    "prediction": "attack" if prediction == 1 else "normal",
    "confidence": float(confidence),
    "risk_level": decision.get("risk_level", "none"),
    "actions": decision.get("actions", []),
    "learning_action": learned_action,
    "reward": reward,
    "cycle": cycle
}


            if not detection_queue.full():
                detection_queue.put(detection_event)

            time.sleep(0.2)

        except Exception as e:
            print(f"[ERROR] Autonomous loop: {e}")
            time.sleep(1)

# --------------------------------------------------
# API ENDPOINTS
# --------------------------------------------------
@app.route("/api/status", methods=["GET"])
def get_status():
    return jsonify({
        **system_state,
        "learning_metrics": learning_agent.get_performance_metrics()
    })

@app.route("/api/start-monitoring", methods=["POST"])
def start_monitoring():
    if not training_complete:
        return jsonify({"error": "Models not trained"}), 400

    if system_state["autonomous_loop_active"]:
        return jsonify({"message": "Already running"}), 200

    monitoring_agent.start_monitoring()
    system_state["monitoring_active"] = True
    system_state["autonomous_loop_active"] = True

    threading.Thread(target=autonomous_loop, daemon=True).start()
    return jsonify({"message": "Autonomous monitoring started"})

@app.route("/api/stop-monitoring", methods=["POST"])
def stop_monitoring():
    monitoring_agent.stop_monitoring()
    system_state["monitoring_active"] = False
    system_state["autonomous_loop_active"] = False
    return jsonify({"message": "Monitoring stopped"})

@app.route("/api/detections", methods=["GET"])
def get_detections():
    detections = []
    while not detection_queue.empty() and len(detections) < 20:
        detections.append(detection_queue.get())
    return jsonify(detections)

@app.route("/api/blocked-ips", methods=["GET"])
def get_blocked_ips():
    return jsonify({
        "blocked_ips": list(response_agent.blocked_ips),
        "isolated_hosts": list(response_agent.isolated_hosts)
    })

@app.route("/api/crypto/stats", methods=["GET"])
def get_crypto_stats():
    return jsonify(crypto_manager.get_crypto_stats())

@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    return jsonify({
        "total_threats": system_state["total_threats_detected"],
        "total_actions": system_state["total_actions_taken"],
        "false_positives": system_state["false_positives"],
        "false_negatives": system_state["false_negatives"],
        "learning_events": system_state["auto_learning_events"]
    })


# --------------------------------------------------
# STARTUP
# --------------------------------------------------
threading.Thread(target=train_models, daemon=True).start()

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("AUTONOMOUS CYBERSECURITY AI SYSTEM (DATASET-DRIVEN)")
    print("Observe → Detect → Decide → Act → Learn")
    print("=" * 70)
    print("Backend running at http://localhost:5000\n")

    app.run(debug=True, port=5000, threaded=True, use_reloader=False)
