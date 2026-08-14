from styles.sofme_colors import *
import tkinter as tk
from tkinter import ttk

class DashboardWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SOFME - Dashboard")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Configuração do tema
        self.root.configure(background=BG_LIGHT_BLUE)
        
        # Criando o estilo customizado para a sidebar
        self.style = ttk.Style()
        self.style.configure('Sidebar.TFrame', background=WHITE, borderwidth=0)
        self.style.configure('Sidebar.TButton', background=WHITE, foreground=TEXT_DARK, padding=10, font=('Segoe UI', 10, 'bold'))
        self.style.map('Sidebar.TButton',
            activebackground=PRIMARY_BLUE,
            activeforeground=WHITE,
            hoverbackground=EFF6FF
        )
        
        # Sidebar
        self.sidebar = ttk.Frame(self.root, style='Sidebar.TFrame')
        self.sidebar.pack(side='left', fill='y', padx=2, ipadx=230)
        
        # Logotipo
        self.logo = ttk.Label(self.sidebar, text='SOFME', font=('Segoe UI', 16, 'bold'), foreground=PRIMARY_BLUE, background=WHITE, padding=10)
        self.logo.pack(fill='x', pady=20)
        
        # Itens do menu
        self.menu_items = ['Início', 'Cadastros', 'Movimento', 'Relatórios', 'Configurações']
        self.buttons = {}
        for idx, item in enumerate(self.menu_items):
            btn = ttk.Button(self.sidebar, text=item, style='Sidebar.TButton')
            btn.pack(fill='x', pady=5)
            self.buttons[item] = btn
        
        # Área principal
        self.main_frame = ttk.Frame(self.root, style='TFrame')
        self.main_frame.pack(fill='both', expand=True, padx=(230+10), pady=10)
        
        # Barra de navegação superior
        self.nav_bar = ttk.Frame(self.main_frame, style='TFrame')
        self.nav_bar.pack(fill='x', pady=10)
        
        self.welcome_label = ttk.Label(self.nav_bar, text='Bem-vindo de volta, SUPORTE!', font=('Segoe UI', 14, 'bold'), foreground=TEXT_DARK)
        self.welcome_label.pack(side='left', padx=10)
        
        self.subtext_label = ttk.Label(self.nav_bar, text='Última conexão: 2026-08-14 09:30', font=('Segoe UI', 10), foreground=TEXT_SECONDARY)
        self.subtext_label.pack(side='left', padx=(20, 10))
        
        # Cards financeiros
        self.cards_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.cards_frame.pack(fill='x', pady=20)
        
        # Criando cards de demonstração
        self.create_demo_cards()
        
        # Tabela de movimentações recentes
        self.recent_transactions_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.recent_transactions_frame.pack(fill='both', expand=True, pady=20)
        
        self.transactions_label = ttk.Label(self.recent_transactions_frame, text='Movimentações recentes', font=('Segoe UI', 12, 'bold'), foreground=TEXT_DARK)
        self.transactions_label.pack(anchor='w', padx=20)
        
        self.transactions_table = ttk.Treeview(self.recent_transactions_frame, columns=('Data', 'Operação', 'Valor'), show='headings', height=10)
        self.transactions_table.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Configurando colunas
        self.transactions_table.heading('Data', text='Data/Hora')
        self.transactions_table.heading('Operação', text='Descrição')
        self.transactions_table.heading('Valor', text='Valor')
        
        # Adicionando dados de exemplo
        self.demo_transactions()
        
    def create_demo_cards(self):
        colors = [SUCCESS_GREEN, ERROR_RED, WHITE]
        titles = ['Produtos Cadastrados', 'Entradas', 'Saídas', 'Saldo']
        values = ['1.250', 'R$ 125.000,00', 'R$ 75.000,00', 'R$ 50.000,00']
        
        for i, (title, value, color) in enumerate(zip(titles, values, colors)): 
            card = ttk.Frame(self.cards_frame, style='Card.TFrame')
            card.pack(fill='x', padx=20, pady=5, ipady=20)
            
            card_title = ttk.Label(card, text=title, font=('Segoe UI', 10, 'bold'), foreground=TEXT_DARK)
            card_title.pack(anchor='w', padx=10, pady=5)
            
            card_value = ttk.Label(card, text=value, font=('Segoe UI', 16, 'bold'), foreground=color)
            card_value.pack(anchor='w', padx=10)
            
            # Aplicando estilo ao card
            self.style.configure('Card.TFrame', background=WHITE, borderwidth=2, relief='ridge', padding=10)
            
    def demo_transactions(self):
        # Exemplo de dados
        data = [
            ('2026-08-14 08:30', 'Recebimento - Venda 123', 'R$ 1.000,00'),
            ('2026-08-14 08:15', 'Pagamento - Fornecedor XYZ', '-R$ 500,00'),
            ('2026-08-14 07:45', 'Correção de Custo', 'R$ 200,00'),
        ]
        
        for item in data:
            self.transactions_table.insert('', 'end', values=item)
