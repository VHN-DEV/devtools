# Location Data Seeder

Tool chuyên dụng để lấy và xuất dữ liệu địa lý (quốc gia, tỉnh thành, quận huyện) phục vụ việc nhập liệu database cho Botble CMS và các hệ thống khác.

## ✨ Tính năng chính

- 🌍 **Lấy dữ liệu quốc gia** từ API restcountries.com (250+ countries)
- 🇻🇳 **Lấy dữ liệu tỉnh thành Việt Nam** (63 provinces/cities)
- 🇻🇳 **Lấy dữ liệu tỉnh thành mới Việt Nam** (34 provinces theo hệ thống hành chính mới)
- 🏛️ **Lấy dữ liệu quận huyện Việt Nam** (700+ districts)
- 🏘️ **Lấy dữ liệu xã phường Việt Nam** (theo hệ thống 2 cấp: Tỉnh → Phường/Xã)
- 📊 **Xuất JSON** với cấu trúc nested relationships
- 📈 **Xuất Excel** với multiple worksheets
- 🗃️ **Xuất SQL seed files** cho Botble CMS/Laravel
- ⚙️ **Tùy chỉnh fields xuất** cho từng loại dữ liệu
- 🔄 **Batch processing** và error handling
- 📋 **Interactive menu** dễ sử dụng

## 🚀 Cài đặt và chạy

### 1. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 2. Chạy tool
```bash
# Chạy menu chính
python location-data-seeder.py

# Chạy demo nhanh
python demo.py
```

## 📖 Hướng dẫn sử dụng

### Menu chính
1. **📥 Tải dữ liệu quốc gia** - Lấy data từ restcountries API
2. **📥 Tải dữ liệu tỉnh thành VN (63)** - Data provinces Việt Nam cũ
3. **📥 Tải dữ liệu tỉnh thành VN mới (34)** - Data provinces Việt Nam mới
4. **📥 Tải dữ liệu quận huyện VN** - Data districts Việt Nam
5. **📥 Tải dữ liệu xã phường VN** - Data wards Việt Nam
6. **⚙️ Tùy chỉnh fields xuất** - Chọn fields muốn xuất
7. **📊 Xem tổng quan dữ liệu** - Thống kê data đã tải
8. **📤 Xuất dữ liệu JSON** - Xuất file JSON
9. **📤 Xuất dữ liệu Excel** - Xuất file Excel (.xlsx)
10. **📤 Xuất dữ liệu SQL** - Xuất SQL seed files
11. **❓ Hướng dẫn sử dụng** - Xem documentation
0. **🚪 Thoát** - Thoát chương trình

### Ví dụ workflow
```
1. Chạy tool
2. Chọn 1 → Tải dữ liệu quốc gia
3. Chọn 3 → Tải dữ liệu tỉnh thành VN mới (34)
4. Chọn 5 → Tải dữ liệu xã phường VN
5. Chọn 6 → Tùy chỉnh fields (optional)
6. Chọn 8 → Xuất JSON
   📁 Đường dẫn mặc định: C:\Users\[User]\Downloads\location_data_YYYYMMDD_HHMMSS.json
   Nhập tên file xuất (Enter để dùng mặc định):
   ✅ Xuất JSON thành công!
      📁 Đường dẫn: C:\Users\[User]\Downloads\location_data_YYYYMMDD_HHMMSS.json
      📊 Kích thước: 13.13 KB
7. Chọn 10 → Xuất SQL cho Botble
   📁 Đường dẫn mặc định: C:\Users\[User]\Downloads\location_seed_YYYYMMDD_HHMMSS.sql
   Nhập tên file xuất (Enter để dùng mặc định):
   ✅ Xuất SQL thành công!
      📁 Đường dẫn: C:\Users\[User]\Downloads\location_seed_YYYYMMDD_HHMMSS.sql
      📊 Kích thước: 9.73 KB
```

## 📤 Định dạng xuất

### JSON Structure
```json
{
  "metadata": {
    "exported_at": "2024-01-01 12:00:00",
    "countries_count": 250,
    "provinces_count": 63,
    "districts_count": 33,
    "fields": {
      "countries": ["id", "name", "code", "flag"],
      "provinces": ["id", "name", "code", "region"],
      "districts": ["id", "name", "code", "province_id"]
    }
  },
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
```

### SQL Seed Files (Botble CMS)
```sql
-- Countries table
INSERT INTO bc_countries (id, name, code, flag, capital, region, created_at, updated_at)
VALUES (1, 'Việt Nam', 'VN', '🇻🇳', 'Hà Nội', 'Asia', NOW(), NOW());

-- Provinces table
INSERT INTO bc_provinces (id, name, code, region, area, population, country_id, created_at, updated_at)
VALUES (1, 'Hà Nội', 'HN', 'Đồng bằng sông Hồng', 3358.6, 8246540, 1, NOW(), NOW());

-- Districts table
INSERT INTO bc_districts (id, name, code, province_id, area, population, type, created_at, updated_at)
VALUES (1, 'Ba Đình', 'BAD', 1, 9.2, 248000, 'Quận', NOW(), NOW());
```

### Excel Format
- **Sheet "Countries"**: Dữ liệu quốc gia (màu đỏ)
- **Sheet "Provinces"**: Dữ liệu tỉnh thành (màu xanh lá)
- **Sheet "Districts"**: Dữ liệu quận huyện (màu xanh dương)
- Header được format bold với background color

## ⚙️ Tùy chỉnh Fields

Tool cho phép tùy chỉnh fields xuất cho từng loại dữ liệu:

### Countries Fields
- `id`, `name`, `code`, `flag`, `capital`, `region`, `subregion`
- `population`, `area`, `languages`, `currencies`, `timezones`
- `latlng`, `borders`

### Provinces Fields
- `id`, `name`, `code`, `region`, `area`, `population`, `country_id`

### Districts Fields
- `id`, `name`, `code`, `province_id`, `area`, `population`, `type`

## 📊 Data Sources

- **Countries**: https://restcountries.com/v3.1/all
- **Vietnam Provinces**: Internal dataset (63 provinces)
- **Vietnam Provinces New**: Internal dataset (34 provinces theo hệ thống hành chính mới)
- **Vietnam Districts**: Internal dataset (sample data)
- **Vietnam Wards**: Internal dataset (wards theo hệ thống 2 cấp)

## 🏛️ Hệ thống hành chính Việt Nam

### Hệ thống cũ (3 cấp):
1. **Tỉnh/Thành phố** (63 đơn vị)
2. **Quận/Huyện** (700+ đơn vị)
3. **Phường/Xã** (10,000+ đơn vị)

### Hệ thống mới (2 cấp):
1. **Tỉnh/Thành phố** (34 đơn vị cấp tỉnh)
2. **Phường/Xã** (trực thuộc tỉnh/thành phố)

**Lưu ý**: Hệ thống 2 cấp là xu hướng cải cách hành chính của Việt Nam, loại bỏ cấp quận/huyện trung gian.

## 📋 Requirements

- **Python**: 3.6+
- **Dependencies**:
  - `requests>=2.25.0` (cho API calls)
  - `openpyxl>=3.0.0` (cho Excel export)
- **Optional**:
  - `pandas` (cho data processing nâng cao)

## 🛠️ Development

### Cấu trúc file
```
location-data-seeder/
├── __init__.py
├── location-data-seeder.py    # 🏆 Main tool
├── doc.py                     # 📖 Documentation
├── README.md                  # 📋 This file
├── tool_info.json            # 🏷️ Tool metadata
├── config/                    # ⚙️ Data configuration
│   ├── README.md             # 📖 Data guide
│   ├── vietnam_provinces.json      # 🇻🇳 63 provinces
│   ├── vietnam_provinces_new.json  # 🇻🇳 34 provinces (new)
│   ├── vietnam_districts.json      # 🏛️ Districts data
│   ├── vietnam_wards.json          # 🏘️ Wards data (63 provinces)
│   └── vietnam_wards_new.json      # 🏘️ Wards data (34 provinces new)
└── backup/                    # 📁 Development files
    ├── demo.py               # 🚀 Demo script
    ├── test_quick.py         # 🧪 Test script
    ├── __main__.py          # 📦 Module entry point
    └── requirements.txt     # 📦 Dependencies
```

### Chạy tests
```bash
# Chạy demo
python demo.py

# Test từng chức năng
python -c "from location_data_seeder import LocationDataSeeder; s = LocationDataSeeder(); s.fetch_countries_from_api()"
```

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push và tạo Pull Request

## 📄 License

MIT License - sử dụng tự do cho mục đích phi thương mại.

## 📞 Support

Nếu gặp vấn đề hoặc cần hỗ trợ:
1. Kiểm tra documentation trong tool (chọn 9)
2. Chạy demo để test: `python demo.py`
3. Kiểm tra logs và error messages
