
import frappe
from datetime import datetime, timedelta
import calendar

def execute(filters=None):
    if not filters:
        filters = {}

    first_day, last_day = get_date_range(filters)

    columns = get_columns(first_day, last_day)
    data = get_data(filters, first_day, last_day)

    return columns, data


def get_date_range(filters):

    if filters.get("from_date") and filters.get("to_date"):
        first_day = datetime.strptime(filters["from_date"], "%Y-%m-%d").date()
        last_day = datetime.strptime(filters["to_date"], "%Y-%m-%d").date()

    else:
        year = int(filters.get("year"))
        month_name = filters.get("month")
        month = list(calendar.month_name).index(month_name)

        first_day = datetime(year, month, 1).date()
        last_day = datetime(year, month, calendar.monthrange(year, month)[1]).date()

    return first_day, last_day


def get_columns(first_day, last_day):

    columns = [{
        "label": "Employee",
        "fieldname": "employee",
        "fieldtype": "Data",
        "width": 200
    }]

    total_days = (last_day - first_day).days + 1

    for i in range(total_days):

        date_obj = first_day + timedelta(days=i)

        label = f"{date_obj.strftime('%a')} {date_obj.day:02d}"

        columns.append({
            "label": label,
            "fieldname": f"day_{i+1}",
            "fieldtype": "HTML",
            "width": 120
        })

    return columns


def get_data(filters, first_day, last_day):

    company = filters.get("company")
    department = filters.get("department")

    employee_filters = {}

    if company:
        employee_filters["company"] = company

    if department:
        employee_filters["department"] = department

    employees = frappe.get_all(
        "Employee",
        filters=employee_filters,
        fields=["name", "employee_name"]
    )

    if not employees:
        return []

    employee_ids = [e.name for e in employees]

    total_days = (last_day - first_day).days + 1

    # -------------------------
    # SHIFT ASSIGNMENTS
    # -------------------------

    shifts = frappe.db.sql("""
        SELECT employee, shift_type, start_date, end_date
        FROM `tabShift Assignment`
        WHERE docstatus = 1
        AND employee IN %(emp)s
        AND start_date <= %(last)s
        AND (end_date IS NULL OR end_date >= %(first)s)
    """, {
        "emp": tuple(employee_ids),
        "first": first_day,
        "last": last_day
    }, as_dict=1)

    shift_map = {}

    for s in shifts:

        current = max(s.start_date, first_day)
        end = s.end_date if s.end_date else last_day

        while current <= min(end, last_day):
            shift_map[(s.employee, current)] = s.shift_type
            current += timedelta(days=1)

    # -------------------------
    # LEAVE
    # -------------------------

    leaves = frappe.db.sql("""
        SELECT employee, from_date, to_date
        FROM `tabLeave Application`
        WHERE docstatus = 1
        AND status='Approved'
        AND employee IN %(emp)s
        AND from_date <= %(last)s
        AND to_date >= %(first)s
    """, {
        "emp": tuple(employee_ids),
        "first": first_day,
        "last": last_day
    }, as_dict=1)

    leave_map = {}

    for l in leaves:

        current = max(l.from_date, first_day)

        while current <= min(l.to_date, last_day):
            leave_map[(l.employee, current)] = True
            current += timedelta(days=1)

    # -------------------------
    # HOLIDAYS
    # -------------------------

    holiday_list = frappe.db.get_value("Company", company, "default_holiday_list")

    holidays = frappe.db.sql("""
        SELECT holiday_date, description, weekly_off
        FROM `tabHoliday`
        WHERE parent=%s
        AND holiday_date BETWEEN %s AND %s
    """, (holiday_list, first_day, last_day), as_dict=1)

    holiday_map = {h.holiday_date: h for h in holidays}

    # -------------------------
    # BUILD DATA
    # -------------------------

    data = []

    for emp in employees:

        row = {}

        emp_display = f"{emp.employee_name} ({emp.name})"

        row["employee"] = emp_display

        for i in range(total_days):

            date_obj = first_day + timedelta(days=i)

            field = f"day_{i+1}"

            # SHIFT
            if (emp.name, date_obj) in shift_map:
                row[field] = f"<span style='font-weight:bold'>{shift_map[(emp.name,date_obj)]}</span>"

            # LEAVE
            elif (emp.name, date_obj) in leave_map:
                row[field] = "<span style='color:green;font-weight:bold'>L</span>"

            # HOLIDAY
            elif date_obj in holiday_map:

                h = holiday_map[date_obj]

                if h.weekly_off:
                    row[field] = "<span style='color:blue;font-weight:bold'>WO</span>"
                if "Public" in h.description:
                    row[field] = "<span style='color:purple;font-weight:bold'>PH</span>"
                else:
                    row[field] = f"<span style='color:purple'>{h.description}</span>"

            else:
                row[field] = "<span style='color:red'>NA</span>"

        data.append(row)

    return data