import numpy as np
import json
from datetime import datetime
from collections import deque
import random
import os


class LearningAgent:
    def __init__(self, state_size=10, action_size=5, learning_rate=0.001, crypto_manager=None):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate

        # Cryptography integration
        self.crypto_manager = crypto_manager
        self.encryption_enabled = crypto_manager is not None

        # Q-Learning parameters
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995

        # Q-Table
        self.q_table = {}

        # Experience memory
        self.memory = deque(maxlen=2000)

        # Actions
        self.actions = ['allow', 'alert', 'rate_limit', 'block_ip', 'isolate_host']

        # Feedback
        self.feedback_log = []

        if self.encryption_enabled:
            print("🔐 Learning Agent: Encryption ENABLED")
        else:
            print("⚠️  Learning Agent: Encryption DISABLED")

    # --------------------------------------------------
    # Q-Learning Core
    # --------------------------------------------------
    def get_state_key(self, state):
        return tuple(int(x * 10) for x in state)

    def choose_action(self, state, epsilon=None):
        if epsilon is None:
            epsilon = self.epsilon

        state_key = self.get_state_key(state)

        if np.random.rand() < epsilon:
            return np.random.randint(self.action_size)

        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_size)

        return int(np.argmax(self.q_table[state_key]))

    def learn_from_experience(self, state, action, reward, next_state, done):
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)

        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_size)
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = np.zeros(self.action_size)

        current_q = self.q_table[state_key][action]
        target_q = reward if done else reward + self.gamma * np.max(self.q_table[next_state_key])

        self.q_table[state_key][action] += self.learning_rate * (target_q - current_q)

        self.memory.append((state, action, reward, next_state, done))

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    # --------------------------------------------------
    # Reward Function
    # --------------------------------------------------
    def calculate_reward(self, detection_result, actual_label, action_taken):
        reward = 0

        if detection_result == 1 and actual_label == 1:
            reward += 10
            if action_taken in ['block_ip', 'isolate_host']:
                reward += 5
        elif detection_result == 0 and actual_label == 0:
            reward += 5
            if action_taken in ['block_ip', 'isolate_host']:
                reward -= 3
        elif detection_result == 1 and actual_label == 0:
            reward -= 10
            if action_taken in ['block_ip', 'isolate_host']:
                reward -= 5
        elif detection_result == 0 and actual_label == 1:
            reward -= 20

        return reward

    # --------------------------------------------------
    # ✅ FIXED STATE EXTRACTION (NO len(int))
    # --------------------------------------------------
    def _extract_state(self, detection_data):
        state = [
            float(detection_data.get('confidence', 0.5)),
            float(detection_data.get('risk_score', 0.5)),
            float(detection_data.get('packet_count', 0)) / 100,
            float(detection_data.get('byte_count', 0)) / 10000,

            # blocked_ips is ALREADY a number
            float(detection_data.get('blocked_ips', 0)) / 100,

            float(detection_data.get('cpu_usage', 0)) / 100,
            float(detection_data.get('false_positive_rate', 0)),
            float(detection_data.get('false_negative_rate', 0)),
            float(detection_data.get('recent_threats', 0)) / 50,
            1.0 if detection_data.get('peak_hours', False) else 0.0
        ]

        return np.array(state[:self.state_size], dtype=np.float32)

    # --------------------------------------------------
    # Experience Replay
    # --------------------------------------------------
    def experience_replay(self, batch_size=32):
        if len(self.memory) < batch_size:
            return

        batch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in batch:
            self.learn_from_experience(state, action, reward, next_state, done)

    # --------------------------------------------------
    # Metrics
    # --------------------------------------------------
    def get_performance_metrics(self):
        if not self.feedback_log:
            return {
                'total_feedback': 0,
                'accuracy': 0,
                'average_reward': 0,
                'exploration_rate': self.epsilon,
                'q_table_size': len(self.q_table),
                'encryption_enabled': self.encryption_enabled
            }

        correct = sum(1 for f in self.feedback_log if f['correct'])
        total = len(self.feedback_log)
        avg_reward = np.mean([f['reward'] for f in self.feedback_log])

        return {
            'total_feedback': total,
            'accuracy': correct / total if total > 0 else 0,
            'average_reward': avg_reward,
            'exploration_rate': self.epsilon,
            'q_table_size': len(self.q_table),
            'encryption_enabled': self.encryption_enabled
        }

    # --------------------------------------------------
    # Save / Load (Encrypted)
    # --------------------------------------------------
    def save_learning_state(self, filepath='models/learning_state.json'):
        os.makedirs('models', exist_ok=True)

        state = {
            'q_table': {str(k): v.tolist() for k, v in self.q_table.items()},
            'epsilon': self.epsilon,
            'feedback_log': self.feedback_log[-1000:],
            'timestamp': datetime.now().isoformat()
        }

        if self.encryption_enabled and self.crypto_manager:
            encrypted_state = self.crypto_manager.encrypt_data(state)
            with open(filepath, 'w') as f:
                json.dump({'encrypted': True, 'data': encrypted_state}, f, indent=2)
            print("🔐 Learning state saved (ENCRYPTED)")
        else:
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
            print("💾 Learning state saved (UNENCRYPTED)")

    def load_learning_state(self, filepath='models/learning_state.json'):
        if not os.path.exists(filepath):
            print("No saved learning state found")
            return

        with open(filepath, 'r') as f:
            data = json.load(f)

        if data.get('encrypted', False):
            decrypted = self.crypto_manager.decrypt_data(data['data'])
            state = json.loads(decrypted)
        else:
            state = data

        self.q_table = {eval(k): np.array(v) for k, v in state['q_table'].items()}
        self.epsilon = state['epsilon']
        self.feedback_log = state.get('feedback_log', [])

        print(f"✅ Learning state loaded | Q-table size: {len(self.q_table)}")
