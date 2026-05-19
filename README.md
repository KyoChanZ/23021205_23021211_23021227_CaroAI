# Caro AI — Minimax & Alpha-Beta Pruning

Chương trình chơi cờ Caro giữa người và máy, sử dụng thuật toán **Minimax** và **Alpha-Beta Pruning** để AI chọn nước đi.

---

## Thành viên nhóm

| MSSV     | Họ tên           |
|----------|------------------|
| 23021205 | Nguyễn Văn An    |
| 23021211 | Nguyễn Hoàng Anh |
| 23021227 | Đỗ Văn Dũng      |

---

## Yêu cầu hệ thống

- Python **3.11+**
- `pygame >= 2.5.0`
- `numpy >= 1.24.0`

---

## Cài đặt

```bash
# Clone repository
git clone https://github.com/nhom/23021211_23021205_23021227_CaroAI.git
cd 23021211_23021205_23021227_CaroAI

# Cài thư viện
pip install -r requirements.txt
```

---

## Cách chạy

### 1. Chạy giao diện đồ họa (chơi game)

```bash
cd source_code
python main.py
```

**Hướng dẫn chơi:**
- Click vào ô trên bàn cờ để đặt quân **X** (người chơi).
- AI tự động đánh quân **O** sau mỗi lượt.
- Nút **New Game** — bắt đầu ván mới.
- Nút **AI: Alpha-Beta / AI: Minimax** — chuyển đổi thuật toán AI.
- Nút **Depth + / Depth −** — tăng/giảm độ sâu tìm kiếm (1–6).

Panel bên phải hiển thị:
- Lượt chơi hiện tại.
- Thuật toán và độ sâu đang dùng.
- Nước đi, giá trị đánh giá, số trạng thái đã xét và thời gian chạy của mỗi nước AI.

### 2. Chạy thực nghiệm benchmark (Level 3)

```bash
cd source_code
python main.py --benchmark

# Hoặc chỉ định độ sâu cụ thể
python main.py --benchmark --depths=1,2,3
```

Kết quả in ra terminal gồm bảng so sánh số trạng thái, thời gian chạy, nước đi được chọn cho từng trạng thái kiểm thử.

---

## Cấu trúc project

```
23021211_23021205_23021227_CaroAI/
│
├── source_code/
│   ├── main.py        # Điểm vào chương trình
│   ├── config.py      # Hằng số cấu hình (kích thước bàn cờ, màu sắc, điểm...)
│   ├── board.py       # Logic bàn cờ: đặt quân, kiểm tra thắng, sinh nước đi
│   ├── evaluator.py   # Hàm đánh giá trạng thái bàn cờ
│   ├── ai.py          # Thuật toán Minimax và Alpha-Beta Pruning
│   ├── ui.py          # Giao diện đồ họa Pygame
│   └── benchmark.py   # Script thực nghiệm so sánh thuật toán
│
├── requirements.txt
└── README.md
```

---

## Luật chơi

- Bàn cờ **9×9** ô.
- Hai bên lần lượt đặt quân: người chơi là **X**, máy là **O**.
- **Thắng** khi có **4 quân liên tiếp** theo hàng ngang, hàng dọc hoặc đường chéo.
- Không áp dụng luật chặn hai đầu.
- **Hòa** khi bàn cờ đầy mà không ai thắng.

---

## Các thuật toán AI

### Minimax
Duyệt toàn bộ cây trò chơi đến độ sâu giới hạn. Lượt AI chọn nước có giá trị lớn nhất; lượt người chọn nước có giá trị nhỏ nhất.

### Alpha-Beta Pruning
Cải tiến Minimax bằng cách cắt nhánh không cần xét:
- `alpha`: giá trị tốt nhất MAX đã đạt — cập nhật khi tìm được giá trị lớn hơn.
- `beta`: giá trị tốt nhất MIN đã đạt — cập nhật khi tìm được giá trị nhỏ hơn.
- Cắt nhánh khi `beta ≤ alpha`.

### Hàm đánh giá
Tính điểm theo các chuỗi quân liên tiếp của mỗi bên:

| Chuỗi | Hai đầu mở | Một đầu mở |
|-------|-----------|------------|
| 3 quân (sắp = 4) | 10,000 | 5,000 |
| 2 quân | 1,000 | 200 |
| 1 quân | 50 | 10 |

Điểm AI trừ 2× điểm người chơi (ưu tiên phòng thủ).

---

## Tối ưu hóa sinh nước đi

Chỉ sinh các ô trống **trong vùng lân cận 2 ô** xung quanh các quân đã đánh, giảm đáng kể không gian tìm kiếm so với xét toàn bộ bàn cờ. Các ô được sắp xếp ưu tiên gần trung tâm.

---

## Tài liệu tham khảo

- Russell & Norvig, *Artificial Intelligence: A Modern Approach*, Chapter 5.
- https://github.com/husus/gomokuAI-py *(tham khảo cấu trúc project và cách đo benchmark)*
- https://github.com/MonHauVD/Caro_AI *(tham khảo ý tưởng move ordering và tổ chức module)*

> **Lưu ý:** Nhóm tự cài đặt toàn bộ thuật toán, luật chơi và hàm đánh giá theo yêu cầu đề bài. Các repo trên chỉ được dùng để tham khảo cấu trúc và phong cách tổ chức code.
