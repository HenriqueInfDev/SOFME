from styles.sofme_colors import *
import tkinter as tk
from tkinter import ttk

from tkinter import messagebox

class LoginWindow:
    def __init__(self, master):
        self.master = master
        self.config = Config()
        self.create_widgets()
        self.load_databases()

    def create_widgets(self):
        # Database Tab
        self.database_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.database_tab, text='Banco de Dados')

        # Database Name Entry
        self.db_name_label = ttk.Label(self.database_tab, text='Nome do Banco:')
        self.db_name_label.grid(row=0, column=0, padx=10, pady=5)
        self.db_name_entry = ttk.Entry(self.database_tab, width=30)
        self.db_name_entry.grid(row=0, column=1, padx=10, pady=5)

        # Create Database Button
        self.create_db_button = ttk.Button(self.database_tab, text='Criar Banco', command=self.handle_create_database)
        self.create_db_button.grid(row=0, column=2, padx=10, pady=5)

        # Edit Database Button
        self.edit_db_button = ttk.Button(self.database_tab, text='Editar', command=self.handle_new_database)
        self.edit_db_button.grid(row=0, column=3, padx=10, pady=5)

        # Database List
        self.db_list = Listbox(self.database_tab, width=40, height=10)
        self.db_list.grid(row=1, column=0, columnspan=4, padx=10, pady=5)

        # Select Database Button
        self.select_db_button = ttk.Button(self.database_tab, text='Selecionar', command=self.handle_select_database)
        self.select_db_button.grid(row=2, column=0, columnspan=4, padx=10, pady=5)

    def load_databases(self):
        databases = self.config.list_databases()
        for db in databases:
            self.db_list.insert('end', db)

    def handle_create_database(self):
        db_name = self.db_name_entry.get().strip()
        if not db_name:
            messagebox.showwarning('Aviso', 'Por favor, insira um nome para o banco de dados.')
            return

        success, msg = self.config.create_database(db_name)
        if success:
            messagebox.showinfo('Sucesso', 'Banco de dados criado com sucesso!')
            self.load_databases()
            self.db_name_entry.delete(0, 'end')
        else:
            messagebox.showerror('Erro', f'Falha ao criar banco de dados: {msg}')

    def handle_select_database(self):
        selection = self.db_list.curselection()
        if not selection:
            messagebox.showwarning('Aviso', 'Por favor, selecione um banco de dados.')
            return

        db_name = self.db_list.get(selection[0])
        success = self.config.set_current_database(db_name)
        if success:
            messagebox.showinfo('Sucesso', f'Banco de dados selecionado: {db_name}')
        else:
            messagebox.showerror('Erro', 'Falha ao selecionar banco de dados.')

    def handle_new_database(self):
        """
        Handles the creation of a new database
        """
        # Implementation for creating a new database
        print("New database creation triggered")
        # TO DO: Implement actual database creation logic
