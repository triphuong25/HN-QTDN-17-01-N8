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
