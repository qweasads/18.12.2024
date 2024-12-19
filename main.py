import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import asksaveasfilename
import mysql.connector
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from fpdf import FPDF


conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="expense_tracker_db"
)
cursor = conn.cursor()


def register_user():
    username = entry_username.get()
    password = entry_password.get()
    email = entry_email.get()

    if username and password and email:
        query = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, password, email))
        conn.commit()
        messagebox.showinfo("Успех", "Пользователь успешно зарегистрирован!")
    else:
        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")


def get_user_id_by_name(username):
    query = "SELECT id FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    return result[0] if result else None


def add_transaction():
    username = entry_user_name_transaction.get()
    amount = entry_amount.get()
    category = entry_category.get()
    trans_type = combobox_type.get()

    if username and amount and category and trans_type:
        user_id = get_user_id_by_name(username)
        if user_id:
            try:
                amount = float(amount)
                query = "INSERT INTO transactions (user_id, amount, category, type, created_at) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(query, (user_id, amount, category, trans_type, datetime.now()))
                conn.commit()
                messagebox.showinfo("Успех", "Транзакция добавлена!")
            except ValueError:
                messagebox.showerror("Ошибка", "Сумма должна быть числом!")
        else:
            messagebox.showerror("Ошибка", "Пользователь не существует!")
    else:
        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")


def show_balance():
    username = entry_user_name_balance.get()
    if username:
        user_id = get_user_id_by_name(username)
        if user_id:
            query = "SELECT SUM(CASE WHEN type='income' THEN amount ELSE -amount END) as balance FROM transactions WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            balance = result[0] if result[0] else 0.0
            messagebox.showinfo("Баланс", f"Текущий баланс: {balance:.2f}")
        else:
            messagebox.showerror("Ошибка", "Пользователь не существует!")
    else:
        messagebox.showerror("Ошибка", "Введите имя пользователя!")


def show_report():
    username = entry_user_name_report.get()
    if username:
        user_id = get_user_id_by_name(username)
        if user_id:
            query = "SELECT type, SUM(amount) FROM transactions WHERE user_id = %s GROUP BY type"
            cursor.execute(query, (user_id,))
            result = cursor.fetchall()
            if result:
                labels = ["Доход" if row[0] == "income" else "expense" for row in result]
                sizes = [row[1] for row in result]
                amounts = {"Доход": 0, "Расход": 0}
                for row in result:
                    if row[0] == "income":
                        amounts["Доход"] += row[1]
                    else:
                        amounts["Расход"] += row[1]

                fig, ax = plt.subplots()
                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')

                report_window = tk.Toplevel(root)
                report_window.title("Отчет")

                canvas = FigureCanvasTkAgg(fig, master=report_window)
                canvas.draw()
                canvas.get_tk_widget().pack()

                def save_pdf():
                    file_name = asksaveasfilename(
                        defaultextension=".pdf",
                        filetypes=[("PDF files", "*.pdf")],
                        initialfile=f"Отчет доходов и расходов пользователя {username}.pdf"
                    )
                    if file_name:
                        pdf = FPDF()
                        pdf.add_page()


                        pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
                        pdf.set_font('DejaVu', size=12)


                        pdf.cell(200, 10, txt=f"Отчет доходов и расходов пользователя {username}", ln=True, align='C')
                        pdf.ln(10)


                        pdf.cell(100, 10, txt=f"Доход: {amounts['Доход']:.2f}", ln=True)
                        pdf.cell(100, 10, txt=f"Расход: {amounts['Расход']:.2f}", ln=True)
                        pdf.cell(100, 10, txt=f"Баланс: {amounts['Доход'] - amounts['Расход']:.2f}", ln=True)
                        pdf.ln(10)


                        pdf.cell(200, 10, txt="Детализация по категориям:", ln=True)
                        for i, (label, size) in enumerate(zip(labels, sizes)):
                            pdf.cell(100, 10, txt=f"{label}: {size:.2f} ({sizes[i] / sum(sizes) * 100:.1f}%)", ln=True)

                        pdf.output(file_name)
                        messagebox.showinfo("Успех", f"PDF отчет сохранен как {file_name}")

                btn_save_pdf = ttk.Button(report_window, text="Сохранить как PDF", command=save_pdf)
                btn_save_pdf.pack()

            else:
                messagebox.showinfo("Информация", "Нет данных для отображения отчета!")
        else:
            messagebox.showerror("Ошибка", "Пользователь не существует!")
    else:
        messagebox.showerror("Ошибка", "Введите имя пользователя!")


root = tk.Tk()
root.title("Учет расходов и доходов")
root.geometry("400x500")


style = ttk.Style()
style.configure("TButton", font=("Arial", 12), padding=5)
style.configure("TLabel", font=("Arial", 12))
style.configure("TEntry", font=("Arial", 12))


notebook = ttk.Notebook(root)
frame_register = ttk.Frame(notebook)
frame_transaction = ttk.Frame(notebook)
frame_balance = ttk.Frame(notebook)
frame_report = ttk.Frame(notebook)

notebook.add(frame_register, text="Регистрация")
notebook.add(frame_transaction, text="Транзакции")
notebook.add(frame_balance, text="Баланс")
notebook.add(frame_report, text="Отчет")
notebook.pack(expand=True, fill="both")


ttk.Label(frame_register, text="Имя пользователя:").pack(pady=5)
entry_username = ttk.Entry(frame_register)
entry_username.pack(pady=5)

ttk.Label(frame_register, text="Пароль:").pack(pady=5)
entry_password = ttk.Entry(frame_register, show="*")
entry_password.pack(pady=5)

ttk.Label(frame_register, text="Email:").pack(pady=5)
entry_email = ttk.Entry(frame_register)
entry_email.pack(pady=5)

ttk.Button(frame_register, text="Зарегистрироваться", command=register_user).pack(pady=10)


ttk.Label(frame_transaction, text="Имя пользователя:").pack(pady=5)
entry_user_name_transaction = ttk.Entry(frame_transaction)
entry_user_name_transaction.pack(pady=5)

ttk.Label(frame_transaction, text="Сумма:").pack(pady=5)
entry_amount = ttk.Entry(frame_transaction)
entry_amount.pack(pady=5)

ttk.Label(frame_transaction, text="Категория:").pack(pady=5)
entry_category = ttk.Entry(frame_transaction)
entry_category.pack(pady=5)

ttk.Label(frame_transaction, text="Тип:").pack(pady=5)
combobox_type = ttk.Combobox(frame_transaction, values=["income", "expense"], state="readonly")
combobox_type.pack(pady=5)

ttk.Button(frame_transaction, text="Добавить", command=add_transaction).pack(pady=10)


ttk.Label(frame_balance, text="Имя пользователя:").pack(pady=5)
entry_user_name_balance = ttk.Entry(frame_balance)
entry_user_name_balance.pack(pady=5)

ttk.Button(frame_balance, text="Показать баланс", command=show_balance).pack(pady=10)


ttk.Label(frame_report, text="Имя пользователя:").pack(pady=5)
entry_user_name_report = ttk.Entry(frame_report)
entry_user_name_report.pack(pady=5)

ttk.Button(frame_report, text="Показать отчет", command=show_report).pack(pady=10)

root.mainloop()
conn.close()
