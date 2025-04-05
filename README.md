# AI Hashiwokakero Sovler
## Tổng Quan
Dự án giải trò chơi Hashiwokakero, còn được gọi là "Bridges". Trình giải sử dụng phương pháp SAT (Boolean Satisfiability) để mã hóa các ràng buộc của trò chơi và áp dụng kỹ thuật giải SAT để tìm ra lời giải hợp lệ. Chương trình được viết bằng Python và sử dụng thư viện pysat để giải bài toán SAT.
## Hashiwokakero là gì?
**Hashiwokakero** là một trò chơi logic với mục tiêu kết nối tất cả các đảo trên lưới bằng các cây cầu. Các quy tắc như sau:
- Mỗi đảo có một con số biểu thị số lượng cầu phải kết nối với nó.
- Cầu chỉ có thể nằm ngang hoặc dọc và không được cắt nhau.
- Tối đa hai cầu có thể kết nối giữa hai đảo.
- Tất cả các đảo phải được kết nối thành một khối liên thông duy nhất.
## Tính năng
- Mã hóa trò chơi Hashiwokakero thành **CNF (Conjunctive Normal Form)** để giải bằng SAT.
- Sử dụng thư viện `pysat` để xây dựng và giải công thức logic.
- Xuất lời giải dưới dạng văn bản dễ đọc.
- Hỗ trợ các bài toán với kích thước và độ phức tạp khác nhau.
## Yêu Cầu
- Python **3.8+**
- Các thư viện Python:
  ```bash
  pip install pysat numpy
  hashiwokakero-solver/
## Cấu trúc thư mục
- hashiwokakero1.py      # Mã nguồn chính của trình giải
- inputs/                # Chứa các bài toán đầu vào
+ input-01.txt
- Outputs/               # Thư mục lưu trữ kết quả
+ output-01.txt
- README.md              # Tài liệu hướng dẫn 
- LICENSE                # Thông tin bản quyền
## Hạn Chế
- Trình giải giả định rằng bài toán đầu vào là hợp lệ.
- Các bài toán lớn có thể mất nhiều thời gian để giải do độ phức tạp của việc giải SAT.
