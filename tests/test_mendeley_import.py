import os
import sys
import types
import importlib
import django

# Ensure repo root is on sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PaperMetrics.settings')


def test_mendeley_import(monkeypatch):
    dummy = types.ModuleType('mendeley')
    session_mod = types.ModuleType('mendeley.session')
    dummy.Mendeley = object
    session_mod.MendeleySession = object
    dummy.session = session_mod
    monkeypatch.setitem(sys.modules, 'mendeley', dummy)
    monkeypatch.setitem(sys.modules, 'mendeley.session', session_mod)
    django.setup()
    importlib.reload(importlib.import_module('api.views'))
    importlib.reload(importlib.import_module('frontend.views'))
