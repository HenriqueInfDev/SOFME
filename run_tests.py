"""
run_tests.py

Script único para executar os testes organizados por categoria (módulo).
Uso:
  python run_tests.py         # roda todas as categorias
  python run_tests.py --category auth   # roda apenas categorias cujo nome contenha 'auth'
  python run_tests.py --failfast        # para no primeiro erro
"""

import os
import sys
import unittest


def discover_tests(tests_dir):
    loader = unittest.TestLoader()
    return loader.discover(start_dir=tests_dir, pattern='test_*.py')


def iter_tests(suite):
    from unittest import TestSuite
    for t in suite:
        if isinstance(t, TestSuite):
            yield from iter_tests(t)
        else:
            yield t


def group_tests_by_module(suite):
    groups = {}
    for test in iter_tests(suite):
        module = test.__class__.__module__
        groups.setdefault(module, []).append(test)
    return groups


def run_grouped_tests(tests_dir, selected_category=None, failfast=False):
    suite = discover_tests(tests_dir)
    groups = group_tests_by_module(suite)

    total_run = 0
    total_failures = 0
    total_errors = 0

    runner = unittest.TextTestRunner(verbosity=2, failfast=failfast)

    modules = sorted(groups.keys())
    if selected_category:
        modules = [m for m in modules if selected_category in m or selected_category in os.path.basename(m)]

    # small translator for common test name tokens
    token_map = {
        'create': 'criar',
        'can': 'pode',
        'default': 'padrão',
        'duplicate': 'duplicado',
        'is': '',
        'rejected': 'rejeitado',
        'login': 'login',
        'user': 'usuário',
        'users': 'usuários',
        'password': 'senha',
        'change': 'alterar',
        'change_password': 'alterar senha',
        'update': 'atualiza',
        'delete': 'excluir',
        'remove': 'remover',
        'list': 'listar',
        'search': 'pesquisa',
        'searches': 'pesquisas',
        'tests': 'testes',
        'item': 'item',
        'items': 'itens',
        'supplier': 'fornecedor',
        'suppliers': 'fornecedores',
        'unit': 'unidade',
        'sale': 'venda',
        'sales': 'vendas',
        'finalize': 'finalizar',
        'finalized': 'finalizado',
        'entry': 'entrada',
        'entries': 'entradas',
        'stock': 'estoque',
        'add': 'adicionar',
        'get': 'obter',
        'update': 'atualizar',
        'manual': 'manual',
        'input': 'entrada',
        'material': 'material',
        'updates': 'atualiza',
        'average': 'média',
        'cost': 'custo',
        'different': 'diferentes',
        'prices': 'preços',
        'bom': 'BOM',
        'operations': 'operações',
        'op': 'operação',
        'does': 'não',
        'not': 'não',
        'load': 'carrega',
        'all': 'todos',
        'on': 'em',
        'init': 'inicialização',
        'initiation': 'inicialização',
        'database': 'banco de dados',
        'tables': 'tabelas',
        'exist': 'existem',
        'reopen': 'reabrir',
        'cancel': 'cancelar',
        'reduce': 'reduz',
        'list': 'listar',
        'invalid': 'inválido',
        'cnpj': 'CNPJ',
        'in': 'em',
        'use': 'uso',
        'in_use': 'em uso',
        'blocks': 'bloqueia',
        'forbid': 'proibir',
        'support': 'suporte',
        'on': 'ao',
        'auth': 'autenticação',
        'and': 'e',
        'stored': 'armazenado',
        'as': 'como',
        'sim': 'Sim',
        'nao': 'Não',
        'não': 'Não',
    }

    def translate_test_name(name: str) -> str:
        # remove common test_ prefix
        if name.startswith('test_'):
            name = name[5:]
        parts = name.split('_')
        translated_parts = []
        for p in parts:
            tp = token_map.get(p.lower())
            translated_parts.append(tp if tp is not None else p)
        # join and tidy up multiple spaces
        desc = ' '.join([p for p in translated_parts if p])
        if not desc:
            desc = name.replace('_', ' ')
        return desc.capitalize()

    for module in modules:
        readable = module
        if module.startswith('tests.'):
            readable = module[len('tests.'):]
        print('\n' + '=' * 70)
        print(f"Executando categoria: {readable}")
        print('=' * 70)
        # print per-test Portuguese descriptions to help reading console
        for t in groups[module]:
            mname = getattr(t, '_testMethodName', str(t))
            print(f"- {mname}: {translate_test_name(mname)}")

        suite_for_module = unittest.TestSuite(groups[module])
        result = runner.run(suite_for_module)
        total_run += result.testsRun
        total_failures += len(result.failures)
        total_errors += len(result.errors)

    print('\n' + '#' * 70)
    print(f"Resumo: Total executados={total_run}, Failures={total_failures}, Errors={total_errors}")
    print('#' * 70 + '\n')

    return total_failures == 0 and total_errors == 0


def main(argv=None):
    argv = argv or sys.argv[1:]
    here = os.path.dirname(os.path.abspath(__file__))
    tests_dir = os.path.join(here, 'tests')

    selected_category = None
    failfast = False
    if '--category' in argv:
        idx = argv.index('--category')
        if idx + 1 < len(argv):
            selected_category = argv[idx + 1]
    if '--failfast' in argv:
        failfast = True

    ok = run_grouped_tests(tests_dir, selected_category=selected_category, failfast=failfast)
    if not ok:
        sys.exit(1)


if __name__ == '__main__':
    main()
