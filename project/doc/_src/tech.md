# TỔNG HỢP LÝ THUYẾT & KỸ THUẬT HỆ THỐNG

## 1. Lý thuyết Xử lý Tín hiệu Số (DSP - Digital Signal Processing)

Đây là giai đoạn "Tai nghe", giúp chuyển đổi sóng âm vật lý thành dữ liệu số sạch để máy tính xử lý.

### 1.1. Định lý Lấy mẫu Nyquist-Shannon

* **Lý thuyết:** Để tái tạo chính xác một tín hiệu analog, tần số lấy mẫu () phải lớn hơn ít nhất 2 lần tần số cao nhất của tín hiệu đó ().
* **Ứng dụng:** Chúng ta chọn **Hz**.
* Giọng nói con người chủ yếu nằm trong khoảng 300Hz - 3400Hz (băng thông thoại).
* 16kHz là đủ để bao phủ toàn bộ dải tần này với độ trung thực cao (Wideband Audio).


* **Code:** `Config.SAMPLE_RATE = 16000`, `librosa.load(..., sr=16000)`.

### 1.2. Kỹ thuật Pre-emphasis (Làm nổi bật tần số cao)

* **Vấn đề:** Năng lượng giọng nói tự nhiên thường giảm ở các tần số cao. Điều này khiến các âm gió, âm xát (Fricatives) như /s/, /f/, /th/ bị chìm nghỉm so với nguyên âm trầm.
* **Giải pháp:** Sử dụng bộ lọc thông cao (High-pass filter) để cân bằng năng lượng.
* **Công thức:** $y(t) = x(t) - \alpha \cdot x(t-1)$
* Trong đó  là hệ số (thường từ 0.95 đến 0.97).


* **Code:** `librosa.effects.preemphasis(signal, coef=0.95)`.

### 1.3. Phát hiện tiếng nói (VAD - Voice Activity Detection)

* **Kỹ thuật:** Cắt bỏ khoảng lặng (Silence Removal) dựa trên năng lượng (Energy-based).
* **Cải tiến (Padding/Back-off):**
  * Thay vì cắt cụt ngay tại điểm vượt ngưỡng năng lượng, hệ thống lấy lùi về trước và sau một khoảng đệm (Padding ).
  * **Mục đích:** Bảo vệ các âm bật hơi (Plosives) như /b/, /d/, /p/ thường có năng lượng thấp ở điểm khởi đầu (Onset), tránh lỗi nhận "Down" thành "Own".


* **Code:** `librosa.effects.trim` kết hợp logic `pad_size`.

---

## 2. Trích xuất đặc trưng (Feature Extraction)

Đây là giai đoạn "Phiên dịch", chuyển âm thanh thành ngôn ngữ mà HMM hiểu được.

### 2.1. MFCC (Mel-Frequency Cepstral Coefficients)

MFCC là đặc trưng tiêu chuẩn vàng trong nhận dạng giọng nói cổ điển. Quy trình gồm:

1. **Framing:** Chia tín hiệu thành các khung nhỏ (20-30ms) chồng lên nhau. Giả định rằng trong khoảng thời gian ngắn này, giọng nói là dừng (stationary).
2. **FFT (Fast Fourier Transform):** Chuyển từ miền thời gian sang miền tần số.
3. **Mel Filterbank:** Áp dụng bộ lọc Mel mô phỏng thính giác người (nhạy với tần số thấp, kém nhạy với tần số cao).
4. **Log:** Lấy logarit năng lượng (mô phỏng độ to cảm nhận).
5. **DCT (Discrete Cosine Transform):** Giữ lại các thành phần chính, loại bỏ thông tin về cao độ (pitch), chỉ giữ lại thông tin về âm sắc (timbre).

* **Kết quả:** Mỗi khung hình được đại diện bởi vector 13 chiều.

### 2.2. Đặc trưng Động (Dynamic Features - Delta & Delta-Delta)

* **Lý thuyết:** Giọng nói là một quá trình liên tục, sự chuyển tiếp giữa các âm vị chứa đựng thông tin quan trọng. MFCC chỉ là ảnh tĩnh.
* **Giải pháp:** Tính đạo hàm theo thời gian.
* **Delta ($\Delta$):** Vận tốc thay đổi của MFCC (Đạo hàm bậc 1).
* **Delta-Delta ($\Delta$$\Delta$):** Gia tốc thay đổi (Đạo hàm bậc 2).


* **Tổng hợp:** Vector đặc trưng cuối cùng có kích thước **39 chiều** (13 MFCC +  $\Delta$ + 13 $\Delta\Delta$ ).

---

## 3. Mô hình Ngôn ngữ (Stochastic Modeling)

Đây là giai đoạn "Bộ não", sử dụng xác suất thống kê để nhận dạng.

### 3.1. HMM (Hidden Markov Model - Mô hình Markov Ẩn)

* **Khái niệm:** Một từ được coi là một chuỗi các trạng thái ẩn (Hidden States). Ví dụ từ "CAT" có 3 trạng thái: /k/ - /æ/ - /t/.
* **Cấu trúc (Topology):** Sử dụng cấu trúc **Left-to-Right (Bakis Model)**.
* Chỉ cho phép chuyển từ trạng thái $i$ sang $i$ hoặc $i+1$.
* Lý do: Thời gian không quay ngược, âm thanh luôn phát ra theo trình tự thời gian.


* **Tham số:** Hệ thống sử dụng 5 trạng thái (States) cho mỗi từ.

### 3.2. GMM (Gaussian Mixture Model)

* **Vấn đề:** Mỗi người nói âm /a/ một kiểu khác nhau. Một giá trị trung bình là không đủ.
* **Giải pháp:** Tại mỗi trạng thái của HMM, xác suất phát xạ (Emission Probability) được mô hình hóa bằng GMM.
* GMM là sự kết hợp của nhiều phân phối chuẩn (Normal Distributions).
* **Mục đích:** Để mô hình hóa sự đa dạng (Variance) của giọng nói và nhiễu nền.


* **Code:** `hmm.GMMHMM(n_mix=3)`.

---

## 4. Các Thuật toán Cốt lõi (Algorithms)

### 4.1. Huấn luyện (Training): Thuật toán Baum-Welch

* Đây là một dạng của thuật toán Expectation-Maximization (EM).
* **Nhiệm vụ:** Từ dữ liệu âm thanh đầu vào, tự động điều chỉnh các tham số của HMM (xác suất chuyển trạng thái, trung bình, phương sai) để tối ưu hóa khả năng khớp với dữ liệu đó.

### 4.2. Nhận dạng (Decoding): Thuật toán Forward / Viterbi

* **Nhiệm vụ:** Tính điểm **Log-Likelihood** (Độ phù hợp).
* **Cơ chế:** Với một chuỗi tín hiệu  thu được, tính xác suất .
* **Quyết định:** So sánh điểm của tất cả mô hình, chọn từ có điểm cao nhất (Maximum Likelihood).

---

## 5. Kỹ thuật Nâng cao & Tối ưu hóa Hệ thống

Đây là những điểm sáng tạo riêng của project này:

### 5.1. Active Learning (Học chủ động / Online Learning)

* **Nguyên lý:** Hệ thống cho phép người dùng phản hồi kết quả (Đúng/Sai).
* **Quy trình:**
1. Nếu sai, người dùng cung cấp nhãn đúng (Label correction).
2. Hệ thống lưu mẫu mới vào dataset.
3. Hệ thống kích hoạt **Retraining cục bộ**: Chỉ huấn luyện lại đúng mô hình từ vựng đó ngay lập tức mà không cần chạy lại toàn bộ dữ liệu lớn.


* **Hiệu quả:** Giúp hệ thống thích nghi nhanh chóng với giọng và môi trường tiếng ồn cụ thể của người dùng.

### 5.2. Robust Training (Huấn luyện Bền vững)

* **Vấn đề:** Khi người dùng mới thêm từ, dữ liệu rất ít (1-2 mẫu). HMM 5-state sẽ bị lỗi quá khớp (Overfitting) hoặc lỗi tính toán ma trận.
* **Giải pháp:** Adaptive Topology.
* Nếu dữ liệu < 5 mẫu: Tự động giảm độ phức tạp mô hình (Giảm số States xuống 3, giảm số Mixtures xuống 1).
* Nếu dữ liệu đủ lớn: Sử dụng cấu hình chuẩn (5 States, 3 Mixtures).



### 5.3. Xử lý Đa luồng (Parallel Processing)

* Sử dụng thư viện `joblib` để tận dụng đa nhân CPU.
* Áp dụng cho cả khâu trích xuất đặc trưng (Feature Extraction) và huấn luyện (Training), giúp giảm thời gian xử lý từ hàng giờ xuống vài phút.

---

### Sơ đồ luồng dữ liệu (Data Flow):
1. **Input (Mic)** $\rightarrow$ **Buffer** (Slicing & Debounce).
2. **Preprocessing:** Normalization $\rightarrow$ Pre-emphasis $\rightarrow$ VAD (Trim + Padding).
3. **Feature Extraction:** Framing $\rightarrow$ FFT $\rightarrow$ Mel-Filter $\rightarrow$ DCT $\rightarrow$ MFCC +  + $\Delta + \Delta\Delta$.
4. **Decoding:** Feature Vectors $\rightarrow$  **HMM Models** (Viterbi Scoring).
5. **Decision:** Argmax(Scores) $\rightarrow$  **Output Text**.
6. **Feedback Loop:** User Check $\rightarrow$  Add Sample $\rightarrow$  **Retrain HMM**.