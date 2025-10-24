# -*- coding: utf-8 -*-
"""
برنامج السهولة في البناء - النسخة الكاملة
تم التطوير بناء على المواصفات المتفق عليها
"""
import sqlite3
import pandas as pd
from datetime import datetime
import json
import os

class ConstructionProgram:
    def __init__(self, db_name="construction_program.db"):
        self.db_name = db_name
        self.conn = None
        self.setup_database()

    def setup_database(self):
        """إنشاء وتجهيز قاعدة البيانات"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            cursor = self.conn.cursor()

            # جدول الهيكل التنظيمي
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS organizational_structure (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                directorate TEXT NOT NULL,
                department TEXT NOT NULL,
                administration TEXT NOT NULL,
                branch TEXT NOT NULL,
                section TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # جدول الموظفين (الجانب البشري)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                global_id TEXT UNIQUE,
                functional_id TEXT,
                full_name TEXT NOT NULL,
                position TEXT,
                level TEXT,
                qualification TEXT,
                training_courses TEXT,
                personal_equipment TEXT,
                equipment_notes TEXT,
                company TEXT,
                directorate TEXT,
                department TEXT,
                administration TEXT,
                branch TEXT,
                section TEXT,
                attendance_rate REAL DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # جدول البنود المالية
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS financial_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                item_type TEXT,
                amount REAL,
                calculation_formula TEXT,
                employee_count INTEGER,
                attendance_rate REAL,
                total_amount REAL,
                month TEXT,
                directorate TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # جدول العهد والموارد
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_name TEXT NOT NULL,
                asset_type TEXT,
                current_quantity INTEGER,
                required_quantity INTEGER,
                missing_quantity INTEGER,
                calculation_standard TEXT,
                location TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # جدول التحليل والمباينة
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_type TEXT,
                employee_id INTEGER,
                human_data TEXT,
                financial_data TEXT,
                logistic_data TEXT,
                discrepancy_level TEXT,
                recommendations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # جدول الإعدادات
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_type TEXT,
                setting_name TEXT,
                setting_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            self.conn.commit()
            print("✅ تم إنشاء قاعدة البيانات بنجاح")

        except Exception as e:
            print(f"❌ خطأ في إنشاء قاعدة البيانات: {e}")

    # ██████████████████████████████████████████████████████████████████████████████
    # ████████████████████████████ الجانب البشري ███████████████████████████████████
    # ██████████████████████████████████████████████████████████████████████████████

    def add_employee(self, employee_data):
        """إضافة موظف جديد"""
        try:
            cursor = self.conn.cursor()
            query = '''
            INSERT INTO employees (
                global_id, functional_id, full_name, position, level,
                qualification, training_courses, personal_equipment, equipment_notes,
                company, directorate, department, administration, branch, section
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            cursor.execute(query, (
                employee_data['global_id'],
                employee_data['functional_id'],
                employee_data['full_name'],
                employee_data['position'],
                employee_data['level'],
                employee_data.get('qualification', ''),
                employee_data.get('training_courses', ''),
                employee_data.get('personal_equipment', ''),
                employee_data.get('equipment_notes', ''),
                employee_data['company'],
                employee_data['directorate'],
                employee_data['department'],
                employee_data['administration'],
                employee_data['branch'],
                employee_data['section']
            ))
            self.conn.commit()
            print("✅ تم إضافة الموظف بنجاح")
            return True
        except Exception as e:
            print(f"❌ خطأ في إضافة الموظف: {e}")
            return False

    def get_employees(self, directorate=None):
        """جلب بيانات الموظفين"""
        try:
            if directorate:
                query = "SELECT * FROM employees WHERE directorate = ? ORDER BY created_at DESC"
                df = pd.read_sql_query(query, self.conn, params=[directorate])
            else:
                query = "SELECT * FROM employees ORDER BY created_at DESC"
                df = pd.read_sql_query(query, self.conn)
            return df
        except Exception as e:
            print(f"❌ خطأ في جلب بيانات الموظفين: {e}")
            return pd.DataFrame()

    def update_employee_attendance(self, global_id, attendance_rate):
        """تحديث نسبة تواجد الموظف"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE employees SET attendance_rate = ? WHERE global_id = ?",
                (attendance_rate, global_id)
            )
            self.conn.commit()
            print(f"✅ تم تحديث تواجد الموظف {global_id} إلى {attendance_rate}%")
            return True
        except Exception as e:
            print(f"❌ خطأ في تحديث التواجد: {e}")
            return False

    # ██████████████████████████████████████████████████████████████████████████████
    # ████████████████████████████ الجانب المالي ███████████████████████████████████
    # ██████████████████████████████████████████████████████████████████████████████

    def calculate_salary(self, employee_count, attendance_rate, basic_salary=40000):
        """حساب الرواتب"""
        net_salary = (basic_salary / 30) * (attendance_rate / 100) * 30
        return net_salary

    def calculate_feeding(self, employee_count, attendance_rate):
        """حساب التغذية"""
        total_feeding = employee_count * 2500 * 30 * (attendance_rate / 100)
        in_kind = total_feeding * 0.8  # عيني
        cash = total_feeding * 0.2     # نقدي
        return total_feeding, in_kind, cash

    def add_financial_item(self, item_data):
        """إضافة بند مالي"""
        try:
            cursor = self.conn.cursor()
            query = '''
            INSERT INTO financial_items (
                item_name, item_type, amount, calculation_formula,
                employee_count, attendance_rate, total_amount, month, directorate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            cursor.execute(query, (
                item_data['item_name'],
                item_data['item_type'],
                item_data['amount'],
                item_data['calculation_formula'],
                item_data['employee_count'],
                item_data['attendance_rate'],
                item_data['total_amount'],
                item_data['month'],
                item_data['directorate']
            ))
            self.conn.commit()
            print("✅ تم إضافة البند المالي بنجاح")
            return True
        except Exception as e:
            print(f"❌ خطأ في إضافة البند المالي: {e}")
            return False

    def calculate_all_financials(self, directorate, month):
        """حساب جميع البنود المالية"""
        try:
            employees = self.get_employees(directorate)
            employee_count = len(employees)
            avg_attendance = employees['attendance_rate'].mean() if not employees.empty else 0

            financial_report = {
                'الرواتب': self.calculate_salary(employee_count, avg_attendance),
                'التغذية': self.calculate_feeding(employee_count, avg_attendance),
                'الإسكان': employee_count * 15 * 30,
                'الصحية': employee_count * 15 * 30,
                'الإيجارات': employee_count * 40 * 30,
                'الكهرباء': employee_count * 0.5 * 30,
                'الماء': employee_count * 0.5 * 30,
                'القرطاسية': employee_count * 0.5 * 30,
                'النظافة': employee_count * 0.5 * 30,
                'الصيانة': employee_count * 150 * 30
            }

            return financial_report
        except Exception as e:
            print(f"❌ خطأ في الحسابات المالية: {e}")
            return {}

    # ██████████████████████████████████████████████████████████████████████████████
    # ████████████████████████████ العهد والموارد ██████████████████████████████████
    # ██████████████████████████████████████████████████████████████████████████████

    def add_asset(self, asset_data):
        """إضافة عهدة جديدة"""
        try:
            cursor = self.conn.cursor()
            query = '''
            INSERT INTO assets (
                asset_name, asset_type, current_quantity, required_quantity,
                missing_quantity, calculation_standard, location, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            '''
            cursor.execute(query, (
                asset_data['asset_name'],
                asset_data['asset_type'],
                asset_data['current_quantity'],
                asset_data['required_quantity'],
                asset_data['missing_quantity'],
                asset_data['calculation_standard'],
                asset_data['location'],
                asset_data['status']
            ))
            self.conn.commit()
            print("✅ تم إضافة العهدة بنجاح")
            return True
        except Exception as e:
            print(f"❌ خطأ في إضافة العهدة: {e}")
            return False

    def calculate_assets_need(self, directorate, asset_type):
        """احتساب احتياجات العهد"""
        try:
            employee_count = len(self.get_employees(directorate))

            standards = {
                'خفيفة': {'per_employee': 0.5, 'base': 10},
                'متوسطة': {'per_employee': 0.2, 'base': 5},
                'ثقيلة': {'per_employee': 0.1, 'base': 2},
                'تواصلية': {'per_employee': 0.3, 'base': 8},
                'استهلاكية': {'per_employee': 2.0, 'base': 20}
            }

            standard = standards.get(asset_type, {'per_employee': 0.1, 'base': 5})
            required_quantity = int(employee_count * standard['per_employee'] + standard['base'])

            return required_quantity
        except Exception as e:
            print(f"❌ خطأ في احتساب الاحتياجات: {e}")
            return 0

    def update_asset_quantity(self, asset_name, new_quantity, location):
        """تحديث كمية العهدة"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE assets SET current_quantity = ? WHERE asset_name = ? AND location = ?",
                (new_quantity, asset_name, location)
            )
            self.conn.commit()
            print(f"✅ تم تحديث كمية {asset_name} إلى {new_quantity}")
            return True
        except Exception as e:
            print(f"❌ خطأ في تحديث الكمية: {e}")
            return False

    # ██████████████████████████████████████████████████████████████████████████████
    # ████████████████████████████ التحليل والمباينة ████████████████████████████████
    # ██████████████████████████████████████████████████████████████████████████████

    def analyze_discrepancies(self, directorate, month):
        """كشف التناقضات بين الجوانب"""
        try:
            employees = self.get_employees(directorate)

            discrepancies = []
            for _, employee in employees.iterrows():
                attendance = employee['attendance_rate']

                if attendance < 60:
                    discrepancy = {
                        'employee_name': employee['full_name'],
                        'global_id': employee['global_id'],
                        'issue': f'تواجد {attendance}% منخفض مع احتمال صرف كامل',
                        'level': 'high',
                        'recommendation': 'مراجعة نظام الصرف'
                    }
                    discrepancies.append(discrepancy)

                if not employee['training_courses']:
                    discrepancy = {
                        'employee_name': employee['full_name'],
                        'global_id': employee['global_id'],
                        'issue': 'موظف بدون دورات تدريبية أساسية',
                        'level': 'medium',
                        'recommendation': 'توفير تدريبات أساسية'
                    }
                    discrepancies.append(discrepancy)

            return discrepancies
        except Exception as e:
            print(f"❌ خطأ في التحليل: {e}")
            return []

    def analyze_readiness(self, directorate):
        """تحليل الجهوزية"""
        try:
            employees = self.get_employees(directorate)
            total_employees = len(employees)
            active_employees = len(employees[employees['status'] == 'active'])

            readiness_report = {
                'العمال': {
                    'required': total_employees,
                    'ready': active_employees,
                    'percentage': (active_employees / total_employees * 100) if total_employees > 0 else 0
                },
                'التجهيزات': {
                    'required': total_employees * 2,
                    'ready': total_employees * 1,
                    'percentage': 50
                }
            }

            return readiness_report
        except Exception as e:
            print(f"❌ خطأ في تحليل الجهوزية: {e}")
            return {}

    def comprehensive_analysis(self, directorate):
        """تحليل شامل"""
        try:
            analysis = {
                'الموظفين': len(self.get_employees(directorate)),
                'متوسط_التواجد': self.get_employees(directorate)['attendance_rate'].mean(),
                'التناقضات': self.analyze_discrepancies(directorate, datetime.now().strftime('%Y-%m')),
                'الجهوزية': self.analyze_readiness(directorate),
                'الحسابات_المالية': self.calculate_all_financials(directorate, datetime.now().strftime('%Y-%m'))
            }

            return analysis
        except Exception as e:
            print(f"❌ خطأ في التحليل الشامل: {e}")
            return {}

    # ██████████████████████████████████████████████████████████████████████████████
    # ████████████████████████████ الواجهة والتقارير ████████████████████████████████
    # ██████████████████████████████████████████████████████████████████████████████

    def generate_report(self, report_type, directorate=None):
        """إنشاء التقارير"""
        try:
            if report_type == 'بشري':
                return self.get_employees(directorate)
            elif report_type == 'مالي':
                query = "SELECT * FROM financial_items"
                if directorate:
                    query += " WHERE directorate = ?"
                return pd.read_sql_query(query, self.conn, params=[directorate])
                return pd.read_sql_query(query, self.conn)
            elif report_type == 'عهد':
                query = "SELECT * FROM assets"
                if directorate:
                    query += " WHERE location = ?"
                return pd.read_sql_query(query, self.conn, params=[directorate])
                return pd.read_sql_query(query, self.conn)
            elif report_type == 'تحليل':
                return self.analyze_discrepancies(directorate, datetime.now().strftime('%Y-%m'))
        except Exception as e:
            print(f"❌ خطأ في إنشاء التقرير: {e}")
            return pd.DataFrame()

    def show_dashboard(self):
        """عرض لوحة التحكم"""
        try:
            employees_count = len(self.get_employees())
            assets_count = len(pd.read_sql_query("SELECT * FROM assets", self.conn))
            financial_items_count = len(pd.read_sql_query("SELECT * FROM financial_items", self.conn))

            print("\n" + "="*60)
            print("🏗️  لوحة تحكم برنامج السهولة في البناء")
            print("="*60)
            print(f"👥 عدد الموظفين: {employees_count}")
            print(f"📦 عدد العهد: {assets_count}")
            print(f"💰 البنود المالية: {financial_items_count}")
            print("="*60)

        except Exception as e:
            print(f"❌ خطأ في عرض اللوحة: {e}")

    # ██████████████████████████████████████████████████████████████████████████████
    # ████████████████████████████ الإعدادات ███████████████████████████████████████
    # ██████████████████████████████████████████████████████████████████████████████

    def save_setting(self, setting_type, setting_name, setting_value):
        """حفظ الإعدادات"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO settings (setting_type, setting_name, setting_value) VALUES (?, ?, ?)",
                (setting_type, setting_name, setting_value)
            )
            self.conn.commit()
            print(f"✅ تم حفظ الإعداد: {setting_name}")
            return True
        except Exception as e:
            print(f"❌ خطأ في حفظ الإعداد: {e}")
            return False

    def get_setting(self, setting_name):
        """جلب الإعدادات"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT setting_value FROM settings WHERE setting_name = ?",
                (setting_name,)
            )
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"❌ خطأ في جلب الإعداد: {e}")
            return None

    def close_connection(self):
        """إغلاق الاتصال بقاعدة البيانات"""
        if self.conn:
            self.conn.close()
            print("✅ تم إغلاق الاتصال بقاعدة البيانات")


# ██████████████████████████████████████████████████████████████████████████████
# ████████████████████████████ التشغيل الرئيسي █████████████████████████████████
# ██████████████████████████████████████████████████████████████████████████████

def main():
    """الدالة الرئيسية لتشغيل البرنامج"""
    program = ConstructionProgram()

    # عرض لوحة التحكم
    program.show_dashboard()

    # إضافة بيانات تجريبية
    sample_employee = {
        'global_id': 'RSA-2024-001',
        'functional_id': '050',
        'full_name': 'أحمد محمد علي',
        'position': 'كهربائي',
        'level': 'م4',
        'qualification': 'دبلوم كهرباء',
        'training_courses': 'السلامة في المشاريع',
        'personal_equipment': 'خوذة أمان, قفازات عمل',
        'equipment_notes': 'جميع المعدات جيدة',
        'company': 'الشركة المعمارية العالمية',
        'directorate': 'مديرية الرياض',
        'department': 'شعبة المشاريع',
        'administration': 'إدارة المشاريع',
        'branch': 'فرع الكهرباء',
        'section': 'قسم العمل أ'
    }

    program.add_employee(sample_employee)

    # تحديث التواجد
    program.update_employee_attendance('RSA-2024-001', 85.0)

    # إضافة عهدة
    sample_asset = {
        'asset_name': 'كمبريشن هواء',
        'asset_type': 'متوسطة',
        'current_quantity': 8,
        'required_quantity': 12,
        'missing_quantity': 4,
        'calculation_standard': 'لكل 10 عمال',
        'location': 'مديرية الرياض',
        'status': 'جاهز'
    }

    program.add_asset(sample_asset)

    # حسابات مالية
    total_feeding, in_kind, cash = program.calculate_feeding(100, 80)
    print(f"\n💰 الحسابات المالية:")
    print(f"🍽️  إجمالي التغذية: {total_feeding:,.2f} ريال")
    print(f"📦 القيمة العينية: {in_kind:,.2f} ريال")
    print(f"💵 القيمة النقدية: {cash:,.2f} ريال")

    # التحليل
    discrepancies = program.analyze_discrepancies('مديرية الرياض', '2024-03')
    print(f"\n🔍 التحليل والمباينة:")
    for disc in discrepancies:
        print(f"⚠️  {disc['employee_name']} - {disc['issue']}")

    # تقارير
    print(f"\n📊 التقارير:")
    employees_report = program.generate_report('بشري', 'مديرية الرياض')
    if not employees_report.empty:
        print(employees_report[['full_name', 'position', 'attendance_rate']].to_string(index=False))

    # تحليل شامل
    comprehensive = program.comprehensive_analysis('مديرية الرياض')
    print(f"\n📈 تحليل شامل:")
    print(f"عدد الموظفين: {comprehensive.get('الموظفين', 0)}")
    print(f"متوسط التواجد: {comprehensive.get('متوسط_التواجد', 0):.1f}%")

    # إغلاق الاتصال
    program.close_connection()


if __name__ == "__main__":
    print("🚀 بدء تشغيل برنامج السهولة في البناء...")
    main()
    print("\n🎉 اكتمل تشغيل البرنامج بنجاح!")
