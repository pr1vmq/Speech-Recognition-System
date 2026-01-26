"""
----------------------------------------------------------------------------------------------------
FILE: utils.py
PROJECT: Communication Systems Engineering - Speech Recognition System
INSTITUTION: Ho Chi Minh City University of Technology (HCMUT)

DESCRIPTION:
    This module provides utility services used throughout the application.
    It implements a centralized 'Logger' class responsible for:
    1. Session Management: Creates a unique, timestamped directory for each program run.
    2. Event Logging: Records system activities and errors to both the console and a text file.
    3. Data Visualization: Generates high-quality waveform plots of audio signals using 
       'matplotlib' and 'librosa', essential for debugging and reporting.

    Design Pattern:
    - Singleton Instance: A global 'current_logger' object is instantiated at the end 
      of this file to ensure all modules write to the same log session.

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
import matplotlib.pyplot as plt
import librosa
import librosa.display
import numpy as np
from datetime import datetime

# Import project configuration
from config import Config

class Logger:
    """
    Handles file system operations for logging and saving visualization artifacts.
    """

    def __init__(self):
        """
        Initializes the logger. 
        Creates a new directory named with the current timestamp inside the LOG_DIR.
        Example: log/2026-01-24_16-30-00/
        """
        # Generate timestamp for unique session identification
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Define the session directory path
        self.session_log_dir = os.path.join(Config.LOG_DIR, self.timestamp)
        
        # Create the directory
        if not os.path.exists(self.session_log_dir):
            try:
                os.makedirs(self.session_log_dir)
            except OSError as e:
                print(f"[Fatal Error] Could not create log directory: {e}")
                return

        # Define the main text log file
        self.log_file = os.path.join(self.session_log_dir, "process_log.txt")
        
        # Initialize the log file with a header
        self.log(f"Session started at {self.timestamp}")
        self.log(f"Project Root: {Config.BASE_DIR}")

    def log(self, message):
        """
        Writes a message to the console and appends it to the log file.
        
        Parameters:
            message (str): The text content to log.
        """
        # Current time for the log entry
        time_str = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"[{time_str}] {message}"
        
        # 1. Print to Console
        print(formatted_message)
        
        # 2. Append to File
        # Use 'utf-8' encoding to support special characters if needed
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(formatted_message + "\n")
        except IOError as e:
            print(f"[Logger Error] Could not write to file: {e}")

    def save_waveform(self, signal, sr, filename, title="Waveform"):
        """
        Generates and saves a waveform plot of the audio signal.
        
        Parameters:
            signal (np.array): The audio time-series data.
            sr (int): Sampling rate (Hz).
            filename (str): Output filename (e.g., 'wave_test.png').
            title (str): Title to display on the chart.
            
        Returns:
            str: Absolute path to the saved image, or None if failed.
        """
        save_path = os.path.join(self.session_log_dir, filename)
        
        try:
            # Create a figure with high DPI for report quality
            plt.figure(figsize=(10, 4), dpi=150)
            
            # Plot the waveform
            librosa.display.waveshow(signal, sr=sr, alpha=0.8, color='#007acc')
            
            # Add chart details
            plt.title(title, fontsize=12, fontweight='bold')
            plt.xlabel("Time (s)")
            plt.ylabel("Amplitude")
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.tight_layout()
            
            # Save to disk
            plt.savefig(save_path)
            
            # CRITICAL: Close the plot to free memory (RAM). 
            # Matplotlib keeps figures in memory unless explicitly closed.
            plt.close()
            
            return save_path
            
        except Exception as e:
            self.log(f"[Visualization Error] Failed to save waveform '{filename}': {e}")
            return None

# =============================================================================
# GLOBAL INSTANCE
# =============================================================================
# Instantiate the Logger once. All other modules will import 'current_logger'.
# This acts as a Singleton pattern for the application session.
current_logger = Logger()