# 🚀 LinTask Manager - Bản Đặc Tả Kỹ Thuật & Kế Hoạch Dự Án
> **Công cụ quản lý tác vụ và hiệu năng hệ thống Linux phong cách Windows Task Manager**  
> *Dự án mã nguồn mở phát triển bằng Python & PyQt6*

---

## 📌 1. Tổng quan & Vấn đề thực tế (Problem Statement)

### 1.1. Vấn đề
Khi chuyển từ Windows sang Linux (Ubuntu, Debian, Fedora, Arch...), người dùng thường gặp phải các rào cản lớn trong việc theo dõi và quản lý tài nguyên hệ thống:
- **Công cụ dòng lệnh (`top`, `htop`, `btop`)**: Rất mạnh nhưng khó tiếp cận với người dùng phổ thông, không có thao tác chuột đồ họa trực quan.
- **Công cụ mặc định (GNOME / KDE System Monitor)**: Thường phân tán, thiếu các tính năng quan trọng như:
  - Biểu đồ theo dõi đọc/ghi ổ đĩa (Disk I/O) theo thời gian thực.
  - Đo lưu lượng mạng (Network throughput) chi tiết theo từng card mạng.
  - Quản lý ứng dụng tự khởi động cùng hệ thống (Startup Apps).
  - Quản lý trạng thái và điều khiển các dịch vụ hệ thống (`systemd`).

### 1.2. Mục tiêu dự án
**LinTask Manager** được xây dựng nhằm mang lại trải nghiệm quản lý hệ thống:
1. **Dễ hiểu & Trực quan**: Bố cục dạng thẻ (Tabs) giống Windows Task Manager quen thuộc, hiển thị biểu đồ thời gian thực mượt mà.
2. **Không giật lag (Zero-lag UI)**: Kiến trúc đa luồng (Multi-threading) tách biệt hoàn toàn giữa tác vụ đọc thông số OS và tác vụ dựng giao diện.
3. **Đa năng**: Tích hợp đầy đủ: Quản lý tiến trình, Biểu đồ hiệu năng, Quản lý ứng dụng khởi động và Dịch vụ nền.
4. **Chuẩn mã nguồn mở GitHub**: Codebase module hóa, có tài liệu rõ ràng, unit test và quy trình đóng gói dễ cài đặt.

---

## 🛠 2. Công nghệ sử dụng (Tech Stack)

| Thành phần | Công nghệ / Thư viện | Vai trò |
| :--- | :--- | :--- |
| **Ngôn ngữ** | Python 3.10+ | Đảm bảo tính dễ đọc, cộng đồng lớn, phát triển nhanh |
| **Giao diện (GUI)** | PyQt6 / PySide6 | Framework GUI desktop mạnh mẽ, hỗ trợ Dark/Light Theme bằng QSS |
| **Vẽ đồ thị (Plotting)** | `pyqtgraph` | Thư viện vẽ biểu đồ thời gian thực tối ưu bằng C++/Qt, tiêu thụ <1% CPU |
| **Dữ liệu hệ thống** | `psutil`, `/proc`, `/sys` | Thu thập thông số CPU, RAM, Disk, Network và Process |
| **GPU Stats** | `pynvml` (NVIDIA) / sysfs | Đọc nhiệt độ, % tải, VRAM GPU |
| **Dịch vụ & Autostart**| `systemd` / D-Bus, `.desktop` files | Quản lý Startup Apps và Systemd Services |
| **Hình thức cài đặt**| Git Clone & Python venv | Cài đặt trực tiếp qua Git (`git clone`) và chạy trong môi trường ảo Python. Không đóng gói nhị phân (no binary bundle) để giữ tính thuần mở, nhẹ, dễ đọc code, tùy biến và đóng góp |

---

## 🏛 3. Kiến trúc hệ thống (System Architecture)

```
+-------------------------------------------------------------+
|                     MAIN UI THREAD (PyQt6)                 |
|  - MainWindow (Tabs: Processes | Performance | Startup | Services)
|  - Real-time Graphs (pyqtgraph)                             |
|  - QSortFilterProxyModel (Tìm kiếm & Sắp xếp tiến trình)    |
+-------------------------------------------------------------+
                              ▲
                              │ Qt Signals / Slots
                              │ (SystemMetrics Dataclass)
                              ▼
+-------------------------------------------------------------+
|             BACKGROUND WORKER THREAD (QThread)             |
|  - MetricsCollector: Chạy vòng lặp định kỳ (mỗi 1000ms)    |
|  - ProcessManager: Xử lý Kill, Nice, Inspect an toàn       |
|  - AutoStartManager: Đọc/ghi các file .desktop             |
|  - ServiceManager: Giao tiếp systemctl / D-Bus             |
+-------------------------------------------------------------+
                              ▲
                              │ Linux Kernel APIs
                              ▼
+-------------------------------------------------------------+
|               LINUX OS (/proc, /sys, psutil, systemd)       |
+-------------------------------------------------------------+
```

### Nguyên tắc thiết kế:
- **Tách biệt Data Collector & UI Thread**: Mọi tác vụ I/O hệ thống không bao giờ được chạy trên Main Thread để tránh hiện tượng đơ ứng dụng (Not Responding).
- **Model-View Pattern**: Bảng danh sách tiến trình dùng `QAbstractTableModel` giúp hiển thị hàng trăm tiến trình cùng lúc với tốc độ phản hồi tính bằng mili-giây.

---

## 📋 4. Đặc tả tính năng chi tiết (Functional Specifications)

### 4.1. Tab 1: Processes (Quản lý tiến trình)
- **Hiển thị danh sách bảng**:
  - `Tên tiến trình` (kèm icon ứng dụng từ hệ thống).
  - `PID` (Process ID).
  - `CPU %` (mức tải vi xử lý).
  - `Memory` (dung lượng RAM chiếm dụng dạng MB hoặc %).
  - `Disk I/O` (tốc độ đọc/ghi đĩa thời gian thực).
  - `User` (người dùng sở hữu tiến trình).
- **Thao tác người dùng**:
  - Thanh tìm kiếm tức thì theo tên ứng dụng hoặc PID.
  - Chuột phải (Context Menu):
    - **End Task**: Gửi tín hiệu `SIGTERM`, hỗ trợ Force Kill (`SIGKILL`).
    - **Pause / Resume**: Tạm dừng (`SIGSTOP`) hoặc kích hoạt lại (`SIGCONT`).
    - **Set Priority (Nice)**: Điều chỉnh mức ưu tiên từ High (-10) đến Very Low (+19).
    - **Open File Location**: Mở vị trí file thực thi trong trình quản lý file.

### 4.2. Tab 2: Performance (Hiệu năng trực quan)
- **Sidebar bên trái**: Các thẻ mini (Summary Cards) hiển thị % CPU, RAM, Disk, Net, GPU.
- **Khu vực đồ thị bên phải (PyQtGraph)**:
  - **CPU**:
    - Đồ thị sóng 60 giây gần nhất.
    - Tùy chọn xem: Biểu đồ tổng quát HOẶC lưới đồ thị từng Core riêng biệt.
    - Thông số phụ: Tần số xung nhịp (GHz), số Process/Threads, Uptime máy.
  - **Memory**:
    - Đồ thị RAM sử dụng theo thời gian.
    - Thanh phân bổ: Used, Available, Cached/Buffers, Swap.
  - **Disk**:
    - Đồ thị tốc độ đọc / ghi (Read/Write KB/s, MB/s).
    - Danh sách phân vùng ổ đĩa (`/`, `/home`...) và dung lượng đã dùng.
  - **Network**:
    - Đồ thị tải về (Download) và tải lên (Upload).
    - Thông tin card mạng (Ethernet, Wi-Fi), địa chỉ IPv4, MAC.
  - **GPU**:
    - % Tải GPU, VRAM đã dùng, nhiệt độ (°C).

### 4.3. Tab 3: Startup Apps (Ứng dụng khởi động)
- **Nguồn dữ liệu**:
  - Đọc các file `.desktop` trong `~/.config/autostart/` (người dùng) và `/etc/xdg/autostart/` (toàn máy).
- **Chức năng**:
  - Danh sách ứng dụng khởi động cùng máy kèm icon và lệnh chạy.
  - Công tắc Bật/Tắt (Toggle Switch) nhanh cho từng ứng dụng.
  - Nút thêm mới ứng dụng vào danh sách khởi động.

### 4.4. Tab 4: Services (Dịch vụ hệ thống)
- **Nguồn dữ liệu**: Quản lý dịch vụ thông qua `systemd` (hỗ trợ cả user services và system services).
- **Chức năng**:
  - Tìm kiếm dịch vụ theo tên.
  - Xem trạng thái (`active (running)`, `inactive`, `failed`).
  - Nút thao tác: Start, Stop, Restart, Enable (tự chạy khi boot), Disable.

---

## 📂 5. Cấu trúc thư mục mã nguồn (Project Directory)

```text
LinTaskManager/
├── .github/
│   └── workflows/
│       ├── test.yml            # Tự động chạy pytest khi có PR / commit
│       └── release.yml         # Tự động build file chạy khi ra mắt phiên bản mới
├── assets/
│   ├── icons/                  # Icon ứng dụng & nút chức năng
│   └── styles/
│       ├── dark.qss            # Giao diện tối phong cách Windows 11 Fluent
│       └── light.qss           # Giao diện sáng
├── lintask/
│   ├── __init__.py
│   ├── app.py                  # Điểm khởi động ứng dụng Qt
│   ├── core/                   # Tầng logic thu thập dữ liệu & xử lý hệ thống
│   │   ├── __init__.py
│   │   ├── collector.py        # Worker Thread thu thập số liệu CPU, RAM, Disk, Net
│   │   ├── process_mgr.py      # Xử lý Kill, Nice, Tra cứu tiến trình
│   │   ├── startup_mgr.py      # Đọc và ghi file .desktop khởi động
│   │   └── service_mgr.py      # Tương tác với systemd
│   ├── models/                 # Cấu trúc dữ liệu & Qt Models
│   │   ├── __init__.py
│   │   ├── metrics.py          # Dataclass chứa snapshot thông số
│   │   └── process_model.py    # Model bảng danh sách tiến trình (QAbstractTableModel)
│   ├── ui/                     # Tầng hiển thị giao diện
│   │   ├── __init__.py
│   │   ├── main_window.py      # Cửa sổ chính & thanh Tabs
│   │   ├── tabs/
│   │   │   ├── processes_tab.py
│   │   │   ├── performance_tab.py
│   │   │   ├── startup_tab.py
│   │   │   └── services_tab.py
│   │   └── widgets/
│   │       ├── live_graph.py   # Widget biểu đồ thời gian thực (PyQtGraph)
│   │       └── stat_card.py    # Thẻ tóm tắt chỉ số bên sidebar
│   └── utils/
│       ├── __init__.py
│       ├── formatters.py       # Chuyển đổi Bytes sang KB/MB/GB, giây sang giờ:phút
│       └── icon_resolver.py    # Tìm icon tương ứng của app trên Linux
├── tests/                      # Unit tests
│   ├── test_collector.py
│   └── test_formatters.py
├── .gitignore
├── LICENSE                     # GPL-3.0
├── README.md                   # Tài liệu giới thiệu trên GitHub
├── pyproject.toml              # Quản lý dependencies (Poetry / Flit / pip)
├── requirements.txt            # Danh sách thư viện cần thiết
└── run.py                      # Script chạy thử nhanh trong lúc phát triển
```

---

## 🗓 6. Lộ trình phát triển 4 giai đoạn (Roadmap)

### 🔹 Giai đoạn 1: Nền tảng & Performance Tab (MVP - 1 đến 2 tuần)
- Khởi tạo khung dự án, thiết lập `requirements.txt` (`PyQt6`, `pyqtgraph`, `psutil`).
- Xây dựng `MetricsCollector` (Worker thread) thu thập CPU, RAM, Disk, Network.
- Dựng cửa sổ chính `MainWindow` và vẽ biểu đồ thời gian thực cho CPU & RAM.

### 🔹 Giai đoạn 2: Quản lý tiến trình (Process Manager - 1 tuần)
- Xây dựng `ProcessTableModel` và tích hợp tìm kiếm, sắp xếp theo cột.
- Thao tác chuột phải: Kill Process, Set Priority.

### 🔹 Giai đoạn 3: Tính năng mở rộng độc đáo (2 tuần)
- Xây dựng Tab `Startup Apps` (đọc/ghi file `.desktop`).
- Xây dựng Tab `Services` (giao tiếp `systemctl`).
- Tích hợp đo thông số GPU (NVIDIA / AMD).

### 🔹 Giai đoạn 4: Hoàn thiện giao diện & Tối ưu cài đặt qua Git (1 tuần)
- Áp dụng theme Fluent Dark/Light hiện đại với CSS của Qt (QSS).
- Viết unit test cho các module core.
- Xây dựng script `install.sh` tiện lợi: Tự động tạo venv, cài dependencies và đăng ký shortcut `.desktop` vào menu ứng dụng Linux sau khi người dùng `git clone`.
- Hoàn thiện file `README.md` với hướng dẫn clone Git rõ ràng và hình ảnh demo trực quan.

---

## 🤝 7. Đóng góp & Bản quyền (License & Contribution)

- **Giấy phép đề xuất**: GNU General Public License v3.0 (`GPL-3.0`) để đảm bảo dự án luôn tự do và mã nguồn mở.
- **Tiêu chuẩn mã nguồn**: Tuân thủ chuẩn PEP 8, có type hints (`typing`), chú thích hàm rõ ràng để cộng đồng dễ dàng đọc hiểu và đóng góp (PR).

