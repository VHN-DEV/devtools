# -*- coding: utf-8 -*-
"""
Documentation cho Location Data Seeder Tool
"""

def get_documentation():
    """Trả về documentation của tool"""
    return {
        "name": "Location Data Seeder",
        "description": """
Tool chuyên dụng để lấy và xuất dữ liệu địa lý phục vụ việc nhập liệu database.

Tính năng chính:
• Lấy dữ liệu quốc gia từ API restcountries.com
• Lấy dữ liệu tỉnh thành và quận huyện Việt Nam
• Xuất dữ liệu ra nhiều định dạng: JSON, Excel, SQL seed files
• Tùy chỉnh fields xuất cho từng loại dữ liệu
• Hỗ trợ batch export và import
        """.strip(),
        "features": [
            "🌍 Lấy dữ liệu quốc gia (250+ countries)",
            "🇻🇳 Lấy dữ liệu tỉnh thành Việt Nam (63 provinces)",
            "🏛️ Lấy dữ liệu quận huyện Việt Nam (700+ districts)",
            "📊 Xuất JSON structured data",
            "📈 Xuất Excel với multiple sheets",
            "🗃️ Xuất SQL seed files cho Botble CMS",
            "⚙️ Tùy chỉnh fields xuất theo nhu cầu",
            "🔄 Batch processing cho hiệu suất cao"
        ],
        "usage": """
1. Chạy tool: python location-data-seeder.py
2. Chọn nguồn dữ liệu (Countries/Provinces/Districts)
3. Tùy chỉnh fields xuất (optional)
4. Chọn định dạng xuất (JSON/Excel/SQL/CSV)
5. Nhập đường dẫn lưu file (hiển thị đường dẫn mặc định trong Downloads)
6. Xem kết quả với đường dẫn đầy đủ và kích thước file
7. Import file vào database
        """.strip(),
        "output_formats": {
            "json": {
                "description": "JSON structured với nested relationships",
                "structure": """
{
  "countries": [
    {
      "id": 1,
      "name": "Việt Nam",
      "code": "VN",
      "flag": "🇻🇳",
      "capital": "Hà Nội",
      "region": "Asia"
    }
  ],
  "provinces": [...],
  "districts": [...]
}
                """.strip()
            },
            "excel": {
                "description": "Excel file với multiple worksheets",
                "sheets": ["Countries", "Provinces", "Districts"]
            },
            "sql": {
                "description": "SQL INSERT statements cho Botble CMS",
                "tables": ["countries", "provinces", "districts"],
                "example": """
-- Countries table
INSERT INTO countries (name, code, flag, capital, region, created_at, updated_at)
VALUES ('Việt Nam', 'VN', '🇻🇳', 'Hà Nội', 'Asia', NOW(), NOW());

-- Provinces table
INSERT INTO provinces (name, code, country_id, region, created_at, updated_at)
VALUES ('Hà Nội', 'HN', 1, 'Đông Bắc Bộ', NOW(), NOW());
                """.strip()
            }
        },
        "api_sources": {
            "countries": "https://restcountries.com/v3.1/all",
            "vietnam_provinces": "Internal data hoặc API tỉnh thành VN",
            "vietnam_districts": "Internal data hoặc API quận huyện VN"
        },
        "requirements": [
            "Python 3.6+",
            "requests library",
            "openpyxl (pip install openpyxl)",
            "pandas (optional)"
        ]
    }


def show_help():
    """Hiển thị help information"""
    doc = get_documentation()

    print("=" * 70)
    print(f"📍 {doc['name']}")
    print("=" * 70)
    print(doc['description'])
    print()

    print("✨ TÍNH NĂNG CHÍNH:")
    for feature in doc['features']:
        print(f"   {feature}")
    print()

    print("📋 HƯỚNG DẪN SỬ DỤNG:")
    print(doc['usage'])
    print()

    print("📤 ĐỊNH DẠNG XUẤT:")
    for fmt, info in doc['output_formats'].items():
        print(f"   • {fmt.upper()}: {info['description']}")
    print()

    print("🔗 NGUỒN DỮ LIỆU:")
    for source, url in doc['api_sources'].items():
        print(f"   • {source.title()}: {url}")
    print()

    print("📦 THƯ VIỆN CẦN THIẾT:")
    for req in doc['requirements']:
        print(f"   • {req}")
    print()

    print("=" * 70)
