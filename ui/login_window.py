from tkinter import ttk, messagebox
from database.config import Config
import os

class LoginWindow(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.config = Config()
        
        # Configuração da janela
        self.parent.title('Sistema - Login')
        self.style = ttk.Style()
        self.style.configure('TFrame', background='white')
        self.style.configure('TLabel', foreground='black', font=('Helvetica', 10))
        self.style.configure('TButton', font=('Helvetica', 10))
        
        # Cria a aba de login
        self.create_login_tab()
        
        # Cria a aba de gerenciamento de bancos de dados
        self.create_database_tab()
        
        # Notebook para alternar entre abas
        self.notebook = ttk.Notebook(self)
        self.notebook.add(self.login_tab, text='Login')
        self.notebook.add(self.database_tab, text='Bancos de Dados')
        self.notebook.pack(expand=True, fill='both')
        
    def create_login_tab(self):
        self.login_tab = ttk.Frame(self, style='TFrame')
        
        # Campos de login
        ttk.Label(self.login_tab, text='Usuário:').grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = ttk.Entry(self.login_tab)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.login_tab, text='Senha:').grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = ttk.Entry(self.login_tab, show='*')
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Botão de login
        self.login_button = ttk.Button(self.login_tab, text='Entrar', command=self.handle_login)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=10)
        
    def handle_login(self):
        # Implementação do login
        pass
        
    def create_database_tab(self):
        self.database_tab = ttk.Frame(self, style='TFrame')
        
        # Seção de seleção de banco de dados
        ttk.Label(self.database_tab, text='Selecionar Banco de Dados:').grid(row=0, column=0, padx=5, pady=5)
        self.database_selector = ttk.Combobox(self.database_tab, values=self.config.list_databases())
        self.database_selector.grid(row=0, column=1, padx=5, pady=5)
        
        self.select_button = ttk.Button(self.database_tab, text='Selecionar', command=self.handle_select_database)
        self.select_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Seção de criação de novo banco de dados
        ttk.Label(self.database_tab, text='Criar Novo Banco:').grid(row=1, column=0, padx=5, pady=5)
        self.new_database_entry = ttk.Entry(self.database_tab)
        self.new_database_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.create_button = ttk.Button(self.database_tab, text='Criar', command=self.handle_create_database)
        self.create_button.grid(row=1, column=2, padx=5, pady=5)
        
    def handle_select_database(self):
        db_name = self.database_selector.get()
        if db_name:
            success, message = self.config.set_current_database(db_name)
            if success:
                messagebox.showinfo('Banco de Dados', f'Banco {db_name} selecionado com sucesso')
            else:
                messagebox.showerror('Erro', message)
        
    def handle_create_database(self):
        db_name = self.new_database_entry.get().strip()
        if db_name:
            success, message = self.config.create_database(db_name)
            if success:
                messagebox.showinfo('Banco de Dados', message)
                self.update_database_list()
                self.new_database_entry.delete(0, 'end')
            else:
                messagebox.showerror('Erro', message)
        else:
            messagebox.showwarning('Aviso', 'Por favor, insira um nome para o novo banco de dados')
        
    def update_database_list(self):
        databases = self.config.list_databases()
        db_names = [db.name for db in databases]
        self.database_selector['values'] = db_names
        if db_names:
            self.database_selector.current(0)
        
    def on_show(self):
        # Atualiza a lista de bancos de dados quando a aba é exibida
        self.update_database_list()