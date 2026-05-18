from datetime import datetime
from dataset_handler import DatasetHandler

class MonitoringAgent:
    def __init__(self, dataset_path):
        """
        dataset_path:
        - Folder path (CIC-IDS-2018)
        - OR CSV file (TON_IoT)
        """
        self.dataset_handler = DatasetHandler(dataset_path)
        self.data_stream = self.dataset_handler.stream_data()
        self.monitoring = False

    # --------------------------------------------------
    # Real-time dataset-driven observation
    # --------------------------------------------------
    def observe(self):
        """
        Returns one network flow record at a time
        """
        if not self.monitoring:
            return None

        try:
            data = next(self.data_stream)
            data["timestamp"] = datetime.now().isoformat()
            return data
        except StopIteration:
            print("[MonitoringAgent] Dataset stream completed")
            self.monitoring = False
            return None

    # --------------------------------------------------
    # Control methods
    # --------------------------------------------------
    def start_monitoring(self):
        self.monitoring = True
        print("✅ Monitoring started (dataset-driven)")

    def stop_monitoring(self):
        self.monitoring = False
        print("⏹️ Monitoring stopped")
