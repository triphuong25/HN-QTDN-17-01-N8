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
            # We will implement the trigger logic here in Task 4
            record.state = 'done'
