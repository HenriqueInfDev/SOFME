from styles.sofme_colors import *
import tkinter as tk
from tkinter import ttk

class SearchResultWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SOFME - Resultados da Pesquisa")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Configuração do tema
        self.root.configure(background=BG_LIGHT_BLUE)
        
        # Card principal
        self.main_card = ttk.Frame(self.root, style='Card.TFrame')
        self.main_card.pack(padx=20, pady=20, fill='both', expand=True)
        
        # Barra de pesquisa
        self.search_bar = ttk.Frame(self.main_card, style='TFrame')
        self.search_bar.pack(fill='x', padx=20, pady=10)
        
        # Campo de pesquisa
        self.search_entry = ttk.Entry(self.search_bar, font=('Segoe UI', 12), foreground=TEXT_DARK, background=BG_INPUT, borderwidth=2)
        self.search_entry.pack(fill='x', padx=10, pady=5, ipady=5)
        
        # Placeholder
        self.search_entry.insert(0, 'chocolate...')
        self.search_entry.configure(relief='flat')
        
        # Botão de pesquisa
        self.search_button = ttk.Button(self.search_bar, text='Pesquisar', font=('Segoe UI', 11, 'bold'), foreground=WHITE, background=PRIMARY_BLUE, borderwidth=0, padding=(20, 10), cursor='hand2')
        self.search_button.pack(fill='x', padx=10, pady=5, ipady=5)
        
        # Título dos resultados
        self.results_title = ttk.Label(self.main_card, text='Resultados encontrados (2)', font=('Segoe UI', 12, 'bold'), foreground=TEXT_DARK)
        self.results_title.pack(anchor='w', padx=20, pady=10)
        
        # Tabela de resultados
        self.results_table = ttk.Treeview(self.main_card, columns=('Nome', 'Código', 'Categoria', 'Estoque', 'Preço'), show='headings', height=10)
        self.results_table.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Configurando colunas
        self.results_table.heading('Nome', text='Nome do Produto')
        self.results_table.heading('Código', text='Código')
        self.results_table.heading('Categoria', text='Categoria')
        self.results_table.heading('Estoque', text='Estoque')
        self.results_table.heading('Preço', text='Preço de Venda')
        
        # Estilos para a tabela
        self.style = ttk.Style()
        self.style.configure('Treeview', background=WHITE, foreground=TEXT_DARK, fieldbackground=WHITE, rowheight=30)
        self.style.configure('Treeview.Heading', background=EFF6FF, foreground=TEXT_DARK, font=('Segoe UI', 10, 'bold'))
        
        # Adicionando dados de exemplo
        self.demo_results()
        
    def demo_results(self):
        # Exemplo de dados
        data = [
            ('Chocolate ao leite', 'PROD-001', 'Doces', '150 un', 'R$ 5,99'),
            ('Chocolate ao leite com amendoim', 'PROD-002', 'Doces', '80 un', 'R$ 7,99'),
        ]
        
        for item in data:
            self.results_table.insert('', 'end', values=item)
