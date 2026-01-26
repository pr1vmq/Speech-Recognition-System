## 1. Sơ đồ 1: Kiến trúc Tổng quan Hệ thống (System Architecture)
Sơ đồ này mô tả luồng dữ liệu từ lúc người dùng tương tác đến khi hệ thống trả về kết quả và học tập.

* **Luồng dữ liệu (Data Flow):** Trái sang Phải.
* **Các khối thành phần:**

| Thành phần | Chi tiết kỹ thuật |
| :--- | :--- |
| **User Interaction** | Người dùng nhấn giữ phím `Space` (Push-to-Talk). |
| **Audio Acquisition** | Ghi âm qua Microphone (`sounddevice`). Thông số: $F_s = 16\text{kHz}$, Mono, PCM 16-bit. |
| **Signal Preprocessing** | Khối DSP V4: Pre-emphasis, Normalization, Smart VAD (Cắt khoảng lặng có đệm). |
| **Feature Extraction** | Chuyển đổi tín hiệu sang vector đặc trưng 39 chiều (MFCC + $\Delta$ + $\Delta\Delta$). |
| **Inference Engine** | Tính điểm Log-Likelihood với 35 mô hình HMM nạp từ `models/` qua thuật toán Viterbi. |
| **Active Learning** | Chọn từ có điểm cao nhất, nhận phản hồi và kích hoạt Retraining Module. |
| **Output** | Hiển thị tên từ dự đoán và xuất báo cáo biểu đồ (Visualizer). |

---

## 2. Sơ đồ 2: Quy trình Xử lý Tín hiệu số (DSP & Feature Extraction)
Mô tả chi tiết kỹ thuật xử lý "lõi" của hệ thống (Khối 3 và 4).



**Luồng thực hiện (Từ trên xuống dưới):**

1.  **Raw Signal $x[n]$:** Tín hiệu âm thanh đầu vào.
2.  **Pre-emphasis:** Bộ lọc thông cao.
    * *Công thức:* $y[n] = x[n] - 0.95 \cdot x[n-1]$
    * *Mục đích:* Làm nổi bật tần số cao (âm gió).
3.  **Amplitude Normalization:** Chuẩn hóa biên độ về dải $[-1, 1]$.
4.  **Smart VAD (Trim & Padding):**
    * Tìm điểm đầu/cuối dựa trên năng lượng (Top DB = 25).
    * **Padding:** Mở rộng vùng chọn ra $0.15\text{s}$ về hai phía để giữ âm bật hơi.
5.  **Framing & Windowing:**
    * Frame size: 512 mẫu (~32ms) | Hop size: 256 mẫu (~16ms).
    * Sử dụng hàm cửa sổ **Hamming/Hann**.
6.  **FFT & Mel Filterbank:** Chuyển miền tần số và áp dụng bộ lọc Mel mô phỏng tai người.
7.  **Logarithm & DCT:** Lấy log năng lượng và biến đổi Cosine rời rạc $\rightarrow$ 13 hệ số MFCC tĩnh.
8.  **Dynamic Features:** Tính đạo hàm bậc 1 ($\Delta$) và bậc 2 ($\Delta\Delta$).
9.  **Feature Concatenation:** Ghép lại thành vector **39 chiều** ($13 \times 3$).

---

## 3. Sơ đồ 3: Cấu trúc Topo của Mô hình HMM (HMM Topology)
Minh họa cấu trúc toán học của mô hình cho một từ đơn lẻ.



* **Loại mô hình:** GMM-HMM (Gaussian Mixture Model - Hidden Markov Model).
* **Trạng thái (States):** 5 trạng thái ẩn nối tiếp ($S_1 \rightarrow S_5$).
* **Chuyển trạng thái (Transitions):**
    * $a_{ii}$ (Self-loop): Thể hiện độ dài âm tiết.
    * $a_{i, i+1}$ (Forward): Thể hiện diễn biến thời gian.
    * *Lưu ý:* Không có mũi tên quay ngược (**Left-to-Right Topology**).
* **Phát xạ (Emission - GMM):** * Mỗi trạng thái chứa 3 hỗn hợp Gaussian (`HMM_N_MIX = 3`).
    * Đầu vào: Vector đặc trưng $O_t$ (39 chiều).

---

## 4. Sơ đồ 4: Lưu đồ Thuật toán Active Learning (Active Learning Flowchart)
Logic vận hành thông minh giúp hệ thống tự cải thiện qua thời gian.



* **B1:** Khởi động, nạp Models.
* **B2:** Chờ sự kiện nhấn phím `Space` và thu âm.
* **B3:** Tiền xử lý & Trích xuất đặc trưng.
* **B4 (Decision):** Kiểm tra chất lượng (Độ dài < 0.2s hoặc quá nhiễu?).
    * *Yes:* Báo lỗi, quay lại B2.
    * *No:* Tiếp tục Inference.
* **B5:** Tính toán Score $\rightarrow$ Chọn **Best Word** $\rightarrow$ Visualize.
* **B6 (Decision):** Người dùng xác nhận Đúng/Sai?
    * **Nhánh Đúng (Y):** Lưu mẫu vào folder từ tương ứng + Gọi `retrain_word()`.
    * **Nhánh Sai (N):** Nhập nhãn đúng + Lưu mẫu + Gọi `retrain_word()`.
* **B7:** Kết thúc vòng lặp, quay lại B2.

---

## 5. Sơ đồ 5: Biểu đồ Phụ thuộc Module (Module Dependency Diagram)
**Mục đích:** Thể hiện kiến trúc phần mềm phân tầng, xác định rõ vai trò của từng file trong hệ thống.



### Phân tầng kiến trúc (Layered Architecture)

* **Tầng đáy (Foundation Layer):**
    * `config.py`: Chứa các biến toàn cục (Global Variables). Đây là file nền tảng, tất cả các module khác đều phụ thuộc vào đây.
    * `utils.py`: Chứa bộ ghi nhật ký (Logger). Mọi file trong hệ thống (ngoại trừ config) đều gọi đến để ghi log.
* **Tầng công cụ (Utility Layer):**
    * `visualizer.py`: Module chuyên trách việc vẽ biểu đồ và báo cáo. Được gọi bởi các ứng dụng thực thi chính.
* **Tầng xử lý dữ liệu (Processing Layer):**
    * `create_dataset.py`, `preprocess_data.py`, `train_model.py`: Hoạt động độc lập để tạo lập và huấn luyện mô hình, sử dụng chung tài nguyên từ tầng Foundation.
* **Tầng ứng dụng (Application Layer):**
    * `main_app.py` và `main_ml.py`: Điểm cuối của hệ thống, điều phối tất cả các thư viện và tài nguyên để phục vụ người dùng.

---

## 6. Sơ đồ 6: Luồng Dữ liệu Huấn luyện (Offline Training Data Pipeline)
**Mục đích:** Mô tả quá trình biến đổi từ tín hiệu âm thanh thô thành mô hình trí tuệ nhân tạo (HMM Models).



| Bước | Thực thi (Actor) | Thao tác (Action) | Kết quả (Output) |
| :--- | :--- | :--- | :--- |
| **1. Thu thập** | `create_dataset.py` | Ghi âm trực tiếp từ Microphone. | File `.wav` lưu tại `sample/`. |
| **2. Tiền xử lý** | `preprocess_data.py` | Đọc dữ liệu thô, trích xuất đặc trưng MFCC + Delta. | File `features/all_features.pkl`. |
| **3. Huấn luyện** | `train_model.py` | Áp dụng thuật toán **Baum-Welch** để tối ưu tham số. | Các file `models/*.pkl` (Mô hình HMM). |

---

## 7. Sơ đồ 7: Cơ chế Vận hành Runtime & Active Learning
**Mục đích:** Giải thích quy trình vận hành khép kín (vừa nhận dạng vừa học tập) của `main_ml.py`.



### A. Giai đoạn Khởi động
1.  Hệ thống đọc tham số cấu hình từ `config.py`.
2.  Nạp toàn bộ các mô hình `.pkl` từ thư mục `models/` vào bộ nhớ RAM để tối ưu tốc độ nhận dạng.

### B. Vòng lặp Tương tác (Interaction Loop)
* **Input:** Nhận tín hiệu từ Microphone $\rightarrow$ `main_ml.py` xử lý tiền xử lý.
* **Inference:** So khớp đặc trưng với các Models trong RAM để tìm kết quả tối ưu.
* **Reporting:** Gửi dữ liệu qua `visualizer.py` để xuất biểu đồ phân tích vào thư mục `log/`.

### C. Vòng lặp học tập (Active Learning Loop)
Khi có phản hồi (Feedback) từ người dùng về kết quả nhận dạng:
1.  **Lưu trữ:** Lưu file `.wav` mới vào thư mục nhãn tương ứng trong `sample/`.
2.  **Trích xuất:** Trích xuất đặc trưng vector của mẫu mới ngay lập tức.
3.  **Cập nhật RAM:** Cập nhật tham số mô hình đang chạy trong RAM (Học tức thì - Incremental Learning).
4.  **Lưu trữ Model:** Ghi đè trạng thái mô hình mới xuống file `.pkl` để lưu trữ lâu dài.