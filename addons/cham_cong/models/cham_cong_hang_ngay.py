# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ChamCongHangNgay(models.Model):
    _name = 'cham_cong_hang_ngay'
    _description = 'Chấm công hàng ngày'
    _order = 'ngay desc'

    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True)
    ngay = fields.Date(string="Ngày", required=True, default=fields.Date.context_today)
    trang_thai = fields.Selection([
        ('di_lam', 'Đi làm đầy đủ (1.0)'),
        ('nua_ngay', 'Nghỉ nửa ngày (0.5)'),
        ('nghi_co_luong', 'Nghỉ phép có lương (1.0)'),
        ('nghi_khong_luong', 'Nghỉ phép không lương (0.0)'),
        ('vang_mat', 'Vắng mặt không phép (0.0)')
    ], string="Trạng thái", required=True, default='di_lam', compute="_compute_late_early_status", store=True, readonly=False)
    gio_check_in = fields.Float(string="Giờ Check-in", default=8.0)
    gio_check_out = fields.Float(string="Giờ Check-out", default=17.0)
    phut_di_muon = fields.Integer(string="Phút đi muộn", compute="_compute_late_early_status", store=True)
    phut_ve_som = fields.Integer(string="Phút về sớm", compute="_compute_late_early_status", store=True)
    so_gio_ot = fields.Float(string="Giờ làm thêm (OT)", default=0.0)
    ghi_chu = fields.Text(string="Ghi chú")

    @api.depends('gio_check_in', 'gio_check_out')
    def _compute_late_early_status(self):
        for record in self:
            # Phút đi muộn (so với 08:00)
            if record.gio_check_in > 8.0:
                record.phut_di_muon = int(round((record.gio_check_in - 8.0) * 60))
            else:
                record.phut_di_muon = 0

            # Phút về sớm (so với 17:00)
            if record.gio_check_out and record.gio_check_out < 17.0:
                record.phut_ve_som = int(round((17.0 - record.gio_check_out) * 60))
            else:
                record.phut_ve_som = 0

            # Tự động tính trạng thái nếu có check-in / check-out
            if record.gio_check_in and record.gio_check_out:
                work_hours = record.gio_check_out - record.gio_check_in
                if work_hours > 5.0:  # Trừ 1 tiếng nghỉ trưa
                    work_hours -= 1.0
                
                if work_hours >= 7.5:
                    record.trang_thai = 'di_lam'
                elif work_hours >= 4.0:
                    record.trang_thai = 'nua_ngay'
                else:
                    record.trang_thai = 'nghi_khong_luong'
            else:
                record.trang_thai = 'vang_mat'

