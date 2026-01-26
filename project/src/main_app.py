"""
----------------------------------------------------------------------------------------------------
FILE: main_app.py
PROJECT: Communication Systems Engineering - Speech Recognition System
INSTITUTION: Ho Chi Minh City University of Technology (HCMUT)

DESCRIPTION:
    This module serves as the Standard Runtime Environment (Inference Mode) for the system.
    Unlike 'main_ml.py', this module focuses solely on high-speed prediction without 
    the overhead of model retraining.

    Key Features:
    1. Push-to-Talk Interface: Intuitive control where the user holds the SPACE bar 
       to record, mimicking walkie-talkie operation.
    2. Real-time Viterbi Decoding: rapid scoring of input signals against all 35 
       trained HMM models to find the Maximum Likelihood Estimate (MLE).
    3. Advanced Signal Visualization: Generates comparative waveform plots between 
       the user's input and the stored reference samples (Winner vs. Top Candidates).
    4. Robust DSP Pipeline: Implements the V4 preprocessing logic (Pre-emphasis, 
       Normalization, Padding-based Trim) for noise resilience.
    5. Scientific Reporting: Automatically generates detailed technical charts (DSP steps, 
       Spectrograms, Confidence distribution) for every trial via 'visualizer.py'.

AUTHORS:
    1. Do Ngoc Gia Bao    - ID: 2110778
    2. Thai Duc Thien     - ID: 2313222
    3. Pham Minh Quang    - ID: 2312807

INSTRUCTOR:
    Mr. Nguyen Chi Ngoc

DATE: January 2026
----------------------------------------------------------------------------------------------------
"""

import os
import time
import random
import numpy as np
import sounddevice as sd
import keyboard
import joblib
import librosa
import matplotlib.pyplot as plt
from scipy.io.wavfile import write as write_wav
from tqdm import tqdm

# Import project configuration and utilities
from config import Config
from utils import current_logger
from visualizer import ReportGenerator # <--- NEW MODULE INTEGRATION

class RealTimeRecognizer:
    """
    Standard recognition engine optimized for demonstration and production use.
    """

    def __init__(self):
        """Initialize system state and load acoustic models."""
        self.models = {}
        self.is_running = True
        
        # Pre-load all models into RAM to minimize latency during inference
        self.load_all_models()

        # Initialize the Scientific Report Generator
        # It will save detailed charts into the current session's log directory
        self.reporter = ReportGenerator(current_logger.session_log_dir)

    def load_all_models(self):
        """
        Loads trained GMM-HMM models (.pkl files) from the 'models/' directory.
        Uses joblib for efficient deserialization of binary model data.
        """
        current_logger.log("LOADING MODELS...")
        
        # Scan model directory
        model_files = [f for f in os.listdir(Config.MODEL_DIR) if f.endswith('.pkl')]
        
        if not model_files:
            current_logger.log("[CRITICAL] No models found! Please run 'train_model.py' first.")
            return

        # Load models with a progress bar for better UX
        count = 0
        for f in tqdm(model_files, desc="Loading HMMs"):
            word = f.replace('.pkl', '')
            path = os.path.join(Config.MODEL_DIR, f)
            try:
                self.models[word] = joblib.load(path)
                count += 1
            except Exception as e:
                current_logger.log(f"[Error] Failed to load model '{word}': {e}")
        
        current_logger.log(f"System Ready. Loaded {count} models.")
        current_logger.log("INSTRUCTIONS: Hold [SPACE] to speak, [P] to exit.")

    def get_representative_wave(self, word):
        """
        Fetches a random 'standard' audio sample from the dataset for visualization.
        """
        try:
            word_dir = os.path.join(Config.DATA_DIR, word)
            if not os.path.exists(word_dir): return None
                
            wav_files = [f for f in os.listdir(word_dir) if f.endswith('.wav')]
            if not wav_files: return None
                
            # Random selection ensures the user doesn't see the same reference curve every time
            random_file = random.choice(wav_files)
            full_path = os.path.join(word_dir, random_file)
            
            # Load and lightly trim for cleaner plotting
            sig, _ = librosa.load(full_path, sr=Config.SAMPLE_RATE, mono=True)
            sig, _ = librosa.effects.trim(sig, top_db=20)
            return sig
        except:
            return None

    def visualize_result(self, input_signal, scores, best_word, filename_prefix):
        """
        Creates a visual report comparing the input signal with top candidates.
        Output: A .png file saved in the log directory.
        """
        # Sort candidates by Score (Log-Likelihood) descending
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
        
        fig, axes = plt.subplots(6, 1, figsize=(10, 12), dpi=120)
        fig.suptitle(f"RECOGNITION RESULT: {best_word.upper()}", fontsize=16, fontweight='bold', color='darkblue')
        
        # --- ROW 1: USER INPUT ---
        ax_input = axes[0]
        ax_input.plot(input_signal, color='black', linewidth=1.2)
        ax_input.set_title(f"YOUR VOICE (Input Signal)", fontweight='bold', loc='left')
        ax_input.set_facecolor('#e6e6e6')
        ax_input.set_ylabel("Amplitude")
        ax_input.axes.xaxis.set_visible(False)
        
        # --- ROWS 2-6: TOP 5 CANDIDATES ---
        for i, (word, score) in enumerate(sorted_scores):
            ax = axes[i+1]
            sample_sig = self.get_representative_wave(word)
            
            if sample_sig is not None:
                # Color coding: Green for the winner, Red for the rest
                color = '#00aa00' if i == 0 else '#cc0000'
                style = '-' if i == 0 else '--'
                
                ax.plot(sample_sig, color=color, alpha=0.8, linewidth=1, linestyle=style)
                
                # Display Word Label and Likelihood Score
                title = f"#{i+1}: {word.upper()} (Score: {score:.0f})"
                ax.set_title(title, fontsize=10, loc='left', color=color, fontweight='bold')
                
                if i == 0:
                    ax.text(0.98, 0.8, "MATCHED", transform=ax.transAxes, 
                            ha='right', color='green', fontweight='bold')
            else:
                ax.text(0.5, 0.5, "Reference sample missing", ha='center')
            
            ax.axes.xaxis.set_visible(False)
            ax.set_yticks([])
            
        plt.tight_layout()
        plt.subplots_adjust(top=0.93)
        
        img_name = f"{filename_prefix}_comparison.png"
        save_path = os.path.join(current_logger.session_log_dir, img_name)
        plt.savefig(save_path)
        plt.close() # Close plot to prevent memory leaks
        return save_path

    def extract_features(self, audio_path):
        """
        DSP PIPELINE V4 (Robust Feature Extraction)
        Identical to main_ml.py to ensure consistency between training and inference.
        """
        try:
            # 1. Load Audio
            signal, sr = librosa.load(audio_path, sr=Config.SAMPLE_RATE, mono=True)
            
            # 2. Pre-emphasis: y(t) = x(t) - 0.95*x(t-1)
            # Essential for preserving high-frequency components (e.g., /s/ in 'Six')
            signal = librosa.effects.preemphasis(signal, coef=0.95)

            # 3. Amplitude Normalization: Scale to [-1, 1]
            max_amp = np.max(np.abs(signal))
            if max_amp < 0.005: return None, None # Signal is noise
            signal = signal / max_amp 

            # 4. Smart Trim with Context Padding
            # Prevents clipping of onset plosives (e.g., /d/ in 'Down')
            _, index = librosa.effects.trim(signal, top_db=25, frame_length=512, hop_length=128)
            start_idx, end_idx = index[0], index[1]
            pad_size = int(0.15 * sr) 
            
            final_start = max(0, start_idx - pad_size)
            final_end = min(len(signal), end_idx + pad_size)
            final_signal = signal[final_start:final_end]

            # Fallback if signal becomes too short after trimming
            if len(final_signal) < int(0.1 * sr):
                final_signal = signal 

            # 5. Extract MFCC + Delta + Delta-Delta
            # Resulting vector shape: [n_frames, 39]
            mfcc = librosa.feature.mfcc(y=final_signal, sr=sr, n_mfcc=Config.N_MFCC, 
                                        n_fft=Config.N_FFT, hop_length=Config.HOP_LENGTH)
            delta1 = librosa.feature.delta(mfcc, order=1)
            delta2 = librosa.feature.delta(mfcc, order=2)
            
            combined = np.concatenate((mfcc, delta1, delta2), axis=0).T
            return combined, final_signal

        except Exception as e:
            current_logger.log(f"[DSP Error] {e}")
            return None, None

    def record_and_predict(self):
        """
        Executes the 'Record -> Process -> Predict' workflow.
        Uses Push-to-Talk logic: Recording stops when SPACE is released.
        """
        print("\n--- RECORDING... (Release SPACE to stop) ---")
        
        fs = Config.SAMPLE_RATE
        max_duration = 6 # Maximum recording buffer length
        
        # 1. Start Recording (Non-blocking)
        # Note: Recording starts immediately because this function is called 
        # when SPACE is already pressed in the main loop.
        myrecording = sd.rec(int(max_duration * fs), samplerate=fs, channels=1)
        start_time = time.time()
        
        # 2. Wait for Key Release (Push-to-Talk Loop)
        while True:
            # Stop if SPACE is released
            if not keyboard.is_pressed('space'):
                break
            
            # Stop if max duration exceeded
            if (time.time() - start_time) > max_duration:
                break
                
            time.sleep(0.01) # Low CPU usage wait
            
        # 3. Stop Stream
        sd.stop()
        
        # 4. Process Duration
        elapsed_time = time.time() - start_time
        if elapsed_time < 0.2:
            print(">> Too short! Please speak clearly.")
            return

        # 5. Slice Audio Buffer
        valid_samples = int(elapsed_time * fs)
        real_audio = myrecording[:valid_samples]
        
        print(f"--- STOPPED (Duration: {elapsed_time:.2f}s) ---")
        print("--- PROCESSING... ---")
        
        # Save temporary file
        timestamp = int(time.time())
        temp_filename = f"rec_{timestamp}"
        temp_wav_path = os.path.join(current_logger.session_log_dir, f"{temp_filename}.wav")
        write_wav(temp_wav_path, fs, real_audio) 
        
        # 6. Inference Pipeline
        features, signal = self.extract_features(temp_wav_path)
        
        if features is None:
            print(">> Signal quality too low (Noise/Silence).")
            return

        # 7. Viterbi Scoring
        scores = {}
        for word, model in self.models.items():
            try:
                # Calculate Log-Likelihood of the observation sequence given the model
                score = model.score(features)
                scores[word] = score
            except:
                scores[word] = -float('inf')

        # 8. Decision Rule (Maximum Likelihood)
        best_word = max(scores, key=scores.get)
        best_score = scores[best_word]
        
        print(f">> RESULT: [ {best_word.upper()} ] (Score: {best_score:.2f}) - DONE")
        
        # 9. Visualization & Logging
        # A. Standard Quick View
        img_path = self.visualize_result(signal, scores, best_word, temp_filename)
        current_logger.log(f"Recognized: {best_word} (len={elapsed_time:.2f}s) | Log: {img_path}")

        # B. DETAILED SCIENTIFIC REPORT (NEW FEATURE)
        print(">> Generating Technical Report...", end="")
        try:
            # Flatten the raw audio array for visualization (numpy array from sounddevice is 2D)
            raw_flat = real_audio.flatten()
            report_path = self.reporter.generate_all_reports(
                audio_path=temp_wav_path,
                raw_signal=raw_flat, 
                scores=scores, 
                best_word=best_word, 
                timestamp=timestamp
            )
            print(f" Saved to: {report_path}")
        except Exception as e:
            print(f" Failed: {e}")

    def run(self):
        """
        Main application loop.
        Monitors keyboard events to trigger recording or exit.
        """
        print("==================================================")
        print("      REAL-TIME SPEECH RECOGNITION SYSTEM")
        print("==================================================")
        print("INSTRUCTIONS:")
        print("1. HOLD [SPACE] to record.")
        print("2. RELEASE [SPACE] to stop recording.")
        print("3. Press [P] to exit.")
        print("==================================================")
        
        while self.is_running:
            # Exit condition
            if keyboard.is_pressed('p'):
                print("Exiting...")
                self.is_running = False
                break
            
            # Record condition
            if keyboard.is_pressed('space'):
                self.record_and_predict()
                
                # Debounce: Wait for key release before next loop
                # This prevents the recording from restarting instantly
                while keyboard.is_pressed('space'):
                    time.sleep(0.1)
                
                time.sleep(0.2) # Short cooldown

if __name__ == "__main__":
    app = RealTimeRecognizer()
    app.run()