import pandas as pd
import os

def create_dummy_test_cases():
    """Generate a dummy excel file for automation testing."""
    os.makedirs('automation_test', exist_ok=True)
    
    data = [
        {
            "id": 1,
            "question": "Tài liệu CV gồm những gì?",
            "expected_context": "Trong CV có:\n- Thông tin cá nhân\n- Kinh nghiệm làm việc\n- Học vấn\n- Kỹ năng\n- Chứng chỉ\n- Dự án"
        },
        {
            "id": 2,
            "question": "Bảng điểm trong tài liệu là của môn học nào, mã môn học là gì và có bao nhiêu tín chỉ?",
            "expected_context": "Môn học/ Nhóm: Thực tập cuối khóa - TH\nMã MH: TIE903\nSố tín chỉ: 5"
        },
        {
            "id": 3,
            "question": "Công thức tính điểm học phần (TBC) của môn Thực tập cuối khóa được quy định như thế nào?",
            "expected_context": "Điểm học phần = 30% B1 + 70% B2\nTrong đó:\n- B1: Điểm giảng viên hướng dẫn\n- B2: Điểm báo cáo"
        },
        {
            "id": 4,
            "question": "Điểm giảng viên hướng dẫn (B1), điểm báo cáo (B2) và điểm trung bình chung (TBC) của sinh viên Phan Văn Thành (DH23TH3) là bao nhiêu?",
            "expected_context": "Sinh viên: Phan Văn Thành (DH23TH3)\nMã SV: DTH225766\nĐiểm B1: 9.5\nĐiểm B2: 9.6\nĐiểm TBC: 9.6"
        },
        {
            "id": 5,
            "question": "Hạn cuối cùng để sinh viên nộp thắc mắc khiếu nại về điểm Thực tập cuối khóa là khi nào?",
            "expected_context": "Chậm nhất là 16 giờ chiều thứ tư ngày 20/5/2026"
        },
        {
            "id": 6,
            "question": "Bảng điểm Thực tập cuối khóa là của học kỳ nào, năm học nào và thuộc khoa nào?",
            "expected_context": "Học kỳ 2 - Năm học 2025 - 2026\nKhoa: Công nghệ thông tin\nTrường Đại học An Giang (Phòng Khảo thí và ĐBCL)"
        },
        {
            "id": 7,
            "question": "Sinh viên Nguyễn Thị Quỳnh Như (DTH225717) lớp DH23TH3 có điểm số như thế nào và ghi chú gì?",
            "expected_context": "Mã SV: DTH225717\nSinh viên: Nguyễn Thị Quỳnh Như (DH23TH3)\nĐiểm: B1 = 0.0, B2 = 0.0, TBC = 0.0\nGhi chú: Không TT (Không thực tập)"
        },
        {
            "id": 8,
            "question": "Lưu ý trong tài liệu khuyên sinh viên tránh liên hệ giảng viên hướng dẫn và giảng viên chấm vào những ngày nào?",
            "expected_context": "Tránh liên hệ giảng viên hướng dẫn và giảng viên chấm vào thứ bảy và chủ nhật"
        }
    ]
    
    df = pd.DataFrame(data)
    df.to_excel('automation_test/test_cases.xlsx', index=False)
    print("Created test_cases.xlsx successfully.")

if __name__ == "__main__":
    create_dummy_test_cases()
