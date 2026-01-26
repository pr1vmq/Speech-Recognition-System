
# Intelligent Speech Recognition System (GMM-HMM)

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![Status](https://img.shields.io/badge/Status-Completed-green.svg)
![Institution](https://img.shields.io/badge/HCMUT-Communication%20Systems-red.svg)

> **Course:** Communication Systems Engineering 
> **Institution:** Ho Chi Minh City University of Technology (HCMUT - VNU)  
> **Instructor:** Mr. Nguyen Chi Ngoc

## 📖 Introduction

This project implements a robust **Isolated Word Recognition System** utilizing **Gaussian Mixture Models combined with Hidden Markov Models (GMM-HMM)**.

Unlike modern Deep Learning approaches (CNN/RNN), this system is built upon classical statistical signal processing principles, offering high interpretability and efficiency on low-resource hardware. It features a complete pipeline from raw audio acquisition to real-time inference and active learning.

### 👥 Authors
| Student Name | Student ID | 
| :--- | :--- |
| **Do Ngoc Gia Bao** | **2110778** |
| **Thai Duc Thien** | **2313222** |
| **Pham Minh Quang** | **2312807** |

---

## 🚀 Key Features

* **Push-to-Talk Interface:** Intuitive control mechanism mimicking walkie-talkies (Hold Space to speak).
* **Robust DSP Pipeline (V4):** Advanced preprocessing including Pre-emphasis filter, Amplitude Normalization, and Padding-based Silence Trimming to handle environmental noise and plosive sounds.
* **Active Learning (Online Mode):** The system learns from its mistakes in real-time. Users can correct predictions, and the system performs incremental retraining instantly.
* **Adaptive Topology:** Automatically adjusts HMM complexity (states/mixtures) based on the amount of available data to prevent overfitting.
* **Visual Feedback:** Generates comparison waveforms between user input and dataset references for debugging and analysis.

---

## 🛠️ System Architecture

The processing pipeline consists of 5 main stages:

1.  **Acquisition:** Capture 16kHz Mono Audio via `sounddevice`.
2.  **Preprocessing:** Noise reduction, Pre-emphasis ($\alpha=0.95$), and Smart VAD.
3.  **Feature Extraction:** 39-dimensional feature vector per frame (13 MFCCs + 13 $\Delta$ + 13 $\Delta\Delta$).
4.  **Decoding:** Maximum Likelihood Estimation using the **Viterbi Algorithm** across 35+ HMM models.
5.  **Feedback Loop:** User verification triggers the **Baum-Welch** algorithm for model updates.

---

## ⚙️ Installation

### Prerequisites
* Python 3.10 or higher.
* Microphone input.
* (Windows) Microsoft C++ Build Tools (required for `hmmlearn`).

### Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd project
    ```

2.  **Install Dependencies:**
    * **Windows:** Run `install_windows.bat`
    * **macOS/Linux:** Run `install_macos.sh` or `install_linux.sh`
    
    *Or manually:*
    ```bash
    pip install -r requirements.txt
    ```

---

## 🖥️ Usage Guide

### 1. Build your Dataset (Optional)
If you want to create a custom vocabulary from scratch:
```bash
python src/create_dataset.py

```

* Enter a word label (e.g., `light_on`).
* Hold **SPACE** to record multiple samples.

### 2. Preprocess Data

Convert raw `.wav` files into feature vectors (`.pkl`):

```bash
python src/preprocess_data.py

```

* *Output:* `features/all_features.pkl`

### 3. Train Models

Train the HMMs for all vocabulary words:

```bash
python src/train_model.py

```

* *Output:* `.pkl` models in `models/` directory.

### 4. Run Inference (Demo Mode)

For standard usage/demonstration:

```bash
python src/main_app.py

```

* **Hold SPACE** to record.
* **Release** to predict.

### 5. Run Active Learning (Smart Mode)

For testing and teaching the system new words on-the-fly:

```bash
python src/main_ml.py

```

* After prediction, type `y` (correct) or `n` (incorrect) to update the model.

---

## 📂 Project Structure

```text
project/
├── sample/                 # Raw Audio Dataset (e.g., sample/hello/*.wav)
├── log/                    # Runtime logs and waveform visualizations
├── models/                 # Trained HMM models (.pkl)
├── features/               # Extracted feature vectors (.pkl)
├── requirements.txt        # Python dependencies
├── install_windows.bat     # Setup script
│
└── src/                    # Source Code
    ├── config.py           # Central configuration
    ├── utils.py            # Logger & Visualization tools
    ├── create_dataset.py   # Dataset recording tool
    ├── preprocess_data.py  # MFCC extraction pipeline
    ├── train_model.py      # HMM training logic
    ├── main_app.py         # Standard Inference App
    └── main_ml.py          # Active Learning App

```

---

## ⚠️ Troubleshooting

**1. `hmmlearn` installation fails:**

* Ensure you have **Microsoft C++ Build Tools** installed on Windows.
* Alternatively, try installing via conda: `conda install -c conda-forge hmmlearn`

**2. Microphone not detected:**

* Check your OS privacy settings to allow Python to access the microphone.
* Ensure `sounddevice` is correctly installed (`pip install sounddevice`).

**3. "Singularity matrix" error during training:**

* This means you have too few samples for a word. The system handles this automatically, but try to record at least 5 samples per word for stability.

---

**© 2026 HCMUT - Communication Systems Engineering Class**
