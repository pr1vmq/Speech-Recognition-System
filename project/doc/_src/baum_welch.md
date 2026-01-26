# THUẬT TOÁN BAUM-WELCH (FORWARD-BACKWARD ALGORITHM)

---

## 1. Mục đích và Định nghĩa

Thuật toán Baum-Welch giải quyết bài toán thứ ba trong ba bài toán cơ bản của HMM: **Bài toán Huấn luyện (Learning)**.

* **Đầu vào:** Một chuỗi quan sát $O$ (ví dụ: tín hiệu âm thanh) và tập hợp các trạng thái ẩn khả dĩ $Q$.
* **Mục tiêu:** Tự động học các tham số của mô hình HMM, cụ thể là ma trận chuyển trạng thái $A$ và ma trận phát xạ $B$, sao cho khả năng sinh ra chuỗi quan sát $O$ là lớn nhất ($P(O|\lambda)$ đạt cực đại).

---

## 2. Bản chất thuật toán (EM Algorithm)

Baum-Welch là một trường hợp đặc biệt của thuật toán **Expectation-Maximization (EM)**. Vì các trạng thái là "ẩn", chúng ta không thể đếm trực tiếp số lần chuyển trạng thái hay phát xạ. Thuật toán giải quyết bằng cách lặp lại hai bước:

1.  **Bước E (Expectation):** Sử dụng các tham số hiện có để ước tính các đại lượng kỳ vọng.
2.  **Bước M (Maximization):** Sử dụng các ước tính đó để cập nhật lại các tham số $A$ và $B$ nhằm tối đa hóa khả năng của dữ liệu.



---

## 3. Các thành phần tính toán cốt lõi

Để thực hiện thuật toán, chúng ta cần định nghĩa các xác suất trung gian:

* **Xác suất Backward ($\beta_t(i)$):** Xác suất quan sát phần còn lại của chuỗi (từ $t+1$ đến kết thúc $T$), biết rằng hệ thống đang ở trạng thái $i$ tại thời điểm $t$.
* **Biến $\xi_t(i, j)$:** Xác suất tại thời điểm $t$ hệ thống ở trạng thái $i$ và tại thời điểm $t+1$ chuyển sang trạng thái $j$.
    $$\xi_t(i, j) = \frac{\alpha_t(i) a_{ij} b_j(o_{t+1}) \beta_{t+1}(j)}{P(O|\lambda)}$$
* **Biến $\gamma_t(j)$:** Xác suất hệ thống đang ở trạng thái $j$ tại thời điểm $t$.
    $$\gamma_t(j) = \frac{\alpha_t(j)\beta_t(j)}{P(O|\lambda)}$$



---

## 4. Quy trình thực hiện (Chu trình cập nhật)

Thuật toán bắt đầu với một ước lượng khởi tạo cho $A$ và $B$, sau đó lặp lại quy trình sau cho đến khi hội tụ:

### Bước 1: Tính toán kỳ vọng (E-step)
Dựa trên $A$ và $B$ hiện tại, tính toán $\gamma_t(j)$ (kỳ vọng số lần ở trạng thái $j$) và $\xi_t(i,j)$ (kỳ vọng số lần chuyển từ $i$ sang $j$) cho toàn bộ thời gian $t$.

### Bước 2: Cập nhật tham số (M-step)
Cập nhật lại ma trận $A$ và $B$ dựa trên các kỳ vọng vừa tính được:

* **Cập nhật xác suất chuyển trạng thái ($\hat{a}_{ij}$):**
    $$\hat{a}_{ij} = \frac{\sum_{t=1}^{T-1} \xi_t(i,j)}{\sum_{t=1}^{T-1} \gamma_t(i)}$$
* **Cập nhật xác suất phát xạ ($\hat{b}_j(v_k)$):**
    $$\hat{b}_j(v_k) = \frac{\sum_{t=1, s.t. O_t=v_k}^{T} \gamma_t(j)}{\sum_{t=1}^{T} \gamma_t(j)}$$

---

## 5. Kết luận

* **Ưu điểm:** Cho phép HMM tự "học" đặc trưng từ dữ liệu thô không nhãn.
* **Hạn chế:** Là thuật toán leo đồi (**hill-climbing**) nên có thể bị kẹt tại cực đại địa phương (**local maximum**). Kết quả phụ thuộc nhiều vào việc khởi tạo tham số ban đầu.
* **Thực tế:** Cấu trúc HMM thường được thiết kế thủ công (ví dụ: 5 trạng thái cho một từ) và Baum-Welch được dùng để tinh chỉnh các xác suất chuyển và phát xạ sao cho khớp nhất với dữ liệu giọng nói thực tế.

---