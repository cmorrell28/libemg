from libemg._custom_models.dtw_one_class import DTWClassifier
from libemg.feature_extractor import FeatureExtractor
from libemg.utils import get_windows
from libemg.emg_classifier import EMGClassifier
from multiprocessing import Process, Value
import numpy as np
import time
from collections import deque
import winsound
from pygame import mixer

class WakeWordDetector:
    def __init__(self, online_data_handler, features, window_size, window_increment, gesture_length, classifier, subject, feature_params={}):
        self.raw_data = online_data_handler.raw_data
        self.features = features 
        self.feature_params = feature_params
        self.window_size = window_size
        self.window_increment = window_increment
        self.gesture_length = gesture_length
        self.running = False
        self.subject = subject
        
        self.v = Value('i', 0)
        self.alignment_buffer = deque(maxlen=5)

        classifier.process = Process(target=classifier._run_helper, daemon=True, args=(self.v,))
        classifier.run(block=False)

        self.process = Process(target=self._run_helper)

    def fit(self, num_stds, training_features):
        self.ww_detector = DTWClassifier(std=num_stds)
        self.ww_detector.fit(training_features)

    def run(self, block):
        """Runs the wake word detector.

        Parameters
        ----------
        block: bool (optional), default = True
            If True, the run function blocks the main thread. Otherwise it runs in a 
            seperate process.
        """
        if block:
            self._run_helper()
        else:
            self.process.start()
    
    def _run_helper(self):
        # TODO: I think now the other buffer will grow indefinitely 
        self.raw_data.reset_emg()
        filename = 'data/S' + str(self.subject) + '/ww_activations.txt'
        mixer.init()
        while True:
            if len(self.raw_data.get_emg2()) >= self.gesture_length:
                data = np.array(self.raw_data.get_emg2())
                # Extract window and predict sample
                windows = get_windows(data[-self.gesture_length:][:], self.window_size, self.window_increment)
                features = EMGClassifier()._format_data(FeatureExtractor().extract_features(self.features, windows))
                prediction = self.ww_detector.predict(np.array([features]))[0]
                self.alignment_buffer.append(prediction)
                if sum(self.alignment_buffer) >  0: # Indicates inlier 
                    # poor mans reset
                    for _ in range(0,self.alignment_buffer.maxlen):
                        self.alignment_buffer.append(-1)
                    self.v.value = not self.v.value
                    self.raw_data.reset_emg()
                    
                    print('WW Triggered!')
                    
                    if self.v.value:
                        mixer.music.load('_sounds/connect.mp3')
                        mixer.music.play()
                    else:
                        mixer.music.load('_sounds/disconnect.mp3')
                        mixer.music.play() 
        
                    with open(filename, 'a+') as f:
                        f.write(f"{time.time()}\n")
                else:
                    self.raw_data.adjust_increment2(self.gesture_length-self.window_increment, 0)
