# Individual contribution report

## Thông tin

- Họ và tên: Nguyễn Khánh Sơn
- Mã học viên: 2A202602388
- Nhóm: Nhóm K4-L3A (RAG Pipeline Ký túc xá FPT)
- Repository/branch: main

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 6 — Lexical Search (BM25) | Hiện thực hóa tìm kiếm từ khóa với BM25Okapi trên cùng tập corpus chunks của Task 4 | `src/task6_lexical_search.py` | Done |
| Task 7 — Reranking (RRF) | Cài đặt thuật toán Reciprocal Rank Fusion gộp bảng xếp hạng Dense và Sparse với hằng số k=60 | `src/task7_reranking.py` | Done |
| Task 8 & 9 — Fallback & Pipeline | Xây dựng chiến lược Fallback vectorless và tổng hợp pipeline truy xuất hoàn chỉnh theo đúng contract | `src/task8_pageindex_vectorless.py`, `src/task9_retrieval_pipeline.py` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Sử dụng công thức RRF chuẩn: $RRF\_Score = \sum \frac{1}{k + rank}$ với $k = 60$, rank bắt đầu từ 1 và chỉ gộp bảng xếp hạng một lần duy nhất.  
   **Lý do/evidence:** Hằng số $k = 60$ giúp cân bằng giữa những tài liệu đứng đầu và những tài liệu đứng sau ở cả 2 bảng xếp hạng. Việc chỉ fuse một lần ngăn ngừa việc méo mó trọng số và đảm bảo tuân thủ đúng module contract.  
   **Trade-off:** RRF chỉ dựa trên thứ hạng (rank) mà bỏ qua độ lớn tuyệt đối của điểm số cosine hay BM25.

2. **Quyết định:** Sử dụng điểm tương đồng cosine gốc của Dense Retrieval để kích hoạt Fallback thay vì dùng điểm RRF.  
   **Lý do/evidence:** Điểm RRF phụ thuộc vào số lượng danh sách gộp và không phản ánh trực tiếp độ tương quan tuyệt đối của câu hỏi với ngữ liệu. Khi `dense_cosine_score < score_threshold (0.30)`, hệ thống nhận biết câu hỏi có thể ngoài phạm vi hoặc dùng từ khóa hiếm để chuyển sang cơ chế vectorless fallback.  
   **Trade-off:** Cần kiểm tra điểm dense search trước khi thực hiện fusion.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: `pytest tests/test_contracts.py -k "test_lexical_search or test_rrf or test_retrieve"`
- Kết quả trước/sau nếu có: Với câu hỏi chứa từ khóa số liệu cụ thể như "định mức điện 200 số", BM25 xếp chunk này ở vị trí số 1, sau khi fuse qua RRF chunk này đã vượt lên đầu context so với việc chỉ dùng dense search.
- Lỗi đã phát hiện và cách xử lý: Xử lý trường hợp fallback provider gặp sự cố mạng -> bọc trong khối `try...except` để đảm bảo hệ thống không bị crash và trả về safe refusal hoặc kết quả hybrid tốt nhất có thể.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: Hiện tại hàm tiền xử lý từ khóa cho BM25 chỉ dựa trên ngắt từ cơ bản, chưa có từ điển đồng nghĩa (Synonym Mapping) cho tiếng Việt.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: Bổ sung từ điển đồng nghĩa chuyên biệt cho ký túc xá (ví dụ: "KTX" = "Ký túc xá", "BQL" = "Ban quản lý", "Dom" = "Tòa nhà") để tăng Recall cho BM25.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 20/09/2026
- Tên thành viên: Nguyễn Khánh Sơn
