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
    
    luong_co_ban = fields.Float(string="Lương cơ bản gốc", readonly=True)
    phu_cap = fields.Float(string="Phụ cấp cố định", readonly=True)
    muc_dong_bao_hiem = fields.Float(string="Mức đóng bảo hiểm", readonly=True)
    
    luong_thuc_te = fields.Float(string="Lương thực tế", compute="_compute_luong_chi_tiet", store=True)
    luong_ot = fields.Float(string="Lương làm thêm", compute="_compute_luong_chi_tiet", store=True)
    tien_bhxh = fields.Float(string="Khấu trừ BHXH", compute="_compute_luong_chi_tiet", store=True)
    tien_bhyt = fields.Float(string="Khấu trừ BHYT", compute="_compute_luong_chi_tiet", store=True)
    tien_bhtn = fields.Float(string="Khấu trừ BHTN", compute="_compute_luong_chi_tiet", store=True)
    tong_khau_tru = fields.Float(string="Tổng khấu trừ BH", compute="_compute_luong_chi_tiet", store=True)
    thuc_linh = fields.Float(string="Thực lĩnh", compute="_compute_luong_chi_tiet", store=True)
    
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('approved', 'Đã duyệt'),
        ('paid', 'Đã thanh toán')
    ], string="Trạng thái", default='draft')
    
    display_name = fields.Char(string="Tên phiếu lương", compute="_compute_display_name")

    @api.depends('nhan_vien_id', 'thang', 'nam')
    def _compute_display_name(self):
        for record in self:
            name = record.nhan_vien_id.ho_va_ten or "Nhân viên"
            record.display_name = f"Phiếu lương {name} - {record.thang}/{record.nam}"

    @api.depends('ngay_cong_chuan', 'ngay_cong_thuc_te', 'so_gio_ot', 'luong_co_ban', 'phu_cap', 'muc_dong_bao_hiem')
    def _compute_luong_chi_tiet(self):
        for record in self:
            # 1. Real salary
            if record.ngay_cong_chuan > 0:
                record.luong_thuc_te = (record.luong_co_ban / record.ngay_cong_chuan) * record.ngay_cong_thuc_te
                # Overtime salary (1.5x hourly rate)
                record.luong_ot = (record.luong_co_ban / record.ngay_cong_chuan / 8.0) * record.so_gio_ot * 1.5
            else:
                record.luong_thuc_te = 0.0
                record.luong_ot = 0.0
                
            # 2. Insurance deductions
            emp = record.nhan_vien_id
            pct_bhxh = emp.ty_le_bhxh if emp else 8.0
            pct_bhyt = emp.ty_le_bhyt if emp else 1.5
            pct_bhtn = emp.ty_le_bhtn if emp else 1.0
            
            record.tien_bhxh = record.muc_dong_bao_hiem * (pct_bhxh / 100.0)
            record.tien_bhyt = record.muc_dong_bao_hiem * (pct_bhyt / 100.0)
            record.tien_bhtn = record.muc_dong_bao_hiem * (pct_bhtn / 100.0)
            record.tong_khau_tru = record.tien_bhxh + record.tien_bhyt + record.tien_bhtn
            
            # 3. Take-home pay
            record.thuc_linh = record.luong_thuc_te + record.luong_ot + record.phu_cap - record.tong_khau_tru

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_pay(self):
        self.write({'state': 'paid'})
