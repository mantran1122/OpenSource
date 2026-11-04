# 🎨 LinTask Manager - Thiết Kế Giao Diện & UI/UX Hiện Đại (Design System Specification)
> **Đặc tả chiến lược nâng cấp giao diện toàn diện: Từ QtWidgets cổ điển sang chuẩn Fluent Design Windows 11 hiện đại nhất.**

---

## 🛑 1. Thực trạng & Vấn đề của UI hiện tại (Post-Mortem)

Giao diện sơ khởi đang sử dụng các thành phần `QtWidgets` tiêu chuẩn. Dù đã thêm một số dòng CSS (QSS), kết quả vẫn mang lại cảm giác:
- **Thô cứng & Lỗi thời**: Các viền phân cách cứng nhắc, tab bar ngang kiểu cũ của thập niên 2000.
- **Thiếu Micro-interactions**: Không có hiệu ứng chuyển động mượt (animations), không có hiệu ứng lướt (hover feedback), chuyển tab bị giật cục.
- **Typography & Bố cục chưa tinh tế**: Khoảng cách (padding/margin) chưa theo chuẩn thiết kế hiện đại (8pt grid system).
- **Trải nghiệm khác xa Windows 11**: Windows 11 Task Manager hiện đại sử dụng **Navigation Bar bên trái (Icon-based Collapsible Sidebar)**, hiệu ứng kính mờ (Mica/Acrylic) và các Card bo tròn có đổ bóng tinh tế.

---

## 🚀 2. Lựa chọn Công nghệ UI Tiên Tiến Nhất cho Python

Để biến LinTask thành một ứng dụng desktop đẳng cấp, hiện đại và thu hút hàng nghìn Stars trên GitHub, chúng ta đánh giá các giải pháp công nghệ UI hàng đầu hiện nay:

| Giải pháp | Đặc điểm | Ưu điểm | Nhược điểm | Đánh giá |
| :--- | :--- | :--- | :--- | :---: |
| **1. `QFluentWidgets` (PyQt-Fluent-Widgets)** | Thư viện Fluent Design chuẩn Windows 11 xịn sò nhất trên PyQt6 (10k+ Stars) | ✅ Giao diện giống 100% Windows 11 Task Manager<br>✅ Hỗ trợ Dark/Light Theme tự động<br>✅ Bo góc, acrylic, animation mượt mà<br>✅ Dễ tích hợp với code logic hiện có | Cần cài thêm thư viện phụ thuộc | ⭐⭐⭐⭐⭐ **(Khuyên dùng số 1)** |
| **2. PyQt6 + Custom Modern QSS Engine** | Tự dựng toàn bộ component từ `QFrame` với chuẩn thiết kế Tailwind CSS + SVG icons | ✅ Hoàn toàn không phụ thuộc thư viện ngoài<br>✅ Tự do tùy biến 100% chi tiết pixel | Tốn nhiều công sức để viết animation và bo góc | ⭐⭐⭐⭐ |
| **3. QML / Qt Quick 6** | Ngôn ngữ khai báo hiện đại của Qt (tương tự React/CSS) | ✅ GPU Accelerated 60-120 FPS mượt mà tuyệt đối | Phải viết lại tầng UI bằng cú pháp QML | ⭐⭐⭐ |

👉 **Quyết định công nghệ**: Chúng ta sẽ áp dụng **`QFluentWidgets` kết hợp với hệ thống Design Tokens hiện đại**, mang lại giao diện Fluent Design Windows 11 thực thụ cho LinTask.

---

## 🎯 3. Hệ thống Thiết kế (LinTask Design System)

### 3.1. Bảng màu Dark Theme (Fluent Dark Palette)

Lấy cảm hứng từ giao diện Windows 11 và Tailwind Dark Zinc:

```
[ Nền chính (App Canvas) ]  #1c1c1c (Mica Dark Base)
  └── [ Sidebar điều hướng ] #202020
  └── [ Thẻ Card nội dung ]   #272727 (Border: 1px solid #383838, Radius: 8px)
        └── [ Hover Card ]    #303030
        └── [ Active/Click ]  #383838

[ Màu Accent & Biểu đồ ]
  ├── CPU:     #0078d4 (Windows Electric Blue) / #38bdf8
  ├── Memory:  #8b5cf6 (Vibrant Purple)
  ├── Disk:    #10b981 (Emerald Green)
  ├── Network: #f59e0b (Amber Orange)
  └── Warning: #ef4444 (Crimson Red)

[ Typography Colors ]
  ├── Text Primary:   #ffffff (Độ tương phản cao nhất)
  ├── Text Secondary: #a1a1aa (Thông số phụ, mô tả)
  └── Text Tertiary:  #71717a (Label nhỏ, đơn vị đo)
```

### 3.2. Cấu trúc Bố cục Windows 11 Task Manager Layout

Thay vì dùng tab bar ngang cổ điển ở trên đỉnh, chuyển sang **Cột điều hướng bên trái (Vertical Icon Navigation)**:

```
+----+---------------------------------------------------------------+
|    |  [Header: Tiêu đề trang + Search Box + Nút hành động]          |
| ☰  +---------------------------------------------------------------+
|    |                                                               |
| ⚡ |  [Khu vực nội dung chính hiển thị dạng Card bo tròn]          |
| 📈 |  - Viền mỏng 1px tinh tế (#383838)                             |
| 🚀 |  - Đồ thị thời gian thực PyQtGraph viền mượt, nền hòa sắc     |
| ⚙️ |  - Heatmap trực quan cho Process (Ăn nhiều CPU tự sáng màu)   |
|    |                                                               |
+----+---------------------------------------------------------------+
```

1. **Sidebar bên trái (Gọn gàng & Chuyên nghiệp)**:
   - Nút Hamburger `☰` để thu gọn / mở rộng sidebar.
   - Các icon Fluent:
     - 📈 **Performance** (Biểu đồ hiệu năng CPU, RAM, Disk, Net)
     - ⚙️ **Processes** (Quản lý tiến trình)
     - 🚀 **Startup Apps** (Ứng dụng khởi động)
     - 🛠️ **Services** (Dịch vụ hệ thống)
     - ⚙️ **Settings** (Cài đặt tần suất quét, theme)

---

## 📐 4. Chi tiết Nâng cấp từng Màn hình

### 4.1. Performance Page (Hiệu năng trực quan)
- **Sidebar danh sách linh kiện**:
  - Dùng `CardWidget` với bo góc 8px.
  - Khi chọn linh kiện nào, sẽ có thanh trượt highlight xanh dương di chuyển mượt mà (accent pill).
  - Có mini sparkline hoặc thanh đo % tải chạy mượt.
- **Khu vực đồ thị**:
  - Tối ưu hóa màu nền biểu đồ hòa quyện hoàn hảo với màu nền cửa sổ `#1c1c1c`.
  - Đổ bóng nhẹ dạng gradient dưới đường cong (Area chart) tạo chiều sâu 3D.
  - Lưới tọa độ kẻ nét đứt cực mảnh (#2d2d2d), không gây rối mắt.
- **Lưới thông số kỹ thuật (Hardware Specs Cards)**:
  - Chia thành các ô nhỏ (Stat Tiles) với font số to đậm (`Segoe UI Variable` hoặc `Inter`, 20px Bold), bên dưới là nhãn mô tả xám nhạt (`11px Medium`).

### 4.2. Processes Page (Quản lý tiến trình - Heatmap)
- **Bảng dữ liệu Fluent Table**:
  - Không dùng bảng xám mặc định của hệ thống.
  - Mỗi hàng có độ cao chuẩn 36px, hiệu ứng hover đổi màu nền mềm mại.
  - **Tính năng Heatmap kiểu Windows**: Cột `CPU %` và `Memory` có màu nền cam/vàng/đỏ nhạt tự động đậm dần theo mức độ ngốn tài nguyên, giúp người dùng nhận ra ngay app nào đang làm đơ máy.
- **Thanh tìm kiếm & Hành động**:
  - Thanh tìm kiếm bo tròn chuẩn `SearchLineEdit` với icon kính lúp.
  - Nút **End Task** màu đỏ hiện đại với icon thùng rác hoặc dấu X viền mỏng.

---

## 🛠 5. Kế hoạch Triển khai Nâng cấp UI (Action Plan)

- [ ] **Bước 1: Cài đặt và tích hợp `QFluentWidgets`**:
  - Thêm `qfluentwidgets` vào `requirements.txt`.
  - Cài đặt vào môi trường ảo `.venv`.
- [ ] **Bước 2: Tái cấu trúc Cửa sổ chính (`MainWindow`)**:
  - Kế thừa `FluentWindow` hoặc `MSFluentWindow` của `qfluentwidgets`.
  - Dựng thanh Navigation Bar bên trái (Icon sidebar).
- [ ] **Bước 3: Đại tu Performance Tab**:
  - Dùng `ElevatedCardWidget` cho các thẻ linh kiện.
  - Tinh chỉnh lại màu sắc `pyqtgraph` để đạt độ thẩm mỹ cao nhất.
- [ ] **Bước 4: Nâng cấp Processes Tab với Fluent Table**:
  - Dùng `TableWidget` hiện đại có bo góc và style Fluent.

