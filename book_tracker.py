import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class BookTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker")
        self.data_file = "books.json"
        
        # ====== Фрейм ввода ======
        input_frame = ttk.LabelFrame(root, text="Добавить книгу", padding=10)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky="w")
        self.title_entry = ttk.Entry(input_frame, width=40)
        self.title_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(input_frame, text="Автор:").grid(row=1, column=0, sticky="w")
        self.author_entry = ttk.Entry(input_frame, width=40)
        self.author_entry.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(input_frame, text="Жанр:").grid(row=2, column=0, sticky="w")
        self.genre_entry = ttk.Entry(input_frame, width=40)
        self.genre_entry.grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(input_frame, text="Страниц:").grid(row=3, column=0, sticky="w")
        self.pages_entry = ttk.Entry(input_frame, width=10)
        self.pages_entry.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        
        self.add_button = ttk.Button(input_frame, text="Добавить книгу", command=self.add_book)
        self.add_button.grid(row=4, column=0, columnspan=2, pady=10)
        
        # ====== Таблица ======
        table_frame = ttk.Frame(root)
        table_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        columns = ("title", "author", "genre", "pages")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        self.tree.heading("title", text="Название")
        self.tree.heading("author", text="Автор")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("pages", text="Страниц")
        self.tree.column("title", width=200)
        self.tree.column("author", width=150)
        self.tree.column("genre", width=120)
        self.tree.column("pages", width=80, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # ====== Фильтр ======
        filter_frame = ttk.LabelFrame(root, text="Фильтр", padding=10)
        filter_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        ttk.Label(filter_frame, text="По жанру:").grid(row=0, column=0, sticky="w")
        self.filter_genre = ttk.Combobox(filter_frame, state="readonly", width=20)
        self.filter_genre.grid(row=0, column=1, padx=5)
        
        ttk.Label(filter_frame, text="Страниц >=").grid(row=1, column=0, sticky="w", pady=5)
        self.filter_pages = ttk.Entry(filter_frame, width=10)
        self.filter_pages.grid(row=1, column=1, sticky="w", padx=5)
        
        self.apply_filter_btn = ttk.Button(filter_frame, text="Применить", command=self.apply_filter)
        self.apply_filter_btn.grid(row=2, column=0, pady=5, sticky="w")
        
        self.reset_filter_btn = ttk.Button(filter_frame, text="Сбросить", command=self.reset_filter)
        self.reset_filter_btn.grid(row=2, column=1, pady=5, sticky="e")
        
        # ====== Данные ======
        self.books = []
        self.load_books()
        self.refresh_table()
        self.update_genre_filter()
        
        # Растяжение колонок при изменении размера окна
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)

    # ---------- Работа с данными ----------
    def load_books(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.books = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.books = []
        else:
            self.books = []

    def save_books(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.books, f, ensure_ascii=False, indent=4)

    def add_book(self):
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_entry.get().strip()
        pages_str = self.pages_entry.get().strip()
        
        if not all([title, author, genre, pages_str]):
            messagebox.showerror("Ошибка", "Все поля обязательны для заполнения.")
            return
        if not pages_str.isdigit():
            messagebox.showerror("Ошибка", "Количество страниц должно быть целым числом.")
            return
        
        pages = int(pages_str)
        book = {
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages
        }
        self.books.append(book)
        self.save_books()
        self.clear_entries()
        self.refresh_table()
        self.update_genre_filter()

    def clear_entries(self):
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.pages_entry.delete(0, tk.END)

    def refresh_table(self, filtered_books=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        books_to_show = filtered_books if filtered_books is not None else self.books
        for book in books_to_show:
            self.tree.insert("", tk.END, values=(book["title"], book["author"], book["genre"], book["pages"]))

    def update_genre_filter(self):
        genres = sorted(set(book["genre"] for book in self.books))
        self.filter_genre['values'] = genres
        # Не сбрасываем выбранное значение автоматически, чтобы не мешать пользователю

    # ---------- Фильтрация ----------
    def apply_filter(self):
        genre = self.filter_genre.get()
        pages_str = self.filter_pages.get().strip()
        
        min_pages = None
        if pages_str:
            if not pages_str.isdigit():
                messagebox.showerror("Ошибка", "Минимальное количество страниц должно быть целым числом.")
                return
            min_pages = int(pages_str)
        
        filtered = []
        for book in self.books:
            if genre and book["genre"] != genre:
                continue
            if min_pages is not None and book["pages"] < min_pages:
                continue
            filtered.append(book)
        
        self.refresh_table(filtered)

    def reset_filter(self):
        self.filter_genre.set('')
        self.filter_pages.delete(0, tk.END)
        self.refresh_table()
        self.update_genre_filter()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("700x500")
    root.resizable(True, True)
    app = BookTrackerApp(root)
    root.mainloop()