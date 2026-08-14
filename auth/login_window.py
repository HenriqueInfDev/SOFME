from styles.sofme_colors import *
import tkinter as tk
from tkinter import ttk

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SOFME - Sistema de Organização Financeira para Microempreendedor")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Configuração do tema
        self.root.configure(background=BG_LIGHT_BLUE)
        
        # Fundo com degradê (simulado com canvas)
        self.canvas = tk.Canvas(self.root, bg=BG_LIGHT_BLUE, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        # Card central
        self.card_frame = ttk.Frame(self.root, style='Card.TFrame')
        self.card_frame.configure(background=BG_CARD, padding=20)
        self.card_frame.place(relx=0.5, rely=0.5, anchor='center', width=360, height=390)
        
        # Cabeçalho do card
        self.lock_icon = ttk.Label(self.card_frame, text='🔒', font=('Segoe UI', 48), foreground=PRIMARY_BLUE, background=BG_CARD, padding=10)
        self.lock_icon.pack(pady=20)
        
        # Título
        self.title = ttk.Label(self.card_frame, text='Acesso ao sistema', font=('Segoe UI', 14, 'semibold'), foreground=TEXT_DARK, background=BG_CARD)
        self.title.pack(pady=10)
        
        # Banco de dados selecionado
        self.database_label = ttk.Label(self.card_frame, text='Banco: SQLite (sistema)', font=('Segoe UI', 10), foreground=TEXT_SECONDARY, background=BG_CARD)
        self.database_label.pack(pady=5)
        
        # Campo de login
        self.login_label = ttk.Label(self.card_frame, text='Login', font=('Segoe UI', 10), foreground=TEXT_DARK, background=BG_CARD)
        self.login_label.pack(anchor='w', padx=20, pady=5)
        
        self.login_entry = ttk.Entry(self.card_frame, font=('Segoe UI', 12), foreground=TEXT_DARK, background=BG_INPUT, borderwidth=2, cursor='ibeam')
        self.login_entry.pack(fill='x', padx=20, pady=5, ipady=5)
        
        # Campo de senha
        self.password_label = ttk.Label(self.card_frame, text='Senha', font=('Segoe UI', 10), foreground=TEXT_DARK, background=BG_CARD)
        self.password_label.pack(anchor='w', padx=20, pady=5)
        
        self.password_entry = ttk.Entry(self.card_frame, font=('Segoe UI', 12), foreground=TEXT_DARK, background=BG_INPUT, borderwidth=2, show='*', cursor='ibeam')
        self.password_entry.pack(fill='x', padx=20, pady=5, ipady=5)
        
        # Botão entrar
        self.login_button = ttk.Button(self.card_frame, text='Entrar', font=('Segoe UI', 11, 'bold'), foreground=WHITE, background=PRIMARY_BLUE, borderwidth=0, padding=(20, 10), cursor='hand2')
        self.login_button.pack(fill='x', padx=20, pady=15, ipady=5)
        
        # Estilo customizado para o card
        self.style = ttk.Style()
        self.style.configure('Card.TFrame', background=BG_CARD, borderwidth=0, padding=20)
        self.style.configure('TButton', padding=6, relief='flat', background=PRIMARY_BLUE)
        
        # Efeito de sombra (simulado com borda externa)
        self.card_frame.configure(relief='raised', borderwidth=4)
