"""
----------------------------------------------------------------------------------------------------
FILE: create_dataset.py
PROJECT: Communication Systems Engineering - Speech Recognition System
INSTITUTION: Ho Chi Minh City University of Technology (HCMUT)

DESCRIPTION:
    This module is a utility tool designed for building custom speech datasets.
    It provides a Command Line Interface (CLI) for users to record audio samples 
    for specific vocabulary.

    Key Features:
    1. Push-to-Talk Mechanism: Records only when the SPACE bar is held down, ensuring 
       precise capture of the speech segment without needing complex VAD at this stage.
    2. Automatic Organization: Creates labeled directories and handles file naming 
       conventions (e.g., word_001.wav, word_002.wav).
    3. Signal Standardization: Immediately saves audio in the project's standard format 
       (16kHz, Mono, 16-bit PCM) defined in Config.

TECHNICAL OVERVIEW:
    - Input: Microphone audio via 'sounddevice'.
    - Control: Keyboard event handling via 'keyboard' library.
    - Output: .wav files stored in the 'sample/' directory.

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
import sounddevice as sd
import numpy as np
import keyboard
from scipy.io.wavfile import write as write_wav

# Import project configuration
from config import Config

def record_sample(word, index):
    """
    Captures a single audio sample for a given word.
    
    Parameters:
        word (str): The label of the word being recorded (e.g., 'hello').
        index (int): The sequence number of the sample (used for filename).
        
    Returns:
        bool: True if recording was successful and saved, False otherwise.
    """
    
    # Use global sampling rate from config
    fs = Config.SAMPLE_RATE
    
    # Maximum allowed duration for a single word (buffer size)
    max_duration = 4 
    
    # -------------------------------------------------------------------------
    # 1. WAIT FOR USER INTERACTION
    # -------------------------------------------------------------------------
    print(f"\n--- Sample #{index:03d}: HOLD [SPACE] to record '{word}' ---")
    
    # Block execution until the Space key is pressed down
    keyboard.wait('space')
    
    print(">> RECORDING... (Release SPACE to stop)")
    start_time = time.time()
    
    # -------------------------------------------------------------------------
    # 2. NON-BLOCKING RECORDING
    # -------------------------------------------------------------------------
    # Record into a buffer for max_duration. 
    # We will slice this buffer later based on actual hold time.
    myrecording = sd.rec(int(max_duration * fs), samplerate=fs, channels=1)
    
    # -------------------------------------------------------------------------
    # 3. PUSH-TO-TALK LOGIC (Active Loop)
    # -------------------------------------------------------------------------
    while True:
        # Check if the Space key has been released
        if not keyboard.is_pressed('space'):
            break
            
        # Check if maximum duration is exceeded
        if (time.time() - start_time) > max_duration:
            break
            
        # Small sleep to prevent high CPU usage during this polling loop
        time.sleep(0.01)
        
    # Stop the recording stream immediately
    sd.stop()
    
    # -------------------------------------------------------------------------
    # 4. POST-PROCESSING & VALIDATION
    # -------------------------------------------------------------------------
    # Calculate exact duration the key was held
    elapsed = time.time() - start_time
    
    # Validation: Reject samples that are too short (likely accidental clicks)
    if elapsed < 0.2:
        print("!! Too short (< 0.2s). Sample ignored. Please speak clearly.")
        return False

    # Slicing: Keep only the recorded portion, discard the rest of the buffer
    valid_samples = int(elapsed * fs)
    myrecording = myrecording[:valid_samples]
    
    # -------------------------------------------------------------------------
    # 5. SAVE TO DISK
    # -------------------------------------------------------------------------
    # Ensure the directory exists: data/word/
    save_dir = os.path.join(Config.DATA_DIR, word)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    # Format filename: word_001.wav, word_002.wav...
    filename = f"{word}_{index:03d}.wav"
    filepath = os.path.join(save_dir, filename)
    
    # Write to WAV file
    write_wav(filepath, fs, myrecording)
    print(f">> Saved: {filename} (Duration: {elapsed:.2f}s)")
    
    # -------------------------------------------------------------------------
    # 6. DEBOUNCE / COOL-DOWN
    # -------------------------------------------------------------------------
    # Pause for 0.5s to allow the user to lift their finger completely.
    # This prevents the next loop from immediately triggering if the key is sticky.
    time.sleep(0.5) 
    
    return True

def main():
    """
    Main entry point for the dataset creation tool.
    Handles the user interface loop for word selection and recording management.
    """
    print("========================================================")
    print("      CUSTOM DATASET CREATOR TOOL")
    print(f"      Target Directory: {Config.DATA_DIR}")
    print("========================================================")
    print("INSTRUCTIONS:")
    print("1. Enter the word label you want to record.")
    print("2. Hold [SPACE] to speak, Release to stop.")
    print("3. Press [ESC] to switch to a new word.")
    print("========================================================\n")
    
    while True:
        # ---------------------------------------------------------------------
        # PHASE 1: WORD SELECTION
        # ---------------------------------------------------------------------
        word = input("\n>>> Enter word label (or type 'exit' to quit): ").strip().lower()
        
        if word == 'exit':
            print("Exiting tool. Goodbye!")
            break
            
        if word == '':
            continue # Ignore empty input
        
        # Check for existing samples to continue numbering correctly
        save_dir = os.path.join(Config.DATA_DIR, word)
        existing_files = []
        if os.path.exists(save_dir):
            existing_files = [f for f in os.listdir(save_dir) if f.endswith('.wav')]
        
        current_index = len(existing_files) + 1
        print(f"-> Found {len(existing_files)} existing samples for '{word}'.")
        print(f"-> Starting recording at index #{current_index:03d}")
        
        # ---------------------------------------------------------------------
        # PHASE 2: RECORDING LOOP
        # ---------------------------------------------------------------------
        while True:
            # Record a single sample
            success = record_sample(word, current_index)
            
            if success:
                current_index += 1
            
            # -----------------------------------------------------------------
            # PHASE 3: NAVIGATION DECISION
            # -----------------------------------------------------------------
            print("-" * 50)
            print("  [SPACE] : Record another sample")
            print("  [ESC]   : Finish and switch to new word")
            print("-" * 50)
            
            decision = None
            
            # Wait for user decision (Blocking wait with CPU optimization)
            while True:
                if keyboard.is_pressed('space'):
                    decision = 'continue'
                    break
                if keyboard.is_pressed('esc'):
                    decision = 'new_word'
                    break
                time.sleep(0.05) 
            
            # Handle decision
            if decision == 'new_word':
                # Wait for ESC release to prevent accidental triggers in main loop
                while keyboard.is_pressed('esc'): time.sleep(0.05)
                print(f"\nFinished recording for '{word}'. Returning to menu...")
                break 
            
            elif decision == 'continue':
                # Wait for SPACE release to prevent accidental recording trigger
                while keyboard.is_pressed('space'): time.sleep(0.05)
                print("\n> Preparing next sample...")
                time.sleep(0.2) # Short pause for UI smoothness

if __name__ == "__main__":
    main()