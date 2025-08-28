import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

DB_NAME = 'college_sms.db'

# ---------------------------- Database Layer ---------------------------- #
class Database:
    def __init__(self, db_path=DB_NAME):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        con = self._connect()
        cur = con.cursor()
        cur.execute("PRAGMA foreign_keys = ON;")
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                dob TEXT NOT NULL, -- YYYY-MM-DD
                department TEXT,
                email TEXT,
                phone TEXT
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                term TEXT NOT NULL,
                grade TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                date TEXT NOT NULL, -- YYYY-MM-DD
                subject TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('Present','Absent')),
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            );
            """
        )
        # Seed a default teacher if not exists
        cur.execute("SELECT COUNT(*) FROM teachers")
        if cur.fetchone()[0] == 0:
            cur.execute(
                "INSERT INTO teachers(name, username, password) VALUES (?,?,?)",
                ("Administrator", "admin", "admin"),
            )
        con.commit()
        con.close()

    # Teacher auth
    def teacher_auth(self, username, password):
        con = self._connect()
        cur = con.cursor()
        cur.execute(
            "SELECT id, name FROM teachers WHERE username=? AND password=?",
            (username, password),
        )
        row = cur.fetchone()
        con.close()
        return row  # (id, name) or None

    # Student auth (roll + dob)
    def student_auth(self, roll, dob):
        con = self._connect()
        cur = con.cursor()
        cur.execute(
            "SELECT id, name FROM students WHERE roll=? AND dob=?",
            (roll, dob),
        )
        row = cur.fetchone()
        con.close()
        return row

    # Student CRUD
    def add_student(self, roll, name, dob, department, email, phone):
        con = self._connect()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO students(roll,name,dob,department,email,phone) VALUES (?,?,?,?,?,?)",
            (roll, name, dob, department, email, phone),
        )
        con.commit()
        con.close()

    def update_student(self, student_id, roll, name, dob, department, email, phone):
        con = self._connect()
        cur = con.cursor()
        cur.execute(
            """
            UPDATE students SET roll=?, name=?, dob=?, department=?, email=?, phone=?
            WHERE id=?
            """,
            (roll, name, dob, department, email, phone, student_id),
        )
        con.commit()
        con.close()

    def delete_student(self, student_id):
        con = self._connect()
        cur = con.cursor()
        cur.execute("DELETE FROM students WHERE id=?", (student_id,))
        con.commit()
        con.close()

    def list_students(self, q=""):
        con = self._connect()
        cur = con.cursor()
        if q:
            pattern = f"%{q}%"
            cur.execute(
                "SELECT id, roll, name, dob, department, email, phone FROM students\n                 WHERE roll LIKE ? OR name LIKE ? OR department LIKE ? ORDER BY roll",
                (pattern, pattern, pattern),
            )
        else:
            cur.execute(
                "SELECT id, roll, name, dob, department, email, phone FROM students ORDER BY roll"
            )
        rows = cur.fetchall()
        con.close()
        return rows

    # Grades
    def add_grade(self, student_id, subject, term, grade):
        con = self._connect()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO grades(student_id, subject, term, grade) VALUES (?,?,?,?)",
            (student_id, subject, term, grade),
        )
        con.commit()
        con.close()

    def list_grades(self, student_id):
        con = self._connect()
        cur = con.cursor()
        cur.execute(
            "SELECT id, subject, term, grade FROM grades WHERE student_id=? ORDER BY term, subject",
            (student_id,),
        )
        rows = cur.fetchall()
        con.close()
        return rows

    def delete_grade(self, grade_id):
        con = self._connect()
        cur = con.cursor()
        cur.execute("DELETE FROM grades WHERE id=?", (grade_id,))
        con.commit()
        con.close()

    # Attendance
    def add_attendance(self, student_id, date, subject, status):
        con = self._connect()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO attendance(student_id, date, subject, status) VALUES (?,?,?,?)",
            (student_id, date, subject, status),
        )
        con.commit()
        con.close()

    def list_attendance(self, student_id):
        con = self._connect()
        cur = con.cursor()
        cur.execute(
            "SELECT id, date, subject, status FROM attendance WHERE student_id=? ORDER BY date DESC",
            (student_id,),
        )
        rows = cur.fetchall()
        con.close()
        return rows

    def delete_attendance(self, att_id):
        con = self._connect()
        cur = con.cursor()
        cur.execute("DELETE FROM attendance WHERE id=?", (att_id,))
        con.commit()
        con.close()

    # Utility
    def get_student_by_roll(self, roll):
        con = self._connect()
        cur = con.cursor()
        cur.execute(
            "SELECT id, roll, name, dob, department, email, phone FROM students WHERE roll=?",
            (roll,),
        )
        row = cur.fetchone()
        con.close()
        return row

# ---------------------------- UI Helpers ---------------------------- #
class LabeledEntry(ttk.Frame):
    def __init__(self, master, text, **kwargs):
        super().__init__(master)
        self.label = ttk.Label(self, text=text, width=14, anchor='w')
        self.label.pack(side=tk.LEFT, padx=(0,6))
        self.var = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.var, **kwargs)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def get(self):
        return self.var.get().strip()

    def set(self, value):
        self.var.set(value if value is not None else "")

# ---------------------------- Main Application ---------------------------- #
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("College Student Management System")
        self.geometry("980x640")
        self.minsize(960, 600)
        self.db = Database()
        self._style()
        self.container = ttk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)
        self.frames = {}
        for F in (Home, TeacherLogin, TeacherDashboard, StudentLogin, StudentDashboard):
            frame = F(parent=self.container, app=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show("Home")

    def _style(self):
        style = ttk.Style(self)
        try:
            self.tk.call("source", "azure.tcl")  # If user has a ttk theme
            style.theme_use("azure")
        except Exception:
            style.theme_use("clam")
        style.configure("TButton", padding=8)
        style.configure("Card.TFrame", background="#f7f7fb")
        style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"))

    def show(self, name, **kwargs):
        frame = self.frames[name]
        if hasattr(frame, 'on_show'):
            frame.on_show(**kwargs)
        frame.tkraise()

# ---------------------------- Screens ---------------------------- #
class Home(ttk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent, padding=20)
        self.app = app
        header = ttk.Label(self, text="College Student Management System", style="Header.TLabel")
        header.pack(pady=(10, 20))

        card = ttk.Frame(self, style="Card.TFrame", padding=20)
        card.pack(fill=tk.BOTH, expand=True)

        ttk.Label(card, text="Choose a portal:", font=("Segoe UI", 12)).pack(pady=(0, 10))

        btns = ttk.Frame(card)
        btns.pack(pady=10)
        ttk.Button(btns, text="Teacher Portal", command=lambda: self.app.show("TeacherLogin"), width=24).grid(row=0, column=0, padx=10, pady=10)
        ttk.Button(btns, text="Student Portal", command=lambda: self.app.show("StudentLogin"), width=24).grid(row=0, column=1, padx=10, pady=10)

        info = ttk.Label(card, text="Default teacher login: admin / admin", foreground="#666")
        info.pack(pady=(30,0))

class TeacherLogin(ttk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent, padding=20)
        self.app = app
        ttk.Label(self, text="Teacher Login", style="Header.TLabel").pack(pady=(10,20))

        form = ttk.Frame(self, padding=20, style="Card.TFrame")
        form.pack(pady=10, ipadx=10, ipady=10)
        self.username = LabeledEntry(form, "Username:")
        self.username.pack(fill=tk.X, pady=6)
        self.password = LabeledEntry(form, "Password:")
        self.password.entry.config(show="*")
        self.password.pack(fill=tk.X, pady=6)

        btnrow = ttk.Frame(form)
        btnrow.pack(pady=10)
        ttk.Button(btnrow, text="Login", command=self.login).pack(side=tk.LEFT, padx=6)
        ttk.Button(btnrow, text="Back", command=lambda: self.app.show("Home")).pack(side=tk.LEFT, padx=6)

    def login(self):
        u = self.username.get()
        p = self.password.get()
        user = self.app.db.teacher_auth(u, p)
        if user:
            self.app.show("TeacherDashboard", teacher_id=user[0], teacher_name=user[1])
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

class StudentLogin(ttk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent, padding=20)
        self.app = app
        ttk.Label(self, text="Student Login", style="Header.TLabel").pack(pady=(10,20))

        form = ttk.Frame(self, padding=20, style="Card.TFrame")
        form.pack(pady=10, ipadx=10, ipady=10)
        self.roll = LabeledEntry(form, "Roll No:")
        self.roll.pack(fill=tk.X, pady=6)
        self.dob = LabeledEntry(form, "DOB (YYYY-MM-DD):")
        self.dob.pack(fill=tk.X, pady=6)

        btnrow = ttk.Frame(form)
        btnrow.pack(pady=10)
        ttk.Button(btnrow, text="Login", command=self.login).pack(side=tk.LEFT, padx=6)
        ttk.Button(btnrow, text="Back", command=lambda: self.app.show("Home")).pack(side=tk.LEFT, padx=6)

    def login(self):
        roll = self.roll.get()
        dob = self.dob.get()
        user = self.app.db.student_auth(roll, dob)
        if user:
            self.app.show("StudentDashboard", student_id=user[0], student_name=user[1])
        else:
            messagebox.showerror("Login Failed", "Invalid Roll/DOB or account not found.")

class TeacherDashboard(ttk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent, padding=8)
        self.app = app
        self.teacher_id = None
        self.teacher_name = None

        # Header
        top = ttk.Frame(self)
        top.pack(fill=tk.X)
        self.title_lbl = ttk.Label(top, text="Teacher Dashboard", style="Header.TLabel")
        self.title_lbl.pack(side=tk.LEFT, pady=10)
        ttk.Button(top, text="Logout", command=lambda: self.app.show("Home")).pack(side=tk.RIGHT, padx=6, pady=10)

        # Notebook with tabs
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill=tk.BOTH, expand=True, pady=4)

        self.tab_students = ttk.Frame(self.nb, padding=10)
        self.tab_grades = ttk.Frame(self.nb, padding=10)
        self.tab_att = ttk.Frame(self.nb, padding=10)

        self.nb.add(self.tab_students, text="Students")
        self.nb.add(self.tab_grades, text="Grades")
        self.nb.add(self.tab_att, text="Attendance")

        self._build_students_tab()
        self._build_grades_tab()
        self._build_attendance_tab()

    def on_show(self, teacher_id, teacher_name):
        self.teacher_id = teacher_id
        self.teacher_name = teacher_name
        self.title_lbl.config(text=f"Teacher Dashboard – Welcome, {teacher_name}")
        self.refresh_students()
        self.refresh_grade_students()
        self.refresh_att_students()

    # ---- Students Tab ---- #
    def _build_students_tab(self):
        left = ttk.Frame(self.tab_students)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))
        right = ttk.Frame(self.tab_students)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Form
        ttk.Label(left, text="Manage Students", font=("Segoe UI", 12, 'bold')).pack(pady=(0,8))
        self.s_roll = LabeledEntry(left, "Roll No:")
        self.s_name = LabeledEntry(left, "Name:")
        self.s_dob = LabeledEntry(left, "DOB (YYYY-MM-DD):")
        self.s_dept = LabeledEntry(left, "Department:")
        self.s_email = LabeledEntry(left, "Email:")
        self.s_phone = LabeledEntry(left, "Phone:")
        for w in (self.s_roll, self.s_name, self.s_dob, self.s_dept, self.s_email, self.s_phone):
            w.pack(fill=tk.X, pady=4)

        btns = ttk.Frame(left)
        btns.pack(pady=6)
        ttk.Button(btns, text="Add", command=self.add_student).grid(row=0, column=0, padx=4)
        ttk.Button(btns, text="Update", command=self.update_student).grid(row=0, column=1, padx=4)
        ttk.Button(btns, text="Delete", command=self.delete_student).grid(row=0, column=2, padx=4)
        ttk.Button(btns, text="Clear", command=self.clear_student_form).grid(row=0, column=3, padx=4)

        # Search
        sea = ttk.Frame(right)
        sea.pack(fill=tk.X, pady=(0,6))
        ttk.Label(sea, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        ttk.Entry(sea, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
        ttk.Button(sea, text="Go", command=self.refresh_students).pack(side=tk.LEFT)

        # Table
        cols = ("id","roll","name","dob","department","email","phone")
        self.tree = ttk.Treeview(right, columns=cols, show='headings', selectmode='browse')
        for c in cols:
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=110 if c!="email" else 160, anchor=tk.W)
        self.tree.column("id", width=40)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_student_select)

    def refresh_students(self):
        q = self.search_var.get().strip() if hasattr(self, 'search_var') else ""
        for r in self.tree.get_children():
            self.tree.delete(r)
        for row in self.app.db.list_students(q):
            self.tree.insert('', tk.END, values=row)

    def on_student_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], 'values')
        sid, roll, name, dob, dept, email, phone = vals
        self.selected_student_id = int(sid)
        self.s_roll.set(roll)
        self.s_name.set(name)
        self.s_dob.set(dob)
        self.s_dept.set(dept)
        self.s_email.set(email)
        self.s_phone.set(phone)

    def clear_student_form(self):
        self.selected_student_id = None
        for w in (self.s_roll, self.s_name, self.s_dob, self.s_dept, self.s_email, self.s_phone):
            w.set("")

    def add_student(self):
        try:
            roll = self.s_roll.get(); name = self.s_name.get(); dob = self.s_dob.get()
            if not (roll and name and dob):
                raise ValueError("Roll, Name, DOB are required.")
            # basic date validation
            datetime.strptime(dob, "%Y-%m-%d")
            self.app.db.add_student(roll, name, dob, self.s_dept.get(), self.s_email.get(), self.s_phone.get())
            messagebox.showinfo("Success", "Student added.")
            self.refresh_students()
            self.clear_student_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_student(self):
        try:
            if not hasattr(self, 'selected_student_id') or not self.selected_student_id:
                raise ValueError("Select a student from the table.")
            roll = self.s_roll.get(); name = self.s_name.get(); dob = self.s_dob.get()
            if not (roll and name and dob):
                raise ValueError("Roll, Name, DOB are required.")
            datetime.strptime(dob, "%Y-%m-%d")
            self.app.db.update_student(self.selected_student_id, roll, name, dob, self.s_dept.get(), self.s_email.get(), self.s_phone.get())
            messagebox.showinfo("Success", "Student updated.")
            self.refresh_students()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_student(self):
        try:
            if not hasattr(self, 'selected_student_id') or not self.selected_student_id:
                raise ValueError("Select a student from the table.")
            if messagebox.askyesno("Confirm", "Delete selected student? This cannot be undone."):
                self.app.db.delete_student(self.selected_student_id)
                self.refresh_students()
                self.clear_student_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---- Grades Tab ---- #
    def _build_grades_tab(self):
        wrapper = ttk.Frame(self.tab_grades)
        wrapper.pack(fill=tk.BOTH, expand=True)
        left = ttk.Frame(wrapper)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))
        right = ttk.Frame(wrapper)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(left, text="Record Grades", font=("Segoe UI", 12, 'bold')).pack(pady=(0,8))
        self.g_roll = LabeledEntry(left, "Roll No:")
        self.g_subject = LabeledEntry(left, "Subject:")
        self.g_term = LabeledEntry(left, "Term:")
        self.g_grade = LabeledEntry(left, "Grade:")
        for w in (self.g_roll, self.g_subject, self.g_term, self.g_grade):
            w.pack(fill=tk.X, pady=4)
        ttk.Button(left, text="Add Grade", command=self.add_grade).pack(pady=6)

        cols = ("id","subject","term","grade")
        self.grade_tree = ttk.Treeview(right, columns=cols, show='headings', selectmode='browse')
        for c in cols:
            self.grade_tree.heading(c, text=c.capitalize())
            self.grade_tree.column(c, width=140, anchor=tk.W)
        self.grade_tree.column("id", width=50)
        self.grade_tree.pack(fill=tk.BOTH, expand=True)

        controls = ttk.Frame(right)
        controls.pack(pady=6)
        ttk.Button(controls, text="Load by Roll", command=self.refresh_grade_students).pack(side=tk.LEFT, padx=6)
        ttk.Button(controls, text="Delete Selected Grade", command=self.delete_grade).pack(side=tk.LEFT, padx=6)

    def refresh_grade_students(self):
        roll = self.g_roll.get()
        for r in self.grade_tree.get_children():
            self.grade_tree.delete(r)
        if not roll:
            return
        s = self.app.db.get_student_by_roll(roll)
        if not s:
            messagebox.showerror("Not Found", "Student not found.")
            return
        sid = s[0]
        for row in self.app.db.list_grades(sid):
            self.grade_tree.insert('', tk.END, values=row)

    def add_grade(self):
        try:
            roll = self.g_roll.get(); subject = self.g_subject.get(); term = self.g_term.get(); grade = self.g_grade.get()
            if not all([roll, subject, term, grade]):
                raise ValueError("All fields are required.")
            s = self.app.db.get_student_by_roll(roll)
            if not s:
                raise ValueError("Student not found.")
            self.app.db.add_grade(s[0], subject, term, grade)
            self.refresh_grade_students()
            self.g_subject.set(""); self.g_term.set(""); self.g_grade.set("")
            messagebox.showinfo("Success", "Grade added.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_grade(self):
        sel = self.grade_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a grade entry to delete.")
            return
        gid = int(self.grade_tree.item(sel[0], 'values')[0])
        if messagebox.askyesno("Confirm", "Delete selected grade?"):
            self.app.db.delete_grade(gid)
            self.refresh_grade_students()

    # ---- Attendance Tab ---- #
    def _build_attendance_tab(self):
        wrapper = ttk.Frame(self.tab_att)
        wrapper.pack(fill=tk.BOTH, expand=True)
        left = ttk.Frame(wrapper)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))
        right = ttk.Frame(wrapper)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(left, text="Mark Attendance", font=("Segoe UI", 12, 'bold')).pack(pady=(0,8))
        self.a_roll = LabeledEntry(left, "Roll No:")
        self.a_date = LabeledEntry(left, "Date (YYYY-MM-DD):")
        self.a_subject = LabeledEntry(left, "Subject:")
        ttk.Label(left, text="Status:").pack(anchor='w', pady=(6,2))
        self.a_status = tk.StringVar(value='Present')
        ttk.Radiobutton(left, text='Present', variable=self.a_status, value='Present').pack(anchor='w')
        ttk.Radiobutton(left, text='Absent', variable=self.a_status, value='Absent').pack(anchor='w')

        for w in (self.a_roll, self.a_date, self.a_subject):
            w.pack(fill=tk.X, pady=4)
        ttk.Button(left, text="Add Attendance", command=self.add_attendance).pack(pady=6)

        cols = ("id","date","subject","status")
        self.att_tree = ttk.Treeview(right, columns=cols, show='headings', selectmode='browse')
        for c in cols:
            self.att_tree.heading(c, text=c.capitalize())
            self.att_tree.column(c, width=140, anchor=tk.W)
        self.att_tree.column("id", width=50)
        self.att_tree.pack(fill=tk.BOTH, expand=True)

        controls = ttk.Frame(right)
        controls.pack(pady=6)
        ttk.Button(controls, text="Load by Roll", command=self.refresh_att_students).pack(side=tk.LEFT, padx=6)
        ttk.Button(controls, text="Delete Selected Record", command=self.delete_attendance).pack(side=tk.LEFT, padx=6)

    def refresh_att_students(self):
        roll = self.a_roll.get()
        for r in self.att_tree.get_children():
            self.att_tree.delete(r)
        if not roll:
            return
        s = self.app.db.get_student_by_roll(roll)
        if not s:
            messagebox.showerror("Not Found", "Student not found.")
            return
        sid = s[0]
        for row in self.app.db.list_attendance(sid):
            self.att_tree.insert('', tk.END, values=row)

    def add_attendance(self):
        try:
            roll = self.a_roll.get(); date = self.a_date.get(); subject = self.a_subject.get(); status = self.a_status.get()
            if not all([roll, date, subject, status]):
                raise ValueError("All fields are required.")
            # date validation
            datetime.strptime(date, "%Y-%m-%d")
            s = self.app.db.get_student_by_roll(roll)
            if not s:
                raise ValueError("Student not found.")
            self.app.db.add_attendance(s[0], date, subject, status)
            self.refresh_att_students()
            self.a_subject.set("")
            messagebox.showinfo("Success", "Attendance added.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_attendance(self):
        sel = self.att_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a record to delete.")
            return
        aid = int(self.att_tree.item(sel[0], 'values')[0])
        if messagebox.askyesno("Confirm", "Delete selected attendance record?"):
            self.app.db.delete_attendance(aid)
            self.refresh_att_students()

class StudentDashboard(ttk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent, padding=8)
        self.app = app
        self.student_id = None
        self.student_name = None

        top = ttk.Frame(self)
        top.pack(fill=tk.X)
        self.title_lbl = ttk.Label(top, text="Student Dashboard", style="Header.TLabel")
        self.title_lbl.pack(side=tk.LEFT, pady=10)
        ttk.Button(top, text="Logout", command=lambda: self.app.show("Home")).pack(side=tk.RIGHT, padx=6, pady=10)

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill=tk.BOTH, expand=True)
        self.tab_profile = ttk.Frame(self.nb, padding=10)
        self.tab_grades = ttk.Frame(self.nb, padding=10)
        self.tab_att = ttk.Frame(self.nb, padding=10)
        self.nb.add(self.tab_profile, text="Profile")
        self.nb.add(self.tab_grades, text="Grades")
        self.nb.add(self.tab_att, text="Attendance")

        # Profile
        self.profile_text = tk.Text(self.tab_profile, height=12, wrap='word')
        self.profile_text.pack(fill=tk.BOTH, expand=True)
        self.profile_text.config(state=tk.DISABLED)

        # Grades table
        gcols = ("subject","term","grade")
        self.s_grade_tree = ttk.Treeview(self.tab_grades, columns=gcols, show='headings')
        for c in gcols:
            self.s_grade_tree.heading(c, text=c.capitalize())
            self.s_grade_tree.column(c, width=160, anchor=tk.W)
        self.s_grade_tree.pack(fill=tk.BOTH, expand=True)

        # Attendance table
        acols = ("date","subject","status")
        self.s_att_tree = ttk.Treeview(self.tab_att, columns=acols, show='headings')
        for c in acols:
            self.s_att_tree.heading(c, text=c.capitalize())
            self.s_att_tree.column(c, width=160, anchor=tk.W)
        self.s_att_tree.pack(fill=tk.BOTH, expand=True)

    def on_show(self, student_id, student_name):
        self.student_id = student_id
        self.student_name = student_name
        self.title_lbl.config(text=f"Student Dashboard – Hello, {student_name}")
        self.load_profile()
        self.load_grades()
        self.load_attendance()

    def load_profile(self):
        con = self.app.db._connect()
        cur = con.cursor()
        cur.execute("SELECT roll, name, dob, department, email, phone FROM students WHERE id=?", (self.student_id,))
        row = cur.fetchone()
        con.close()
        if row:
            roll, name, dob, dept, email, phone = row
            info = [
                f"Roll: {roll}",
                f"Name: {name}",
                f"DOB: {dob}",
                f"Department: {dept}",
                f"Email: {email}",
                f"Phone: {phone}",
            ]
            self.profile_text.config(state=tk.NORMAL)
            self.profile_text.delete('1.0', tk.END)
            self.profile_text.insert(tk.END, "\n".join(info))
            self.profile_text.config(state=tk.DISABLED)

    def load_grades(self):
        for r in self.s_grade_tree.get_children():
            self.s_grade_tree.delete(r)
        for _id, subject, term, grade in self.app.db.list_grades(self.student_id):
            self.s_grade_tree.insert('', tk.END, values=(subject, term, grade))

    def load_attendance(self):
        for r in self.s_att_tree.get_children():
            self.s_att_tree.delete(r)
        for _id, date, subject, status in self.app.db.list_attendance(self.student_id):
            self.s_att_tree.insert('', tk.END, values=(date, subject, status))


if __name__ == '__main__':
    app = App()
    app.mainloop()
