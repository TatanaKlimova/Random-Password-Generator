import random
import string
import json
import os
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # Файл для сохранения истории
        self.history_file = "password_history.json"
        self.history = self.load_history()
        
        self.setup_ui()
        self.update_password_length_label()
        
    def setup_ui(self):
        # Основной фрейм
        main_frame = Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Заголовок
        title_label = Label(main_frame, text="Генератор случайных паролей", 
                            font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Фрейм для настроек
        settings_frame = LabelFrame(main_frame, text="Настройки пароля", padx=10, pady=10)
        settings_frame.pack(fill=X, pady=10)
        
        # Ползунок длины пароля
        length_frame = Frame(settings_frame)
        length_frame.pack(fill=X, pady=5)
        
        Label(length_frame, text="Длина пароля:").pack(side=LEFT)
        self.length_var = IntVar(value=12)
        self.length_slider = Scale(length_frame, from_=4, to=50, orient=HORIZONTAL,
                                   variable=self.length_var, command=self.update_password_length_label)
        self.length_slider.pack(side=LEFT, padx=10, fill=X, expand=True)
        
        self.length_label = Label(length_frame, text="12", width=5)
        self.length_label.pack(side=LEFT)
        
        # Чекбоксы для выбора символов
        self.use_uppercase = BooleanVar(value=True)
        self.use_lowercase = BooleanVar(value=True)
        self.use_digits = BooleanVar(value=True)
        self.use_special = BooleanVar(value=True)
        
        checkbox_frame = Frame(settings_frame)
        checkbox_frame.pack(fill=X, pady=10)
        
        Checkbutton(checkbox_frame, text="Заглавные буквы (A-Z)", 
                    variable=self.use_uppercase).pack(side=LEFT, padx=5)
        Checkbutton(checkbox_frame, text="Строчные буквы (a-z)", 
                    variable=self.use_lowercase).pack(side=LEFT, padx=5)
        Checkbutton(checkbox_frame, text="Цифры (0-9)", 
                    variable=self.use_digits).pack(side=LEFT, padx=5)
        Checkbutton(checkbox_frame, text="Спецсимволы (!@#$%^&*)", 
                    variable=self.use_special).pack(side=LEFT, padx=5)
        
        # Кнопка генерации
        self.generate_btn = Button(main_frame, text="Сгенерировать пароль", 
                                   command=self.generate_password,
                                   font=("Arial", 12), bg="#4CAF50", fg="white",
                                   padx=20, pady=5)
        self.generate_btn.pack(pady=10)
        
        # Поле для отображения сгенерированного пароля
        password_frame = Frame(main_frame)
        password_frame.pack(fill=X, pady=10)
        
        Label(password_frame, text="Сгенерированный пароль:", font=("Arial", 10)).pack(anchor=W)
        
        self.password_var = StringVar()
        self.password_entry = Entry(password_frame, textvariable=self.password_var, 
                                    font=("Courier", 12), width=50, state='readonly')
        self.password_entry.pack(fill=X, pady=5)
        
        # Кнопка копирования
        self.copy_btn = Button(password_frame, text="Копировать в буфер", 
                               command=self.copy_to_clipboard, state=DISABLED)
        self.copy_btn.pack(pady=5)
        
        # История паролей
        history_frame = LabelFrame(main_frame, text="История паролей", padx=10, pady=10)
        history_frame.pack(fill=BOTH, expand=True, pady=10)
        
        # Таблица истории
        columns = ("date", "password", "length", "charset")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=8)
        
        self.history_tree.heading("date", text="Дата и время")
        self.history_tree.heading("password", text="Пароль")
        self.history_tree.heading("length", text="Длина")
        self.history_tree.heading("charset", text="Набор символов")
        
        self.history_tree.column("date", width=150)
        self.history_tree.column("password", width=250)
        self.history_tree.column("length", width=60)
        self.history_tree.column("charset", width=150)
        
        scrollbar = Scrollbar(history_frame, orient=VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Кнопки управления историей
        history_buttons_frame = Frame(history_frame)
        history_buttons_frame.pack(fill=X, pady=5)
        
        Button(history_buttons_frame, text="Очистить историю", 
               command=self.clear_history).pack(side=LEFT, padx=5)
        Button(history_buttons_frame, text="Экспорт истории", 
               command=self.export_history).pack(side=LEFT, padx=5)
        
        # Загрузка истории в таблицу
        self.refresh_history_table()
        
    def update_password_length_label(self, event=None):
        self.length_label.config(text=str(self.length_var.get()))
        
    def get_character_set(self):
        characters = ""
        
        if self.use_uppercase.get():
            characters += string.ascii_uppercase
        if self.use_lowercase.get():
            characters += string.ascii_lowercase
        if self.use_digits.get():
            characters += string.digits
        if self.use_special.get():
            characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
            
        return characters
    
    def get_charset_description(self):
        desc = []
        if self.use_uppercase.get():
            desc.append("A-Z")
        if self.use_lowercase.get():
            desc.append("a-z")
        if self.use_digits.get():
            desc.append("0-9")
        if self.use_special.get():
            desc.append("спец")
        return ", ".join(desc) if desc else "нет"
    
    def generate_password(self):
        # Проверка выбора символов
        characters = self.get_character_set()
        
        if not characters:
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов!")
            return
        
        length = self.length_var.get()
        
        # Проверка длины
        if length < 4:
            messagebox.showerror("Ошибка", "Минимальная длина пароля - 4 символа!")
            return
        if length > 50:
            messagebox.showerror("Ошибка", "Максимальная длина пароля - 50 символов!")
            return
        
        # Генерация пароля
        password = ''.join(random.choice(characters) for _ in range(length))
        
        # Отображение пароля
        self.password_var.set(password)
        self.copy_btn.config(state=NORMAL)
        
        # Сохранение в историю
        self.save_to_history(password, length)
        
    def save_to_history(self, password, length):
        history_entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "password": password,
            "length": length,
            "charset": self.get_charset_description()
        }
        
        self.history.insert(0, history_entry)  # Новые записи в начало
        
        # Ограничим историю 50 записями
        if len(self.history) > 50:
            self.history = self.history[:50]
            
        self.save_history()
        self.refresh_history_table()
        
    def copy_to_clipboard(self):
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")
            
    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")
    
    def refresh_history_table(self):
        # Очистка таблицы
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        # Добавление записей
        for entry in self.history:
            self.history_tree.insert("", END, values=(
                entry["date"],
                entry["password"],
                entry["length"],
                entry["charset"]
            ))
    
    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.save_history()
            self.refresh_history_table()
            messagebox.showinfo("Успех", "История очищена!")
    
    def export_history(self):
        if not self.history:
            messagebox.showwarning("Предупреждение", "История пуста!")
            return
            
        export_file = f"password_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Успех", f"История экспортирована в файл: {export_file}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать историю: {e}")

def main():
    root = Tk()
    app = PasswordGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()