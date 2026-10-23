# variants

Tất cả các bản của luật short khi pump mà OI giảm, và 2 alpha chia theo cỡ coin. IS 2021-01 .. 2023-12 (dữ liệu OI
của altcoin bắt đầu từ 2021-12, nên lệnh bắt đầu từ 2022), OS 2024-01 .. 2026-06. Chi phí 16 bp khứ hồi + funding.

## A / A* / B / B*

| Bản | Luật (short) | Giữ · hedge · stop · lọc biến động |
|---|---|---|
| A (mining) | OI 7 ngày ≤ −25% & lợi nhuận 1 ngày ≥ +13% | 7 ngày · hedge BTC · không · không |
| B (mining) | OI 7 ngày ≤ −30% & lợi nhuận 1 ngày ≥ +15% | 7 ngày · không · không · không |
| A* (tối ưu) | OI 7 ngày ≤ −25% & lợi nhuận 1 ngày ≥ +13% | 10 ngày · không · giá đóng cửa ngày ≥ giá vào × 1.5 · σ30 ≤ 0.12 |
| B* (tối ưu) | OI 7 ngày ≤ −30% & lợi nhuận 1 ngày ≥ +13% | 10 ngày · không · giá đóng cửa ngày ≥ giá vào × 1.5 · σ30 ≤ 0.10 |

| Bản | IS lệnh · thắng · TB · tệ nhất · SR | OS lệnh · thắng · TB · tệ nhất · SR |
|---|---|---|
| A | 114 · 71% · +3.6% · −36% · 0.89 | 213 · 58% · +2.6% · −216% · 0.31 |
| B | 56 · 79% · +7.1% · −24% · 1.08 | 111 · 63% · +5.4% · −248% · 0.46 |
| A* | 97 · 79% · +7.7% · −58% · 0.75 | 83 · 69% · +5.9% · −34% · 1.02 |
| B* | 52 · 89% · +9.1% · −13% · 0.69 | 34 · 71% · +6.6% · −25% · 0.57 |

SR ở đây = sổ chia đều cho các lệnh đang mở (như trong script tối ưu); sổ 10 slot trong README cho A* 0.47 / 0.92.
A và B được đóng băng trước khi chạy OS. A* và B* được tối ưu khi đã xem OS: OS của chúng là in-sample đối với bước
tối ưu, chỉ sổ paper forward (từ 2026-10-23) là sạch. A* theo năm: 2022 +12.9%, 2023 −6.4%, 2024 +5.6%,
2025 +6.0%, 2026 nửa đầu +8.0% mỗi lệnh.

![các bản](variants.png)

Biểu đồ cộng dồn lợi nhuận từng lệnh (không phải sổ có chia vốn). Cú nhảy tháng 11/2022 là vụ FTX sập: rất nhiều tín
hiệu cùng lúc, một phần lớn lợi nhuận IS đến từ cụm lệnh đó.

File: `variants_trades.csv` (bản, giai đoạn, coin, vào, ra, có dính stop, lợi nhuận ròng), `variants.json`.

## Theo cỡ coin (top-30 so với hạng 31-100)

Cùng luật, stop −50% và sổ 10 slot như README, rổ coin chia theo thứ hạng volume $ 30 ngày (tại thời điểm đó).

| Alpha · rổ coin | IS lệnh · thắng · TB · SR | OS lệnh · thắng · TB · SR · DD |
|---|---|---|
| A* · top-30 | 33 · 67% · +4.0% · 0.28 | 22 · 68% · +6.3% · 0.63 · −8% |
| A* · hạng 31-100 | 64 · 86% · +9.7% · 0.78 | 61 · 69% · +5.7% · 0.79 · −15% |
| retail · top-30 | 13 · 85% · +9.6% · 0.79 | 79 · 61% · +2.3% · 0.35 · −31% |
| retail · hạng 31-100 | 24 · 62% · +6.1% · 0.62 | 226 · 71% · +4.0% · 0.49 · −47% |

Cả hai vẫn đứng được trên 30 perp lớn nhất, chỉ ít lệnh hơn: edge không chỉ là hiệu ứng coin nhỏ.

## Liên quan

- [README](README.md)
- [origin](origin.md)
