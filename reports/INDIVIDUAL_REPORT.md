# Individual contribution report

## Thông tin

- Họ và tên: Bùi Thị Thu Uyên
- Mã học viên: 2A202602603
- Nhóm: [Tên nhóm] SHUP


## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Data collection | Thu thập và rà soát tài liệu nguồn; xác định đúng dạng dữ liệu legal/news cần lưu trong landing folder. | [data/landing](../data/landing) | Done |
| Data standardization | Chuẩn hóa nội dung theo cấu trúc Markdown đồng nhất, đảm bảo file có đủ độ dài và metadata rõ ràng. | [data/standardized](../data/standardized) | Done / Partial |
| Chunking + indexing | Nghiên cứu và triển khai logic chia chunk, giữ metadata và id ổn định cho từng chunk. | [src/task4_chunking_indexing.py](../src/task4_chunking_indexing.py) | Partial |
| Semantic retrieval | Kiểm tra cách query embedding, map cosine distance sang similarity và định dạng SearchResult đúng contract. | [src/task5_semantic_search.py](../src/task5_semantic_search.py) | Partial |
| Lexical retrieval | Tìm hiểu và áp dụng BM25 trên corpus chunks, đảm bảo rank giảm dần và filter các score <= 0. | [src/task6_lexical_search.py](../src/task6_lexical_search.py) | Partial |
| Hybrid retrieval + fallback | Tham gia thiết kế logic dùng dense + BM25 + RRF; xác định fallback dựa trên dense score và xử lý provider error. | [src/task7_reranking.py](../src/task7_reranking.py), [src/task9_retrieval_pipeline.py](../src/task9_retrieval_pipeline.py) | Partial |
| Generation + citation | Rà soát các yêu cầu của generation result, sources và retrieval_source để đáp ứng contract. | [src/task10_generation.py](../src/task10_generation.py) | Partial |
| Evaluation report | Soạn bộ câu hỏi test, kiểm tra golden dataset và viết phần đóng góp cá nhân. | [group_project/evaluation](../group_project/evaluation) | Partial |

Chỉ kê khai các phần có thể đối chiếu bằng file, commit, test hoặc kết quả thực thi.

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Dùng mô hình hybrid retrieval: dense + BM25 + RRF.
   **Lý do/evidence:** Theo contract và đề bài, retrieval cần vượt qua cả dense search lẫn lexical search; RRF giúp hợp nhất kết quả từ hai nguồn mà không cần hard-code ranking manua. Đây là mô hình phù hợp cho câu hỏi có từ khóa cụ thể và câu hỏi ngữ nghĩa.
   **Trade-off:** Tăng độ phức tạp và tốn thêm công đoạn đánh giá, nhưng cải thiện ổn định hơn so với chỉ dùng dense hoặc BM25 riêng lẻ.

2. **Quyết định:** Fallback dùng score gốc của dense retrieval thay vì RRF score.
   **Lý do/evidence:** Contract quy định rõ: threshold phải so sánh với cosine score của dense search và chỉ fallback khi dense score thấp. Điều này giúp tránh vô tình trả về tài liệu không đủ độ tin cậy vì hybrid score quá nhỏ.
   **Trade-off:** Nếu dense retrieval yếu, pipeline có thể chuyển sang pageindex hoặc safe refusal; lợi ích là giảm false positive nhưng có thể làm câu trả lời ít dữ liệu hơn khi không có nguồn mạnh.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng:
  - `pytest tests/test_contracts.py -q`
  - `pytest tests/test_acceptance.py -q`
  - `pytest -q`
- Kết quả trước/sau nếu có:
  - Ban đầu, repo đang ở trạng thái skeleton với nhiều `NotImplementedError` và các file chưa triển khai toàn bộ logic.
  - Các test acceptance bắt đầu fail do thiếu dữ liệu landing/standardized và file evaluation chưa hoàn thành.
  - Tôi đã sử dụng các output test để xác định đúng module cần sửa và ưu tiên fix theo contract.
- Lỗi đã phát hiện và cách xử lý:
  - Thiếu chunking và retrieval implementation: ưu tiên triển khai đúng theo signature và schema contract.
  - Thiếu dữ liệu tối thiểu: bổ sung dữ liệu vào đúng folder theo yêu cầu.
  - Report evaluation còn `TODO`: cập nhật bảng tiêu chí và nội dung đánh giá theo mô tả đề bài.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: phần retrieval và generation vẫn cần được triển khai/điều chỉnh thêm để đạt mức ổn định trên nhiều loại câu hỏi.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: tối ưu logic chunking + threshold calibration để tránh trường hợp retrieval quá nhạy hoặc quá chặt cho câu hỏi out-of-domain.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

