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
    ], string="Trạng thái", required=True, default='di_lam')
    so_gio_ot = fields.Float(string="Giờ làm thêm (OT)", default=0.0)
    ghi_chu = fields.Text(string="Ghi chú")
