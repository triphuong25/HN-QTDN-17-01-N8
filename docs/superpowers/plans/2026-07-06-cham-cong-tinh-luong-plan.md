# Chấm công + Tính lương Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete attendance and automated payroll system integrated with HRM in Odoo 15.

**Architecture:** Extend the existing `nhan_su` module to store salary and insurance settings. Create two new Odoo modules: `cham_cong` for daily logs and monthly closing, and `tinh_luong` for payslip calculation. Implement a trigger in `chot_cong_thang` that automatically aggregates attendance records and generates Draft payslips in `tinh_luong` using the employee's HRM data.

**Tech Stack:** Python, Odoo 15 ORM, XML views.

## Global Constraints
- Target platform: Odoo 15.0
- Base dependencies: `nhan_su`
- All custom models must have security rules in `ir.model.access.csv`
- All field names and labels should be in Vietnamese

---

### Task 1: Extend HRM Module with Salary and Insurance Fields

**Files:**
- Modify: `addons/nhan_su/models/nhan_vien.py`
- Modify: `addons/nhan_su/views/nhan_vien.xml`

**Interfaces:**
- Consumes: Existing `nhan_vien` model.
- Produces: New fields `luong_co_ban`, `phu_cap`, `he_so_bao_hiem`, `ty_le_bhxh`, `ty_le_bhyt`, `ty_le_bhtn` on `nhan_vien` model.

- [ ] **Step 1: Modify nhan_vien.py to add salary and insurance fields**

Modify `addons/nhan_su/models/nhan_vien.py` to add:
```python
    luong_co_ban = fields.Float(string="Lương cơ bản (VND)")
    phu_cap = fields.Float(string="Phụ cấp cố định (VND)")
    he_so_bao_hiem = fields.Float(string="Mức đóng bảo hiểm (VND)")
    ty_le_bhxh = fields.Float(string="Tỷ lệ đóng BHXH (%)", default=8.0)
    ty_le_bhyt = fields.Float(string="Tỷ lệ đóng BHYT (%)", default=1.5)
    ty_le_bhtn = fields.Float(string="Tỷ lệ đóng BHTN (%)", default=1.0)
```

- [ ] **Step 2: Modify nhan_vien.xml to expose new fields in views**

Modify `addons/nhan_su/views/nhan_vien.xml` to include the fields under a new notebook page "Thông tin Lương & Bảo hiểm" in the Form view.
```xml
                <page string="Lương &amp; Bảo hiểm">
                    <group>
                        <group string="Thông tin Lương">
                            <field name="luong_co_ban"/>
                            <field name="phu_cap"/>
                        </group>
                        <group string="Thông tin Bảo hiểm">
                            <field name="he_so_bao_hiem"/>
                            <field name="ty_le_bhxh"/>
                            <field name="ty_le_bhyt"/>
                            <field name="ty_le_bhtn"/>
                        </group>
                    </group>
                </page>
```
Also add `luong_co_ban` to the Tree/List view of `nhan_vien`.

- [ ] **Step 3: Verify Odoo updates successfully**

Run a command to upgrade the `nhan_su` module.
Run: `python odoo-bin.py -c odoo.conf -u nhan_su --stop-after-init`
Expected: Module updates without errors.

- [ ] **Step 4: Commit changes**
```bash
git add addons/nhan_su/models/nhan_vien.py addons/nhan_su/views/nhan_vien.xml
git commit -m "feat(hrm): add salary and insurance configuration fields to nhan_vien"
```

---

### Task 2: Scaffold and Implement the `cham_cong` Module

**Files:**
- Create: `addons/cham_cong/__init__.py`
- Create: `addons/cham_cong/__manifest__.py`
- Create: `addons/cham_cong/models/__init__.py`
- Create: `addons/cham_cong/models/cham_cong_hang_ngay.py`
- Create: `addons/cham_cong/models/chot_cong_thang.py`
- Create: `addons/cham_cong/security/ir.model.access.csv`
- Create: `addons/cham_cong/views/cham_cong_hang_ngay.xml`
- Create: `addons/cham_cong/views/chot_cong_thang.xml`
- Create: `addons/cham_cong/views/menu.xml`

**Interfaces:**
- Consumes: `nhan_vien` model from `nhan_su` module.
- Produces: Daily attendance and monthly closing logic and views.

- [ ] **Step 1: Create module configuration files**

Write `addons/cham_cong/__manifest__.py`:
```python
# -*- coding: utf-8 -*-
{
    'name': 'Quản lý Chấm công',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Chấm công hàng ngày và chốt công tháng',
    'depends': ['nhan_su'],
    'data': [
        'security/ir.model.access.csv',
        'views/cham_cong_hang_ngay.xml',
        'views/chot_cong_thang.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
}
```
Write `addons/cham_cong/__init__.py`:
```python
from . import models
```
Write `addons/cham_cong/models/__init__.py`:
```python
from . import cham_cong_hang_ngay
from . import chot_cong_thang
```

- [ ] **Step 2: Create the `cham_cong_hang_ngay` model**

Write `addons/cham_cong/models/cham_cong_hang_ngay.py`:
```python
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
```

- [ ] **Step 3: Create the `chot_cong_thang` model**

Write `addons/cham_cong/models/chot_cong_thang.py`:
```python
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
```

- [ ] **Step 4: Create security rules**

Write `addons/cham_cong/security/ir.model.access.csv`:
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_cham_cong_hang_ngay,access_cham_cong_hang_ngay,model_cham_cong_hang_ngay,,1,1,1,1
access_chot_cong_thang,access_chot_cong_thang,model_chot_cong_thang,,1,1,1,1
```

- [ ] **Step 5: Create Views and Menus**

Write `addons/cham_cong/views/cham_cong_hang_ngay.xml`:
```xml
<odoo>
    <record id="view_cham_cong_hang_ngay_tree" model="ir.ui.view">
        <field name="name">cham_cong_hang_ngay.tree</field>
        <field name="model">cham_cong_hang_ngay</field>
        <field name="arch" type="xml">
            <tree editable="top">
                <field name="nhan_vien_id"/>
                <field name="ngay"/>
                <field name="trang_thai"/>
                <field name="so_gio_ot"/>
                <field name="ghi_chu"/>
            </tree>
        </field>
    </record>

    <record id="view_cham_cong_hang_ngay_search" model="ir.ui.view">
        <field name="name">cham_cong_hang_ngay.search</field>
        <field name="model">cham_cong_hang_ngay</field>
        <field name="arch" type="xml">
            <search>
                <field name="nhan_vien_id"/>
                <field name="ngay"/>
                <filter string="Tháng Này" name="current_month" 
                        domain="[('ngay', '&gt;=', context_today().strftime('%Y-%m-01')), 
                                 ('ngay', '&lt;', (context_today() + relativedelta(months=1)).strftime('%Y-%m-01'))]"/>
            </search>
        </field>
    </record>

    <record id="action_cham_cong_hang_ngay" model="ir.actions.act_window">
        <field name="name">Chấm công hàng ngày</field>
        <field name="res_model">cham_cong_hang_ngay</field>
        <field name="view_mode">tree</field>
        <field name="search_view_id" ref="view_cham_cong_hang_ngay_search"/>
    </record>
</odoo>
```

Write `addons/cham_cong/views/chot_cong_thang.xml`:
```xml
<odoo>
    <record id="view_chot_cong_thang_tree" model="ir.ui.view">
        <field name="name">chot_cong_thang.tree</field>
        <field name="model">chot_cong_thang</field>
        <field name="arch" type="xml">
            <tree>
                <field name="display_name"/>
                <field name="thang"/>
                <field name="nam"/>
                <field name="ngay_cong_chuan"/>
                <field name="state"/>
            </tree>
        </field>
    </record>

    <record id="view_chot_cong_thang_form" model="ir.ui.view">
        <field name="name">chot_cong_thang.form</field>
        <field name="model">chot_cong_thang</field>
        <field name="arch" type="xml">
            <form>
                <header>
                    <button name="action_confirm_chot_cong" string="Chốt công tháng" 
                            type="object" class="oe_highlight" states="draft"/>
                    <field name="state" widget="statusbar" statusbar_visible="draft,done"/>
                </header>
                <sheet>
                    <group>
                        <group>
                            <field name="thang" attrs="{'readonly': [('state', '=', 'done')]}"/>
                            <field name="nam" attrs="{'readonly': [('state', '=', 'done')]}"/>
                        </group>
                        <group>
                            <field name="ngay_cong_chuan" attrs="{'readonly': [('state', '=', 'done')]}"/>
                        </group>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <record id="action_chot_cong_thang" model="ir.actions.act_window">
        <field name="name">Chốt công tháng</field>
        <field name="res_model">chot_cong_thang</field>
        <field name="view_mode">tree,form</field>
    </record>
</odoo>
```

Write `addons/cham_cong/views/menu.xml`:
```xml
<odoo>
    <menuitem id="menu_cham_cong_root" name="Chấm công" sequence="20" web_icon="cham_cong,static/description/icon.png"/>
    <menuitem id="menu_cham_cong_hang_ngay" name="Chấm công hàng ngày" parent="menu_cham_cong_root" action="action_cham_cong_hang_ngay" sequence="10"/>
    <menuitem id="menu_chot_cong_thang" name="Chốt công tháng" parent="menu_cham_cong_root" action="action_chot_cong_thang" sequence="20"/>
</odoo>
```

- [ ] **Step 6: Install the new module**

Run Odoo command to install the `cham_cong` module.
Run: `python odoo-bin.py -c odoo.conf -i cham_cong --stop-after-init`
Expected: Module installs successfully.

- [ ] **Step 7: Commit changes**
```bash
git add addons/cham_cong/
git commit -m "feat(attendance): scaffold cham_cong module with daily logs and monthly closing models"
```

---

### Task 3: Scaffold and Implement the `tinh_luong` Module

**Files:**
- Create: `addons/tinh_luong/__init__.py`
- Create: `addons/tinh_luong/__manifest__.py`
- Create: `addons/tinh_luong/models/__init__.py`
- Create: `addons/tinh_luong/models/phieu_luong.py`
- Create: `addons/tinh_luong/security/ir.model.access.csv`
- Create: `addons/tinh_luong/views/phieu_luong.xml`
- Create: `addons/tinh_luong/views/menu.xml`

**Interfaces:**
- Consumes: `nhan_vien` from `nhan_su` and calculations from `cham_cong`.
- Produces: Payslip views and automated salary/insurance calculations.

- [ ] **Step 1: Create module configuration files**

Write `addons/tinh_luong/__manifest__.py`:
```python
# -*- coding: utf-8 -*-
{
    'name': 'Quản lý Tính lương',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Tính lương và bảo hiểm tự động cho nhân viên',
    'depends': ['nhan_su', 'cham_cong'],
    'data': [
        'security/ir.model.access.csv',
        'views/phieu_luong.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
}
```
Write `addons/tinh_luong/__init__.py`:
```python
from . import models
```
Write `addons/tinh_luong/models/__init__.py`:
```python
from . import phieu_luong
```

- [ ] **Step 2: Create the `phieu_luong` model and calculations**

Write `addons/tinh_luong/models/phieu_luong.py`:
```python
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
            # Fetch percentages from employee profile, or default to standard rates
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
```

- [ ] **Step 3: Create security rules**

Write `addons/tinh_luong/security/ir.model.access.csv`:
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_phieu_luong,access_phieu_luong,model_phieu_luong,,1,1,1,1
```

- [ ] **Step 4: Create Views and Menus**

Write `addons/tinh_luong/views/phieu_luong.xml`:
```xml
<odoo>
    <record id="view_phieu_luong_tree" model="ir.ui.view">
        <field name="name">phieu_luong.tree</field>
        <field name="model">phieu_luong</field>
        <field name="arch" type="xml">
            <tree decoration-info="state == 'draft'" decoration-success="state == 'paid'">
                <field name="display_name"/>
                <field name="nhan_vien_id"/>
                <field name="thang"/>
                <field name="nam"/>
                <field name="luong_thuc_te"/>
                <field name="luong_ot"/>
                <field name="tong_khau_tru"/>
                <field name="thuc_linh"/>
                <field name="state"/>
            </tree>
        </field>
    </record>

    <record id="view_phieu_luong_form" model="ir.ui.view">
        <field name="name">phieu_luong.form</field>
        <field name="model">phieu_luong</field>
        <field name="arch" type="xml">
            <form>
                <header>
                    <button name="action_approve" string="Phê duyệt" type="object" class="oe_highlight" states="draft"/>
                    <button name="action_pay" string="Thanh toán" type="object" class="oe_highlight" states="approved"/>
                    <field name="state" widget="statusbar" statusbar_visible="draft,approved,paid"/>
                </header>
                <sheet>
                    <div class="oe_title">
                        <h1>
                            <field name="display_name" readonly="1"/>
                        </h1>
                    </div>
                    <group>
                        <group string="Thông tin chung">
                            <field name="nhan_vien_id"/>
                            <field name="thang"/>
                            <field name="nam"/>
                        </group>
                        <group string="Thông tin công">
                            <field name="ngay_cong_chuan"/>
                            <field name="ngay_cong_thuc_te"/>
                            <field name="so_gio_ot"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Chi tiết lương">
                            <group>
                                <group string="Khoản nhận">
                                    <field name="luong_co_ban"/>
                                    <field name="luong_thuc_te"/>
                                    <field name="luong_ot"/>
                                    <field name="phu_cap"/>
                                </group>
                                <group string="Khấu trừ bảo hiểm">
                                    <field name="muc_dong_bao_hiem"/>
                                    <field name="tien_bhxh"/>
                                    <field name="tien_bhyt"/>
                                    <field name="tien_bhtn"/>
                                    <field name="tong_khau_tru" style="font-weight: bold;"/>
                                </group>
                            </group>
                            <group class="oe_subtotal_footer oe_right">
                                <field name="thuc_linh" class="oe_subtotal_footer_separator" style="font-size: 1.5em; font-weight: bold;"/>
                            </group>
                        </page>
                    </notebook>
                </sheet>
            </form>
        </field>
    </record>

    <record id="action_phieu_luong" model="ir.actions.act_window">
        <field name="name">Phiếu lương nhân viên</field>
        <field name="res_model">phieu_luong</field>
        <field name="view_mode">tree,form</field>
    </record>
</odoo>
```

Write `addons/tinh_luong/views/menu.xml`:
```xml
<odoo>
    <menuitem id="menu_tinh_luong_root" name="Tính lương" sequence="30" web_icon="tinh_luong,static/description/icon.png"/>
    <menuitem id="menu_phieu_luong" name="Phiếu lương" parent="menu_tinh_luong_root" action="action_phieu_luong" sequence="10"/>
</odoo>
```

- [ ] **Step 5: Install the new module**

Run Odoo command to install the `tinh_luong` module.
Run: `python odoo-bin.py -c odoo.conf -i tinh_luong --stop-after-init`
Expected: Module installs successfully.

- [ ] **Step 6: Commit changes**
```bash
git add addons/tinh_luong/
git commit -m "feat(payroll): scaffold tinh_luong module with payslip model and calculations"
```

---

### Task 4: Implement Trigger "Chốt công tháng" to Automatically Create Payslips

**Files:**
- Modify: `addons/cham_cong/models/chot_cong_thang.py`

**Interfaces:**
- Consumes: Records from `cham_cong_hang_ngay`, variables from `chot_cong_thang`.
- Produces: Generated `phieu_luong` records in `tinh_luong` module.

- [ ] **Step 1: Write automatic Payslip generation logic**

Modify `addons/cham_cong/models/chot_cong_thang.py` to implement `action_confirm_chot_cong`:
```python
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
                    # Skip or overwrite
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
```

- [ ] **Step 2: Upgrade and test the code**

Run Odoo command to upgrade the `cham_cong` and `tinh_luong` modules.
Run: `python odoo-bin.py -c odoo.conf -u cham_cong,tinh_luong --stop-after-init`
Expected: Modules upgrade successfully.

- [ ] **Step 3: Commit changes**
```bash
git add addons/cham_cong/models/chot_cong_thang.py
git commit -m "feat(automation): implement chot_cong_thang trigger to automatically generate payslips"
```

---

### Task 5: Create Business Flow Diagram and Update README

**Files:**
- Create: `docs/business-flow/Nhom08_BusinessFlow_ChamCongTinhLuong.svg`
- Modify: `README.md`

**Interfaces:**
- Consumes: BPMN Swimlane conceptual flow.
- Produces: Diagram file in repository and updated project documentation.

- [ ] **Step 1: Write a python script to generate a beautiful SVG diagram**

Create a temporary script `scratch/generate_flow_diagram.py` to output the business flow SVG.
```python
# scratch/generate_flow_diagram.py
import os

svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 650" width="100%" height="100%">
  <!-- Background -->
  <rect width="1000" height="650" fill="#f8fafc" rx="10"/>
  
  <!-- Header -->
  <text x="500" y="40" font-family="Arial, sans-serif" font-size="22" font-weight="bold" fill="#0f172a" text-anchor="middle">LUỒNG NGHIỆP VỤ CHẤM CÔNG VÀ TÍNH LƯƠNG TỰ ĐỘNG (NHÓM 08)</text>
  
  <!-- Swimlanes Headers -->
  <rect x="20" y="80" width="160" height="120" fill="#e2e8f0" rx="5"/>
  <text x="100" y="145" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#334155" text-anchor="middle">Quản lý / HR</text>
  
  <rect x="20" y="210" width="160" height="120" fill="#e2e8f0" rx="5"/>
  <text x="100" y="275" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#334155" text-anchor="middle">Chấm công (Nghiệp vụ 1)</text>

  <rect x="20" y="340" width="160" height="120" fill="#e2e8f0" rx="5"/>
  <text x="100" y="405" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#334155" text-anchor="middle">Hệ thống Odoo (Trigger)</text>

  <rect x="20" y="470" width="160" height="120" fill="#e2e8f0" rx="5"/>
  <text x="100" y="535" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#334155" text-anchor="middle">Kế toán / Tính lương</text>

  <!-- Flow Nodes -->
  <!-- Lane: HR -->
  <rect x="220" y="115" width="150" height="50" fill="#bae6fd" stroke="#0284c7" stroke-width="2" rx="8"/>
  <text x="295" y="145" font-family="Arial, sans-serif" font-size="12" fill="#0369a1" text-anchor="middle" font-weight="bold">1. Tạo hồ sơ nhân viên</text>

  <!-- Lane: Attendance -->
  <rect x="420" y="245" width="150" height="50" fill="#fef08a" stroke="#ca8a04" stroke-width="2" rx="8"/>
  <text x="495" y="275" font-family="Arial, sans-serif" font-size="12" fill="#854d0e" text-anchor="middle" font-weight="bold">2. Chấm công hàng ngày</text>

  <rect x="620" y="245" width="150" height="50" fill="#fef08a" stroke="#ca8a04" stroke-width="2" rx="8"/>
  <text x="695" y="275" font-family="Arial, sans-serif" font-size="12" fill="#854d0e" text-anchor="middle" font-weight="bold">3. Nhấn "Chốt công tháng"</text>

  <!-- Lane: Odoo System -->
  <rect x="620" y="375" width="150" height="50" fill="#bbf7d0" stroke="#16a34a" stroke-width="2" rx="8"/>
  <text x="695" y="405" font-family="Arial, sans-serif" font-size="12" fill="#166534" text-anchor="middle" font-weight="bold">4. Quét công &amp; Tự tạo lương</text>

  <!-- Lane: Accountant -->
  <rect x="800" y="505" width="150" height="50" fill="#fbcfe8" stroke="#db2777" stroke-width="2" rx="8"/>
  <text x="875" y="535" font-family="Arial, sans-serif" font-size="12" fill="#9d174d" text-anchor="middle" font-weight="bold">5. Duyệt &amp; Thanh toán</text>

  <!-- Arrows -->
  <line x1="370" y1="140" x2="395" y2="140" stroke="#64748b" stroke-width="2"/>
  <line x1="395" y1="140" x2="395" y2="270" stroke="#64748b" stroke-width="2"/>
  <line x1="395" y1="270" x2="420" y2="270" stroke="#64748b" stroke-width="2"/>
  
  <line x1="570" y1="270" x2="620" y2="270" stroke="#64748b" stroke-width="2"/>
  <line x1="695" y1="295" x2="695" y2="375" stroke="#64748b" stroke-width="2"/>
  <line x1="770" y1="400" x2="785" y2="400" stroke="#64748b" stroke-width="2"/>
  <line x1="785" y1="400" x2="785" y2="530" stroke="#64748b" stroke-width="2"/>
  <line x1="785" y1="530" x2="800" y2="530" stroke="#64748b" stroke-width="2"/>
</svg>
"""
os.makedirs("docs/business-flow", exist_ok=True)
with open("docs/business-flow/Nhom08_BusinessFlow_ChamCongTinhLuong.svg", "w", encoding="utf-8") as f:
    f.write(svg_content)
```

Run this script to generate the diagram.
Run: `python scratch/generate_flow_diagram.py`
Expected: File `docs/business-flow/Nhom08_BusinessFlow_ChamCongTinhLuong.svg` is created successfully.

- [ ] **Step 2: Update README.md to describe the integration and point to the diagram**

Add a section at the bottom of `README.md` linking to the diagram and detailing the three modules' relationships.

- [ ] **Step 3: Commit diagram and README**
```bash
git add docs/business-flow/Nhom08_BusinessFlow_ChamCongTinhLuong.svg README.md
git commit -m "docs(diagram): add Swimlane BPMN business flow diagram and update README"
```

---

### Task 6: Add Odoo Demo Data

**Files:**
- Create: `addons/nhan_su/demo/nhan_vien_demo.xml`
- Create: `addons/cham_cong/demo/cham_cong_demo.xml`
- Modify: `addons/nhan_su/__manifest__.py`
- Modify: `addons/cham_cong/__manifest__.py`

**Interfaces:**
- Consumes: Odoo standard demo data XML layout.
- Produces: Pre-populated database records for testing.

- [ ] **Step 1: Create Employee demo data**

Create `addons/nhan_su/demo/nhan_vien_demo.xml`:
```xml
<odoo>
    <data noupdate="1">
        <record id="demo_nhan_vien_a" model="nhan_vien">
            <field name="ho_ten_dem">Nguyễn Văn</field>
            <field name="ten">A</field>
            <field name="ma_dinh_danh">anv</field>
            <field name="ngay_sinh">1995-05-15</field>
            <field name="luong_co_ban">12000000</field>
            <field name="phu_cap">1500000</field>
            <field name="he_so_bao_hiem">6000000</field>
        </record>

        <record id="demo_nhan_vien_b" model="nhan_vien">
            <field name="ho_ten_dem">Trần Thị</field>
            <field name="ten">B</field>
            <field name="ma_dinh_danh">btt</field>
            <field name="ngay_sinh">1998-08-20</field>
            <field name="luong_co_ban">15000000</field>
            <field name="phu_cap">2000000</field>
            <field name="he_so_bao_hiem">8000000</field>
        </record>
    </data>
</odoo>
```

Update `addons/nhan_su/__manifest__.py` to load this in `demo`:
```python
    'demo': [
        'demo/demo.xml',
        'demo/nhan_vien_demo.xml',
    ],
```

- [ ] **Step 2: Create Attendance demo data**

Create `addons/cham_cong/demo/cham_cong_demo.xml`:
```xml
<odoo>
    <data noupdate="1">
        <record id="demo_attendance_a_1" model="cham_cong_hang_ngay">
            <field name="nhan_vien_id" ref="nhan_su.demo_nhan_vien_a"/>
            <field name="ngay" eval="time.strftime('%Y-%m-01')"/>
            <field name="trang_thai">di_lam</field>
            <field name="so_gio_ot">2.0</field>
        </record>
        <record id="demo_attendance_a_2" model="cham_cong_hang_ngay">
            <field name="nhan_vien_id" ref="nhan_su.demo_nhan_vien_a"/>
            <field name="ngay" eval="time.strftime('%Y-%m-02')"/>
            <field name="trang_thai">di_lam</field>
            <field name="so_gio_ot">0.0</field>
        </record>
        <record id="demo_attendance_b_1" model="cham_cong_hang_ngay">
            <field name="nhan_vien_id" ref="nhan_su.demo_nhan_vien_b"/>
            <field name="ngay" eval="time.strftime('%Y-%m-01')"/>
            <field name="trang_thai">di_lam</field>
            <field name="so_gio_ot">0.0</field>
        </record>
        <record id="demo_attendance_b_2" model="cham_cong_hang_ngay">
            <field name="nhan_vien_id" ref="nhan_su.demo_nhan_vien_b"/>
            <field name="ngay" eval="time.strftime('%Y-%m-02')"/>
            <field name="trang_thai">nua_ngay</field>
            <field name="so_gio_ot">0.0</field>
        </record>
    </data>
</odoo>
```

Update `addons/cham_cong/__manifest__.py` to load this in `demo`:
```python
    'demo': [
        'demo/cham_cong_demo.xml',
    ],
```

- [ ] **Step 3: Update modules and verify demo data is loaded**

Run Odoo with `--without-demo=` to ensure demo data loads.
Run: `python odoo-bin.py -c odoo.conf -u nhan_su,cham_cong --stop-after-init`
Expected: Demo data loads correctly without Odoo validation errors.

- [ ] **Step 4: Commit changes**
```bash
git add addons/nhan_su/demo/nhan_vien_demo.xml addons/cham_cong/demo/cham_cong_demo.xml addons/nhan_su/__manifest__.py addons/cham_cong/__manifest__.py
git commit -m "feat(demo): add XML demo data for employees and attendance logs"
```

