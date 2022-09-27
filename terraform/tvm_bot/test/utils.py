import pytest
import tvm_bot


def parameterize_named(**kwargs):
    keys = next(iter(kwargs.values())).keys()
    return pytest.mark.parametrize(
        ",".join(keys), [tuple(d.values()) for d in kwargs.values()], ids=kwargs.keys()
    )


def assert_in(needle: str, haystack: str):
    """
    Check that 'needle' is in 'haystack'
    """
    if needle not in haystack:
        raise AssertionError(f"item not found:\n{needle}\nin:\n{haystack}")


def patch_github(monkeypatch, test_data):
    orig_init = tvm_bot.git_utils.GitHubRepo.__init__

    def mock_init(self, *args, **kwargs):
        orig_init(self, *args, **kwargs)
        self.test_data = test_data

    monkeypatch.setattr(tvm_bot.git_utils.GitHubRepo, "__init__", mock_init)
