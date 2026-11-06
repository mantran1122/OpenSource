# ⚡ LinTask Manager

<p align="center">
  <img src="assets/icons/lintask.svg" width="100" height="100" alt="LinTask Manager Logo">
</p>

<p align="center">
  <b>A Modern, Intuitive Windows 11 Fluent-Style Task Manager for Linux</b><br>
  <i>Built with Python 3, PyQt6, QFluentWidgets, and pyqtgraph</i>
</p>

<p align="center">
  <a href="https://www.gnu.org/licenses/gpl-3.0"><img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="License: GPLv3"></a>
  <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue?logo=python" alt="Python Versions">
  <img src="https://img.shields.io/badge/Platform-Linux-orange?logo=linux" alt="Platform">
  <img src="https://img.shields.io/badge/UI-Fluent%20Design-0078d4?logo=windows" alt="Fluent Design">
  <img src="https://img.shields.io/badge/Tests-14%20Passed-brightgreen" alt="Tests">
</p>

---

## 📖 Giới thiệu (About LinTask)

**LinTask Manager** là ứng dụng theo dõi hiệu năng hệ thống và quản lý tiến trình dành riêng cho Linux, được thiết kế theo chuẩn ngôn ngữ **Windows 11 Fluent Design** hiện đại.

Dự án ra đời nhằm giải quyết những hạn chế của các công cụ mặc định trên Linux:
- **CLI (`top`, `htop`, `btop`)**: Rất mạnh mẽ nhưng thiếu thao tác chuột đồ họa trực quan và khó tiếp cận cho người mới chuyển từ Windows sang Linux.
- **Công cụ GUI mặc định (GNOME/KDE System Monitor)**: Bố cục rời rạc, thiếu biểu đồ sóng nhỏ gọn (mini sparklines) tại cột điều hướng, thiếu tính năng **quản lý ứng dụng tự khởi động (Startup Apps)** và **quản lý dịch vụ hệ thống (Systemd Services)** tập trung.

---

## ✨ Tính năng nổi bật (Key Features)

### 📈 1. Tab Performance (Hiệu năng trực quan 60 FPS)
- **Sidebar Mini Sparklines**: Cột bên trái hiển thị đồng thời cả 4 biểu đồ sóng thời gian thực cho **CPU**, **Memory**, **Disk I/O** và **Network** (không cần nhấp chuột chuyển tab vẫn nắm bắt toàn bộ trạng thái máy).
- **CPU Monitoring**: Đồ thị sóng 60 giây gần nhất, xung nhịp hiện tại (GHz), số Process, Threads, Socket/Cores/Threads, và thời gian hoạt động (Up time `D:HH:MM:SS`).
- **Memory Monitoring**: Mức tiêu thụ RAM thời gian thực, phân bổ In-use, Available, Cached, Buffers và bộ nhớ ảo Swap.
- **Disk I/O**: Tốc độ đọc / ghi thời gian thực, tự động co giãn dải đo và thống kê phân vùng ổ đĩa chính (`/`).
- **Network Throughput**: Đồ thị gửi (Send / Upload) và nhận (Receive / Download) theo từng card mạng.

### ⚙️ 2. Tab Processes (Quản lý tiến trình thông minh)
- **Kiến trúc Model-View hiệu năng cao**: Tải và lọc hàng trăm tiến trình trong nền ngầm với mức tiêu tốn CPU < 1%.
- **Sắp xếp số học (Numeric Sorting)**: Nhấp vào tiêu đề bất kỳ (`CPU %`, `Memory`, `Disk`, `PID`) để đảo chiều tăng/giảm chính xác tuyệt đối (100% luôn xếp trên 15%, 1.2 GB luôn xếp trên 450 MB).
- **Hiệu ứng Heatmap đổi màu**: Tự động phủ dải màu cảnh báo thông minh theo phong cách Windows 11:
  - Ứng dụng ăn nhiều CPU (20% – 50%+) tự động sáng màu cam/đỏ.
  - Ứng dụng chiếm nhiều RAM (500MB – 1.5GB+) tự động sáng màu tím đặc trưng.
- **Menu chuột phải (`RoundMenu`)**:
  - 🛑 **End Task** (`SIGTERM` - tắt an toàn).
  - ⚡ **Force Kill** (`SIGKILL` - buộc dừng tức thì).
  - ⏸ **Pause Process** (`SIGSTOP`) & ▶ **Resume Process** (`SIGCONT`).
  - 📊 **Set Priority**: Menu con điều chỉnh Nice value (High `-10`, Normal `0`, Low `10`).
  - 📂 **Open File Location**: Mở thư mục chứa file chạy của ứng dụng trong File Manager.
  - 📋 **Copy PID** vào clipboard.

### 🚀 3. Tab Startup Apps (Ứng dụng khởi động cùng máy)
- **Quét thông minh chuẩn XDG**: Quét cả ứng dụng cá nhân (`~/.config/autostart`) và toàn hệ thống (`/etc/xdg/autostart`).
- **Công tắc Switch Fluent**: Bật/tắt ứng dụng tự khởi động tức thì chỉ bằng một cú click chuột (tự động xử lý `Hidden=true/false`).
- **Thêm ứng dụng mới (+ Add App)**: Hộp thoại đồ họa cho phép nhập tên, lệnh thực thi và nút **Browse...** duyệt file chạy.
- **Xóa ứng dụng**: Nút thùng rác dọn dẹp các mục khởi động cá nhân không dùng đến.

### 🛠️ 4. Tab Services (Quản lý dịch vụ Systemd)
- **Quản lý toàn diện**: Quét toàn bộ dịch vụ `systemd` trên máy, phân loại trạng thái bằng màu sắc trực quan (Active = xanh lá, Inactive = xám, Failed = đỏ).
- **Bộ lọc đa năng**: Lọc nhanh theo nhóm (*All*, *Active/Running*, *Inactive/Stopped*, *Failed*) và tìm kiếm theo tên/mô tả dịch vụ.
- **Điều khiển một chạm**: Các nút **Start**, **Stop**, **Restart**, **Enable** (chạy khi boot máy), **Disable**.
- **Tích hợp Polkit (`pkexec`)**: Tự động mở hộp thoại xác thực quyền quản trị khi thao tác với dịch vụ hệ thống.

### ⚙️ 5. Tab Settings & Tích hợp hệ thống
- **Tần suất cập nhật (Update Frequency)**: Tùy chỉnh tần số quét giữa *High (0.5s)*, *Normal (1.0s)*, hoặc *Eco / Power Saving (2.0s)*.
- **Theme**: Chuyển đổi giữa giao diện tối (Dark Theme) và giao diện sáng (Light Theme).
- **Đăng ký Shortcut Menu Linux**: Bấm nút **Add to App Menu** để đăng ký LinTask Manager vào menu ứng dụng máy tính (GNOME App Grid, KDE Kickoff, Mint Menu...), có thể tìm và mở app mà không cần mở Terminal.

---

## 📥 Hướng dẫn cài đặt & Chạy (Installation)

### ⚡ Cài đặt nhanh 1 dòng lệnh (One-Liner Install)

Mở Terminal và dán lệnh sau để tự động tải, thiết lập môi trường ảo và tích hợp vào thanh tác vụ:

```bash
git clone https://github.com/mantran1122/OpenSource.git && cd OpenSource && chmod +x install.sh && ./install.sh
```

> [!TIP]
> **Dành cho Ubuntu / Debian / Zorin OS / Linux Mint:** Nếu máy bạn chưa cài công cụ môi trường ảo Python, chỉ cần chạy lệnh này trước:
> ```bash
> sudo apt update && sudo apt install -y python3-venv python3-pip
> ```

---

### Cách 1: Cài đặt tự động từng bước bằng Script

```bash
# 1. Clone mã nguồn từ GitHub
git clone https://github.com/mantran1122/OpenSource.git
cd OpenSource

# 2. Cấp quyền và chạy cài đặt tự động (tự tạo môi trường ảo và tích hợp Taskbar)
chmod +x install.sh
./install.sh

# 3. Khởi chạy ứng dụng
python3 run.py
```

---

### Cách 2: Cài đặt thủ công từng bước

#### 1. Yêu cầu hệ thống (Prerequisites)
Đảm bảo máy bạn đã cài Python 3.10 trở lên và thư viện đồ họa cơ bản của Qt:

- **Ubuntu / Debian / Linux Mint**:
  ```bash
  sudo apt update
  sudo apt install -y python3 python3-pip python3-venv git libgl1 libegl1 libxkbcommon-x11-0
  ```
- **Fedora / RHEL**:
  ```bash
  sudo dnf install -y python3 python3-pip git mesa-libGL mesa-libEGL libxkbcommon-x11
  ```
- **Arch Linux / Manjaro**:
  ```bash
  sudo pacman -S --needed python python-pip git
  ```

#### 2. Khởi tạo môi trường ảo & Cài đặt thư viện
```bash
# Tạo môi trường ảo
python3 -m venv .venv
source .venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt

# Khởi chạy LinTask Manager
python3 run.py
```

> **Mẹo nhỏ**: File `run.py` đã được tích hợp cơ chế tự động nhận diện `.venv`. Lần sau bạn chỉ cần gõ `python3 run.py` là app sẽ tự kích hoạt môi trường ảo ngầm!

---

## 🗂 Cấu trúc thư mục mã nguồn (Project Architecture)

```text
LinTask-Manager/
├── .github/
│   └── workflows/
│       └── test.yml                 # GitHub Actions CI tự động kiểm thử 4 bản Python
├── assets/
│   └── icons/
│       └── lintask.svg              # Logo ứng dụng chính thức
├── lintask/
│   ├── __init__.py
│   ├── app.py                       # Khởi tạo QApplication
│   ├── core/                        # Tầng logic xử lý hệ thống
│   │   ├── collector.py             # QThread chạy ngầm lấy thông số OS (Non-blocking)
│   │   ├── process_mgr.py           # Quản lý tiến trình (Kill, Pause, Priority, Inspect)
│   │   ├── startup_mgr.py           # Quét và chỉnh sửa file .desktop autostart
│   │   └── service_mgr.py           # Tương tác với systemctl & pkexec
│   ├── models/                      # Cấu trúc dữ liệu & Qt Models
│   │   ├── metrics.py               # Dataclass CPU, RAM, Disk, Network
│   │   ├── process_info.py          # Dataclass ProcessInfo
│   │   ├── process_model.py         # TableModel tiến trình với Heatmap & Numeric Sort
│   │   ├── startup_item.py          # Dataclass StartupItem
│   │   ├── service_item.py          # Dataclass ServiceItem
│   │   └── service_model.py         # TableModel dịch vụ với Color-coded Status
│   ├── ui/                          # Tầng hiển thị giao diện Fluent
│   │   ├── main_window.py           # Cửa sổ chính FluentWindow & Sidebar navigation
│   │   ├── tabs/
│   │   │   ├── performance_tab.py   # Tab biểu đồ hiệu năng & phần cứng
│   │   │   ├── processes_tab.py     # Tab bảng danh sách tiến trình
│   │   │   ├── startup_tab.py       # Tab quản lý ứng dụng khởi động
│   │   │   ├── services_tab.py      # Tab quản lý dịch vụ systemd
│   │   │   └── settings_tab.py      # Tab cài đặt tần số, theme và desktop shortcut
│   │   └── widgets/
│   │       ├── live_graph.py        # Widget biểu đồ sóng pyqtgraph & MiniSparkline
│   │       └── stat_card.py         # Thẻ card linh kiện với biểu đồ mini tích hợp
│   └── utils/
│       ├── formatters.py            # Chuyển đổi Bytes/s, Uptime, Tần số GHz
│       └── desktop_integration.py   # Tự động tạo .desktop vào menu Linux
├── tests/                           # 14 Unit Tests kiểm thử tự động
│   ├── test_desktop_integration.py
│   ├── test_formatters.py
│   ├── test_process_mgr.py
│   ├── test_service_mgr.py
│   └── test_startup_mgr.py
├── .gitignore
├── install.sh                       # Script cài đặt một chạm
├── LICENSE                          # Giấy phép GNU GPL-3.0
├── pyproject.toml
├── requirements.txt
├── run.py                           # Điểm chạy ứng dụng chính
├── PROJECT_SPECIFICATION.md         # Đặc tả kỹ thuật và kiến trúc chi tiết
└── UI_UX_SPECIFICATION.md           # Thiết kế hệ thống Fluent Design
```

---

## 🧪 Chạy Kiểm thử Tự động (Running Tests)

Dự án được bảo vệ bởi bộ Unit Test tự động cho toàn bộ các module core:

```bash
# Kích hoạt môi trường và chạy pytest
source .venv/bin/activate
pytest
```

Kết quả: **14/14 tests passed in 0.08s**.

---

## 🤝 Đóng góp phát triển (Contributing)

Mọi đóng góp từ cộng đồng đều được hoan nghênh nồng nhiệt!
1. Fork dự án trên GitHub.
2. Tạo nhánh tính năng mới (`git checkout -b feature/AmazingFeature`).
3. Commit thay đổi (`git commit -m 'feat: Add some AmazingFeature'`).
4. Đẩy lên nhánh của bạn (`git push origin feature/AmazingFeature`).
5. Mở một **Pull Request** trên GitHub.

---

## 📄 Giấy phép Bản quyền (License)

Dự án được phân phối dưới giấy phép **GNU General Public License v3.0 (GPL-3.0)**. Xem chi tiết tại file [LICENSE](./LICENSE).
