import quansyn
from quansyn.depval import DepValAnalyzer, analyze, convert, getDepValFeatures
from quansyn.lawfitter import fit
from quansyn.lingnet import conllu2edge, load_edges


def test_package_imports():
    assert hasattr(quansyn, "__all__")
    assert "depval" in quansyn.__all__


def test_public_api_symbols():
    assert callable(getDepValFeatures)
    assert callable(analyze)
    assert callable(convert)
    assert callable(conllu2edge)
    assert callable(load_edges)
    assert callable(fit)
    assert DepValAnalyzer is not None
