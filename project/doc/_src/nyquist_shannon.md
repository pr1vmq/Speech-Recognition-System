## 1. Định lý Lấy mẫu Nyquist-Shannon

### Lý thuyết
Định lý lấy mẫu phát biểu rằng để tái tạo chính xác (hoặc hoàn toàn) một tín hiệu analog từ các mẫu của nó, tín hiệu đó phải được lấy mẫu với tốc độ ít nhất là gấp đôi tần số cao nhất có trong tín hiệu.

* Gọi $f_{max}$ (hoặc $B$) là tần số cao nhất của tín hiệu analog.
* Gọi $f_s$ là tần số lấy mẫu (Sampling frequency).

**Điều kiện cần:** $$f_s \ge 2f_{max}$$



Tần số $2f_{max}$ được gọi là **Tốc độ Nyquist** (Nyquist rate). Nếu $f_s < 2f_{max}$, các thành phần phổ sẽ bị chồng chéo lên nhau, gây ra hiện tượng méo tiếng gọi là **Aliasing** (chồng phổ), khiến việc khôi phục tín hiệu gốc trở nên bất khả thi.

### Điều kiện thực tế
Mặc dù lý thuyết cho phép khôi phục hoàn hảo tại $f_s = 2f_{max}$, nhưng thực tế các bộ lọc không thể cắt tín hiệu một cách lý tưởng (thẳng đứng). Do đó, người ta thường chọn $f_s > 2f_{max}$ để tạo ra một **Khoảng bảo vệ (Guard band)**. Khoảng cách này cho phép các bộ lọc thực tế hoạt động hiệu quả mà không gây ra hiện tượng aliasing.

---

## 2. Đặc điểm Giọng nói Con người (Băng thông Thoại)

Các tiêu chuẩn viễn thông xác định các thông số phổ biến của giọng nói con người như sau:

* **Dải tần số:** Một tín hiệu thoại analog tiêu chuẩn (Voice-Frequency - VF) thường chiếm dải tần từ **300 Hz đến 3400 Hz**. Trong một số thiết kế hệ thống, dải này có thể được xem xét xấp xỉ từ 3 kHz đến 4 kHz.
* **Đặc điểm:** Mặc dù giọng nói có thể tạo ra các tần số cao hơn, nhưng phần lớn năng lượng và thông tin cần thiết để nghe hiểu/nhận dạng người nói nằm tập trung trong khoảng băng thông này.



---

## 3. Ứng dụng: Chọn Tần số Lấy mẫu 16kHz (Wideband Audio)

Việc chọn tần số lấy mẫu $f_s = 16$ kHz mang lại các lợi ích vượt trội cho âm thanh băng rộng (Wideband Audio) dựa trên các cơ sở sau:

### So sánh với chuẩn cũ (Narrowband)
Trong hệ thống điện thoại truyền thống (8 kHz), với băng thông thoại 3.4 kHz, tần số lấy mẫu là 8 kHz ($8000 > 2 \times 3400$). Điều này chỉ đáp ứng vừa đủ định lý Nyquist và có khoảng bảo vệ rất hẹp.

### Lợi ích của tần số 16 kHz
1.  **Mở rộng băng thông tín hiệu:**
    Theo định lý Nyquist, với $f_s = 16$ kHz, hệ thống có thể tái tạo chính xác các tín hiệu lên đến:
    $$\frac{f_s}{2} = \frac{16}{2} = 8 \text{ kHz}$$
    Điều này cho phép mở rộng băng thông thoại thực tế lên mức 7 kHz (thay vì 3.4 kHz), mang lại chất lượng âm thanh cao hơn hẳn.

2.  **Độ trung thực cao (High Fidelity):**
    Việc mở rộng dải tần lên 7-8 kHz giúp thu được nhiều âm sắc và độ chi tiết của giọng nói hơn, tạo ra âm thanh tự nhiên và rõ ràng (chuẩn Wideband Audio).

3.  **Khoảng bảo vệ lớn hơn:**
    Với tín hiệu thoại thông thường (chủ yếu dưới 4 kHz), lấy mẫu ở 16 kHz tạo ra một khoảng bảo vệ rất lớn (từ 4 kHz đến 12 kHz). Điều này:
    * Giảm khắt khe đối với bộ lọc chống aliasing (**Anti-aliasing filter**).
    * Đơn giản hóa thiết kế phần cứng và giảm méo tín hiệu.

---

## Kết luận
Với giọng nói chủ yếu nằm trong khoảng 300 Hz - 3400 Hz, việc chọn tần số lấy mẫu **16 kHz** là hoàn toàn thỏa mãn định lý Nyquist:
$$16 \text{ kHz} \gg 2 \times 3.4 \text{ kHz}$$

Sự lựa chọn này không chỉ đảm bảo tái tạo chính xác mà còn nâng cấp chất lượng âm thanh lên chuẩn băng rộng, vượt trội so với các hệ thống viễn thông truyền thống.