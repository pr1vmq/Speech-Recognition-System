# THUẬT TOÁN FORWARD VÀ VITERBI TRONG NHẬN DẠNG GIỌNG NÓI

---

## 1. Phân biệt Mục đích Cơ bản

Mặc dù cả hai thuật toán đều sử dụng cấu trúc lưới (**trellis**) và quy hoạch động, chúng giải quyết hai bài toán khác nhau trong mô hình HMM:

| Thuật toán | Bài toán HMM | Mục tiêu chính (Goal) |
| :--- | :--- | :--- |
| **Forward** | **Bài toán 1 (Likelihood)** | Tính tổng xác suất $P(O|\lambda)$ để mô hình sinh ra chuỗi quan sát. Xét **tất cả** các con đường có thể. |
| **Viterbi** | **Bài toán 2 (Decoding)** | Tìm chuỗi trạng thái ẩn $Q$ **tốt nhất** tương ứng với chuỗi quan sát. Chỉ xét con đường có xác suất cao nhất. |



---

## 2. Thuật toán Forward (Tính Tổng Likelihood)

Đây là phương pháp đánh giá mức độ "phù hợp" tổng thể của một mô hình đối với dữ liệu đầu vào.

* **Nguyên lý:** Cộng dồn xác suất của mọi chuỗi trạng thái khả dĩ bằng quy hoạch động để tránh bùng nổ tính toán.
* **Biến Forward ($\alpha_t(j)$):** Xác suất hệ thống ở trạng thái $j$ tại thời điểm $t$ sau khi quan sát chuỗi $o_1, ..., o_t$.
* **Công thức đệ quy (Summing):**
  $$\alpha_t(j) = \sum_{i=1}^{N} \alpha_{t-1}(i) a_{ij} b_j(o_t)$$
  > *Giải thích:* Lấy tổng xác suất từ tất cả trạng thái trước đó ($i$), nhân với xác suất chuyển ($a_{ij}$) và xác suất phát xạ ($b_j$).

---

## 3. Thuật toán Viterbi (Tính Điểm Likelihood Cực đại)

Trong nhận dạng (ví dụ từ "CAT"), Viterbi thường được ưu tiên vì nó chỉ ra con đường "khớp" nhất, đồng thời giải mã được chuỗi âm vị.

* **Nguyên lý:** Chỉ giữ lại con đường đơn lẻ có xác suất cao nhất xuyên suốt lưới trạng thái.
* **Biến Viterbi ($v_t(j)$):** Xác suất của con đường tối ưu nhất dẫn đến trạng thái $j$ tại thời điểm $t$.
* **Công thức đệ quy (Maximizing):**
  $$v_t(j) = \max_{i=1}^{N} v_{t-1}(i) a_{ij} b_j(o_t)$$
* **Truy vết (Backtrace):** Lưu lại các "dấu vết" (backpointers) để khôi phục lại chuỗi trạng thái ẩn (ví dụ: trình tự âm vị `/k/` $\to$ `/æ/` $\to$ `/t/`).



---

## 4. Tại sao gọi là "Log-Likelihood"?

Trong cài đặt thực tế, thay vì dùng xác suất $P$, các kỹ sư luôn sử dụng **Logarithm** ($\log P$) vì hai lý do:

1.  **Tránh Underflow:** Việc nhân liên tiếp các số nhỏ hơn 1 khiến giá trị tiến về 0 cực nhanh, vượt quá khả năng xử lý của máy tính. Logarithm biến phép nhân thành phép cộng: $\log(a \cdot b) = \log a + \log b$.
2.  **Hiệu năng:** Máy tính thực hiện phép cộng nhanh hơn đáng kể so với phép nhân.

**Khi sử dụng Log-Likelihood:**
* **Viterbi:** Trở thành bài toán tìm đường đi có **tổng trọng số lớn nhất**.
* **Forward:** Trở nên phức tạp hơn vì phép cộng xác suất $\log(A+B)$ cần dùng xấp xỉ *LogSumExp*.

---

## Tóm lại

* **Forward:** Cung cấp độ phù hợp tổng thể (xét mọi cách phát âm biến thiên).
* **Viterbi:** Cung cấp độ phù hợp của cách phát âm tốt nhất. Đây là thuật toán phổ biến nhất trong thực tế để đưa ra quyết định nhận dạng vì nó vừa tính điểm vừa giải mã được nội dung.

---