"""
----------------------------------------------------------------------------------------------------
FILE: main_ml.py
PROJECT: Communication Systems Engineering - Speech Recognition System
INSTITUTION: Ho Chi Minh City University of Technology (HCMUT)

DESCRIPTION:
    This is the core execution module of the Intelligent Speech Recognition System.
    It integrates Real-time Inference with an Online Learning (Active Learning) mechanism.

    Key Capabilities:
    1. Real-time Decoding: Captures audio via Push-to-Talk, processes signals, and uses 
       trained HMMs to predict the spoken word using Maximum Likelihood Estimation.
    2. Active Learning Loop: Allows the user to provide feedback on the prediction.
       - If Correct: The sample is added to the dataset to reinforce the model.
       - If Incorrect: The user provides the correct label, and the system learns from the mistake.
    3. Incremental Retraining: Automatically triggers a localized retraining process 
       for the specific word that was updated, ensuring the system gets smarter over time.
    4. Robust Signal Processing: Implements V4 logic (Pre-emphasis + Smart Padding) to handle 
       short utterances and environmental noise.
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
import shutil
import random
import numpy as np
import sounddevice as sd
import keyboard
import joblib
import librosa
import matplotlib.pyplot as plt
from scipy.io.wavfile import write as write_wav
from hmmlearn import hmm

# Import project modules
from config import Config
from utils import current_logger
from visualizer import ReportGenerator  # <--- NEW MODULE INTEGRATION

class SmartRecognizer:
    """
    The main controller class for the speech recognition system.
    Manages the lifecycle of recording, feature extraction, decoding, model updating, 
    and report generation.
    """

    def __init__(self):
        """Initialize the recognizer, load models, and setup reporter."""
        self.models = {}
        self.is_running = True
        self.load_all_models()
        
        # Initialize the Scientific Report Generator
        # It will save detailed charts into the current session's log directory
        self.reporter = ReportGenerator(current_logger.session_log_dir)

    def load_all_models(self):
        """
        Deserializes trained HMM models (.pkl) from the disk into RAM.
        This ensures low-latency prediction during runtime.
        """
        current_logger.log("LOADING MODELS...")
        model_files = [f for f in os.listdir(Config.MODEL_DIR) if f.endswith('.pkl')]
        
        if not model_files:
            print("[Warning] No pre-trained models found. The system will start blank.")
            print("          You can teach it new words using the Active Learning feature.")
        
        count = 0
        for f in model_files:
            word = f.replace('.pkl', '')
            path = os.path.join(Config.MODEL_DIR, f)
            try:
                # Load the GMM-HMM object
                self.models[word] = joblib.load(path)
                count += 1
            except Exception as e:
                current_logger.log(f"[Error] Failed to load model '{word}': {e}")
        
        print(f">> Successfully loaded {count} vocabulary models.")

    def get_representative_wave(self, word):
        """
        Retrieves a random sample waveform from the dataset for visualization purposes.
        This helps the user visually compare their input with the 'standard' signal.
        """
        try:
            word_dir = os.path.join(Config.DATA_DIR, word)
            if not os.path.exists(word_dir): return None
            
            wav_files = [f for f in os.listdir(word_dir) if f.endswith('.wav')]
            if not wav_files: return None
            
            # Pick a random file
            random_file = random.choice(wav_files)
            sig, _ = librosa.load(os.path.join(word_dir, random_file), sr=Config.SAMPLE_RATE, mono=True)
            
            # Trim silence for a cleaner visual plot
            sig, _ = librosa.effects.trim(sig, top_db=20)
            return sig
        except:
            return None

    def visualize_result(self, input_signal, scores, best_word, filename_prefix):
        """
        Generates a quick comparison chart (Quick View):
        - Row 1: The user's input signal.
        - Rows 2-6: Representative signals of the Top 5 predicted candidates.
        """
        # Sort scores descending (Best match first)
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Create figure
        fig, axes = plt.subplots(6, 1, figsize=(10, 12), dpi=100)
        fig.suptitle(f"RECOGNITION RESULT: {best_word.upper()}", fontsize=16, fontweight='bold', color='darkblue')
        
        # --- PLOT 1: USER INPUT ---
        ax_input = axes[0]
        ax_input.plot(input_signal, color='black', linewidth=1.2)
        ax_input.set_title("YOUR VOICE (Input Signal)", fontweight='bold', loc='left')
        ax_input.set_facecolor('#e6e6e6')
        ax_input.set_yticks([])
        ax_input.axes.xaxis.set_visible(False)
        
        # --- PLOT 2-6: CANDIDATES ---
        for i, (word, score) in enumerate(sorted_scores):
            ax = axes[i+1]
            sample_sig = self.get_representative_wave(word)
            if sample_sig is not None:
                color = '#00aa00' if i == 0 else '#cc0000' # Green for winner, Red for others
                ax.plot(sample_sig, color=color, alpha=0.8, linewidth=1)
                ax.set_title(f"#{i+1}: {word.upper()} (Log-Likelihood: {score:.0f})", 
                             fontsize=10, loc='left', color=color, fontweight='bold')
            else:
                ax.text(0.5, 0.5, "No reference sample available", ha='center')
            ax.set_yticks([])
            ax.axes.xaxis.set_visible(False)
            
        plt.tight_layout()
        plt.subplots_adjust(top=0.93)
        
        # Save to log directory
        img_name = f"{filename_prefix}_check.png"
        save_path = os.path.join(current_logger.session_log_dir, img_name)
        plt.savefig(save_path)
        plt.close() # Free memory
        return save_path

    def extract_features(self, audio_path):
        """
        CORE DSP PIPELINE (Version 4 - Optimized for Robustness)
        Steps: Pre-emphasis -> Normalization -> Smart Trim -> MFCC -> Delta
        """
        try:
            signal, sr = librosa.load(audio_path, sr=Config.SAMPLE_RATE, mono=True)
            
            # 1. Pre-emphasis filter (High-pass)
            signal = librosa.effects.preemphasis(signal, coef=0.95)
            
            # 2. Amplitude Normalization
            max_amp = np.max(np.abs(signal))
            if max_amp < 0.005: return None, None # Signal is basically silence/noise
            signal = signal / max_amp 
            
            # 3. Smart Trim with Context Padding
            _, index = librosa.effects.trim(signal, top_db=25, frame_length=512, hop_length=128)
            start_idx, end_idx = index[0], index[1]
            
            pad_size = int(0.15 * sr) 
            final_start = max(0, start_idx - pad_size)
            final_end = min(len(signal), end_idx + pad_size)
            
            final_signal = signal[final_start:final_end]
            
            # Safety check
            if len(final_signal) < int(0.1 * sr): final_signal = signal 

            # 4. MFCC + Delta + Delta-Delta
            mfcc = librosa.feature.mfcc(y=final_signal, sr=sr, n_mfcc=Config.N_MFCC, 
                                        n_fft=Config.N_FFT, hop_length=Config.HOP_LENGTH)
            delta1 = librosa.feature.delta(mfcc, order=1)
            delta2 = librosa.feature.delta(mfcc, order=2)
            
            combined = np.concatenate((mfcc, delta1, delta2), axis=0).T
            return combined, final_signal
            
        except Exception as e:
            print(f"[DSP Error] {e}")
            return None, None

    def retrain_word(self, word):
        """
        INCREMENTAL LEARNING ENGINE
        Re-trains the HMM for a specific word using all available samples.
        """
        print(f">> [System] Retraining model for '{word}'...")
        word_dir = os.path.join(Config.DATA_DIR, word)
        
        # Gather all .wav files
        wav_files = [os.path.join(word_dir, f) for f in os.listdir(word_dir) if f.endswith('.wav')]
        if not wav_files: return

        # Extract features for all files
        X_train = []
        for wav_path in wav_files:
            feat, _ = self.extract_features(wav_path)
            if feat is not None:
                X_train.append(feat)
        
        if not X_train: return

        # Prepare data
        X_concat = np.concatenate(X_train)
        lengths = [len(x) for x in X_train]
        
        # --- ADAPTIVE TOPOLOGY ---
        n_components = Config.HMM_N_COMPONENTS
        if len(X_train) < 5: 
            n_components = 3 
            print(f"   -> Low data mode: Reduced states to {n_components}")

        try:
            # Re-initialize and fit
            model = hmm.GMMHMM(n_components=n_components, 
                               n_mix=Config.HMM_N_MIX, 
                               covariance_type='diag', 
                               n_iter=Config.HMM_ITER, 
                               verbose=False)
            model.fit(X_concat, lengths)
            
            # Update Memory and Disk
            self.models[word] = model
            joblib.dump(model, os.path.join(Config.MODEL_DIR, f"{word}.pkl"))
            print(f">> [Success] Model '{word}' updated (Total samples: {len(X_train)}).")
        except Exception as e:
            print(f">> [Error] Retraining failed: {e}")

    def save_and_learn(self, temp_path, correct_word):
        """
        Moves the temporary recording to the permanent dataset and triggers retraining.
        """
        # Create directory if it's a new word
        target_dir = os.path.join(Config.DATA_DIR, correct_word)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        
        # Generate unique filename
        new_filename = f"{correct_word}_added_{int(time.time())}.wav"
        new_path = os.path.join(target_dir, new_filename)
        
        # Save file
        shutil.copy(temp_path, new_path)
        print(f">> [Storage] Sample saved to: {new_path}")
        
        # Trigger learning
        self.retrain_word(correct_word)

    def record_and_process(self):
        """
        Main interaction cycle: Record -> Predict -> Generate Report -> Feedback.
        Returns: False if user requests exit, True otherwise.
        """
        print("\n" + "="*50)
        print(" WAITING: Hold [SPACE] to speak, Release to stop.")
        print("="*50)
        
        # 1. Wait for key press (Idle state)
        while True:
            if keyboard.is_pressed('p'): return False # Exit
            if keyboard.is_pressed('space'): break    # Start Recording
            time.sleep(0.01)

        # 2. Recording State
        print(">> RECORDING... (Microphone Active)")
        fs = Config.SAMPLE_RATE
        # Record into large buffer (6 seconds max)
        myrecording = sd.rec(int(6 * fs), samplerate=fs, channels=1)
        start_time = time.time()
        
        # Wait for key release
        while True: 
            if not keyboard.is_pressed('space') or (time.time()-start_time > 6): break
            time.sleep(0.01)
        sd.stop()
        
        # 3. Post-processing (Duration Check & Slicing)
        elapsed = time.time() - start_time
        if elapsed < 0.2:
            print("!! Too short (< 0.2s). Please speak clearer.")
            time.sleep(0.5)
            return True

        valid_samples = int(elapsed * fs)
        real_audio = myrecording[:valid_samples]
        
        # Save temporary file for processing
        temp_filename = f"temp_{int(time.time())}.wav"
        temp_path = os.path.join(current_logger.session_log_dir, temp_filename)
        write_wav(temp_path, fs, real_audio)
        
        # 4. Feature Extraction & Decoding
        features, signal = self.extract_features(temp_path)
        if features is None:
            print("!! Signal quality too low (Noise/Silence).")
            return True

        # Calculate Log-Likelihood for all models
        scores = {}
        for word, model in self.models.items():
            try: scores[word] = model.score(features)
            except: scores[word] = -float('inf')

        # Find the best match (Maximum Likelihood)
        best_word = "???"
        if scores:
            best_word = max(scores, key=scores.get)
        
        print(f"\n>> PREDICTION: [ {best_word.upper()} ]")
        
        # A. Quick Visualization (Comparison Chart)
        self.visualize_result(signal, scores, best_word, temp_filename)
        
        # B. DETAILED SCIENTIFIC REPORT (NEW FEATURE)
        print(">> Generating Technical Report...", end="")
        try:
            # Flatten the raw audio array for visualization
            raw_flat = real_audio.flatten()
            report_path = self.reporter.generate_all_reports(
                audio_path=temp_path,
                raw_signal=raw_flat, 
                scores=scores, 
                best_word=best_word, 
                timestamp=int(time.time())
            )
            print(f" Saved to: {report_path}")
        except Exception as e:
            print(f" Failed: {e}")

        # 5. Feedback Loop (Active Learning)
        # Flush keyboard buffer to prevent accidental input
        while keyboard.is_pressed('space'): time.sleep(0.05)
        
        print("\n--- FEEDBACK REQUIRED ---")
        user_input = input(f"Is '{best_word}' correct? (y/n): ").strip().lower()
        
        if user_input == 'y':
            print(">> Positive Feedback. Reinforcing model...")
            self.save_and_learn(temp_path, best_word)
            
        elif user_input == 'n':
            correct_word = input(">> Please enter the CORRECT word (or Enter to skip): ").strip().lower()
            if correct_word:
                self.save_and_learn(temp_path, correct_word)
            else:
                print(">> Skipped.")
        else:
            print(">> Skipped.")

        print("\n>> Ready for next cycle...")
        time.sleep(0.5)
        return True

    def run(self):
        """Entry point for the application loop."""
        print("--------------------------------------------------")
        print(" INTELLIGENT SPEECH RECOGNITION SYSTEM (ONLINE LEARNING)")
        print(" Press [P] to Exit program.")
        print("--------------------------------------------------")
        
        while self.is_running:
            try:
                should_continue = self.record_and_process()
                if not should_continue:
                    print("Exiting system. Goodbye!")
                    break
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    app = SmartRecognizer()
    app.run()