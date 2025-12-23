import flet as ft
import sqlite3
import os
import sys
from datetime import datetime, timedelta

# --- DATABASE LOGIC ---
class DatabaseManager:
    def __init__(self):
        self.db_path = self.get_db_path()
        self.init_db()

    def get_db_path(self):
        """
        Determines the correct path for the database.
        On Android, it uses the app's private storage.
        On Desktop/Colab, it uses the current directory.
        """
        db_filename = "history.db"
        try:
            # Check if running on Android (Buildozer sets this)
            if "ANDROID_ARGUMENT" in os.environ:
                from android.storage import app_storage_path
                settings_path = app_storage_path()
                return os.path.join(settings_path, db_filename)
        except ImportError:
            pass
        
        # Fallback for Desktop or Google Colab Web Preview
        return db_filename

    def get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS history 
                              (id INTEGER PRIMARY KEY, name TEXT, compound INTEGER, 
                               destiny INTEGER, date TEXT)''')
            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            cursor.execute("DELETE FROM history WHERE date < ?", (thirty_days_ago,))
            conn.commit()

    def save_to_history(self, name, compound, destiny):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            date_str = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("INSERT INTO history (name, compound, destiny, date) VALUES (?, ?, ?, ?)",
                           (name, compound, destiny, date_str))
            conn.commit()

    def fetch_history(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, compound, destiny, date FROM history ORDER BY id DESC")
            return cursor.fetchall()

# Initialize DB at module level
db = DatabaseManager()

# --- NUMEROLOGY LOGIC ---
def calculate_chaldean(name):
    chart = {
        'A': 1, 'I': 1, 'J': 1, 'Q': 1, 'Y': 1, 'B': 2, 'K': 2, 'R': 2,
        'C': 3, 'G': 3, 'L': 3, 'S': 3, 'D': 4, 'M': 4, 'T': 4,
        'E': 5, 'H': 5, 'N': 5, 'X': 5, 'U': 6, 'V': 6, 'W': 6,
        'O': 7, 'Z': 7, 'F': 8, 'P': 8
    }
    total = sum(chart.get(char, 0) for char in name.upper() if char.isalpha())
    
    def reduce_digit(n):
        while n > 9:
            n = sum(int(digit) for digit in str(n))
        return n if n > 0 else 0
        
    return total, reduce_digit(total)

# --- UI LOGIC ---
def main(page: ft.Page):
    page.title = "Numerology Pro"
    page.bgcolor = "#F5F7FA"
    page.padding = 20
    # Note: Window size properties are ignored on Mobile but good for testing
    page.window_width = 400  
    page.window_height = 700
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO # Added scroll for smaller screens

    # UI Components
    name_input = ft.TextField(
        label="Name/Business Name", 
        border_radius=15, 
        bgcolor="white", 
        text_align="center",
        color="green",
        label_style=ft.TextStyle(color="green"),
        focused_border_color="green",
        on_submit=lambda e: on_calculate_click(e) 
    )
    
    compound_val = ft.Text("0", size=30, weight="bold", color="green")
    destiny_val = ft.Text("0", size=30, weight="bold", color="green")
    
    result_card = ft.Card(
        content=ft.Container(
            padding=20,
            content=ft.Row([
                ft.Column([ft.Text("Compound", size=12, color="green"), compound_val], horizontal_alignment="center"),
                ft.Column([ft.Text("Destiny", size=12, color="green"), destiny_val], horizontal_alignment="center"),
            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
        ),
        visible=False
    )

    history_list = ft.ListView(expand=True, spacing=10, padding=10)

    # Move BottomSheet definition up or define properly
    bottom_sheet = ft.BottomSheet(
        ft.Container(
            ft.Column([
                ft.Text("Last 30 Days History", size=20, weight="bold", color="green"),
                ft.Divider(color="green"),
                history_list,
                ft.ElevatedButton("Close", on_click=lambda e: setattr(bottom_sheet, 'open', False) or page.update(), color="white", bgcolor="green")
            ], tight=True, horizontal_alignment="center"),
            padding=20, height=400, bgcolor="white"
        )
    )
    page.overlay.append(bottom_sheet)

    def show_history(e):
        history_list.controls.clear()
        rows = db.fetch_history()
        if not rows:
             history_list.controls.append(ft.Text("No history found.", color="grey"))
        else:
            for row in rows:
                history_list.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.HISTORY, color="green"),
                        title=ft.Text(f"{row[0]}", color="green"),
                        subtitle=ft.Text(f"Date: {row[3]}", size=12, color="green"),
                        trailing=ft.Text(f"C:{row[1]} | D:{row[2]}", weight="bold", color="green")
                    )
                )
        bottom_sheet.open = True
        page.update()

    def on_calculate_click(e):
        clean_name = "".join(filter(str.isalpha, name_input.value))
        if clean_name:
            total, destiny = calculate_chaldean(name_input.value)
            compound_val.value = str(total)
            destiny_val.value = str(destiny)
            result_card.visible = True
            db.save_to_history(name_input.value, total, destiny)
            name_input.error_text = None
            page.update()
        else:
            name_input.error_text = "Please enter a valid name"
            page.update()

    # Layout
    page.add(
        ft.Row([
            ft.IconButton(ft.Icons.HISTORY, on_click=show_history, icon_color="green")
        ], alignment=ft.MainAxisAlignment.END),
        ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, size=50, color="green"),
        ft.Text("CHALDEAN PRO", size=24, weight="bold", color="green"),
        ft.Container(height=20),
        name_input,
        ft.ElevatedButton(
            "CALCULATE", 
            bgcolor="green", 
            color="white", 
            width=200, 
            on_click=on_calculate_click
        ),
        ft.Container(height=20),
        result_card,
        ft.Container(expand=True),
        ft.Text("Note: History is automatically cleared after 30 days.", size=10, color="green")
    )

if __name__ == "__main__":
    ft.app(target=main)
