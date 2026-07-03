import os

DEFAULT_SETTINGS_FILE = 'local_params.txt'


def get_project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def get_local_params_path(filename=DEFAULT_SETTINGS_FILE):
    return os.path.join(get_project_root(), filename)


def load_local_params(filename=DEFAULT_SETTINGS_FILE):
    path = get_local_params_path(filename)
    params = {}
    if not os.path.exists(path):
        return params

    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, value = line.split('=', 1)
            params[key.strip()] = value.strip()

    return params


def save_local_params(params, filename=DEFAULT_SETTINGS_FILE):
    path = get_local_params_path(filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as file:
        for key in sorted(params.keys()):
            file.write(f'{key}={params[key]}\n')


def load_table_column_widths(table_name, filename=DEFAULT_SETTINGS_FILE):
    params = load_local_params(filename)
    value = params.get(f'table.{table_name}.columns')
    if not value:
        return []

    widths = []
    for part in value.split(','):
        part = part.strip()
        if not part:
            continue
        try:
            widths.append(int(part))
        except ValueError:
            continue

    return widths


def save_table_column_widths(table_name, widths, filename=DEFAULT_SETTINGS_FILE):
    params = load_local_params(filename)
    params[f'table.{table_name}.columns'] = ','.join(str(int(width)) for width in widths)
    save_local_params(params, filename)
