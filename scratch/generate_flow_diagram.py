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
print("Business flow diagram created successfully!")
