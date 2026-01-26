# CƠ SỞ LÝ THUYẾT VỀ MÔ HÌNH HMM-GMM TRONG NHẬN DẠNG GIỌNG NÓI

---

## 3.1. HMM (Hidden Markov Model - Mô hình Markov Ẩn)

### Khái niệm: Chuỗi trạng thái ẩn
HMM là mô hình xác suất mô tả các sự kiện quan sát được (tín hiệu âm thanh) dựa trên các nhân tố nguyên nhân ẩn (hidden factors).

* **Ví dụ:** Từ **"CAT"** được coi là một chuỗi các trạng thái ẩn tương ứng với các âm vị `/k/`, `/æ/`, `/t/`.
* **Trạng thái ($Q$):** Tập hợp $N$ trạng thái $Q = \{q_1, q_2, ..., q_N\}$. Trong nhận dạng giọng nói, các trạng thái này đại diện cho các đơn vị âm thanh cơ bản tạo nên từ đó.



### Cấu trúc (Topology): Left-to-Right (Mô hình Bakis)
Được quy định bởi ma trận xác suất chuyển trạng thái $A$, với $a_{ij}$ là xác suất chuyển từ trạng thái $i$ sang trạng thái $j$.

* **Quy tắc:** Chỉ cho phép chuyển từ trạng thái $i$ sang chính nó ($i \to i$ - self-loop) hoặc sang trạng thái kế tiếp ($i \to i+1$).
* **Lý do (Tính thời gian):** Giọng nói diễn ra theo trình tự tuyến tính. Cấu trúc này đảm bảo mô hình phản ánh đúng thực tế vật lý: không thể quay ngược thời gian để phát âm lại một âm vị đã qua (không có chuyển đổi $i \to i-1$).

### Các tham số của HMM ($\lambda$):
1.  **$Q$:** Tập hợp các trạng thái (ví dụ: 5 trạng thái cho mỗi từ).
2.  **$A$:** Ma trận xác suất chuyển trạng thái.
3.  **$B$:** Tập hợp các xác suất phát xạ (Emission probability).
4.  **$\pi$:** Phân phối xác suất khởi tạo.

---

## 3.2. GMM (Gaussian Mixture Model - Mô hình Hỗn hợp Gaussian)

### Vấn đề: Sự đa dạng của giọng nói
Dữ liệu giọng nói có tính chất **"đa đỉnh" (multimodal)**. Ví dụ: Âm `/a/` phát âm bởi người nam, người nữ hoặc các vùng miền khác nhau sẽ có đặc điểm tần số khác nhau. Một phân phối chuẩn đơn lẻ (**unimodal**) không thể bao phủ toàn bộ các biến thể này.



### Giải pháp: Kết hợp HMM và GMM
Trong HMM, mỗi trạng thái cần một hàm xác suất phát xạ $b_i(o_t)$ để tính xác suất quan sát $o_t$ được sinh ra từ trạng thái $i$. GMM được dùng để mô hình hóa hàm mật độ xác suất này.

**Công thức tổng quát cho GMM với $K$ thành phần:**
$$p(x) = \sum_{i=1}^{K} \phi_i \mathcal{N}(x | \mu_i, \Sigma_i)$$

**Trong đó:**
* $\mu_i$: Vector trung bình của thành phần thứ $i$.
* $\Sigma_i$: Ma trận hiệp phương sai của thành phần thứ $i$.
* $\phi_i$: Trọng số của thành phần thứ $i$ (với $\sum \phi_i = 1$).

### Mục đích của GMM:
* **Mô hình hóa sự đa dạng:** Sử dụng nhiều thành phần Gaussian với các cặp $(\mu, \sigma^2)$ khác nhau để bao phủ các biến thể phát âm (giọng nam/nữ, giọng địa phương).
* **Xử lý nhiễu:** Khả năng điều chỉnh phương sai giúp mô hình thích nghi tốt hơn với nhiễu nền; các dữ liệu nhiễu thường được giải thích bởi các thành phần có phương sai rộng hơn.



---

## Kết luận: Sự phối hợp HMM-GMM
Trong hệ thống nhận dạng:
1.  **HMM** đóng vai trò quản lý cấu trúc thời gian và trình tự của các âm vị.
2.  **GMM** đóng vai trò mô hình hóa đặc điểm âm học chi tiết của từng âm vị đó tại mỗi thời điểm.

Sự kết hợp này tạo nên một hệ thống nhận dạng mạnh mẽ, có khả năng xử lý cả sự biến đổi về mặt thời gian lẫn sự đa dạng về mặt âm học của con người.