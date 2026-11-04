# 🤝 Hướng Dẫn Đóng Góp Phát Triển (Contributing to LinTask Manager)

Cảm ơn bạn đã quan tâm và muốn đóng góp cho **LinTask Manager**! Chúng tôi hoan nghênh mọi đóng góp từ cộng đồng mã nguồn mở, bao gồm báo lỗi, đề xuất tính năng mới và gửi Pull Request.

---

## 🛠️ Thiết lập Môi trường Phát triển (Development Setup)

1. **Fork và Clone repository**:
   ```bash
   git clone https://github.com/mantran1122/OpenSource.git
   cd OpenSource
   ```

2. **Khởi tạo môi trường ảo Python**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install pytest flake8
   ```

3. **Chạy ứng dụng trong lúc phát triển**:
   ```bash
   python3 run.py
   ```

4. **Chạy Unit Tests**:
   ```bash
   pytest
   ```

---

## 📝 Quy chuẩn Viết Code (Code Conventions)

- **Chuẩn phong cách**: Tuân thủ hướng dẫn chuẩn **PEP 8**.
- **Type Hints**: Khuyến khích sử dụng chú thích kiểu (`typing`) cho tất cả các hàm và phương thức mới.
- **Không làm block UI**: Mọi tác vụ I/O hệ thống, đọc file nặng hoặc gọi lệnh OS bắt buộc phải được xử lý trong Worker Thread (`QThread`), không chạy trực tiếp trên luồng giao diện chính.
- **Kiểm thử**: Viết thêm unit test trong thư mục `tests/` khi tạo tính năng hoặc module mới.

---

## 🚀 Quy trình Gửi Pull Request (PR Workflow)

1. Tạo một branch riêng cho tính năng hoặc sửa lỗi của bạn:
   ```bash
   git checkout -b feature/ten-tinh-nang
   # hoặc
   git checkout -b fix/ten-loi
   ```
2. Thực hiện commit thay đổi với thông điệp rõ ràng theo chuẩn Conventional Commits (ví dụ: `feat: add gpu monitoring`, `fix: handle missing psutil sensors`).
3. Chạy lại `pytest` để đảm bảo 100% test suite đều pass.
4. Đẩy branch lên kho fork của bạn:
   ```bash
   git push origin feature/ten-tinh-nang
   ```
5. Mở **Pull Request** trên GitHub kèm theo mô tả ngắn gọn về những thay đổi bạn đã thực hiện!

