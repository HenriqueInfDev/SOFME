from styles.sofme_colors import *
import tkinter as tk
from tkinter import ttk

class ProductRegistrationWindow:
    def __init__(self, master):
        self.master = master
        
        # Criando a janela modal
        self.main_frame = ttk.Frame(master, style='TFrame', width=800, height=600)
        self.main_frame.pack(fill='both', expand=True)
        
        # Fundo escurecido ao redor da janela modal
        self.master.configure(background=BG_LIGHT_BLUE)
        
        # Card do formulário
        self.card_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        self.card_frame.pack(expand=True, padx=40, pady=40)
        
        # Barra de ações superiores
        self.action_bar = ttk.Frame(self.card_frame, style='TFrame')
        self.action_bar.pack(anchor='ne', pady=10)
        
        # Botões de ação
        self.new_button = ttk.Button(self.action_bar, text='Novo', style='New.TButton', width=8)
        self.new_button.pack(side='left', padx=2)
        
        self.save_button = ttk.Button(self.action_bar, text='Salvar', style='Save.TButton', width=8)
        self.save_button.pack(side='left', padx=2)
        
        self.copy_button = ttk.Button(self.action_bar, text='Copiar', style='Copy.TButton', width=8)
        self.copy_button.pack(side='left', padx=2)
        
        self.delete_button = ttk.Button(self.action_bar, text='Excluir', style='Delete.TButton', width=8)
        self.delete_button.pack(side='left', padx=2)
        
        self.close_button = ttk.Button(self.action_bar, text='Fechar', style='Close.TButton', width=8)
        self.close_button.pack(side='left', padx=2)
        
        # Configurando estilos customizados para os botões
        self.style = ttk.Style()
        self.style.configure('New.TButton', background=SUCCESS_GREEN, foreground=WHITE, font=('Segoe UI', 10, 'bold'), padding=6)
        self.style.configure('Save.TButton', background=SUCCESS_GREEN, foreground=WHITE, font=('Segoe UI', 10, 'bold'), padding=6)
        self.style.configure('Copy.TButton', background=WARNING_ORANGE, foreground=WHITE, font=('Segoe UI', 10, 'bold'), padding=6)
        self.style.configure('Delete.TButton', background=ERROR_RED, foreground=WHITE, font=('Segoe UI', 10, 'bold'), padding=6)
        self.style.configure('Close.TButton', background='#475569', foreground=WHITE, font=('Segoe UI', 10, 'bold'), padding=6)
        
        # Abas do formulário
        self.notebook = ttk.Notebook(self.card_frame)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Aba principal
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text='Principal')
        
        # Campo de código
        ttk.Label(self.main_tab, text='Código:', font=('Segoe UI', 10)).grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.code_entry = ttk.Entry(self.main_tab, font=('Segoe UI', 12), foreground=TEXT_DARK, background=BG_INPUT, borderwidth=2)
        self.code_entry.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
        
        # Campo de nome
        ttk.Label(self.main_tab, text='Nome:', font=('Segoe UI', 10)).grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.name_entry = ttk.Entry(self.main_tab, font=('Segoe UI', 12), foreground=TEXT_DARK, background=BG_INPUT, borderwidth=2)
        self.name_entry.grid(row=1, column=1, padx=10, pady=5, sticky='ew')
        
        # Campo de categoria
        ttk.Label(self.main_tab, text='Categoria:', font=('Segoe UI', 10)).grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.category_entry = ttk.Entry(self.main_tab, font=('Segoe UI', 12), foreground=TEXT_DARK, background=BG_INPUT, borderwidth=2)
        self.category_entry.grid(row=2, column=1, padx=10, pady=5, sticky='ew')
        
        # Campo de estoque
        ttk.Label(self.main_tab, text='Estoque:', font=('Segoe UI', 10)).grid(row=3, column=0, sticky='w', padx=10, pady=5)
        self.stock_entry = ttk.Entry(self.main_tab, font=('Segoe UI', 12), foreground=TEXT_DARK, background=BG_INPUT, borderwidth=2)
        self.stock_entry.grid(row=3, column=1, padx=10, pady=5, sticky='ew')
        
        # Campo de preço
        ttk.Label(self.main_tab, text='Preço de Venda:', font=('Segoe UI', 10)).grid(row=4, column=0, sticky='w', padx=10, pady=5)
        self.price_entry = ttk.Entry(self.main_tab, font=('Segoe UI', 12), foreground=TEXT_DARK, background=BG_INPUT, borderwidth=2)
        self.price_entry.grid(row=4, column=1, padx=10, pady=5, sticky='ew')
        
        # Aplicando estilo ao card
        self.style.configure('Card.TFrame', background=WHITE, borderwidth=2, relief='ridge', padding=20)
