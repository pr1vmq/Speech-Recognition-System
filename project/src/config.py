"""
----------------------------------------------------------------------------------------------------
FILE: config.py
PROJECT: Communication Systems Engineering - Speech Recognition System
INSTITUTION: Ho Chi Minh City University of Technology (HCMUT)

DESCRIPTION:
    This module serves as the centralized configuration hub for the entire project.
    It defines immutable constants for:
    1. Dynamic File Paths: Automatically detects project root regardless of the operating system.
    2. Audio Processing: Parameters for signal processing (Sample rate, MFCC, FFT).
    3. HMM Hyperparameters: Tuning values for the Hidden Markov Models (States, Mixtures).
    4. System Settings: CPU utilization for parallel processing.

TECHNICAL OVERVIEW:
    - Signal Processing: Uses standard 16kHz sampling and MFCC feature extraction suitable for human speech.
    - Model: GMM-HMM architecture configured for isolated word recognition.
    - Infrastructure: Support for automatic directory generation and multi-core processing.

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
import multiprocessing

class Config:
    """
    Global configuration class. 
    All parameters are static to ensure consistency across modules.
    """

    # =========================================================================
    # 1. DIRECTORY & PATH CONFIGURATION (Dynamic Resolution)
    # =========================================================================
    
    # Get the absolute path of the directory containing this file (src/)
    _SRC_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Navigate one level up to get the Project Root Directory (project/)
    BASE_DIR = os.path.dirname(_SRC_DIR)

    # Define sub-directories based on the dynamic BASE_DIR
    # Use os.path.join for cross-platform compatibility (Windows/Linux/macOS)
    DATA_DIR = os.path.join(BASE_DIR, "sample")          # Raw audio samples
    LOG_DIR = os.path.join(BASE_DIR, "log")              # Execution logs & visualizations
    MODEL_DIR = os.path.join(BASE_DIR, "models")         # Trained HMM models (.pkl)
    OUTPUT_FEATURE_DIR = os.path.join(BASE_DIR, "features") # Intermediate feature files

    # List of folder names to ignore during data scanning (e.g., noise profiles)
    EXCLUDED_FOLDERS = ['_background_noise_', 'silence']

    # =========================================================================
    # 2. AUDIO SIGNAL PROCESSING PARAMETERS
    # =========================================================================
    
    # Sampling Rate (Hz). 16kHz is standard for wideband speech recognition.
    # It captures frequencies up to 8kHz (Nyquist limit), covering main human vocal formants.
    SAMPLE_RATE = 16000     
    
    # Target duration for standardizing/padding audio (in seconds).
    DURATION = 1            

    # MFCC (Mel-Frequency Cepstral Coefficients) Parameters
    # N_MFCC: Number of coefficients to retain. 13 is the standard for speech, 
    # capturing the vocal tract filter shape (timbre) while discarding pitch.
    N_MFCC = 13             
    
    # FFT Window Size. 512 samples @ 16kHz ~= 32ms window.
    # This duration is short enough for the signal to be considered stationary.
    N_FFT = 512             
    
    # Hop Length. Number of samples to slide the window.
    # 256 samples (50% overlap) ensures smooth feature transitions.
    HOP_LENGTH = 256        

    # Pre-emphasis coefficient (High-pass filter).
    # Used to amplify high frequencies (formants) that are naturally attenuated in speech.
    PRE_EMPHASIS_COEF = 0.97

    # =========================================================================
    # 3. HMM MODEL HYPERPARAMETERS
    # =========================================================================
    
    # Number of Hidden States in HMM.
    # 5 states are chosen to model the temporal evolution of a word (Start-Middle-End phonemes).
    # Topology: Left-to-Right (Bakis).
    HMM_N_COMPONENTS = 5  
    
    # Number of Gaussian Mixtures (GMM) per State.
    # 3 mixtures allow the model to capture variances in pronunciation (e.g., accents, pitch).
    HMM_N_MIX = 3         
    
    # Maximum number of iterations for the Baum-Welch training algorithm.
    HMM_ITER = 100        
    
    # Random seed for reproducibility of experiments.
    RANDOM_SEED = 42

    # =========================================================================
    # 4. SYSTEM & HARDWARE SETTINGS
    # =========================================================================
    
    # Number of CPU cores to use for parallel processing (Feature extraction/Training).
    # Logic: Use ~2/3 of available cores to prevent system freeze. Minimum is 1.
    N_JOBS = max(1, int(multiprocessing.cpu_count() * 0.67))

    @staticmethod
    def ensure_dirs():
        """
        Utility method to create necessary directory structure if it does not exist.
        This should be called at the start of the program.
        """
        required_dirs = [
            Config.DATA_DIR, 
            Config.LOG_DIR, 
            Config.MODEL_DIR, 
            Config.OUTPUT_FEATURE_DIR
        ]
        
        for directory in required_dirs:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory)
                    print(f"[Config] Created directory: {directory}")
                except OSError as e:
                    print(f"[Config] Error creating directory {directory}: {e}")

# Automatically ensure directories exist when this module is imported.
Config.ensure_dirs()