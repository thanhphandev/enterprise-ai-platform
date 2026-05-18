import pandas as pd
import os

def create_dummy_test_cases():
    """Generate a dummy excel file for automation testing."""
    os.makedirs('automation_test', exist_ok=True)
    
    data = [
        {"id": 1, "question": "Hệ thống AI Agent này được viết bằng ngôn ngữ gì?", "expected_context": "Python"},
        {"id": 2, "question": "Hệ thống sử dụng Vector Database nào?", "expected_context": "ChromaDB"},
        {"id": 3, "question": "Frontend Admin được làm bằng công nghệ gì?", "expected_context": "Streamlit"},
        {"id": 4, "question": "Bầu trời màu gì?", "expected_context": "Không có trong tài liệu"}, # To test Faithfulness/Hallucination
    ]
    
    df = pd.DataFrame(data)
    df.to_excel('automation_test/test_cases.xlsx', index=False)
    print("Created test_cases.xlsx successfully.")

if __name__ == "__main__":
    create_dummy_test_cases()
