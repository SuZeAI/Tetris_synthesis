# Tetris_AI_DG
## Mở đầu
    * Trong github này tôi sẽ dùng thuật toán genetic kết hợp với Deeplearning
    * Và dùng môi trường có sẵn ở dưới

## Cách thức
    * Tôi sau khi tìm hiểu và tham khảo nhiều chỗ thì tôi thấy nó tối ưu cho con Agent là:
        1. Tổng số chiều cao
        2. Tổng số chênh lệch
        3. Tổng số hàng clear
        4. Tổng số lỗ
    * Tôi tập trung vào các thông tin trên và xây dựng mạng NN, nó gồm có đầu vào là (1, 4) và đầu ra là điểm số
    * Sau đó tôi thực hiện bằng cách tạo thuật toán genetic
    * Nghe có vẻ phức tạp nhưng chúng ta chỉ cần thực hiện từng con Agent chơi game và lấy điểm
    * Lấy những con có điểm cao nhất rồi cho lai với nhau và tạo ra các con Agent khác 
    và từ đó lặp lại ta sẽ tạo ra con Agent chs được game tetris

## Đánh giá
    Mô hình học sâu kết hợp genetic
## Tham Khảo
* [Env](https://github.com/fthomasmorel/Tetris-AI)
* [Env1](https://github.com/ylsung/TetrisBattle.git)