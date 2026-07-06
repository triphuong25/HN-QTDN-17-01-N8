# -*- coding: utf-8 -*-
from odoo import models, fields, api

class HopDongLaoDong(models.Model):
    _name = 'hop_dong_lao_dong'
    _description = 'Hợp đồng Lao động'

    name = fields.Char(string="Số hợp đồng", required=True)
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True, ondelete='cascade')
    loai_hop_dong = fields.Selection([
        ('thu_viec', 'Thử việc'),
        ('chinh_thuc', 'Chính thức')
    ], string="Loại hợp đồng", default='chinh_thuc', required=True)
    ngay_bat_dau = fields.Date(string="Ngày bắt đầu", required=True)
    ngay_ket_thuc = fields.Date(string="Ngày kết thúc")
    luong_co_ban = fields.Float(string="Lương cơ bản (VND)", required=True)
    phu_cap = fields.Float(string="Phụ cấp cố định (VND)", default=0.0)
    he_so_bao_hiem = fields.Float(string="Mức đóng bảo hiểm (VND)", default=0.0)
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('hieu_luc', 'Đang hiệu lực'),
        ('het_han', 'Hết hạn')
    ], string="Trạng thái", default='nhap', required=True)

    def action_confirm(self):
        for record in self:
            # Set other active contracts of this employee to 'het_han'
            other_contracts = self.search([
                ('nhan_vien_id', '=', record.nhan_vien_id.id),
                ('id', '!=', record.id),
                ('trang_thai', '=', 'hieu_luc')
            ])
            other_contracts.write({'trang_thai': 'het_han'})
            record.write({'trang_thai': 'hieu_luc'})

    def action_draft(self):
        self.write({'trang_thai': 'nhap'})

    def action_expire(self):
        self.write({'trang_thai': 'het_han'})
