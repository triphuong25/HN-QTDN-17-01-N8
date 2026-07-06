# Thiết kế hệ thống Chấm công + Tính lương tích hợp HRM (Odoo 15)

Tài liệu thiết kế chi tiết (Spec) cho hệ thống Chấm công và Tính lương tích hợp tự động với quản lý nhân sự (HRM) dành cho học phần Thực tập Doanh nghiệp (K17) trên nền tảng Odoo 15.

---

## 1. Phân tích nghiệp vụ & Luồng xử lý (Business Flow)

### Tác nhân (Actors)
* **Nhân viên (Employee):** Đối tượng được quản lý thông tin hồ sơ gốc trong HRM, được chấm công hàng ngày và nhận phiếu lương hàng tháng.
* **Quản lý/HR (Manager/HR):** Quản lý hồ sơ nhân sự, thực hiện chấm công hàng ngày và bấm nút chốt công tháng.
* **Kế toán (Accountant):** Xem phiếu lương được sinh tự động, kiểm tra dữ liệu tính toán, duyệt và xác nhận thanh toán lương.
* **Hệ thống (System):** Thực thi các trigger tự động hóa quy trình (khi chốt công tháng thì tự động tạo phiếu lương).

### Quy trình nghiệp vụ End-to-End (Happy Path)
1. **[HRM]** HR tạo hồ sơ nhân viên mới trong module `nhan_su`, khai báo mức Lương cơ bản, Phụ cấp, Mức đóng bảo hiểm và Tỷ lệ đóng bảo hiểm.
2. **[Chấm công]** Hàng ngày trong tháng, quản lý chấm công cho nhân viên thông qua bản ghi `cham_cong_hang_ngay` (xác định đi làm, nghỉ phép, làm thêm giờ OT).
3. **[Tự động hóa - Trigger]** Cuối tháng, Quản lý/HR tạo bản ghi chốt công tháng `chot_cong_thang` cho tháng/năm hiện tại, điền số Ngày công chuẩn (ví dụ: 24 ngày) và bấm nút **"Chốt công tháng"** (`action_done`).
4. **[Tự động hóa - Hệ thống]** Khi bảng chốt công chuyển trạng thái sang **Đã chốt (Done)**:
   * Hệ thống tự động quét toàn bộ bản ghi `cham_cong_hang_ngay` của tháng đó để tổng hợp:
     * Tổng số ngày công đi làm thực tế (`ngay_cong_thuc_te`).
     * Tổng số giờ làm thêm (`so_gio_ot`).
   * Hệ thống tự động tạo ra một bản ghi Phiếu lương (`phieu_luong`) bên module `tinh_luong` cho từng nhân viên tương ứng với trạng thái Nháp (Draft).
   * Phiếu lương tự động liên kết dữ liệu gốc từ HRM (`luong_co_ban`, `phu_cap`, bảo hiểm) và kết quả chấm công (`ngay_cong_thuc_te`, `so_gio_ot`).
5. **[Tính lương]** Kế toán vào kiểm tra phiếu lương tự động tính toán chính xác theo công thức quy định.
6. **[Tính lương]** Kế toán phê duyệt phiếu lương (`approved`) và đánh dấu đã thanh toán (`paid`) sau khi chuyển khoản lương cho nhân viên.

---

## 2. Mô hình cơ sở dữ liệu (Database Schema)

### 2.1. Module HRM (`nhan_su` - Cải tiến)
Sửa đổi model `nhan_vien` (trong [nhan_vien.py](file:///d:/TP/HN-QTDN-17-01-N8/addons/nhan_su/models/nhan_vien.py)):
* `luong_co_ban`: `fields.Float(string="Lương cơ bản (VND)")`
* `phu_cap`: `fields.Float(string="Phụ cấp cố định (VND)")`
* `he_so_bao_hiem`: `fields.Float(string="Mức đóng bảo hiểm (VND)")`
* `ty_le_bhxh`: `fields.Float(string="Tỷ lệ đóng BHXH (%)", default=8.0)`
* `ty_le_bhyt`: `fields.Float(string="Tỷ lệ đóng BHYT (%)", default=1.5)`
* `ty_le_bhtn`: `fields.Float(string="Tỷ lệ đóng BHTN (%)", default=1.0)`

### 2.2. Module Chấm công (`cham_cong` - Mới)
* **Model 1: `cham_cong_hang_ngay`**
  * `nhan_vien_id`: `fields.Many2one('nhan_vien', string="Nhân viên", required=True)`
  * `ngay`: `fields.Date(string="Ngày", required=True, default=fields.Date.context_today)`
  * `trang_thai`: `fields.Selection([('di_lam', 'Đi làm đầy đủ (1.0)'), ('nua_ngay', 'Nghỉ nửa ngày (0.5)'), ('nghi_co_luong', 'Nghỉ phép có lương (1.0)'), ('nghi_khong_luong', 'Nghỉ phép không lương (0.0)'), ('vang_mat', 'Vắng mặt không phép (0.0)')], string="Trạng thái", required=True, default='di_lam')`
  * `so_gio_ot`: `fields.Float(string="Giờ làm thêm (OT)")`
  * `ghi_chu`: `fields.Text(string="Ghi chú")`
* **Model 2: `chot_cong_thang`**
  * `thang`: `fields.Selection([(str(i), f"Tháng {i}") for i in range(1, 13)], string="Tháng", required=True)`
  * `nam`: `fields.Integer(string="Năm", required=True, default=lambda self: fields.Date.today().year)`
  * `ngay_cong_chuan`: `fields.Integer(string="Số ngày công chuẩn", default=24, required=True)`
  * `state`: `fields.Selection([('draft', 'Nháp'), ('done', 'Đã chốt')], string="Trạng thái", default='draft')`

### 2.3. Module Tính lương (`tinh_luong` - Mới)
* **Model: `phieu_luong`**
  * `nhan_vien_id`: `fields.Many2one('nhan_vien', string="Nhân viên", required=True, readonly=True)`
  * `thang`: `fields.Selection([(str(i), f"Tháng {i}") for i in range(1, 13)], string="Tháng", required=True, readonly=True)`
  * `nam`: `fields.Integer(string="Năm", required=True, readonly=True)`
  * `ngay_cong_chuan`: `fields.Integer(string="Số ngày công chuẩn", readonly=True)`
  * `ngay_cong_thuc_te`: `fields.Float(string="Số ngày công thực tế", readonly=True)`
  * `so_gio_ot`: `fields.Float(string="Số giờ OT thực tế", readonly=True)`
  * `luong_co_ban`: `fields.Float(string="Lương cơ bản gốc", readonly=True)`
  * `phu_cap`: `fields.Float(string="Phụ cấp cố định", readonly=True)`
  * `muc_dong_bao_hiem`: `fields.Float(string="Mức đóng bảo hiểm", readonly=True)`
  * `luong_thuc_te`: `fields.Float(string="Lương thực tế", compute="_compute_luong_chi_tiet", store=True)`
  * `luong_ot`: `fields.Float(string="Lương làm thêm", compute="_compute_luong_chi_tiet", store=True)`
  * `tien_bhxh`: `fields.Float(string="Khấu trừ BHXH", compute="_compute_luong_chi_tiet", store=True)`
  * `tien_bhyt`: `fields.Float(string="Khấu trừ BHYT", compute="_compute_luong_chi_tiet", store=True)`
  * `tien_bhtn`: `fields.Float(string="Khấu trừ BHTN", compute="_compute_luong_chi_tiet", store=True)`
  * `tong_khau_tru`: `fields.Float(string="Tổng khấu trừ BH", compute="_compute_luong_chi_tiet", store=True)`
  * `thuc_linh`: `fields.Float(string="Thực lĩnh", compute="_compute_luong_chi_tiet", store=True)`
  * `state`: `fields.Selection([('draft', 'Nháp'), ('approved', 'Đã duyệt'), ('paid', 'Đã thanh toán')], string="Trạng thái", default='draft')`

---

## 3. Công thức tính lương chi tiết
* **Lương thực tế:**
  $$LuongThucTe = \frac{LuongCoBan}{NgayCongChuan} \times NgayCongThucTe$$
* **Lương làm thêm giờ (OT) với hệ số 1.5:**
  $$LuongOT = \frac{LuongCoBan}{NgayCongChuan \times 8} \times SoGioOT \times 1.5$$
* **Các khoản bảo hiểm khấu trừ:**
  * $$TienBHXH = MucDongBaoHiem \times \frac{TyLeBHXH}{100}$$
  * $$TienBHYT = MucDongBaoHiem \times \frac{TyLeBHYT}{100}$$
  * $$TienBHTN = MucDongBaoHiem \times \frac{TyLeBHTN}{100}$$
  * $$TongKhauTru = TienBHXH + TienBHYT + TienBHTN$$
* **Thực lĩnh:**
  $$ThucLinh = LuongThucTe + LuongOT + PhuCap - TongKhauTru$$

---

## 4. Minh chứng sản phẩm & Dữ liệu mẫu (Demo Data)

### 4.1. Sơ đồ luồng nghiệp vụ (Business Flow)
* **Tên file:** `docs/business-flow/Nhom08_BusinessFlow_ChamCongTinhLuong.png` (hoặc `.pdf` / `.svg`)
* **Kiểu sơ đồ:** Swimlane / BPMN mô tả các làn của các Actor (Nhân viên, Quản lý/HR, Hệ thống Odoo, Kế toán) với trigger "Chốt công tháng" tự động sinh phiếu lương bên module `tinh_luong`.
* **Cập nhật README:** Thêm 1-2 dòng mô tả về sơ đồ luồng nghiệp vụ này tại `README.md` của repository.

### 4.2. Dữ liệu mẫu (Demo Data trong Odoo)
Chúng ta sẽ định nghĩa file dữ liệu mẫu (XML/CSV) trong thư mục `demo/` của từng module để khi cài đặt hoặc cập nhật hệ thống, Odoo tự động nạp dữ liệu mẫu:
* **HRM (`nhan_su`):** Nạp sẵn thông tin chi tiết (Lương cơ bản, phụ cấp, bảo hiểm) cho 3 nhân viên mẫu:
  * Nhân viên A: Nguyễn Văn A (Lương: 12M, Phụ cấp: 1.5M, BH: 6M)
  * Nhân viên B: Trần Thị B (Lương: 15M, Phụ cấp: 2M, BH: 8M)
  * Nhân viên C: Lê Văn C (Lương: 9M, Phụ cấp: 1M, BH: 5M)
* **Chấm công (`cham_cong`):** Nạp sẵn các bản ghi chấm công hàng ngày cho cả 3 nhân viên trong tháng hiện tại (đi làm, nghỉ phép, tăng ca OT).

---

## 5. Kế hoạch kiểm thử & Xác minh (Verification Plan)
1. **Tạo dữ liệu mẫu:** Tạo 3 nhân viên với các mức lương, phụ cấp và tỷ lệ đóng bảo hiểm khác nhau.
2. **Chấm công mẫu:** 
   * Nhân viên A: Đi làm đầy đủ các ngày trong tháng, làm thêm 10 giờ OT.
   * Nhân viên B: Nghỉ nửa ngày (0.5 công) và nghỉ không lương 1 ngày.
   * Nhân viên C: Nghỉ phép có lương 2 ngày, làm việc đầy đủ các ngày còn lại.
3. **Thử nghiệm chốt công:** 
   * Tạo bảng chốt công tháng, nhập ngày công chuẩn là 24 ngày.
   * Nhấn nút "Chốt công tháng".
   * Kiểm tra xem các phiếu lương tương ứng có tự động tạo ra bên module `tinh_luong` hay không.
4. **Kiểm tra công thức:** 
   * Tính tay đối chiếu với số liệu tự động tính toán trên phiếu lương của từng nhân viên để kiểm tra tính chính xác của thuật toán.

