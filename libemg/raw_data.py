import multiprocessing

class RawData:
    def __init__(self):
        self.emg_lock = multiprocessing.Lock()
        self.imu_lock = multiprocessing.Lock()
        self.emg_data = []
        self.emg_data2 = []
        self.imu_data = []

    def get_imu(self):
        return self.imu_data

    def get_emg(self):
        return list(self.emg_data)

    def add_emg(self,data):
        with self.emg_lock:
            self.emg_data.append(data)

    def add_imu(self,data):
        with self.imu_lock:
            self.imu_data.append(data)
    
    def reset_emg(self):
        with self.emg_lock:
            self.emg_data = []
            self.emg_data2 = []
    
    def adjust_increment(self, window, increment):
        with self.emg_lock:
            self.emg_data = self.emg_data[-window:]
            self.emg_data = self.emg_data[increment:window]

    def get_emg2(self):
        return list(self.emg_data2)

    def add_emg2(self,data):
        with self.emg_lock:
            self.emg_data2.append(data)

    def adjust_increment2(self, window, increment):
        with self.emg_lock:
            self.emg_data2 = self.emg_data2[-window:]
            self.emg_data2 = self.emg_data2[increment:window]
