"""
----------------------------------------------------------------------------------------------------
FILE: visualizer.py
PROJECT: Communication Systems Engineering - Speech Recognition System
INSTITUTION: HCMUT

DESCRIPTION:
    This module provides advanced visualization tools for the Inference Phase.
    It generates a comprehensive 'Scientific Report' for every single prediction trial.

    Generated Artifacts per Trial:
    1. DSP Analysis: Input Waveform -> Pre-emphasis -> VAD Trim.
    2. Spectral Analysis: Mel-Spectrogram & MFCC Heatmaps.
    3. Decision Analysis: Bar chart showing Log-Likelihood scores of Top 5 candidates.

AUTHORS:
    1. Do Ngoc Gia Bao    - ID: 2110778
    2. Thai Duc Thien     - ID: 2313222
    3. Pham Minh Quang    - ID: 2312807
----------------------------------------------------------------------------------------------------
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
from config import Config

class ReportGenerator:
    """
    Helper class to generate scientific charts for each inference trial.
    """
    
    def __init__(self, session_dir):
        """
        Args:
            session_dir (str): Path to the current log folder (e.g., log/2026-01-24...)
        """
        self.save_dir = session_dir

    def generate_all_reports(self, audio_path, raw_signal, scores, best_word, timestamp):
        """
        Master function to trigger all plots.
        """
        # Create a sub-folder for this specific trial to keep things organized
        trial_dir = os.path.join(self.save_dir, f"Trial_{timestamp}_{best_word}")
        if not os.path.exists(trial_dir):
            os.makedirs(trial_dir)

        # 1. Plot Signal Processing Steps
        self._plot_dsp_steps(raw_signal, trial_dir)

        # 2. Plot Feature Extraction (Spectrogram/MFCC)
        self._plot_features(audio_path, trial_dir)

        # 3. Plot Decision Confidence
        self._plot_confidence(scores, best_word, trial_dir)

        return trial_dir

    def _plot_dsp_steps(self, raw_signal, save_dir):
        """
        Visualizes the transformation of the signal in time domain.
        """
        try:
            # Re-create the steps (Simulation)
            # 1. Pre-emphasis
            pre_emph = librosa.effects.preemphasis(raw_signal, coef=0.95)
            # 2. Trim (Simulated for visual)
            trimmed, _ = librosa.effects.trim(pre_emph, top_db=25)

            plt.figure(figsize=(10, 8), dpi=100)
            
            plt.subplot(3, 1, 1)
            plt.plot(raw_signal, color='gray', linewidth=0.8)
            plt.title("Step 1: Raw Input Signal", fontweight='bold')
            plt.margins(x=0)
            
            plt.subplot(3, 1, 2)
            plt.plot(pre_emph, color='#1f77b4', linewidth=0.8)
            plt.title("Step 2: Pre-emphasis (High-freq Boost)", fontweight='bold')
            plt.margins(x=0)

            plt.subplot(3, 1, 3)
            plt.plot(trimmed, color='#2ca02c', linewidth=0.8)
            plt.title("Step 3: After VAD Trimming (Input to MFCC)", fontweight='bold')
            plt.margins(x=0)
            plt.xlabel("Samples")

            plt.tight_layout()
            plt.savefig(os.path.join(save_dir, "1_DSP_Analysis.png"))
            plt.close()
        except Exception as e:
            print(f"[Vis Error] DSP Plot: {e}")

    def _plot_features(self, audio_path, save_dir):
        """
        Visualizes the frequency domain features.
        """
        try:
            y, sr = librosa.load(audio_path, sr=Config.SAMPLE_RATE)
            y = librosa.effects.preemphasis(y, coef=0.95)
            
            # Compute Spectrogram
            D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
            # Compute MFCC
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

            plt.figure(figsize=(10, 8), dpi=100)
            
            plt.subplot(2, 1, 1)
            librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log')
            plt.colorbar(format='%+2.0f dB')
            plt.title("Frequency Domain: Mel-Spectrogram", fontweight='bold')
            
            plt.subplot(2, 1, 2)
            librosa.display.specshow(mfcc, sr=sr, x_axis='time')
            plt.colorbar()
            plt.title("Cepstral Domain: MFCC Vectors (Model Input)", fontweight='bold')
            plt.ylabel("Coefficients")

            plt.tight_layout()
            plt.savefig(os.path.join(save_dir, "2_Spectral_Analysis.png"))
            plt.close()
        except Exception as e:
            print(f"[Vis Error] Feature Plot: {e}")

    def _plot_confidence(self, scores, best_word, save_dir):
        """
        Visualizes the decision making process (Top 5 Candidates).
        """
        try:
            # Sort scores
            sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
            words = [item[0].upper() for item in sorted_items]
            values = [item[1] for item in sorted_items]

            # Normalize for better visualization (Relative to max)
            # Since scores are negative log-likelihoods (e.g., -1500, -2000)
            # We shift them so the winner is at 0.
            max_val = values[0]
            rel_values = [v - max_val for v in values] 

            plt.figure(figsize=(8, 5), dpi=100)
            bars = plt.barh(words, rel_values, color=['green' if w==best_word.upper() else 'gray' for w in words])
            plt.gca().invert_yaxis() # Top winner at top
            
            plt.title(f"Decision Confidence (Winner: {best_word.upper()})", fontweight='bold')
            plt.xlabel("Relative Log-Likelihood (Close to 0 is better)")
            plt.grid(axis='x', linestyle='--', alpha=0.5)
            
            # Add labels
            for i, v in enumerate(rel_values):
                plt.text(v, i, f" {values[i]:.0f}", va='center', fontweight='bold')

            plt.tight_layout()
            plt.savefig(os.path.join(save_dir, "3_Decision_Analysis.png"))
            plt.close()
        except Exception as e:
            print(f"[Vis Error] Confidence Plot: {e}")