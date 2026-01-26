## 1. Vấn đề: Đặc điểm phổ năng lượng của giọng nói

Năng lượng của tín hiệu giọng nói tự nhiên không phân bố đều trên toàn bộ dải tần, dẫn đến một số hạn chế trong truyền dẫn và nhận dạng:

* **Sự suy giảm năng lượng:** Biên độ phổ tín hiệu thường giảm dần khi tần số tăng lên. Ở các tần số trên $500\text{ Hz}$, phổ giọng nói thường giảm dần (**roll-off**) với tốc độ khoảng $6\text{ dB/decade}$.
* **Hậu quả:** * Các thành phần tần số cao (như âm gió, âm xát: /s/, /f/, /th/) mang năng lượng rất nhỏ.
    * Trong các hệ thống truyền thông, nhiễu thường tập trung ở tần số cao. 
    * **Hệ quả:** Các âm sắc quan trọng dễ bị nhiễu che lấp, làm giảm độ rõ và độ chính xác của hệ thống nhận dạng.



---

## 2. Giải pháp: Kỹ thuật Pre-emphasis

Kỹ thuật Pre-emphasis được áp dụng để bù đắp sự suy giảm năng lượng ở dải tần cao trước khi thực hiện các bước xử lý tiếp theo.

### Nguyên lý hoạt động
Mục tiêu là **"làm phẳng" (equalize)** phổ tín hiệu bằng cách khuếch đại các thành phần tần số cao sao cho biên độ của chúng tương đương với các thành phần tần số thấp. Hệ thống sử dụng một bộ lọc thông cao (**High-pass filter**).

### Phân tích công thức (Dạng rời rạc)
Công thức lọc Pre-emphasis phổ biến trong xử lý số tín hiệu:
$$y[n] = x[n] - \alpha \cdot x[n-1]$$

**Trong đó:**
* **Bản chất vi phân:** Đây là một phép tính sai phân. Trong miền tần số, nó tương đương với việc nhân với tần số ($j2\pi f$), giúp làm nổi bật các vùng tín hiệu thay đổi nhanh (tần số cao).
* **Hệ số $\alpha$:** Thường nằm trong khoảng $[0.95, 0.97]$.
    * Nếu $\alpha$ càng gần $1$, bộ lọc càng loại bỏ mạnh các thành phần DC (tần số thấp) và làm nổi bật sự thay đổi đột ngột của tín hiệu.



---

## 3. Ứng dụng và Kết hợp với De-emphasis

Kỹ thuật này thường là một phần của quy trình khép kín nhằm tối ưu hóa tỷ số tín hiệu trên nhiễu (**SNR**).

| Giai đoạn | Tên kỹ thuật | Loại bộ lọc | Chức năng chính |
| :--- | :--- | :--- | :--- |
| **Phía phát (Transmitter)** | **Pre-emphasis** | Thông cao (High-pass) | Tăng cường tần số cao để vượt lên trên nền nhiễu của kênh truyền. |
| **Phía thu (Receiver)** | **De-emphasis** | Thông thấp (Low-pass) | Khôi phục cân bằng phổ tự nhiên và triệt tiêu nhiễu tần số cao đã lọt vào. |

### Kết quả thu được:
* **Cải thiện SNR:** Tỷ số tín hiệu trên nhiễu đầu ra tăng lên đáng kể (có thể tới hàng chục dB trong hệ thống FM).
* **Độ trung thực:** Tín hiệu gốc được khôi phục nguyên vẹn nhưng sạch nhiễu hơn.
* **Nhận dạng:** Trong các bài toán ML/AI, Pre-emphasis giúp các vector đặc trưng (như MFCC) thu thập được nhiều thông tin hữu ích hơn từ các âm gió.

---