# Data Configuration Files

Thư mục này chứa các file JSON cấu hình dữ liệu địa lý Việt Nam.

## Files

### vietnam_provinces.json
- **Mô tả**: Dữ liệu 63 tỉnh thành Việt Nam (bao gồm tất cả)
- **Cấu trúc**:
```json
[
  {
    "id": 1,
    "name": "Hà Nội",
    "code": "HN",
    "region": "Đồng bằng sông Hồng",
    "area": 3358.6,
    "population": 8246540
  }
]
```

### vietnam_provinces_new.json
- **Mô tả**: Dữ liệu 34 tỉnh thành Việt Nam mới (theo phân cấp hành chính 2023)
- **Cấu trúc**: Giống `vietnam_provinces.json` nhưng có thêm trường `type`
```json
[
  {
    "id": 1,
    "name": "Hà Nội",
    "code": "HN",
    "region": "Đồng bằng sông Hồng",
    "area": 3358.6,
    "population": 8246540,
    "type": "Thành phố"
  }
]
```

### vietnam_districts.json
- **Mô tả**: Dữ liệu quận huyện Việt Nam (mẫu)
- **Cấu trúc**:
```json
[
  {
    "id": 1,
    "name": "Ba Đình",
    "code": "BAD",
    "province_id": 1,
    "area": 9.2,
    "population": 248000,
    "type": "Quận"
  }
]
```

### vietnam_wards.json
- **Mô tả**: Dữ liệu xã phường Việt Nam (mẫu cho 63 tỉnh)
- **Cấu trúc**:
```json
[
  {
    "id": 1,
    "name": "Chương Dương",
    "code": "CD",
    "district_id": 2,
    "type": "Phường"
  }
]
```

### vietnam_wards_new.json
- **Mô tả**: Dữ liệu xã phường Việt Nam (theo hệ thống hành chính 2 cấp)
- **Cấu trúc**: Tham chiếu trực tiếp tới provinces (không qua districts)
```json
[
  {
    "id": 1,
    "name": "Phúc Xá",
    "code": "PX",
    "province_id": 1,
    "type": "Phường"
  }
]
```

## Cập nhật dữ liệu

### Cách cập nhật:
1. Mở file JSON tương ứng
2. Chỉnh sửa dữ liệu theo cấu trúc có sẵn
3. Lưu file
4. Tool sẽ tự động load dữ liệu mới khi chạy

### Lưu ý:
- Giữ nguyên cấu trúc JSON và tên trường
- ID phải là duy nhất trong mỗi file
- province_id và district_id phải tham chiếu đúng
- Đảm bảo encoding UTF-8 khi lưu file

## Mở rộng dữ liệu

Để thêm dữ liệu cho tỉnh/thành phố khác:
1. Thêm record vào `vietnam_provinces.json`
2. Thêm districts cho tỉnh đó vào `vietnam_districts.json`
3. Thêm wards cho các districts đó vào `vietnam_wards.json`

## Validation

Tool sẽ tự động validate:
- File JSON hợp lệ
- Cấu trúc dữ liệu đúng
- Tham chiếu ID hợp lệ
- Dữ liệu không bị trùng lặp
