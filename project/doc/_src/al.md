### PHÂN TÍCH CHI TIẾT QUY TRÌNH HỆ THỐNG NHẬN DẠNG GIỌNG NÓI GMM-HMM (END-TO-END)

Hệ thống hoạt động theo mô hình **Pipeline (Đường ống)**: Dữ liệu chảy qua từng khối, được biến đổi và đẩy sang khối tiếp theo qua 5 bước chính dưới đây.

***

#### BƯỚC 1: THU THẬP TÍN HIỆU (SIGNAL ACQUISITION)

Đây là bước chuyển đổi sóng âm vật lý thành dữ liệu số mà máy tính có thể xử lý.

* **Lý thuyết áp dụng:**

  * **Định lý Lấy mẫu Nyquist-Shannon:** Để tái tạo chính xác tín hiệu analog, tần số lấy mẫu ($F\_s$) phải lớn hơn ít nhất 2 lần tần số cao nhất của tín hiệu ($F\_{max}$).

  * Giọng nói người nằm trong khoảng 300Hz - 3400Hz, hệ thống chọn $F\_s = 16000Hz$ (Wideband Audio) để đảm bảo độ trung thực.

* **Cơ chế vận hành:**

  * Sử dụng cơ chế **Push-to-Talk** (Nhấn để nói).

  * **Event Loop:** Lắng nghe sự kiện bàn phím để kích hoạt thu âm.

  * **Non-blocking Recording:** Ghi vào bộ đệm RAM (Buffer) giúp chương trình không bị treo.

* **Dữ liệu:**

  * **Input:** Sóng âm thanh analog.

  * **Output:** Mảng 1 chiều (NumPy array), định dạng `Float32`.

* **Vị trí trong Code:**

  * **File:** `main_ml.py`, `main_app.py`.

  * **Hàm:** `record_and_process`.

  * **Lệnh quan trọng:** `sd.rec(int(max_duration * fs), ...)`

***

#### BƯỚC 2: TIỀN XỬ LÝ TÍN HIỆU (SIGNAL PREPROCESSING)

Làm sạch tín hiệu thô (nhiễu nền, khoảng lặng, biên độ không đều).

##### 2.1. Lọc thông cao (Pre-emphasis)

* **Lý thuyết:** Giọng nói có đặc tính "nghiêng phổ" (Spectral Tilt) – năng lượng giảm ở tần số cao. Bộ lọc này giúp tăng cường các âm gió (như /s/, /f/) để không bị mờ nhạt.

* **Công thức:** $y[n] = x[n] - \alpha \cdot x[n-1]$ (với $\alpha = 0.95$).

* **Code:** `librosa.effects.preemphasis(signal, coef=0.95)`

##### 2.2. Chuẩn hóa biên độ (Normalization)

* **Lý thuyết:** Đảm bảo tính nhất quán. Giúp mô hình tập trung học "âm sắc" thay vì học "độ to" của các loại Microphone khác nhau.

* **Vận hành:** Chia tất cả giá trị cho biên độ tuyệt đối lớn nhất để đưa về dải $\[-1, 1]$.

* **Code:** `signal = signal / max_amp`

##### 2.3. Cắt khoảng lặng thông minh (Smart VAD - Padding Trim)

* **Lý thuyết:** Voice Activity Detection (VAD) dựa trên năng lượng.

* **Vấn đề:** Nếu cắt sát ngưỡng, dễ mất phần "khởi phát" (Onset) của âm bật hơi như /b/, /d/.

* **Vận hành:** Tìm điểm $T\_{start}$ và $T\_{end}$ vượt ngưỡng 25dB, sau đó mở rộng thêm **150ms (Padding)** về hai phía.

* **Code:** Tính `pad_size` và trích xuất `final_signal` trong hàm `extract_features`.

***

#### BƯỚC 3: TRÍCH XUẤT ĐẶC TRƯNG (MFCC)

Chuyển sóng âm sang miền tần số mô phỏng cách tai người nghe.

* **Lý thuyết:**

  * **Giả định dừng (Stationarity):** Coi tín hiệu ổn định trong các khung ngắn (20-30ms).

  * **Thang đo Mel (Mel Scale):** Mô phỏng tai người (nhạy với tần số thấp hơn tần số cao).

* **Quy trình (Pipeline):**

  1. **Framing:** Chia khung 25ms, độ đè (overlap) 10ms.

  2. **Windowing:** Nhân cửa sổ Hamming để giảm rò rỉ phổ.

  3. **FFT:** Biến đổi Fourier nhanh sang phổ năng lượng.

  4. **Mel Filterbank:** Áp dụng bộ lọc Mel.

  5. **Log & DCT:** Lấy logarit và biến đổi Cosine rời rạc để có 13 hệ số MFCC tĩnh.

  6. **Delta ($\Delta$) & Delta-Delta ($\Delta\Delta$):** Tính đạo hàm bậc 1 & 2 để bắt thông tin sự thay đổi khẩu hình.

* **Dữ liệu:**

  * **Output:** Ma trận đặc trưng $(T \times 39)$, với $T$ là số khung hình.

***

#### BƯỚC 4: GIẢI MÃ & NHẬN DẠNG (DECODING / INFERENCE)

Tìm từ có xác suất cao nhất khớp với chuỗi đặc trưng.

* **Lý thuyết:**

  * **HMM (Hidden Markov Model):** Mô hình hóa diễn biến thời gian (trình tự các âm).

  * **GMM (Gaussian Mixture Model):** Mô hình hóa sự đa dạng âm sắc trong từng trạng thái.

  * **MLE (Maximum Likelihood Estimation):** Chọn mô hình sinh ra xác suất lớn nhất.

* **Vận hành:**

  1. Nạp các mô hình `.pkl` vào RAM.

  2. Chạy vòng lặp qua từng mô hình.

  3. Sử dụng thuật toán **Forward** tính điểm Log-Likelihood: $P(O | \text{Model}\_i)$.

  4. **Kết quả:** $\text{Best\\\_Word} = \arg\max(\text{Scores})$.

* **Code:** `model.score(features)` trong vòng lặp `for word, model in self.models.items()`.

***

#### BƯỚC 5: HỌC CHỦ ĐỘNG & CẬP NHẬT (ACTIVE LEARNING)

Cơ chế giúp hệ thống tự thông minh hơn mà không cần nạp lại toàn bộ dữ liệu từ đầu.

* **Lý thuyết:** **Incremental Learning** (Học tăng cường).

* **Quy trình:**

  1. **Feedback:** Người dùng xác nhận Đúng/Sai.

  2. **Storage:** Lưu mẫu lỗi vào thư mục nhãn đúng.

  3. **Adaptive Retraining:** \* Tải dữ liệu cũ + mới của riêng từ đó.

     * **Adaptive Topology:** Nếu mẫu quá ít, tự động giảm số trạng thái HMM để tránh lỗi toán học.

     * Chạy lại **Baum-Welch** để cập nhật tham số và lưu đè file `.pkl`.

* **Code:** Hàm `save_and_learn` gọi `retrain_word`.

***

#### BƯỚC 6: XUẤT BÁO CÁO (VISUALIZATION REPORTING)

Cung cấp bằng chứng kỹ thuật cho kết quả nhận dạng.

* **Vận hành:** Module `visualizer.py` tạo báo cáo đồ họa:

  * Đồ thị cắt gọt tín hiệu (DSP).

  * Phổ tần số (Spectrogram).

  * Biểu đồ cột so sánh điểm số giữa các từ (Bar chart).

* **Lưu trữ:** File báo cáo được lưu trong thư mục `log/`.

