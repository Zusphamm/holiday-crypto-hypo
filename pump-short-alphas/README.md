# pump-short-alphas

Hai luật short trên perpetual Binance USDT-M đã sống qua một lần chạy out-of-sample, đến từ một dự án mining riêng
(không liên quan ngày lễ). Cả hai đều đánh ngược một cú pump không có vị thế mới đứng sau.

| Tài liệu | Nội dung |
|---|---|
| [origin](origin.md) | mỗi ý tưởng đến từ đâu (LLM mining / ý tưởng viết tay) và anomaly nằm ở đâu |
| [variants](variants.md) | tất cả các bản A / A* / B / B*, và 2 alpha trên top-30 so với coin nhỏ hơn |

## Luật

| Alpha | Tín hiệu trên nến ngày d (UTC) | Lệnh |
|---|---|---|
| A* (pump khi OI giảm) | open interest 7 ngày giảm ≥ 25% và lợi nhuận 1 ngày ≥ +13% và độ lệch chuẩn lợi nhuận ngày 30 ngày ≤ 0.12 | short 10 ngày |
| retail_crowded_long | z-score tỷ lệ tài khoản long/short toàn sàn ≥ 1.806 và lợi nhuận 7 ngày ≥ +24.95% | short 7 ngày |

| Mục | Giá trị |
|---|---|
| Rổ coin | top-100 perp theo volume $ trung bình 30 ngày, tại thời điểm đó, có cả coin đã bị delist |
| Vào / ra | giá đóng nến 1h lúc 01:00 UTC ngày d+1, thoát sau thời gian giữ |
| Chi phí | 16 bp khứ hồi + funding trả / nhận |
| Stop | thoát ở mốc ngày đầu tiên lỗ −50% (A*: giá đóng cửa ngày ≥ giá vào × 1.5) |
| Trùng lệnh | mỗi coin chỉ 1 lệnh mở cho mỗi luật |
| Sổ | 10 slot, mỗi slot 10% (1/n khi hơn 10 lệnh mở), còn lại để tiền mặt |
| Dữ liệu | nến, funding và `metrics` (OI, tỷ lệ long/short) của Binance từ data.binance.vision; OI / tỷ lệ của altcoin chỉ có từ 2021-12 |

## Kết quả

IS 2021-01 .. 2023-12, OS 2024-01 .. 2026-06. Lợi nhuận ròng mỗi lệnh sau phí và funding; SR và drawdown của sổ 10 slot.

| Alpha | IS lệnh · thắng · TB · SR · DD | OS lệnh · thắng · TB · SR · DD |
|---|---|---|
| A* | 97 · 79% · +7.7% · 0.47 · −27% | 83 · 69% · +5.9% · 0.92 · −16% |
| retail_crowded_long | 37 · 70% · +7.3% · 0.83 · −8% | 302 · 68% · +3.4% · 0.36 · −58% |

Theo regime BTC (xu hướng = dấu lợi nhuận 30 ngày của BTC, biến động = vol 30 ngày của BTC so với trung vị 365 ngày),
TB mỗi lệnh trên OS:

| Alpha | tăng·êm | tăng·biến động | giảm·êm | giảm·biến động |
|---|---|---|---|---|
| A* | 11 · +0.7% | 22 · +3.4% | 8 · +3.4% | 42 · thắng 81% · +9.0% |
| retail_crowded_long | 108 · +4.8% | 112 · +2.7% | 34 · −1.8% | 48 · thắng 81% · +5.6% |

![biểu đồ](pump_short_alphas.png)

File: `trades.csv` (mọi lệnh: alpha, giai đoạn, coin, vào, ra, regime BTC, lợi nhuận ròng), `results.json`.

## Lưu ý

| Lưu ý | Ảnh hưởng |
|---|---|
| Chọn lọc | retail_crowded_long là 1 trong 17 ý tưởng đạt IS được OS giữ lại; tham số A* được tối ưu sau khi OS đã bị nhìn 1 lần. OS không còn là holdout sạch |
| Stop bị trượt | stop chỉ kiểm tra theo mốc ngày, nên 1 lệnh vẫn có thể lỗ > 50% (lệnh OS tệ nhất −124%) |
| Short coin pump | nhiều lệnh thua bị giá vọt rất xa trước khi sập; stop chặt hơn làm TB trên OS thành âm |
| Regime | giảm·biến động trông tốt nhất cho cả hai, nhưng chỉ thấy sau khi đã xem OS: chưa phải là luật |
| Kiểm định forward | sổ paper forward cho cả 2 luật bắt đầu từ 2026-10-23 |

Chỉ để nghiên cứu, không phải lời khuyên đầu tư.

## Liên quan

- [origin](origin.md) · [variants](variants.md)
- [kiểm định ngày lễ](../README.md)
