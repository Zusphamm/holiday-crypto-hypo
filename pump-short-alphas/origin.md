# origin

Hai ý tưởng đến từ đâu, và anomaly nằm ở chỗ nào.

## A / A* được tìm ra thế nào (máy mining, 2026-10-22)

| Bước | Chuyện gì xảy ra |
|---|---|
| 1. Bộ feature | feature theo ngày cho mỗi perp: lợi nhuận (1 ngày / 7 ngày), thay đổi open interest, funding, tỷ lệ taker mua, z-score volume / biên độ, khoảng cách tới đỉnh 30 ngày |
| 2. LLM đề xuất | một LLM chạy local (Qwen3-8B) đọc bảng xếp hạng các luật cũ + các lần trượt gần đây rồi đề xuất luật mới, mỗi vòng bắt buộc dùng 2 feature |
| 3. Ngưỡng | code chỉnh ngưỡng sao cho có ~40 lần vào lệnh in-sample, chỉ dựa trên số lần tín hiệu (không nhìn lợi nhuận) |
| 4. Test IS | backtest 2021-2023: `oi_chg_7d <= -0.25 & ret_1d >= 0.13 -> short 7 ngày, hedge BTC` = luật A, phép thử thứ 417: 114 lệnh, thắng 71%, +3.6% mỗi lệnh. Trượt các kiểm tra chặt (deflated Sharpe 0.08, một năm yếu) nhưng đạt ngưỡng "hit" (n >= 15, thắng >= 65%, TB >= +2%) |
| 5. OS batch | 160 luật đã đóng băng chạy 1 lần trên 2024-01 .. 2026-06; 25 luật đạt (n >= 10, thắng >= 55%, TB >= +1%). A (+2.6%) và bản anh em B (`oi <= -0.30 & ret_1d >= 0.15`, không hedge, +5.4%) nằm trong số đó, nhưng có lệnh lỗ −216% / −248% |
| 6. Tối ưu | 12.000 ô lưới (ngưỡng OI, ngưỡng pump, thời gian giữ, hedge, kiểu stop, lọc biến động) trên IS và OS, nhằm tìm stop vẫn cho giá chạy nhưng chặn được các pha sập. OS đã bị nhìn trước đó, nên bước này không còn là holdout sạch |
| 7. A* | giữ 10 ngày, không hedge, thoát nếu giá đóng cửa ngày >= giá vào × 1.5, và bỏ qua coin có độ lệch chuẩn lợi nhuận ngày 30 ngày > 0.12 (các pha sập trên OS là coin có độ lệch chuẩn 0.2-0.4) |

Lời giải thích của LLM là sai: nó hiểu `oi_chg_7d` là giá giảm 7 ngày. Luật được giữ vì con số; cơ chế bên dưới
được phân tích lại sau.

## Anomaly nằm ở đâu (A*)

| Cú pump bình thường | Cú pump này |
|---|---|
| giá +13% trong ngày đi kèm open interest tăng: long đòn bẩy mới đuổi theo | open interest đã **giảm >= 25% trong 7 ngày**: vị thế đang được đóng, không phải mở mới |
| tiền mới tiếp tục mua | lực mua chủ yếu là bị ép: short đóng lệnh (đóng short = lệnh mua market, và làm OI giảm) hoặc sổ lệnh mỏng bị đẩy |
| xu hướng có thể tiếp diễn | đóng short xong thì không còn ai mua; giá trôi về lại trong những ngày sau |

Vậy anomaly là **sự lệch nhau giữa giá và vị thế**: một ngày tăng mạnh mà không có open interest mới đứng sau.
"Giá tăng + OI giảm = short đóng lệnh, đợt tăng yếu" là một kinh nghiệm cũ của thị trường futures; luật này biến nó
thành thứ kiểm định được trên perp. Bộ lọc biến động loại đi những trường hợp hỏng nặng nhất: coin đang trong cơn hưng
phấn, nơi cú squeeze còn chạy tiếp. Luật chạy tốt nhất khi BTC đang giảm và biến động mạnh (OS thắng 81%, +9% mỗi
lệnh trong regime đó), lúc một altcoin pump đơn lẻ càng khó là cầu thật. Đây là giải thích hợp lý nhất, chưa được
chứng minh là nguyên nhân.

## retail_crowded_long được tìm ra thế nào (viết tay, 2026-10-23)

| Bước | Chuyện gì xảy ra |
|---|---|
| Ý tưởng | một trong 10 ý tưởng viết tay theo hướng "ai đang bị buộc phải giao dịch": sau một tuần tăng mạnh, retail đổ xô vào long |
| Tín hiệu | tỷ lệ long/short theo **số tài khoản** toàn sàn Binance (đếm tài khoản, không theo khối lượng: thước đo đám đông retail), dạng z-score so với lịch sử của chính nó, cộng lợi nhuận 7 ngày |
| Chỉnh ngưỡng | ý tưởng ban đầu là z >= 3 & ret_7d >= 30%; ngưỡng được chỉnh để có 15-150 lần vào lệnh IS -> z >= 1.806 & ret_7d >= 24.95% |
| IS | 37 lệnh, thắng 70%, +7.3%, dương ở mọi năm IS |
| OS | 1 trong 17 ý tưởng đạt IS vượt được ngưỡng OS (302 lệnh, thắng 68%, +3.4%) |

Anomaly: sau một tuần +25%, tỷ lệ tài khoản đang long cao bất thường. Đó là bên mua muộn, nhỏ lẻ, dùng đòn bẩy; còn
rất ít cầu mới và bên dưới có nhiều stop / điểm thanh lý. Lệnh short đặt cược rằng phía đông người sẽ phải xả.

## Liên quan

- [README](README.md)
- [variants](variants.md)
