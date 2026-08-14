from styles.sofme_colors import *
import tkinter as tk
from tkinter import ttk

class ProductSearchWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SOFME - Pesquisa de Produtos")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Configuração do tema
        self.root.configure(background=BG_LIGHT_BLUE)
        
        # Estilo customizado para o card de busca
        self.style = ttk.Style()
        self.style.configure('SearchCard.TFrame', background=BG_CARD, borderwidth=2, relief='ridge', padding=20)
        
        # Card de busca
        self.search_card = ttk.Frame(self.root, style='SearchCard.TFrame')
        self.search_card.place(relx=0.5, rely=0.1, anchor='center', width=800, height=120)
        
        # Título da busca
        self.search_title = ttk.Label(self.search_card, text='Pesquisa de Produto', font=('Segoe UI', 14, 'bold'), foreground=TEXT_DARK)
        self.search_title.pack(anchor='w', pady=10)
        
        # Campo de pesquisa
        self.search_entry = ttk.Entry(self.search_card, font=('Segoe UI', 12), foreground=TEXT_DARK, background=BG_INPUT, borderwidth=2)
        self.search_entry.pack(fill='x', padx=20, pady=5, ipady=5)
        
        # Placeholder
        self.search_entry.config(relief='flat')
        self.search_entry.insert(0, 'Digite o nome do produto...')
        self.search_entry.bind('<FocusIn>', lambda e: self.search_entry.delete(0, 'end') if self.search_entry.get() == 'Digite o nome do produto...' else None)
        self.search_entry.bind('<FocusOut>', lambda e: self.search_entry.insert(0, 'Digite o nome do produto...') if self.search_entry.get() == '' else None)
        
        # Botão de pesquisa
        self.search_button = ttk.Button(self.search_card, text='Pesquisar', font=('Segoe UI', 11, 'bold'), foreground=WHITE, background=PRIMARY_BLUE, borderwidth=0, padding=(20, 10), cursor='hand2')
        self.search_button.pack(fill='x', pady=10)
        
        # Tabela de resultados
        self.results_frame = ttk.Frame(self.root, style='TFrame')
        self.results_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título dos resultados
        self.results_title = ttk.Label(self.results_frame, text='Resultados encontrados (2)', font=('Segoe UI', 12, 'bold'), foreground=TEXT_DARK)
        self.results_title.pack(anchor='w', padx=10, pady=5)
        
        # Tabela
        self.results_table = ttk.Treeview(self.results_frame, columns=('Nome', 'Código', 'Categoria', 'Estoque', 'Preço'), show='headings', height=10)
        self.results_table.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Configurando colunas
        self.results_table.heading('Nome', text='Nome do Produto')
        self.results_table.heading('Código', text='Código')
        self.results_table.heading('Categoria', text='Categoria')
        self.results_table.heading('Estoque', text='Estoque')
        self.results_table.heading('Preço', text='Preço de Venda')
        
        # Estilos para a tabela
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
