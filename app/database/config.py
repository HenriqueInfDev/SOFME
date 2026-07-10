import os
from dataclasses import dataclass
from typing import Dict, List, Optional
import app.utils.local_settings as local_settings

DEFAULT_DATABASE_SETTINGS_FILE = 'database_params.txt'
DATABASE_PREFIX = 'db.'
SELECTED_KEY = 'db.selected'

@dataclass(frozen=True)
class DatabaseConfig:
    key: str
    name: str
    directory: str
    filename: str

    @property
    def full_path(self) -> str:
        return os.path.abspath(os.path.join(self.directory, self.filename))


def _normalize_filename(filename: str) -> str:
    if not filename:
        return filename
    filename = filename.strip()
    if not filename.lower().endswith('.db'):
        filename += '.db'
    return filename


def load_database_params(filename: str = DEFAULT_DATABASE_SETTINGS_FILE) -> Dict[str, str]:
    return local_settings.load_local_params(filename)


def save_database_params(params: Dict[str, str], filename: str = DEFAULT_DATABASE_SETTINGS_FILE) -> None:
    local_settings.save_local_params(params, filename)


def _load_database_params_for_update(filename: str = DEFAULT_DATABASE_SETTINGS_FILE) -> Dict[str, str]:
    params = load_database_params(filename)
    return params


def get_database_settings_path(filename: str = DEFAULT_DATABASE_SETTINGS_FILE) -> str:
    return local_settings.get_local_params_path(filename)


def _collect_database_fields(params: Dict[str, str]) -> Dict[str, Dict[str, str]]:
    configs: Dict[str, Dict[str, str]] = {}
    for key, value in params.items():
        if not key.startswith(DATABASE_PREFIX):
            continue
        if key == SELECTED_KEY:
            continue
        parts = key.split('.')
        if len(parts) != 3:
            continue
        _, config_id, field_name = parts
        configs.setdefault(config_id, {})[field_name] = value
    return configs


def load_database_configs(filename: str = DEFAULT_DATABASE_SETTINGS_FILE) -> List[DatabaseConfig]:
    params = load_database_params(filename)
    configs = []
    for config_id, fields in _collect_database_fields(params).items():
        name = fields.get('name', '').strip()
        directory = fields.get('directory', '').strip()
        filename_value = fields.get('filename', '').strip()
        if not name or not directory or not filename_value:
            continue
        configs.append(DatabaseConfig(
            key=config_id,
            name=name,
            directory=os.path.abspath(directory),
            filename=_normalize_filename(filename_value),
        ))
    return sorted(configs, key=lambda item: item.name.lower())


def get_selected_database_key(filename: str = DEFAULT_DATABASE_SETTINGS_FILE) -> Optional[str]:
    params = load_database_params(filename)
    selected = params.get(SELECTED_KEY)
    if selected:
        return selected.strip()
    return None


def get_selected_database_config(filename: str = DEFAULT_DATABASE_SETTINGS_FILE) -> Optional[DatabaseConfig]:
    selected_key = get_selected_database_key(filename)
    configs = {config.key: config for config in load_database_configs(filename)}
    if selected_key and selected_key in configs:
        return configs[selected_key]
    if len(configs) == 1:
        return next(iter(configs.values()))
    return None


def get_selected_database_path(filename: str = DEFAULT_DATABASE_SETTINGS_FILE) -> Optional[str]:
    selected = get_selected_database_config(filename)
    return selected.full_path if selected else None


def _next_database_key(params: Dict[str, str]) -> str:
    keys = []
    for key in params.keys():
        if not key.startswith(DATABASE_PREFIX) or key == SELECTED_KEY:
            continue
        parts = key.split('.')
        if len(parts) != 3:
            continue
        _, config_id, _ = parts
        if config_id.isdigit():
            keys.append(int(config_id))
    next_id = max(keys) + 1 if keys else 1
    return str(next_id)


def add_database_config(name: str, directory: str, filename: str, filename_override: str = DEFAULT_DATABASE_SETTINGS_FILE) -> DatabaseConfig:
    params = _load_database_params_for_update(filename_override)
    config_id = _next_database_key(params)
    safe_name = name.strip()
    safe_directory = os.path.abspath(directory.strip())
    safe_filename = _normalize_filename(filename.strip())

    params[f'{DATABASE_PREFIX}{config_id}.name'] = safe_name
    params[f'{DATABASE_PREFIX}{config_id}.directory'] = safe_directory
    params[f'{DATABASE_PREFIX}{config_id}.filename'] = safe_filename

    if SELECTED_KEY not in params or not params[SELECTED_KEY].strip():
        params[SELECTED_KEY] = config_id

    save_database_params(params, filename_override)
    return DatabaseConfig(key=config_id, name=safe_name, directory=safe_directory, filename=safe_filename)


def set_selected_database(config_id: str, filename: str = DEFAULT_DATABASE_SETTINGS_FILE) -> None:
    params = _load_database_params_for_update(filename)
    configs = _collect_database_fields(params)
    if config_id not in configs:
        params.pop(SELECTED_KEY, None)
        save_database_params(params, filename)
        return
    params[SELECTED_KEY] = config_id
    save_database_params(params, filename)


def remove_database_config(config_id: str, filename: str = DEFAULT_DATABASE_SETTINGS_FILE) -> None:
    params = _load_database_params_for_update(filename)
    changed = False
    for suffix in ('name', 'directory', 'filename'):
        key = f'{DATABASE_PREFIX}{config_id}.{suffix}'
        if key in params:
            params.pop(key)
            changed = True

    selected_key = params.get(SELECTED_KEY)
    if selected_key == config_id:
        params.pop(SELECTED_KEY, None)
        remaining = load_database_configs(filename)
        if remaining:
            params[SELECTED_KEY] = remaining[0].key
            changed = True

    if changed:
        save_database_params(params, filename)


def update_database_config(config_id: str, name: str, directory: str, filename: str, filename_override: str = DEFAULT_DATABASE_SETTINGS_FILE) -> Optional[DatabaseConfig]:
    params = _load_database_params_for_update(filename_override)
    configs = _collect_database_fields(params)
    if config_id not in configs:
        return None
    safe_name = name.strip()
    safe_directory = os.path.abspath(directory.strip())
    safe_filename = _normalize_filename(filename.strip())
    params[f'{DATABASE_PREFIX}{config_id}.name'] = safe_name
    params[f'{DATABASE_PREFIX}{config_id}.directory'] = safe_directory
    params[f'{DATABASE_PREFIX}{config_id}.filename'] = safe_filename
    save_database_params(params, filename_override)
    return DatabaseConfig(key=config_id, name=safe_name, directory=safe_directory, filename=safe_filename)
