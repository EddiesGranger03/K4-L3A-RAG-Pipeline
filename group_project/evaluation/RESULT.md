# RAG evaluation results

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 2026-09-20 |
| Framework and version              | RAGAS 0.4.3 / Python 3.14 |
| Evaluator model                    | meta/llama-3.1-70b-instruct (NVIDIA NIM) |
| Generator model                    | meta/llama-3.1-70b-instruct (NVIDIA NIM) |
| Embedding model                    | BAAI/bge-m3 (1024 dims) |
| Corpus version/commit              | FPT Dormitory Corpus v1.0 (7 documents) |
| Golden dataset size                | 16 Q&A pairs |
| `top_k`                            | 5 |
| Fallback threshold and calibration | Cosine threshold = 0.30 |

## Configurations

- **Config A — dense-only:** Sử dụng vector search đơn thuần (cosine similarity) từ ChromaDB với top_k=5, không sử dụng BM25 hay RRF.
- **Config B — hybrid + RRF:** Kết hợp dense semantic search (ChromaDB) và lexical search (BM25Okapi) trên cùng corpus chunks, sau đó áp dụng Reciprocal Rank Fusion (RRF với k=60) để xếp hạng lại top_k=5, kèm vectorless fallback khi dense score < 0.30.

Hai config phải dùng cùng golden dataset, generator, evaluator, prompt và `top_k`; chỉ thay retrieval strategy.

## Overall scores

| Metric            | Config A | Config B | Delta B−A |
| ----------------- | -------: | -------: | --------: |
| Faithfulness      |    0.842 |    0.938 |    +0.096 |
| Answer relevance  |    0.815 |    0.912 |    +0.097 |
| Context recall    |    0.789 |    0.941 |    +0.152 |
| Context precision |    0.801 |    0.925 |    +0.124 |
| **Average**       | **0.812**| **0.929**|**+0.117** |

## A/B comparison

- **Cấu hình tốt hơn:** Config B (Hybrid + RRF) vượt trội hơn Config A trên tất cả các tiêu chí đánh giá với mức tăng trung bình **+11.7%**.
- **Evidence:** 
  - Đối với các câu hỏi chứa từ khóa chuyên ngành, số liệu cụ thể (ví dụ: số phòng bảo vệ `(024) 668 05913`, định mức điện `200 số`, mã cổng `ocd.fpt.edu.vn`), BM25 giúp truy xuất chính xác chunk chứa con số tuyệt đối mà dense search đôi khi làm loãng trong không gian vector.
  - Điểm Context Recall tăng mạnh nhất (+15.2%), cho thấy sự kết hợp từ vựng và ngữ nghĩa giảm thiểu tình trạng bỏ sót ngữ cảnh quan trọng.
- **Trade-off về latency/cost:** 
  - Latency của Config B tăng khoảng 15ms so với Config A (do phải chạy thêm BM25 và phép tính RRF đơn giản trên CPU). Mức tăng này hoàn toàn không đáng kể so với thời gian sinh văn bản của LLM (thường từ 800ms - 1500ms).
  - Chi phí gọi LLM không đổi do cùng số lượng chunk (`top_k=5`) được chuyển vào context prompt.

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage             | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------------------- | ---------- |
|   1 | Cán bộ Ban Quản lý KTX kiểm tra phòng định kỳ vào những khung giờ nào? | Config A | 0.720 | 0.750 | 0.650 | 0.700 | retrieval | Dense search trả về chunks của slide giới thiệu chung thay vì chunk quy định SOP kiểm tra phòng của BQL. |
|   2 | Dịch vụ Internet tại KTX FPT do đơn vị nào cung cấp và đăng ký ở đâu? | Config A | 0.780 | 0.810 | 0.700 | 0.720 | retrieval | Từ khóa "Internet" và tên nhà mạng "FPT Telecom, Viettel" bị phân tán ở nhiều văn bản, dense không đạt top 1. |
|   3 | Đơn giá điện và nước phụ trội khi dùng vượt định mức tại KTX FPT là bao nhiêu? | Config A | 0.810 | 0.840 | 0.750 | 0.790 | generation | Mô hình trả lời đúng giá điện nhưng nhầm lẫn đơn vị tính của nước (khối vs số) khi context bị cắt giữa chừng. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
|        1 | Duy trì Hybrid + RRF làm phương thức mặc định cho hệ thống chatbot KTX | Context recall tăng từ 0.789 lên 0.941 và giảm thiểu lỗi tìm kiếm số liệu | Nâng cao độ tin cậy và sự hài lòng của sinh viên khi tra cứu quy định | Chạy bộ test tự động trên toàn bộ 16 câu hỏi golden dataset |
|        2 | Tối ưu hóa kích thước chunk và overlap đối với các bảng biểu/quy chuẩn số liệu | Các câu hỏi về định mức điện nước và số điện thoại cần ngữ cảnh nguyên vẹn | Ngăn chặn việc ngắt đôi câu hoặc mất tiêu đề bảng | Kiểm tra độ dài chunk thực tế qua `task4_chunking_indexing` |
|        3 | Bổ sung câu trả lời từ chối an toàn (Safe Refusal) khi câu hỏi nằm ngoài phạm vi | Giảm thiểu ảo tưởng (hallucination) khi người dùng hỏi về trường khác | Độ chính xác đạt 100% đối với các truy vấn out-of-domain | Test với câu hỏi kiểm thử out-of-domain trong test suite |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| Lost-in-the-middle Document Reordering | Thứ tự điểm RRF thông thường | Faithfulness: +0.035 | Latency: +0ms / Chi phí: 0$ | Đưa chunk điểm cao về 2 đầu prompt giúp LLM chú ý tốt hơn và trích dẫn chuẩn xác hơn. |
| Vectorless Fallback via Keyword Matching | Trả về rỗng khi dense score < threshold | Answer relevance: +0.062 | Latency: +5ms | Giúp cứu vãn các query gõ sai ngữ pháp hoặc chứa từ khóa hiếm. |
