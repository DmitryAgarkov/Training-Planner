"""
Training Planner - План тренировок
Автор: [Ваше Имя]
Описание: GUI-приложение для планирования и учёта тренировок
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# Типы тренировок для выпадающего списка
TRAINING_TYPES = [
    "🏃 Бег",
    "🚴 Велосипед",
    "🏊 Плавание",
    "💪 Силовая",
    "🧘 Йога",
    "🚶 Ходьба",
    "⚽ Футбол",
    "🏀 Баскетбол",
    "🎾 Теннис",
    "🥊 Бокс"
]

class TrainingPlanner:
    """
    Основной класс приложения для планирования тренировок.
    Управляет GUI, фильтрацией данных и работой с JSON-файлом.
    """
    
    def __init__(self, root):
        """Инициализация приложения: настройка интерфейса, загрузка данных."""
        self.root = root
        self.root.title("🏋️ Training Planner - План тренировок")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        # Список для хранения всех тренировок
        self.trainings = []
        
        # Файл для сохранения данных
        self.data_file = "training_data.json"
        
        # Загрузка сохранённых данных
        self.load_data()
        
        # Создание интерфейса
        self.setup_ui()
        
        # Обновление таблицы
        self.update_table()
    
    def setup_ui(self):
        """Создание всех элементов интерфейса"""
        
        # Основной контейнер с отступами
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # === ЗАГОЛОВОК ===
        title = ttk.Label(main_frame, text="🏆 План тренировок", font=("Arial", 20, "bold"))
        title.grid(row=0, column=0, columnspan=4, pady=10)
        
        # === ФОРМА ДЛЯ ДОБАВЛЕНИЯ ТРЕНИРОВКИ ===
        form_frame = ttk.LabelFrame(main_frame, text="➕ Добавить тренировку", padding="10")
        form_frame.grid(row=1, column=0, columnspan=4, pady=10, sticky=(tk.W, tk.E))
        
        # Поле: Дата
        ttk.Label(form_frame, text="Дата (ГГГГ-ММ-ДД):", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.date_entry = ttk.Entry(form_frame, font=("Arial", 10), width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))  # Текущая дата по умолчанию
        
        # Поле: Тип тренировки (выпадающий список)
        ttk.Label(form_frame, text="Тип тренировки:", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.training_type = ttk.Combobox(form_frame, values=TRAINING_TYPES, font=("Arial", 10), 
                                          state="readonly", width=15)
        self.training_type.set("🏃 Бег")  # Значение по умолчанию
        self.training_type.grid(row=0, column=3, padx=5, pady=5)
        
        # Поле: Длительность (минуты)
        ttk.Label(form_frame, text="Длительность (мин):", font=("Arial", 10)).grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.duration_entry = ttk.Entry(form_frame, font=("Arial", 10), width=10)
        self.duration_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Кнопка добавления
        self.add_btn = ttk.Button(form_frame, text="✅ Добавить тренировку", command=self.add_training)
        self.add_btn.grid(row=0, column=6, padx=10, pady=5)
        
        # === ФИЛЬТРАЦИЯ ===
        filter_frame = ttk.LabelFrame(main_frame, text="🔍 Фильтрация", padding="10")
        filter_frame.grid(row=2, column=0, columnspan=4, pady=10, sticky=(tk.W, tk.E))
        
        # Фильтр по типу тренировки
        ttk.Label(filter_frame, text="Фильтр по типу:", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5)
        self.filter_type = ttk.Combobox(filter_frame, values=["Все"] + TRAINING_TYPES, font=("Arial", 10),
                                        state="readonly", width=15)
        self.filter_type.set("Все")
        self.filter_type.grid(row=0, column=1, padx=5, pady=5)
        self.filter_type.bind('<<ComboboxSelected>>', lambda e: self.update_table())
        
        # Фильтр по дате
        ttk.Label(filter_frame, text="Фильтр по дате:", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5)
        self.filter_date = ttk.Entry(filter_frame, font=("Arial", 10), width=15)
        self.filter_date.grid(row=0, column=3, padx=5, pady=5)
        self.filter_date.insert(0, "")  # Пустое значение = без фильтра
        
        # Кнопка применения фильтра
        self.apply_filter_btn = ttk.Button(filter_frame, text="🔍 Применить фильтр", command=self.update_table)
        self.apply_filter_btn.grid(row=0, column=4, padx=10, pady=5)
        
        # Кнопка сброса фильтра
        self.reset_filter_btn = ttk.Button(filter_frame, text="🗑 Сбросить фильтр", command=self.reset_filters)
        self.reset_filter_btn.grid(row=0, column=5, padx=5, pady=5)
        
        # === ТАБЛИЦА ТРЕНИРОВОК ===
        table_frame = ttk.LabelFrame(main_frame, text="📋 Список тренировок", padding="10")
        table_frame.grid(row=3, column=0, columnspan=4, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Создание таблицы
        columns = ("id", "Дата", "Тип тренировки", "Длительность (мин)")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Настройка колонок
        self.tree.heading("id", text="ID")
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Тип тренировки", text="Тип тренировки")
        self.tree.heading("Длительность (мин)", text="Длительность (мин)")
        
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("Дата", width=100, anchor="center")
        self.tree.column("Тип тренировки", width=150)
        self.tree.column("Длительность (мин)", width=100, anchor="center")
        
        # Скроллбары
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Размещение таблицы и скроллбаров
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Настройка веса для растягивания
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # === КНОПКИ УПРАВЛЕНИЯ ===
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=4, column=0, columnspan=4, pady=10)
        
        # Кнопка удаления выбранной тренировки
        self.delete_btn = ttk.Button(control_frame, text="🗑 Удалить выбранное", command=self.delete_selected)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопка редактирования
        self.edit_btn = ttk.Button(control_frame, text="✏ Редактировать", command=self.edit_selected)
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопка экспорта
        self.export_btn = ttk.Button(control_frame, text="💾 Экспорт в JSON", command=self.export_data)
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопка импорта
        self.import_btn = ttk.Button(control_frame, text="📂 Импорт из JSON", command=self.import_data)
        self.import_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопка очистки всех данных
        self.clear_all_btn = ttk.Button(control_frame, text="⚠ Очистить всё", command=self.clear_all_data)
        self.clear_all_btn.pack(side=tk.LEFT, padx=5)
        
        # Статистика
        self.stats_label = ttk.Label(main_frame, text="", font=("Arial", 9), foreground="blue")
        self.stats_label.grid(row=5, column=0, columnspan=4, pady=5)
        
        # Статус-бар
        self.status_bar = ttk.Label(self.root, text="✅ Готов к работе", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def add_training(self):
        """
        Добавление новой тренировки.
        Проверяет корректность ввода:
        - Дата в формате ГГГГ-ММ-ДД
        - Длительность - положительное число
        """
        # Получение данных из полей
        date_str = self.date_entry.get().strip()
        training_type = self.training_type.get()
        duration_str = self.duration_entry.get().strip()
        
        # === ПРОВЕРКА ДАТЫ ===
        try:
            # Попытка преобразовать строку в дату
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", 
                "Некорректный формат даты!\n"
                "Используйте формат: ГГГГ-ММ-ДД (например, 2024-12-31)")
            return
        
        # === ПРОВЕРКА ДЛИТЕЛЬНОСТИ ===
        if not duration_str:
            messagebox.showerror("Ошибка", "Введите длительность тренировки!")
            return
        
        try:
            duration = float(duration_str)
        except ValueError:
            messagebox.showerror("Ошибка", 
                "Некорректный ввод длительности!\n"
                "Введите число (например, 30 или 45.5)")
            return
        
        # Проверка: длительность должна быть положительной
        if duration <= 0:
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом!")
            return
        
        # Создание новой записи
        new_id = max([t["id"] for t in self.trainings], default=0) + 1
        
        new_training = {
            "id": new_id,
            "date": date_str,
            "type": training_type,
            "duration": duration
        }
        
        # Добавление в список
        self.trainings.append(new_training)
        
        # Сохранение и обновление интерфейса
        self.save_data()
        self.update_table()
        
        # Очистка поля длительности (дату и тип оставляем для удобства)
        self.duration_entry.delete(0, tk.END)
        
        self.status_bar.config(text=f"✅ Добавлена тренировка: {training_type}, {duration} мин")
    
    def update_table(self):
        """
        Обновление таблицы с применением текущих фильтров.
        Фильтрация по:
        - Типу тренировки (если выбран не "Все")
        - Дате (если поле не пустое)
        """
        # Очистка текущей таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получение значений фильтров
        filter_type = self.filter_type.get()
        filter_date = self.filter_date.get().strip()
        
        # Фильтрация данных
        filtered_trainings = self.trainings.copy()
        
        if filter_type != "Все":
            filtered_trainings = [t for t in filtered_trainings if t["type"] == filter_type]
        
        if filter_date:
            filtered_trainings = [t for t in filtered_trainings if t["date"] == filter_date]
        
        # Сортировка по дате (от новых к старым)
        filtered_trainings.sort(key=lambda x: x["date"], reverse=True)
        
        # Добавление записей в таблицу
        for training in filtered_trainings:
            self.tree.insert("", tk.END, values=(
                training["id"],
                training["date"],
                training["type"],
                f"{training['duration']:.1f}"
            ))
        
        # Обновление статистики
        total_duration = sum(t["duration"] for t in filtered_trainings)
        self.stats_label.config(text=f"📊 Показано: {len(filtered_trainings)} тренировок | Общая длительность: {total_duration:.1f} мин")
        
        self.status_bar.config(text=f"🔍 Отфильтровано: {len(filtered_trainings)} записей")
    
    def reset_filters(self):
        """Сброс всех фильтров и обновление таблицы"""
        self.filter_type.set("Все")
        self.filter_date.delete(0, tk.END)
        self.update_table()
        self.status_bar.config(text="🔄 Фильтры сброшены")
    
    def delete_selected(self):
        """Удаление выбранной тренировки из списка"""
        selected = self.tree.selection()
        
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите тренировку для удаления!")
            return
        
        # Получение ID выбранной записи
        item = self.tree.item(selected[0])
        training_id = int(item["values"][0])
        
        # Поиск и удаление тренировки
        for i, training in enumerate(self.trainings):
            if training["id"] == training_id:
                training_type = training["type"]
                self.trainings.pop(i)
                break
        
        # Сохранение и обновление
        self.save_data()
        self.update_table()
        self.status_bar.config(text=f"🗑 Удалена тренировка: {training_type}")
    
    def edit_selected(self):
        """Редактирование выбранной тренировки"""
        selected = self.tree.selection()
        
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите тренировку для редактирования!")
            return
        
        # Получение данных выбранной тренировки
        item = self.tree.item(selected[0])
        training_id = int(item["values"][0])
        
        # Поиск тренировки
        training = None
        for t in self.trainings:
            if t["id"] == training_id:
                training = t
                break
        
        if not training:
            return
        
        # Создание окна редактирования
        edit_window = tk.Toplevel(self.root)
        edit_window.title("✏ Редактирование тренировки")
        edit_window.geometry("400x250")
        edit_window.resizable(False, False)
        edit_window.grab_set()  # Модальное окно
        
        # Поля ввода
        ttk.Label(edit_window, text="Дата (ГГГГ-ММ-ДД):", font=("Arial", 10)).pack(pady=5)
        date_edit = ttk.Entry(edit_window, font=("Arial", 10), width=20)
        date_edit.insert(0, training["date"])
        date_edit.pack(pady=5)
        
        ttk.Label(edit_window, text="Тип тренировки:", font=("Arial", 10)).pack(pady=5)
        type_edit = ttk.Combobox(edit_window, values=TRAINING_TYPES, font=("Arial", 10), state="readonly", width=20)
        type_edit.set(training["type"])
        type_edit.pack(pady=5)
        
        ttk.Label(edit_window, text="Длительность (мин):", font=("Arial", 10)).pack(pady=5)
        duration_edit = ttk.Entry(edit_window, font=("Arial", 10), width=20)
        duration_edit.insert(0, str(training["duration"]))
        duration_edit.pack(pady=5)
        
        def save_edit():
            """Сохранение изменений"""
            # Проверка даты
            try:
                datetime.strptime(date_edit.get().strip(), "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректный формат даты!")
                return
            
            # Проверка длительности
            try:
                new_duration = float(duration_edit.get().strip())
                if new_duration <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Ошибка", "Длительность должна быть положительным числом!")
                return
            
            # Обновление данных
            training["date"] = date_edit.get().strip()
            training["type"] = type_edit.get()
            training["duration"] = new_duration
            
            self.save_data()
            self.update_table()
            edit_window.destroy()
            self.status_bar.config(text="✏ Тренировка отредактирована")
        
        ttk.Button(edit_window, text="💾 Сохранить", command=save_edit).pack(pady=15)
    
    def export_data(self):
        """Экспорт данных в JSON файл"""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"training_export_{datetime.now().strftime('%Y%m%d')}.json"
        )
        
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(self.trainings, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("Успех", f"Данные экспортированы в {filename}")
                self.status_bar.config(text=f"💾 Экспорт в {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось экспортировать: {e}")
    
    def import_data(self):
        """Импорт данных из JSON файла"""
        from tkinter import filedialog
        
        filename = filedialog.askopenfilename(
            title="Выберите файл для импорта",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    imported_data = json.load(f)
                
                # Проверка структуры данных
                if not isinstance(imported_data, list):
                    raise ValueError("Неверный формат: ожидается список тренировок")
                
                # Проверка обязательных полей
                for item in imported_data:
                    if not all(key in item for key in ["date", "type", "duration"]):
                        raise ValueError("Отсутствуют обязательные поля (date, type, duration)")
                
                # Проверка на дубликаты ID
                max_id = max([t["id"] for t in self.trainings], default=0)
                for item in imported_data:
                    if "id" not in item or item["id"] <= max_id:
                        item["id"] = max_id + 1
                        max_id += 1
                
                self.trainings.extend(imported_data)
                self.save_data()
                self.update_table()
                messagebox.showinfo("Успех", f"Импортировано {len(imported_data)} тренировок")
                self.status_bar.config(text=f"📂 Импортировано {len(imported_data)} записей")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось импортировать: {e}")
    
    def clear_all_data(self):
        """Очистка всех данных после подтверждения"""
        if messagebox.askyesno("Подтверждение", 
            "⚠ ВНИМАНИЕ! Это действие удалит ВСЕ тренировки без возможности восстановления.\n\n"
            "Вы уверены, что хотите продолжить?"):
            self.trainings = []
            self.save_data()
            self.update_table()
            self.reset_filters()
            self.status_bar.config(text="🗑 Все данные очищены")
    
    def save_data(self):
        """Сохранение данных в JSON файл"""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.trainings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
    
    def load_data(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.trainings = json.load(f)
            except:
                self.trainings = []
        else:
            # Демо-данные для первого запуска
            self.trainings = [
                {"id": 1, "date": "2024-12-20", "type": "🏃 Бег", "duration": 30},
                {"id": 2, "date": "2024-12-21", "type": "💪 Силовая", "duration": 45},
                {"id": 3, "date": "2024-12-22", "type": "🏊 Плавание", "duration": 60},
                {"id": 4, "date": "2024-12-23", "type": "🚴 Велосипед", "duration": 90},
                {"id": 5, "date": "2024-12-24", "type": "🧘 Йога", "duration": 40}
            ]
            self.save_data()

# ===== ТОЧКА ВХОДА =====
if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()