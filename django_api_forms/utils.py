from importlib import import_module


def resolve_from_path(path: str):
    module_path, class_name = path.rsplit('.', 1)
    module = import_module(module_path)
    return getattr(module, class_name)
