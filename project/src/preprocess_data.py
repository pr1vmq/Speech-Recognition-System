"""
----------------------------------------------------------------------------------------------------
FILE: preprocess_data.py
PROJECT: Communication Systems Engineering - Speech Recognition System
INSTITUTION: Ho Chi Minh City University of Technology (HCMUT)

DESCRIPTION:
    This module handles the Offline Data Preparation Phase (Stage 1 & 2).
    It transforms raw audio files (.wav) into a machine-readable dataset of feature vectors.

    Key Operations:
    1. Batch Processing: Scans the 'sample/' directory to identify vocabulary classes.
    2. Advanced Signal Processing (DSP Pipeline V4):
       - Pre-emphasis: Boosts high frequencies to capture fricatives (/s/, /f/).
       - Normalization: Standardizes amplitude across all samples.
       - Smart VAD: Trims silence while preserving onset/offset padding for plosives.
    3. Feature Extraction: Computes MFCCs (Static) + Delta (Velocity) + Delta-Delta (Acceleration).
    4. Parallelization: Utilizes multi-core CPUs via 'joblib' to speed up processing of 
       large datasets (100k+ files).

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
import librosa
import numpy as np
import joblib 
from tqdm import tqdm 

# Import project configuration and utilities
from config import Config
from utils import current_logger

def process_single_file(file_path, word_label, save_visuals=False):
    """
    Processes a single audio file through the full DSP pipeline.
    
    Parameters:
        file_path (str): Absolute path to the .wav file.
        word_label (str): The vocabulary word corresponding to this file (Ground Truth).
        save_visuals (bool): If True, generates and saves a waveform plot (for debugging).
        
    Returns:
        dict: A dictionary containing the feature matrix and the label, 
              or None if processing fails.
    """
    try:
        # ---------------------------------------------------------------------
        # STEP 1: LOAD AUDIO
        # ---------------------------------------------------------------------
        # Load and resample to 16kHz (Standard Wideband Speech)
        # mono=True ensures we process a single channel.
        signal, sr = librosa.load(file_path, sr=Config.SAMPLE_RATE, mono=True)

        # ---------------------------------------------------------------------
        # STEP 2: SIGNAL ENHANCEMENT (Pipeline V4)
        # ---------------------------------------------------------------------
        # 2.1. Pre-emphasis: y(t) = x(t) - 0.95*x(t-1)
        # Compensates for the -6dB/octave rolloff in human speech radiation.
        # Crucial for detecting high-frequency consonants like 's' in 'Six'.
        signal = librosa.effects.preemphasis(signal, coef=0.95)

        # 2.2. Amplitude Normalization
        # Scales the signal to the range [-1, 1] to match the volume level 
        # of the Google Dataset (which is normalized) with user recording.
        max_amp = np.max(np.abs(signal))
        if max_amp < 0.005: 
            return None # Reject silence/noise
        signal = signal / max_amp

        # 2.3. Smart Trim with Context Padding
        # Standard trim cuts abruptly at the threshold. We use 'index' to find 
        # boundaries and add padding (~150ms) to keep breath/plosive sounds.
        _, index = librosa.effects.trim(signal, top_db=25, frame_length=512, hop_length=128)
        start_idx, end_idx = index[0], index[1]
        
        pad_size = int(0.15 * sr) 
        final_start = max(0, start_idx - pad_size)
        final_end = min(len(signal), end_idx + pad_size)
        
        final_signal = signal[final_start:final_end]

        # Validation: If signal is too short after trimming, revert to original
        # to prevent FFT errors on empty arrays.
        if len(final_signal) < int(0.1 * sr):
            final_signal = signal

        # ---------------------------------------------------------------------
        # STEP 3: VISUALIZATION (Optional)
        # ---------------------------------------------------------------------
        if save_visuals:
             filename_img = f"wave_{word_label}_{os.path.basename(file_path)}.png"
             current_logger.save_waveform(final_signal, sr, filename_img, title=f"Processed: {word_label}")

        # ---------------------------------------------------------------------
        # STEP 4: FEATURE EXTRACTION
        # ---------------------------------------------------------------------
        # Extract Mel-Frequency Cepstral Coefficients (MFCCs)
        # n_fft=512 (~32ms window), hop_length=256 (~16ms overlap)
        mfcc = librosa.feature.mfcc(y=final_signal, sr=sr, n_mfcc=Config.N_MFCC, 
                                    n_fft=Config.N_FFT, hop_length=Config.HOP_LENGTH)
        
        # Calculate Derivatives (Temporal Dynamics)
        # Delta: Velocity of change (Rate of change of MFCC)
        # Delta-Delta: Acceleration of change
        delta1 = librosa.feature.delta(mfcc, order=1)
        delta2 = librosa.feature.delta(mfcc, order=2)

        # Concatenate features along the frequency axis
        # Final shape: [n_frames, 39] (13 static + 13 delta + 13 accel)
        combined_features = np.concatenate((mfcc, delta1, delta2), axis=0).T

        return {
            "features": combined_features,
            "label": word_label,
            "path": file_path
        }

    except Exception as e:
        # Silently fail on corrupt files to keep the batch running
        # Real-world datasets often contain a few broken headers.
        return None

def main_preprocess():
    """
    Main driver function for data preprocessing.
    Scans directories, distributes work across CPU cores, and serializes results.
    """
    current_logger.log("==================================================")
    current_logger.log("      STAGE 1 & 2: DATA PREPROCESSING (V4)")
    current_logger.log("==================================================")
    current_logger.log(f"Configuration: {Config.N_JOBS} CPU Cores | {Config.SAMPLE_RATE} Hz")

    all_files = []
    
    # -------------------------------------------------------------------------
    # 1. DIRECTORY SCANNING
    # -------------------------------------------------------------------------
    current_logger.log("Scanning dataset structure...")
    
    # Filter valid directories (ignore noise folders or hidden files)
    words = [d for d in os.listdir(Config.DATA_DIR) 
             if os.path.isdir(os.path.join(Config.DATA_DIR, d)) 
             and d not in Config.EXCLUDED_FOLDERS]
    
    current_logger.log(f"Found {len(words)} classes (vocabulary): {words}")

    # Gather all .wav files into a flat list
    for word in words:
        word_path = os.path.join(Config.DATA_DIR, word)
        wav_files = [f for f in os.listdir(word_path) if f.endswith('.wav')]
        for f in wav_files:
            all_files.append((os.path.join(word_path, f), word))

    current_logger.log(f"Total audio samples found: {len(all_files)}")
    
    # -------------------------------------------------------------------------
    # 2. PARALLEL FEATURE EXTRACTION
    # -------------------------------------------------------------------------
    current_logger.log("Starting Feature Extraction (MFCC + Delta + Delta-Delta)...")
    
    # Use joblib to parallelize the 'process_single_file' function.
    # We only save visual plots for the first 2 files of each folder to save disk space.
    processed_data = joblib.Parallel(n_jobs=Config.N_JOBS)(
        joblib.delayed(process_single_file)(
            path, 
            label, 
            save_visuals=(i < 2) 
        ) 
        for i, (path, label) in enumerate(tqdm(all_files, desc="Processing", unit="file"))
    )

    # -------------------------------------------------------------------------
    # 3. DATA CLEANUP & SERIALIZATION
    # -------------------------------------------------------------------------
    # Remove failed entries (None)
    valid_data = [d for d in processed_data if d is not None]
    current_logger.log(f"Successfully processed {len(valid_data)}/{len(all_files)} files.")

    # Save to disk as a binary pickle file
    # This file will be loaded by 'train_model.py'
    output_path = os.path.join(Config.OUTPUT_FEATURE_DIR, "all_features.pkl")
    joblib.dump(valid_data, output_path)
    
    current_logger.log(f"Feature dataset saved to: {output_path}")
    current_logger.log("PREPROCESSING COMPLETED SUCCESSFULLY.")

if __name__ == "__main__":
    # Standard boilerplate to ensure multiprocessing works on Windows
    main_preprocess()