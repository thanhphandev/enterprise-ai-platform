import pandas as pd
import os

def create_dummy_test_cases():
    """Generate a dummy excel file for automation testing."""
    os.makedirs('automation_test', exist_ok=True)
    
    data = [
        {
            "id": 1, 
            "question": "Value Type và Reference Type trong C# khác nhau như thế nào?", 
            "expected_context": "Value Type: Lưu trữ trực tiếp giá trị (VD: int, float, bool, struct, enum)... Reference Type: Lưu trữ tham chiếu... trỏ tới giá trị thực tế"
        },
        {
            "id": 2, 
            "question": "Boxing và Unboxing ảnh hưởng thế nào đến hiệu năng và làm sao để hạn chế?", 
            "expected_context": "Boxing: Ép kiểu Value Type sang Reference Type... Rất tốn hiệu năng... Hạn chế bằng Generics (ví dụ List<T>)"
        },
        {
            "id": 3, 
            "question": "Phân biệt IEnumerable và IQueryable trong LINQ?", 
            "expected_context": "IEnumerable<T>: Truy vấn bộ nhớ (in-memory), Client-side evaluation... IQueryable<T>: Truy vấn cơ sở dữ liệu (out-memory), Server-side evaluation"
        },
        {
            "id": 4, 
            "question": "Lỗi N+1 Query trong EF Core là gì và cách khắc phục?", 
            "expected_context": "Chạy 1 query kéo về N phần tử cha + sau đó chạy N query nhỏ trong vòng lặp... Khắc phục: Dùng Eager Loading (Include())"
        },
        {
            "id": 5, 
            "question": "Khi nào nên chọn cơ sở dữ liệu NoSQL (MongoDB) thay vì SQL?", 
            "expected_context": "Chọn NoSQL (MongoDB): Khi dữ liệu thay đổi cấu trúc liên tục (Schema-less), cần tốc độ Write/Insert cực nhanh, dễ dàng mở rộng theo chiều ngang"
        },
        {
            "id": 6, 
            "question": "Tại sao không nên dùng GUID ngẫu nhiên làm Khóa chính (Clustered Index) trong SQL Server?", 
            "expected_context": "GUID sinh ra lộn xộn, gây ra hiện tượng Page Split (xé trang ổ cứng), làm tụt giảm hiệu năng ghi thảm hại và gây phân mảnh DB (Fragmentation)"
        }
    ]
    
    df = pd.DataFrame(data)
    df.to_excel('automation_test/test_cases.xlsx', index=False)
    print("Created test_cases.xlsx successfully.")

if __name__ == "__main__":
    create_dummy_test_cases()
