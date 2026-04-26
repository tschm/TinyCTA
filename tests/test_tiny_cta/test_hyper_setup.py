"""Tests for tinycta.hyper._setup: _load_yaml and get_config."""

from __future__ import annotations

import tinycta.hyper._setup as setup_mod
from tinycta.hyper._setup import ExperimentConfig, _load_yaml, get_config


class TestLoadYaml:
    """Tests for the private _load_yaml helper."""

    def test_returns_empty_dict_for_nonexistent_path(self, tmp_path):
        """Returns {} when the path does not exist."""
        assert _load_yaml(tmp_path / "missing.yml") == {}

    def test_parses_valid_yaml(self, tmp_path):
        """Parses a well-formed YAML file into a dict."""
        p = tmp_path / "cfg.yml"
        p.write_text("key: value\n")
        assert _load_yaml(p) == {"key": "value"}

    def test_returns_empty_dict_for_empty_file(self, tmp_path):
        """Returns {} for a YAML file with no content."""
        p = tmp_path / "empty.yml"
        p.write_text("")
        assert _load_yaml(p) == {}


class TestGetConfig:
    """Tests for get_config."""

    def test_default_config_path_uses_cwd(self, tmp_path, monkeypatch):
        """When config_path is None, falls back to cwd/config.yml."""
        monkeypatch.chdir(tmp_path)
        cfg = get_config("exp_cwd")
        assert isinstance(cfg, ExperimentConfig)
        assert cfg.name == "exp_cwd"

    def test_accepts_string_config_path(self, tmp_path):
        """config_path can be given as a str."""
        config_file = tmp_path / "config.yml"
        config_file.write_text("")
        cfg = get_config("exp_str", config_path=str(config_file))
        assert cfg.name == "exp_str"

    def test_base_is_grandparent_when_in_config_subdir(self, tmp_path):
        """Base resolves to grandparent when config_path lives inside a 'config' dir."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / "config.yml"
        config_file.write_text("")
        cfg = get_config("exp_subdir", config_path=config_file)
        assert cfg.name == "exp_subdir"

    def test_sibling_yaml_is_merged(self, tmp_path):
        """Params from a sibling {name}.yml in config/ are loaded."""
        config_file = tmp_path / "config.yml"
        config_file.write_text("")
        sibling_dir = tmp_path / "config"
        sibling_dir.mkdir()
        (sibling_dir / "myexp.yml").write_text("params:\n  fast: 8\n")
        cfg = get_config("myexp", config_path=config_file)
        assert cfg.params == {"fast": 8}

    def test_env_var_overrides_output_dir(self, tmp_path, monkeypatch):
        """NOTEBOOK_OUTPUT_FOLDER env var is used as the output directory."""
        env_dir = tmp_path / "env_out"
        monkeypatch.setenv("NOTEBOOK_OUTPUT_FOLDER", str(env_dir))
        config_file = tmp_path / "config.yml"
        config_file.write_text("")
        get_config("exp_env", config_path=config_file)
        assert env_dir.exists()

    def test_file_sink_not_duplicated_on_repeat_call(self, tmp_path):
        """A second get_config call with the same path reuses the existing sink."""
        config_file = tmp_path / "config.yml"
        config_file.write_text("")
        before = len(setup_mod._FILE_SINKS)
        get_config("sink_exp", config_path=config_file)
        get_config("sink_exp", config_path=config_file)
        assert len(setup_mod._FILE_SINKS) == before + 1

    def test_returns_all_config_sections(self, tmp_path):
        """get_config populates params, optuna, and data from config.yml."""
        config_file = tmp_path / "config.yml"
        config_file.write_text("params:\n  fast: 12\noptuna:\n  n_trials: 5\ndata:\n  output_path: out\n")
        cfg = get_config("full_exp", config_path=config_file)
        assert cfg.params == {"fast": 12}
        assert cfg.optuna == {"n_trials": 5}
        assert cfg.data == {"output_path": "out"}
