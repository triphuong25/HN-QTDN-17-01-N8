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
    'demo': [
        'demo/cham_cong_demo.xml',
    ],
    'installable': True,
    'application': True,
}
