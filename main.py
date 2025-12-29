import flet as ft
import sqlite3
import os

# 1. MOVE LOGIC FUNCTIONS TO THE TOP
def calculate_chaldean(name):
    chart = {'A':1,'I':1,'J':1,'Q':1,'Y':1,'B':2,'K':2,'R':2,'C':3,'G':3,'L':3,'S':3,'D':4,'M':4,'T':4,'E':5,'H':5,'N':5,'X':5,'U':6,'V':6,'W':6,'O':7,'Z':7,'F':8,'P':8}
    total = sum(chart.get(char, 0) for char in name.upper() if char.isalpha())
    temp = total
    while temp > 9: 
        temp = sum(int(d) for d in str(temp))
    return total, temp

def get_number_status(n):
    use_it = {3, 5, 6, 10, 12, 14, 15, 19, 23, 24, 27, 32, 33, 37, 41, 42, 45, 46, 50, 51, 55, 59, 60, 64, 66, 68, 69, 73, 77, 86, 91, 95, 96}
    ok_ok = {21, 30, 39, 75, 78, 93}
    if n in use_it:
        return "USE IT", ft.Colors.GREEN_600
    elif n in ok_ok:
        return "OK TO USE", ft.Colors.ORANGE_700
    elif n == 100:
        return "DON'T USE IT (POLICE)", ft.Colors.RED_800
    else:
        return "DON'T USE IT", ft.Colors.RED_600

# 2. UI LOGIC
def main(page: ft.Page):
    page.title = "Chaldean Pro"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT

    name_input = ft.TextField(label="Enter Name", border_radius=15)
    res_compound = ft.Text("0", size=35, weight="bold")
    res_destiny = ft.Text("0", size=35, weight="bold")
    res_status = ft.Text("", size=20, weight="bold")

    def on_calc(e):
        # Now 'calculate_chaldean' is defined above, so no NameError!
        comp, dest = calculate_chaldean(name_input.value)
        status, color = get_number_status(comp)
        res_compound.value = str(comp)
        res_destiny.value = str(dest)
        res_status.value = status
        res_status.color = color
        page.update()

    page.add(
        ft.Text("CHALDEAN PRO", size=25, weight="bold"),
        name_input,
        # Used 'ft.Button' instead of 'ElevatedButton' to fix DeprecationWarning
        ft.Button("CALCULATE", on_click=on_calc, bgcolor=ft.Colors.GREEN_700, color="white"),
        ft.Row([
            ft.Column([ft.Text("Compound"), res_compound], horizontal_alignment="center"),
            ft.Column([ft.Text("Destiny"), res_destiny], horizontal_alignment="center")
        ], alignment=ft.MainAxisAlignment.CENTER),
        res_status
    )

if __name__ == "__main__":
    # Using ft.run(main) to fix DeprecationWarning
    ft.run(main)
