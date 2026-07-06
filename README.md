<h2 align="center">
    <a href="https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin">
    🎓 Faculty of Information Technology (DaiNam University)
    </a>
</h2>
<h2 align="center">
    PLATFORM ERP
</h2>
<div align="center">
    <p align="center">
        <img src="docs/logo/aiotlab_logo.png" alt="AIoTLab Logo" width="170"/>
        <img src="docs/logo/fitdnu_logo.png" alt="AIoTLab Logo" width="180"/>
        <img src="docs/logo/dnu_logo.png" alt="DaiNam University Logo" width="200"/>
    </p>

[![AIoTLab](https://img.shields.io/badge/AIoTLab-green?style=for-the-badge)](https://www.facebook.com/DNUAIoTLab)
[![Faculty of Information Technology](https://img.shields.io/badge/Faculty%20of%20Information%20Technology-blue?style=for-the-badge)](https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin)
[![DaiNam University](https://img.shields.io/badge/DaiNam%20University-orange?style=for-the-badge)](https://dainam.edu.vn)

</div>

## 📖 1. Giới thiệu
Platform ERP được áp dụng vào học phần Thực tập doanh nghiệp dựa trên mã nguồn mở Odoo. 

## 🔧 2. Các công nghệ được sử dụng
<div align="center">

### Hệ điều hành
[![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)](https://ubuntu.com/)
### Công nghệ chính
[![Odoo](https://img.shields.io/badge/Odoo-714B67?style=for-the-badge&logo=odoo&logoColor=white)](https://www.odoo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![XML](https://img.shields.io/badge/XML-FF6600?style=for-the-badge&logo=codeforces&logoColor=white)](https://www.w3.org/XML/)
### Cơ sở dữ liệu
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
</div>

## 🚀 3. Các project đã thực hiện dựa trên Platform

Một số project sinh viên đã thực hiện:
- #### [Khoá 15](./docs/projects/K15/README.md)
- #### [Khoá 16](./docs/projects/K16/README.md)
- #### [Khoá 17](./docs/projects/K17/README.md)
## ⚙️ 4. Cài đặt

### 4.1. Cài đặt công cụ, môi trường và các thư viện cần thiết

#### 4.1.1. Tải project.
```
git clone https://github.com/FIT-DNU/Business-Internship.git
```
#### 4.1.2. Cài đặt các thư viện cần thiết
Người sử dụng thực thi các lệnh sau đề cài đặt các thư viện cần thiết

```
sudo apt-get install libxml2-dev libxslt-dev libldap2-dev libsasl2-dev libssl-dev python3.10-distutils python3.10-dev build-essential libssl-dev libffi-dev zlib1g-dev python3.10-venv libpq-dev
```
#### 4.1.3. Khởi tạo môi trường ảo.
- Khởi tạo môi trường ảo
```
python3.10 -m venv ./venv
```
- Thay đổi trình thông dịch sang môi trường ảo
```
source venv/bin/activate
```
- Chạy requirements.txt để cài đặt tiếp các thư viện được yêu cầu
```
pip3 install -r requirements.txt
```
### 4.2. Setup database

Khởi tạo database trên docker bằng việc thực thi file dockercompose.yml.
```
sudo docker-compose up -d
```
### 4.3. Setup tham số chạy cho hệ thống
Tạo tệp **odoo.conf** có nội dung như sau:
```
[options]
addons_path = addons
db_host = localhost
db_password = odoo
db_user = odoo
db_port = 5431
xmlrpc_port = 8069
```
Có thể kế thừa từ file **odoo.conf.template**
### 4.4. Chạy hệ thống và cài đặt các ứng dụng cần thiết
Lệnh chạy
```
python3 odoo-bin.py -c odoo.conf -u all
```
Người sử dụng truy cập theo đường dẫn _http://localhost:8069/_ để đăng nhập vào hệ thống.

## 📝 5. Đề tài: Chấm công & Tính lương tự động - Nhóm 08 (K15)

Hệ thống ERP quản lý HRM - Chấm công - Tính lương tự động hóa cấp doanh nghiệp được xây dựng trên nền tảng Odoo 15.

### 5.1. Mô tả tính năng và nghiệp vụ chuyên sâu đã thực hiện
*   **Quản lý Hợp đồng Lao động (HRM):**
    *   Tích hợp thực thể Hợp đồng lao động để quản lý loại hợp đồng, lương cơ bản, phụ cấp và mức đóng bảo hiểm.
    *   Lương và phụ cấp của nhân viên được tính toán tự động và động từ Hợp đồng đang có hiệu lực, loại bỏ nhập tĩnh.
    *   Quản lý lịch sử hợp đồng trực tiếp tại tab hồ sơ nhân viên.
*   **Chấm công Check-in/Check-out & Giờ làm việc thực tế:**
    *   Quản lý giờ vào (`gio_check_in`), giờ ra (`gio_check_out`) thực tế của nhân viên.
    *   Tự động tính số phút đi muộn (so với mốc 08:00) và về sớm (so với mốc 17:00).
    *   Quy đổi ngày công tự động dựa trên số giờ làm việc thực tế (trừ 1 tiếng nghỉ trưa).
*   **Phân rã OT theo chuẩn Luật Lao động:**
    *   Tự động phân biệt ngày chấm công làm thêm là ngày thường hay cuối tuần (Thứ 7, Chủ Nhật) dựa theo lịch Gregory.
    *   Tách biệt và nhân hệ số tương ứng: **OT ngày thường (150%)** và **OT cuối tuần (200%)**, tự động hiển thị chi tiết trên dòng lương.
*   **Tính lương & Thuế TNCN lũy tiến từng phần:**
    *   Áp dụng biểu thuế TNCN lũy tiến từng phần chuẩn Việt Nam (từ 5% đến 35%).
    *   Tự động giảm trừ gia cảnh bản thân (11 triệu/tháng) và người phụ thuộc (4.4 triệu/người/tháng lấy động từ hồ sơ HRM).
    *   Tạo bảng kê phân rã dòng lương chi tiết (Lương thực tế, OT thường, OT cuối tuần, phụ cấp, các khoản khấu trừ bảo hiểm BHXH/BHYT/BHTN, và Thuế TNCN).

### 5.2. Các chế độ hiển thị và Báo cáo trực quan (UI/UX)
*   **Giao diện dạng thẻ (Kanban View):** Dành cho hồ sơ Nhân viên (có ảnh chân dung), danh sách Hợp đồng và Phiếu lương nhóm theo trạng thái xử lý.
*   **Giao diện dạng Lịch (Calendar View):** Trực quan hóa nhật ký chấm công hàng ngày của nhân viên trên lịch tháng có phân màu trạng thái đi làm, nghỉ phép.
*   **Báo cáo phân tích đa chiều (Pivot & Graph Dashboard):** Cung cấp bảng phân tích động Pivot kéo thả dữ liệu và biểu đồ cột Graph so sánh trực quan cơ cấu lương thực lĩnh, bảo hiểm và thuế TNCN của nhân viên.
*   **Tô màu dòng chi tiết phiếu lương:** Nhận diện màu sắc trực quan (Xanh lá cho các khoản thu nhập cộng thêm và Đỏ/Cam cho các khoản khấu trừ bảo hiểm, thuế).

### 5.3. Tài liệu liên quan
*   Sơ đồ luồng nghiệp vụ chi tiết dạng Swimlane BPMN: [Nhom08_BusinessFlow_ChamCongTinhLuong.svg](./docs/business-flow/Nhom08_BusinessFlow_ChamCongTinhLuong.svg).
*   Báo cáo chi tiết và hướng dẫn sử dụng giao diện: [walkthrough.md](file:///C:/Users/nguye/.gemini/antigravity-ide/brain/8e9e1401-ec84-4b0c-9354-eef08b606ef6/walkthrough.md).

## 📝 6. License

© 2024 AIoTLab, Faculty of Information Technology, DaiNam University. All rights reserved.

---

    
