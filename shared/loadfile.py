import importlib.util
import inspect
import os
import sys
from types import ModuleType

#> can be import without loop import

def _project_root() -> str:
    # racine du projet : parent du dossier 'shared'
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

def _module_name_for_path(path: str, project_root: str) -> str:
    try:
        rel = os.path.relpath(os.path.abspath(path), project_root)
    except Exception:
        rel = os.path.basename(path)
    if rel.startswith(".."):
        # hors projet : utiliser basename
        name = os.path.splitext(os.path.basename(path))[0]
    else:
        name = os.path.splitext(rel)[0].replace(os.sep, ".")
    return name

def load_module_from_path(path: str) -> ModuleType:
    """
    Charge et exécute le module depuis path en essayant de rajouter la racine
    du projet dans sys.path pour permettre la résolution des imports locaux/relatifs.
    Tente d'abord importlib.import_module(module_name). Si ça échoue, fallback
    sur spec_from_file_location en pré-créant les paquets parents dans sys.modules.
    """
    path = os.path.abspath(path)
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    project_root = _project_root()
    module_name = _module_name_for_path(path, project_root)

    added_project_root = False
    if project_root and project_root not in sys.path:
        sys.path.insert(0, project_root)
        added_project_root = True

    try:
        try:
            return importlib.import_module(module_name)
        except Exception:
            pass

        parts = module_name.split(".")
        for i in range(len(parts) - 1):
            pkg_name = ".".join(parts[: i + 1])
            if pkg_name not in sys.modules:
                pkg = ModuleType(pkg_name)
                pkg.__path__ = [os.path.join(project_root, *parts[: i + 1])]
                pkg.__package__ = pkg_name
                sys.modules[pkg_name] = pkg

        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        module.__package__ = module_name.rpartition(".")[0]
        spec.loader.exec_module(module)
        sys.modules[module_name] = module
        return module
    finally:
        if added_project_root:
            try:
                sys.path.remove(project_root)
            except ValueError:
                pass

def get_defined_classes(path: str) -> list[type]:
    """
    Tente d'importer/exécuter le module pour récupérer les vraies classes.
    Si l'import échoue, une exception est levée (pas de fallback sur classes factices).
    """
    module = load_module_from_path(path)  # laisser lever FileNotFoundError / ImportError
    classes = []
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if getattr(obj, "__module__", None) == module.__name__:
            classes.append(obj)
    classes.sort(key=lambda c: c.__name__)
    return classes