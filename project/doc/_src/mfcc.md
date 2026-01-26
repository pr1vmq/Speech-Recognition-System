## CÁC BƯỚC TRÍCH XUẤT ĐẶC TRƯNG TRONG NHẬN DẠNG TIẾNG NÓI

---

## 1. Framing (Phân khung tín hiệu)

**Nguyên lý:** Tín hiệu tiếng nói là tín hiệu không dừng (**non-stationary**), thay đổi liên tục theo thời gian. Để xử lý, tín hiệu analog trước hết được lấy mẫu tạo thành tín hiệu rời rạc $x[k]$.

* **Quy trình:** Tín hiệu được cắt thành các đoạn ngắn hữu hạn gọi là "cửa sổ" (windows). 
* **Giả định dừng (Quasi-stationary):** Trong các khoảng thời gian rất ngắn (thường là $20\text{ms}$ đến $30\text{ms}$), các đặc tính thống kê của tiếng nói được coi là không đổi (stationary). Điều này cho phép áp dụng các thuật toán phân tích phổ ổn định.



---

## 2. FFT (Fast Fourier Transform - Biến đổi Fourier Nhanh)

**Chức năng:** FFT là thuật toán hiệu quả để tính toán Biến đổi Fourier Rời rạc (DFT), chuyển đổi tín hiệu từ **miền thời gian** sang **miền tần số**.

* **Cơ chế:** Nếu khung tín hiệu có $N$ mẫu, FFT sẽ tạo ra $N$ điểm trong miền tần số.
* **Vai trò:** Phổ biên độ thu được cho biết tỷ lệ các thành phần tần số hiện diện. Đây là bước then chốt vì thông tin về âm sắc và cao độ nằm ở cấu trúc phổ tần số thay vì hình dạng sóng biên độ theo thời gian.



---

## 3. Mel Filterbank (Bộ lọc Mel)

**Cơ sở lý thuyết:** Tai người không cảm nhận tần số theo thang tuyến tính. Chúng ta nhạy cảm hơn với những thay đổi ở tần số thấp so với tần số cao.

* **Ứng dụng:** Bộ lọc Mel mô phỏng đặc tính thính giác bằng cách phân bổ các bộ lọc dày đặc ở dải tần thấp và thưa dần ở dải tần cao. 
* **Cách thức:** Phổ năng lượng sau FFT được đưa qua ngân hàng bộ lọc hình tam giác được phân bố theo thang đo Mel để thu hẹp dữ liệu theo cách "con người nghe".



---

## 4. Log (Logarit năng lượng)

**Mục đích:** Mô phỏng độ to cảm nhận (**Perceived Loudness**) của thính giác con người.

* **Lý do:** Con người không cảm nhận cường độ âm thanh theo đường thẳng mà theo hàm logarit. 
* **Kỹ thuật:** Sử dụng thang đo Decibel (dB): 
    $$L_{dB} = 10 \log_{10} \left( \frac{P}{P_0} \right)$$
* **Lợi ích:** Giúp nén dải động lớn của âm thanh thành một phạm vi nhỏ hơn, giúp thuật toán xử lý ổn định hơn trước các biến động về âm lượng.

---

## 5. DCT (Discrete Cosine Transform - Biến đổi Cosine Rời rạc)

**Chức năng:** Giải tương quan (**Decorrelation**) và nén thông tin.

* **Trong MFCC:** Các giá trị năng lượng sau bộ lọc Mel thường có độ tương quan cao. DCT được áp dụng để tách biệt các thành phần này.
* **Nén dữ liệu:** DCT tập trung phần lớn "năng lượng thông tin" vào một số ít hệ số đầu tiên.
* **Kết quả:** Quá trình này tách biệt được:
    * **Spectral Envelope:** Bao phổ (đại diện cho đặc tính âm sắc/nguyên âm).
    * **Spectral Details:** Chi tiết phổ (đại diện cho cao độ).
* **Đầu ra:** Thường là một vector đặc trưng gọn nhẹ (ví dụ: 13 chiều) đại diện tối ưu cho khung tín hiệu đó.
