"""
----------------------------------------------------------------------------------------------------
FILE: train_model.py
PROJECT: Communication Systems Engineering - Speech Recognition System
INSTITUTION: Ho Chi Minh City University of Technology (HCMUT)

DESCRIPTION:
    This module executes Stage 3 of the pipeline: Acoustic Model Training.
    It trains a separate Hidden Markov Model (HMM) for each word in the vocabulary 
    using the extracted feature vectors.

    Key Algorithms & Techniques:
    1. GMM-HMM Architecture: Uses Gaussian Mixture Models (GMM) to model the emission 
       probabilities of HMM states. This handles the variance in speaker voices.
    2. Baum-Welch Algorithm: An Expectation-Maximization (EM) algorithm used to find 
       the unknown parameters of the HMM (Transition matrix, Means, Variances) that 
       maximize the likelihood of the training data.
    3. Robust Training Strategy: Implements 'Adaptive Topology'.
       - Normal Data (>5 samples): Uses standard 5-state HMM.
       - Scarce Data (<5 samples): Automatically reduces to 3-state or 1-state HMM 
         to prevent overfitting and convergence errors (Singularity matrix).
    4. Parallel Processing: Trains multiple word models simultaneously using CPU cores.

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
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from hmmlearn import hmm
from tqdm import tqdm

# Import project configuration and utilities
from config import Config
from utils import current_logger

def load_processed_data():
    """
    Loads the serialized feature dataset (from Stage 2) into memory.
    
    Returns:
        list: A list of dictionaries containing features and labels.
    """
    feat_path = os.path.join(Config.OUTPUT_FEATURE_DIR, "all_features.pkl")
    
    if not os.path.exists(feat_path):
        current_logger.log(f"[Error] Feature file not found at {feat_path}.")
        current_logger.log("        Please run 'preprocess_data.py' first.")
        return None
    
    current_logger.log(f"Loading feature dataset from: {feat_path}...")
    return joblib.load(feat_path)

def group_data_by_word(data):
    """
    Reorganizes the flat dataset list into a dictionary grouped by word label.
    
    Returns:
        dict: { 'hello': [feature_matrix_1, feature_matrix_2, ...], 'world': [...] }
    """
    dataset = {}
    for item in data:
        label = item['label']
        if label not in dataset:
            dataset[label] = []
        dataset[label].append(item['features'])
    return dataset

def train_single_hmm(word, X_train):
    """
    Trains a single GMM-HMM model for a specific word.
    
    Parameters:
        word (str): The vocabulary label (e.g., 'seven').
        X_train (list): List of feature matrices (MFCCs) for this word.
        
    Returns:
        hmm.GMMHMM: The trained model object, or None if training fails.
    """
    try:
        # Safety check for empty data
        if not X_train or len(X_train) == 0:
            return None

        # ---------------------------------------------------------------------
        # DATA PREPARATION FOR HMMLEARN
        # ---------------------------------------------------------------------
        # hmmlearn expects a single concatenated matrix of all samples,
        # along with a 'lengths' list indicating the size of each sample.
        X_concat = np.concatenate(X_train)
        lengths = [len(x) for x in X_train]

        # ---------------------------------------------------------------------
        # ADAPTIVE TOPOLOGY (Robustness Logic)
        # ---------------------------------------------------------------------
        # Standard configuration from Config
        n_components = Config.HMM_N_COMPONENTS
        n_mix = Config.HMM_N_MIX
        
        # If dataset is extremely small (User just added a new word with 1-2 samples),
        # a complex 5-state model will fail to converge. We reduce complexity.
        if len(X_train) < 5:
            n_components = 3  # Simplified topology
            # n_mix could also be reduced if necessary
            
        if len(X_train) < 3:
             n_components = 1 # Extreme fallback for single-sample training

        # ---------------------------------------------------------------------
        # MODEL INITIALIZATION
        # ---------------------------------------------------------------------
        # covariance_type='diag': Assumes feature dimensions are independent.
        # This is computationally efficient and standard for diagonal MFCCs.
        model = hmm.GMMHMM(n_components=n_components, 
                           n_mix=n_mix, 
                           covariance_type='diag', 
                           n_iter=Config.HMM_ITER,
                           random_state=Config.RANDOM_SEED,
                           verbose=False)

        # ---------------------------------------------------------------------
        # BAUM-WELCH TRAINING (EM Algorithm)
        # ---------------------------------------------------------------------
        model.fit(X_concat, lengths)
        
        return model

    except Exception as e:
        # Fallback Strategy: If training fails (e.g., matrix singularity),
        # try one last time with the simplest possible model (1 State, 1 Mixture).
        try:
             # current_logger.log(f"Warning: Complex model failed for '{word}'. Retrying with simple model.")
             model = hmm.GMMHMM(n_components=1, n_mix=1, covariance_type='diag', n_iter=10)
             model.fit(X_concat, lengths)
             return model
        except:
            current_logger.log(f"[Error] Failed to train model for '{word}': {str(e)}")
            return None

def main_train():
    """
    Main execution flow for Model Training.
    """
    current_logger.log("==================================================")
    current_logger.log("      STAGE 3: HMM ACOUSTIC MODEL TRAINING")
    current_logger.log("==================================================")

    # 1. Load Data
    raw_data = load_processed_data()
    if raw_data is None: return

    # 2. Group Data
    dataset_by_word = group_data_by_word(raw_data)
    
    train_set = {}
    test_set = {}
    
    current_logger.log("Splitting Dataset (Train vs Test)...")
    
    # -------------------------------------------------------------------------
    # 3. SMART DATA SPLITTING
    # -------------------------------------------------------------------------
    for word, samples in dataset_by_word.items():
        n_samples = len(samples)
        
        if n_samples == 0: continue
            
        # Strategy for Small Datasets (e.g., Custom user recordings)
        # If samples < 5, we cannot afford to set aside 20% for testing.
        # Use 100% for training to ensure the model learns something.
        if n_samples < 5:
            current_logger.log(f"   -> Word '{word}': Low data ({n_samples}). Using ALL for training.")
            X_train = samples
            X_test = [] 
        else:
            # Standard Strategy: 80% Train, 20% Test
            try:
                X_train, X_test = train_test_split(samples, test_size=0.2, random_state=Config.RANDOM_SEED)
            except ValueError:
                # Safety fallback
                X_train = samples
                X_test = []

        train_set[word] = X_train
        test_set[word] = X_test
        
    # Save Test Set for later evaluation (Stage 5)
    test_set_path = os.path.join(Config.OUTPUT_FEATURE_DIR, "test_set.pkl")
    joblib.dump(test_set, test_set_path)
    current_logger.log(f"Test set separated and saved to: {test_set_path}")

    # -------------------------------------------------------------------------
    # 4. PARALLEL TRAINING EXECUTION
    # -------------------------------------------------------------------------
    words = list(train_set.keys())
    current_logger.log(f"Starting parallel training for {len(words)} models on {Config.N_JOBS} CPU cores...")

    # Execute 'train_single_hmm' for each word in parallel
    results = joblib.Parallel(n_jobs=Config.N_JOBS)(
        joblib.delayed(train_single_hmm)(word, train_set[word]) 
        for word in tqdm(words, desc="Training Progress", unit="model")
    )

    # -------------------------------------------------------------------------
    # 5. SERIALIZE MODELS
    # -------------------------------------------------------------------------
    successful_models = 0
    for word, model in zip(words, results):
        if model is not None:
            # Save model to .pkl file
            model_path = os.path.join(Config.MODEL_DIR, f"{word}.pkl")
            joblib.dump(model, model_path)
            successful_models += 1
            
    current_logger.log(f"TRAINING COMPLETED.")
    current_logger.log(f"Successfully saved {successful_models}/{len(words)} models to '{Config.MODEL_DIR}'.")

if __name__ == "__main__":
    main_train()