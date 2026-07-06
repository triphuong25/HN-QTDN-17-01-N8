# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import datetime

class ChotCongThang(models.Model):
    _name = 'chot_cong_thang'
    _description = 'Chốt công tháng'
    _rec_name = 'display_name'

    thang = fields.Selection([
        ('1', 'Tháng 1'), ('2', 'Tháng 2'), ('3', 'Tháng 3'),
        ('4', 'Tháng 4'), ('5', 'Tháng 5'), ('6', 'Tháng 6'),
        ('7', 'Tháng 7'), ('8', 'Tháng 8'), ('9', 'Tháng 9'),
        ('10', 'Tháng 10'), ('11', 'Tháng 11'), ('12', 'Tháng 12')
    ], string="Tháng", required=True, default=lambda self: str(fields.Date.today().month))
    nam = fields.Integer(string="Năm", required=True, default=lambda self: fields.Date.today().year)
    ngay_cong_chuan = fields.Integer(string="Số ngày công chuẩn", default=24, required=True)
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('done', 'Đã chốt')
    ], string="Trạng thái", default='draft', readonly=True)
    display_name = fields.Char(string="Tên bảng công", compute="_compute_display_name", store=True)

    @api.depends('thang', 'nam')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"Bảng chốt công tháng {record.thang}/{record.nam}"

    def action_confirm_chot_cong(self):
        for record in self:
            # 1. Find all daily attendance records for this month and year
            start_date = f"{record.nam}-{record.thang.zfill(2)}-01"
            # Calculate last day of month
            thang_int = int(record.thang)
            if thang_int == 12:
                end_date = f"{record.nam}-12-31"
            else:
                next_month = datetime.date(record.nam, thang_int + 1, 1)
                last_day = next_month - datetime.timedelta(days=1)
                end_date = last_day.strftime('%Y-%m-%d')
                
            attendance_records = self.env['cham_cong_hang_ngay'].search([
                ('ngay', '>=', start_date),
                ('ngay', '<=', end_date)
            ])
            
            if not attendance_records:
                raise UserError(f"Không tìm thấy dữ liệu chấm công nào trong tháng {record.thang}/{record.nam} để chốt!")

            # 2. Group by employee and aggregate workdays and OT hours
            emp_attendance = {}
            for att in attendance_records:
                emp_id = att.nhan_vien_id.id
                if emp_id not in emp_attendance:
                    emp_attendance[emp_id] = {
                        'days': 0.0,
                        'ot': 0.0,
                        'employee': att.nhan_vien_id
                    }
                
                # Compute workday multiplier
                multiplier = 0.0
                if att.trang_thai == 'di_lam':
                    multiplier = 1.0
                elif att.trang_thai == 'nua_ngay':
                    multiplier = 0.5
                elif att.trang_thai == 'nghi_co_luong':
                    multiplier = 1.0
                elif att.trang_thai == 'nghi_khong_luong':
                    multiplier = 0.0
                elif att.trang_thai == 'vang_mat':
                    multiplier = 0.0
                
                emp_attendance[emp_id]['days'] += multiplier
                emp_attendance[emp_id]['ot'] += att.so_gio_ot

            # 3. Create a payslip for each employee
            PhieuLuongObj = self.env['phieu_luong']
            for emp_id, data in emp_attendance.items():
                emp = data['employee']
                # Check if payslip already exists for this employee, month, and year
                existing = PhieuLuongObj.search([
                    ('nhan_vien_id', '=', emp_id),
                    ('thang', '=', record.thang),
                    ('nam', '=', record.nam)
                ])
                if existing:
                    existing.write({
                        'ngay_cong_chuan': record.ngay_cong_chuan,
                        'ngay_cong_thuc_te': data['days'],
                        'so_gio_ot': data['ot'],
                        'luong_co_ban': emp.luong_co_ban or 0.0,
                        'phu_cap': emp.phu_cap or 0.0,
                        'muc_dong_bao_hiem': emp.he_so_bao_hiem or 0.0
                    })
                else:
                    PhieuLuongObj.create({
                        'nhan_vien_id': emp_id,
                        'thang': record.thang,
                        'nam': record.nam,
                        'ngay_cong_chuan': record.ngay_cong_chuan,
                        'ngay_cong_thuc_te': data['days'],
                        'so_gio_ot': data['ot'],
                        'luong_co_ban': emp.luong_co_ban or 0.0,
                        'phu_cap': emp.phu_cap or 0.0,
                        'muc_dong_bao_hiem': emp.he_so_bao_hiem or 0.0,
                        'state': 'draft'
                    })
            
            record.state = 'done'
