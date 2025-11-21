import importlib.util
import inspect
import os
from types import ModuleType

def load_module_from_path(path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(os.path.basename(path), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def get_defined_classes(path: str) -> list[type]:
    module = load_module_from_path(path)
    classes = []

    for name, obj in inspect.getmembers(module, inspect.isclass):
        # Vérifie que la classe est définie dans ce fichier (pas importée)
        if obj.__module__ == module.__name__:
            classes.append(obj)

    # Tri alphabétique par nom de classe
    classes.sort(key=lambda c: c.__name__)
    return classes

class test:
    pass

if __name__ == "__main__":
    classes = get_defined_classes("client/packet/clientbound.py")
    print(classes)