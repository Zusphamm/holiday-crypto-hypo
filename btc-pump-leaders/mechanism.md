# mechanism

Vì sao "long coin có volume bùng nổ vào ngày BTC tăng mạnh" lại có lãi, và phần nào của luật thực sự có tác dụng.

## Tách nhóm

Xét mọi ngày BTC tăng ≥ 5% (IS: 70 ngày, OS: 26 ngày). Coin top-100 (trừ BTC) được chia thành 4 nhóm theo 2 điều kiện
của luật. Mỗi nhóm long 21 ngày, có phí và funding. Số trong bảng là lãi trung bình mỗi ngày của cả nhóm.

| Nhóm vào ngày BTC +5% | IS: ngày · coin · lãi TB · ngày thắng | OS: ngày · coin · lãi TB · ngày thắng |
|---|---|---|
| Gần đỉnh 30 ngày (≤ 10%) **+ volume bùng** (z ≥ 2.7) = luật | 39 · 133 · **+42.1%** · 69% | 15 · 64 · **+14.0%** · 60% |
| Xa đỉnh + volume bùng | 33 · 82 · **+53.1%** · 58% | 16 · 29 · **+11.7%** · 50% |
| Gần đỉnh, volume thường | 63 · 1592 · +18.9% · 71% | 25 · 537 · +2.0% · 48% |
| Còn lại | 70 · 4763 · +15.2% · 66% | 26 · 1929 · −0.6% · 46% |

Đọc bảng:

- **Volume là điều kiện chính.** Ở cả IS lẫn OS, hai nhóm có volume bùng đều hơn hẳn hai nhóm volume thường
  (OS: +12–14% so với −1–2%).
- **"Gần đỉnh" thêm rất ít.** Nhóm xa đỉnh mà volume bùng còn tốt hơn ở IS và chỉ kém nhẹ ở OS, nhưng ít ngày thắng
  hơn. Điều kiện gần đỉnh chủ yếu lọc bớt các cú bật hồi kém chắc chắn.
- **Bản thân ngày BTC +5% chỉ có tác dụng ở IS** (nhóm "còn lại" +15% ở 2021–2023, −0.6% ở OS). Phần beta altcoin này
  đã mất sau 2023, và đó là lý do bản gốc không còn vượt thị trường trên OS.

## Giải thích kinh tế

Đây là các giả thuyết phù hợp với bảng trên. Chưa cơ chế nào được kiểm định riêng (ví dụ chưa tách được phần thanh lý
khỏi volume).

| Cơ chế | Vì sao áp dụng ở đây |
|---|---|
| **Sự chú ý dồn vào một số coin** (high-volume return premium, Gervais–Kaniel–Mingelgrin 2001) | Volume tăng đột biến làm coin lọt vào các bảng "top gainers / top volume" trên sàn và mạng xã hội. Lượng người mua mới đến chậm trong vài tuần, nên giá tiếp tục được đẩy lên sau ngày tín hiệu |
| **Altcoin phản ứng chậm hơn BTC** (lead-lag BTC → alts) | Tiền vào BTC trước, rồi mới lan sang altcoin. Coin đã có volume bùng ngay trong ngày BTC tăng là coin được dòng tiền chọn đầu tiên. Đợt lan tiếp theo thường dồn vào chính chúng |
| **Short bị ép** | Coin vừa pump, gần đỉnh thường có nhiều người short theo kiểu "bắt đỉnh". Ngày BTC +5% làm short bị thanh lý hàng loạt, volume bùng một phần chính là lệnh thanh lý, và giá còn bị ép tiếp vài ngày sau đó |
| **Momentum chuỗi thời gian của crypto** | Trên các khung từ 1 đến 4 tuần, crypto có momentum mạnh hơn chứng khoán, vì nhà đầu tư nhỏ lẻ chiếm tỷ trọng lớn và phản ứng theo xu hướng |

Phần lớn các ô tốt nhất trên IS giữ lệnh 21 ngày chứ không phải 7–14 ngày. Điều này khớp với kiểu "dòng tiền đến chậm": phần lớn lãi đến sau tuần đầu tiên.

## Vì sao vẫn nên nghi ngờ

- **Sự kiện hiếm và tập trung.** 15 ngày OS, 3 ngày chiếm khoảng 90% lãi. Nếu bỏ đúng một đợt như sau bầu cử Mỹ
  11/2024 thì kết quả mỏng hẳn.
- **Phần vượt thị trường có t khoảng 1.1–1.3** ở cả IS lẫn OS, chưa đạt ngưỡng t ≥ 2. Lưới thử 7.776 ô, nên cần ngưỡng còn
  cao hơn mới loại được khả năng may mắn.
- **Lệnh lỗ rất nặng.** Lệnh tệ nhất −59%, và không có stop (stop −30% / −50% không cải thiện kết quả trên IS).
- **Coin volume bùng thường có thanh khoản mỏng.** Phí 16 bp giả định khớp lệnh tốt. Ở coin nhỏ, trượt giá lúc 01:00
  ngay sau cú bùng có thể lớn hơn nhiều.
- **OS của bản tối ưu đã bị nhìn trước khi chọn thước đo** (xem [README](README.md)). Chỉ paper chạy tiếp mới là phép
  thử sạch.

## Related

- [README.md](README.md)
- [../README.md](../README.md)
