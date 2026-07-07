# app/supplier/service.py
from app.supplier.supplier_repository import SupplierRepository
from app.validators import validate_cpf_cnpj

class SupplierService:
    def __init__(self):
        self.supplier_repository = SupplierRepository()

    @staticmethod
    def _normalize_optional_document(value):
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None

    @staticmethod
    def _normalize_supplier(supplier):
        if supplier is None:
            return None
        if isinstance(supplier, dict):
            return supplier
        if hasattr(supplier, 'keys'):
            return {key: supplier[key] for key in supplier.keys()}
        return dict(supplier)

    def add_supplier(self, razao_social, nome_fantasia, cnpj, phone, email, address, status):
        if not razao_social:
            return {"success": False, "message": "A Razão Social do fornecedor é obrigatória."}

        normalized_cnpj = self._normalize_optional_document(cnpj)
        if normalized_cnpj and not validate_cpf_cnpj(normalized_cnpj)[0]:
            return {"success": False, "message": "CPF/CNPJ inválido."}

        try:
            new_id = self.supplier_repository.add(razao_social, nome_fantasia, normalized_cnpj, phone, email, address, status)
            if new_id:
                return {"success": True, "data": new_id, "message": "Fornecedor adicionado com sucesso."}
            else:
                return {"success": False, "message": "Já existe um fornecedor com esta Razão Social ou CNPJ."}
        except Exception as e:
            return {"success": False, "message": f"Erro ao adicionar fornecedor: {e}"}

    def get_all_suppliers(self):
        try:
            suppliers = self.supplier_repository.get_all()
            return {"success": True, "data": [self._normalize_supplier(supplier) for supplier in suppliers]}
        except Exception as e:
            return {"success": False, "message": f"Erro ao buscar fornecedores: {e}"}

    def get_supplier_by_id(self, supplier_id):
        try:
            supplier = self.supplier_repository.get_by_id(supplier_id)
            if supplier:
                return {"success": True, "data": self._normalize_supplier(supplier)}
            else:
                return {"success": False, "message": "Fornecedor não encontrado."}
        except Exception as e:
            return {"success": False, "message": f"Erro ao buscar fornecedor: {e}"}

    def update_supplier(self, supplier_id, razao_social, nome_fantasia, cnpj, phone, email, address, status):
        if not razao_social:
            return {"success": False, "message": "A Razão Social do fornecedor é obrigatória."}

        normalized_cnpj = self._normalize_optional_document(cnpj)
        if normalized_cnpj and not validate_cpf_cnpj(normalized_cnpj)[0]:
            return {"success": False, "message": "CPF/CNPJ inválido."}
        
        try:
            if self.supplier_repository.update(supplier_id, razao_social, nome_fantasia, normalized_cnpj, phone, email, address, status):
                return {"success": True, "message": "Fornecedor atualizado com sucesso."}
            else:
                return {"success": False, "message": "Já existe um fornecedor com esta Razão Social ou CNPJ."}
        except Exception as e:
            return {"success": False, "message": f"Erro ao atualizar fornecedor: {e}"}

    def delete_supplier(self, supplier_id):
        try:
            if self.supplier_repository.has_stock_entries(supplier_id):
                return {"success": False, "message": "Não é possível excluir um fornecedor que possui notas de entrada."}

            if self.supplier_repository.is_referenced_by_items(supplier_id):
                return {"success": False, "message": "Não é possível excluir um fornecedor que está vinculado a um ou mais itens."}

            if self.supplier_repository.delete(supplier_id):
                return {"success": True, "message": "Fornecedor excluído com sucesso."}
            else:
                return {"success": False, "message": "Erro: Fornecedor não encontrado para exclusão."}
        except Exception as e:
            return {"success": False, "message": f"Erro no banco de dados ao tentar excluir o fornecedor: {e}"}

    def search_suppliers(self, search_field, search_text):
        try:
            suppliers = self.supplier_repository.search(search_text, search_field)
            return {"success": True, "data": [self._normalize_supplier(supplier) for supplier in suppliers]}
        except Exception as e:
            return {"success": False, "message": f"Erro ao buscar fornecedores: {e}"}
