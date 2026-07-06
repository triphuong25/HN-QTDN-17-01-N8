# -*- coding: utf-8 -*-
from odoo import models, fields, api

class PhieuLuong(models.Model):
    _name = 'phieu_luong'
    _description = 'Phiếu lương nhân viên'
    _rec_name = 'display_name'

    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True, readonly=True)
    thang = fields.Selection([
        ('1', 'Tháng 1'), ('2', 'Tháng 2'), ('3', 'Tháng 3'),
        ('4', 'Tháng 4'), ('5', 'Tháng 5'), ('6', 'Tháng 6'),
        ('7', 'Tháng 7'), ('8', 'Tháng 8'), ('9', 'Tháng 9'),
        ('10', 'Tháng 10'), ('11', 'Tháng 11'), ('12', 'Tháng 12')
    ], string="Tháng", required=True, readonly=True)
    nam = fields.Integer(string="Năm", required=True, readonly=True)
    ngay_cong_chuan = fields.Integer(string="Số ngày công chuẩn", readonly=True)
    ngay_cong_thuc_te = fields.Float(string="Số ngày công thực tế", readonly=True)
    so_gio_ot = fields.Float(string="Số giờ OT thực tế", readonly=True)
    so_gio_ot_thuong = fields.Float(string="Giờ OT ngày thường", readonly=True, default=0.0)
    so_gio_ot_cuoi_tuan = fields.Float(string="Giờ OT cuối tuần", readonly=True, default=0.0)
    
    luong_co_ban = fields.Float(string="Lương cơ bản gốc", readonly=True)
    phu_cap = fields.Float(string="Phụ cấp cố định", readonly=True)
    muc_dong_bao_hiem = fields.Float(string="Mức đóng bảo hiểm", readonly=True)
    
    luong_thuc_te = fields.Float(string="Lương thực tế", compute="_compute_luong_chi_tiet", store=True)
    luong_ot = fields.Float(string="Lương làm thêm", compute="_compute_luong_chi_tiet", store=True)
    tien_bhxh = fields.Float(string="Khấu trừ BHXH", compute="_compute_luong_chi_tiet", store=True)
    tien_bhyt = fields.Float(string="Khấu trừ BHYT", compute="_compute_luong_chi_tiet", store=True)
    tien_bhtn = fields.Float(string="Khấu trừ BHTN", compute="_compute_luong_chi_tiet", store=True)
    tong_khau_tru = fields.Float(string="Tổng khấu trừ BH", compute="_compute_luong_chi_tiet", store=True)
    
    # PIT fields
    giam_tru_ban_than = fields.Float(string="Giảm trừ gia cảnh bản thân (VND)", default=11000000.0)
    so_nguoi_phu_thuoc = fields.Integer(string="Số người phụ thuộc", readonly=True)
    giam_tru_phu_thuoc = fields.Float(string="Giảm trừ người phụ thuộc (VND)", compute="_compute_luong_chi_tiet", store=True)
    thu_nhap_chiu_thue = fields.Float(string="Thu nhập tính thuế TNCN (VND)", compute="_compute_luong_chi_tiet", store=True)
    thue_tncn = fields.Float(string="Thuế TNCN phải nộp (VND)", compute="_compute_luong_chi_tiet", store=True)
    
    thuc_linh = fields.Float(string="Thực lĩnh", compute="_compute_luong_chi_tiet", store=True)
    
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('approved', 'Đã duyệt'),
        ('paid', 'Đã thanh toán')
    ], string="Trạng thái", default='draft')
    
    display_name = fields.Char(string="Tên phiếu lương", compute="_compute_display_name")
    line_ids = fields.One2many('phieu_luong_line', 'phieu_luong_id', string="Chi tiết các dòng lương", compute="_compute_luong_chi_tiet", store=True)

    @api.depends('nhan_vien_id', 'thang', 'nam')
    def _compute_display_name(self):
        for record in self:
            name = record.nhan_vien_id.ho_va_ten or "Nhân viên"
            record.display_name = f"Phiếu lương {name} - {record.thang}/{record.nam}"

    @api.depends('ngay_cong_chuan', 'ngay_cong_thuc_te', 'so_gio_ot', 'so_gio_ot_thuong', 'so_gio_ot_cuoi_tuan', 'luong_co_ban', 'phu_cap', 'muc_dong_bao_hiem', 'giam_tru_ban_than', 'so_nguoi_phu_thuoc')
    def _compute_luong_chi_tiet(self):
        for record in self:
            # 1. Lương thực tế & Lương OT
            if record.ngay_cong_chuan > 0:
                record.luong_thuc_te = (record.luong_co_ban / record.ngay_cong_chuan) * record.ngay_cong_thuc_te
                luong_ot_thuong = (record.luong_co_ban / record.ngay_cong_chuan / 8.0) * record.so_gio_ot_thuong * 1.5
                luong_ot_cuoi_tuan = (record.luong_co_ban / record.ngay_cong_chuan / 8.0) * record.so_gio_ot_cuoi_tuan * 2.0
                record.luong_ot = luong_ot_thuong + luong_ot_cuoi_tuan
            else:
                record.luong_thuc_te = 0.0
                record.luong_ot = 0.0
                luong_ot_thuong = 0.0
                luong_ot_cuoi_tuan = 0.0
                
            # 2. Khấu trừ bảo hiểm
            emp = record.nhan_vien_id
            pct_bhxh = emp.ty_le_bhxh if emp else 8.0
            pct_bhyt = emp.ty_le_bhyt if emp else 1.5
            pct_bhtn = emp.ty_le_bhtn if emp else 1.0
            
            # Luật Việt Nam:
            # - Trần đóng BHXH & BHYT = 20 lần lương cơ sở (20 * 2,340,000 = 46,800,000 VND)
            # - Trần đóng BHTN = 20 lần lương tối thiểu vùng I (20 * 4,960,000 = 99,200,000 VND)
            luong_co_so = 2340000.0
            luong_tt_vung = 4960000.0
            
            base_bhxh_bhyt = min(record.muc_dong_bao_hiem, 20.0 * luong_co_so)
            base_bhtn = min(record.muc_dong_bao_hiem, 20.0 * luong_tt_vung)
            
            record.tien_bhxh = base_bhxh_bhyt * (pct_bhxh / 100.0)
            record.tien_bhyt = base_bhxh_bhyt * (pct_bhyt / 100.0)
            record.tien_bhtn = base_bhtn * (pct_bhtn / 100.0)
            record.tong_khau_tru = record.tien_bhxh + record.tien_bhyt + record.tien_bhtn
            
            # 3. Tính thuế TNCN (Lũy tiến Việt Nam)
            # Tổng thu nhập = Lương thực tế + Phụ cấp + Lương OT
            tong_thu_nhap = record.luong_thuc_te + record.phu_cap + record.luong_ot
            
            # Giảm trừ phụ thuộc = Số người phụ thuộc * 4.400.000 VND
            record.giam_tru_phu_thuoc = record.so_nguoi_phu_thuoc * 4400000.0
            
            # Thu nhập tính thuế = Tổng thu nhập - Bảo hiểm - Giảm trừ bản thân - Giảm trừ phụ thuộc
            tntt = tong_thu_nhap - record.tong_khau_tru - record.giam_tru_ban_than - record.giam_tru_phu_thuoc
            record.thu_nhap_chiu_thue = max(0.0, tntt)
            
            # Tính thuế TNCN lũy tiến
            record.thue_tncn = record._calculate_progressive_pit(record.thu_nhap_chiu_thue)
            
            # 4. Thực lĩnh
            record.thuc_linh = tong_thu_nhap - record.tong_khau_tru - record.thue_tncn

            # 5. Sinh dòng chi tiết lương (Payslip Lines)
            lines_vals = [
                (5, 0, 0),  # Xóa toàn bộ dòng cũ
                (0, 0, {'name': 'Lương thực tế', 'code': 'BASIC_REAL', 'amount': record.luong_thuc_te, 'type': 'thu_nhap'}),
            ]
            if luong_ot_thuong > 0:
                lines_vals.append((0, 0, {'name': 'Lương làm thêm ngày thường (150%)', 'code': 'OT_NORMAL', 'amount': luong_ot_thuong, 'type': 'thu_nhap'}))
            if luong_ot_cuoi_tuan > 0:
                lines_vals.append((0, 0, {'name': 'Lương làm thêm cuối tuần (200%)', 'code': 'OT_WEEKEND', 'amount': luong_ot_cuoi_tuan, 'type': 'thu_nhap'}))
            
            lines_vals.extend([
                (0, 0, {'name': 'Phụ cấp cố định', 'code': 'ALW', 'amount': record.phu_cap, 'type': 'thu_nhap'}),
                (0, 0, {'name': 'Bảo hiểm Xã hội (BHXH)', 'code': 'SI', 'amount': record.tien_bhxh, 'type': 'khau_tru'}),
                (0, 0, {'name': 'Bảo hiểm Y tế (BHYT)', 'code': 'HI', 'amount': record.tien_bhyt, 'type': 'khau_tru'}),
                (0, 0, {'name': 'Bảo hiểm Thất nghiệp (BHTN)', 'code': 'UI', 'amount': record.tien_bhtn, 'type': 'khau_tru'}),
                (0, 0, {'name': 'Thuế thu nhập cá nhân (TNCN)', 'code': 'PIT', 'amount': record.thue_tncn, 'type': 'khau_tru'}),
            ])
            record.line_ids = lines_vals

    def _calculate_progressive_pit(self, tntt):
        if tntt <= 0:
            return 0.0
        if tntt <= 5000000:
            return tntt * 0.05
        elif tntt <= 10000000:
            return tntt * 0.10 - 250000
        elif tntt <= 18000000:
            return tntt * 0.15 - 750000
        elif tntt <= 32000000:
            return tntt * 0.20 - 1650000
        elif tntt <= 52000000:
            return tntt * 0.25 - 3250000
        elif tntt <= 80000000:
            return tntt * 0.30 - 5850000
        else:
            return tntt * 0.35 - 9850000

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_pay(self):
        self.write({'state': 'paid'})


class PhieuLuongLine(models.Model):
    _name = 'phieu_luong_line'
    _description = 'Chi tiết Dòng Phiếu lương'

    phieu_luong_id = fields.Many2one('phieu_luong', string="Phiếu lương", ondelete='cascade')
    name = fields.Char(string="Tên khoản mục", required=True)
    code = fields.Char(string="Mã khoản mục", required=True)
    amount = fields.Float(string="Số tiền (VND)", default=0.0)
    type = fields.Selection([
        ('thu_nhap', 'Thu nhập (+)'),
        ('khau_tru', 'Khấu trừ (-)')
    ], string="Loại", required=True)
