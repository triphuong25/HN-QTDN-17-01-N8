from odoo import models, fields, api
from datetime import date

from odoo.exceptions import ValidationError

class NhanVien(models.Model):
    _name = 'nhan_vien'
    _description = 'Bảng chứa thông tin nhân viên'
    _rec_name = 'ho_va_ten'
    _order = 'ten asc, tuoi desc'

    ma_dinh_danh = fields.Char("Mã định danh", required=True)

    ho_ten_dem = fields.Char("Họ tên đệm", required=True)
    ten = fields.Char("Tên", required=True)
    ho_va_ten = fields.Char("Họ và tên", compute="_compute_ho_va_ten", store=True)
    
    ngay_sinh = fields.Date("Ngày sinh")
    que_quan = fields.Char("Quê quán")
    email = fields.Char("Email")
    so_dien_thoai = fields.Char("Số điện thoại")
    lich_su_cong_tac_ids = fields.One2many(
        "lich_su_cong_tac", 
        inverse_name="nhan_vien_id", 
        string = "Danh sách lịch sử công tác")
    tuoi = fields.Integer("Tuổi", compute="_compute_tuoi", store=True)
    anh = fields.Binary("Ảnh")
    danh_sach_chung_chi_bang_cap_ids = fields.One2many(
        "danh_sach_chung_chi_bang_cap", 
        inverse_name="nhan_vien_id", 
        string = "Danh sách chứng chỉ bằng cấp")
    so_nguoi_bang_tuoi = fields.Integer("Số người bằng tuổi", 
                                        compute="so_nguoi_bang_tuoi",
                                        store=True
                                        )
    luong_co_ban = fields.Float(string="Lương cơ bản (VND)", compute="_compute_active_contract_details", store=True)
    phu_cap = fields.Float(string="Phụ cấp cố định (VND)", compute="_compute_active_contract_details", store=True)
    he_so_bao_hiem = fields.Float(string="Mức đóng bảo hiểm (VND)", compute="_compute_active_contract_details", store=True)
    ty_le_bhxh = fields.Float(string="Tỷ lệ đóng BHXH (%)", default=8.0)
    ty_le_bhyt = fields.Float(string="Tỷ lệ đóng BHYT (%)", default=1.5)
    ty_le_bhtn = fields.Float(string="Tỷ lệ đóng BHTN (%)", default=1.0)
    phu_thuoc_ids = fields.One2many("nhan_vien_phu_thuoc", "nhan_vien_id", string="Danh sách người phụ thuộc")
    so_nguoi_phu_thuoc = fields.Integer(string="Số người phụ thuộc", compute="_compute_so_nguoi_phu_thuoc", store=True, default=0)
    hop_dong_ids = fields.One2many("hop_dong_lao_dong", "nhan_vien_id", string="Danh sách hợp đồng")
    contract_count = fields.Integer(string="Số hợp đồng", compute="_compute_contract_count")
    
    @api.depends('hop_dong_ids.trang_thai', 'hop_dong_ids.luong_co_ban', 'hop_dong_ids.phu_cap', 'hop_dong_ids.he_so_bao_hiem')
    def _compute_active_contract_details(self):
        for record in self:
            active_contract = record.hop_dong_ids.filtered(lambda c: c.trang_thai == 'hieu_luc')
            if active_contract:
                c = active_contract[0]
                record.luong_co_ban = c.luong_co_ban
                record.phu_cap = c.phu_cap
                record.he_so_bao_hiem = c.he_so_bao_hiem
            else:
                record.luong_co_ban = 0.0
                record.phu_cap = 0.0
                record.he_so_bao_hiem = 0.0

    @api.depends("tuoi")
    def _compute_so_nguoi_bang_tuoi(self):
        for record in self:
            if record.tuoi:
                records = self.env['nhan_vien'].search(
                    [
                        ('tuoi', '=', record.tuoi),
                        ('ma_dinh_danh', '!=', record.ma_dinh_danh)
                    ]
                )
                record.so_nguoi_bang_tuoi = len(records)
    _sql_constrains = [
        ('ma_dinh_danh_unique', 'unique(ma_dinh_danh)', 'Mã định danh phải là duy nhất')
    ]

    @api.depends("ho_ten_dem", "ten")
    def _compute_ho_va_ten(self):
        for record in self:
            if record.ho_ten_dem and record.ten:
                record.ho_va_ten = record.ho_ten_dem + ' ' + record.ten
    
    
    
                
    @api.onchange("ten", "ho_ten_dem")
    def _default_ma_dinh_danh(self):
        for record in self:
            if record.ho_ten_dem and record.ten:
                chu_cai_dau = ''.join([tu[0][0] for tu in record.ho_ten_dem.lower().split()])
                record.ma_dinh_danh = record.ten.lower() + chu_cai_dau
    
    @api.depends("ngay_sinh")
    def _compute_tuoi(self):
        for record in self:
            if record.ngay_sinh:
                year_now = date.today().year
                record.tuoi = year_now - record.ngay_sinh.year

    @api.constrains('tuoi')
    def _check_tuoi(self):
        for record in self:
            if record.tuoi < 18:
                raise ValidationError("Tuổi không được bé hơn 18")

    @api.depends('phu_thuoc_ids.trang_thai')
    def _compute_so_nguoi_phu_thuoc(self):
        for record in self:
            active_dependents = record.phu_thuoc_ids.filtered(lambda d: d.trang_thai == 'hieu_luc')
            record.so_nguoi_phu_thuoc = len(active_dependents)

    def _compute_contract_count(self):
        for record in self:
            record.contract_count = len(record.hop_dong_ids)

    def action_view_contracts(self):
        self.ensure_one()
        return {
            'name': 'Hợp đồng lao động',
            'type': 'ir.actions.act_window',
            'res_model': 'hop_dong_lao_dong',
            'view_mode': 'kanban,tree,form',
            'domain': [('nhan_vien_id', '=', self.id)],
            'context': {'default_nhan_vien_id': self.id},
        }


class NhanVienPhuThuoc(models.Model):
    _name = 'nhan_vien_phu_thuoc'
    _description = 'Người phụ thuộc của nhân viên'

    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", ondelete='cascade')
    name = fields.Char(string="Họ tên người phụ thuộc", required=True)
    ngay_sinh = fields.Date(string="Ngày sinh")
    moi_quan_he = fields.Selection([
        ('con_ruot', 'Con ruột'),
        ('vo_chong', 'Vợ / Chồng'),
        ('bo_me', 'Bố / Mẹ'),
        ('khac', 'Khác')
    ], string="Mối quan hệ", default='con_ruot', required=True)
    ma_so_thue = fields.Char(string="Mã số thuế")
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('hieu_luc', 'Có hiệu lực'),
        ('het_han', 'Hết hạn')
    ], string="Trạng thái", default='hieu_luc', required=True)
