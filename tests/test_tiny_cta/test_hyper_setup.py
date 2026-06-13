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


class TestExperimentConfigDefaults:
    """The optional config sections default to None on the NamedTuple."""

    def test_optional_sections_default_to_none(self):
        """params, optuna and data default to None (not an empty string)."""
        cfg = ExperimentConfig(name="x", logger=None)
        assert cfg.params is None
        assert cfg.optuna is None
        assert cfg.data is None


class TestGetConfigMutationKills:
    """Pin the exact paths, filenames and side effects of get_config."""

    def test_default_filename_is_config_yml(self, tmp_path, monkeypatch):
        """With no config_path, get_config reads ``config.yml`` from the cwd."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "config.yml").write_text("params:\n  fast: 7\n")
        cfg = get_config("exp_default_name")
        assert cfg.params == {"fast": 7}

    def test_base_is_grandparent_loads_sibling_in_config_dir(self, tmp_path):
        """When config_path is inside a 'config' dir, the sibling resolves via the grandparent."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "config.yml").write_text("")
        (config_dir / "myexp.yml").write_text("params:\n  fast: 21\n")
        cfg = get_config("myexp", config_path=config_dir / "config.yml")
        assert cfg.params == {"fast": 21}

    def test_sibling_data_and_optuna_are_merged(self, tmp_path):
        """Data and optuna fall back to the sibling file when absent from config.yml."""
        (tmp_path / "config.yml").write_text("")
        sibling_dir = tmp_path / "config"
        sibling_dir.mkdir()
        (sibling_dir / "sib.yml").write_text("data:\n  output_path: out\noptuna:\n  n_trials: 9\n")
        cfg = get_config("sib", config_path=tmp_path / "config.yml")
        assert cfg.data == {"output_path": "out"}
        assert cfg.optuna == {"n_trials": 9}

    def test_output_path_from_data_is_used(self, tmp_path, monkeypatch):
        """Without the env override, the output folder comes from data['output_path']."""
        monkeypatch.delenv("NOTEBOOK_OUTPUT_FOLDER", raising=False)
        (tmp_path / "config.yml").write_text("data:\n  output_path: custom_out\n")
        get_config("exp_op", config_path=tmp_path / "config.yml")
        assert (tmp_path / "custom_out" / "exp_op").is_dir()

    def test_output_path_defaults_to_output(self, tmp_path, monkeypatch):
        """When data has no output_path, the folder defaults to 'output'."""
        monkeypatch.delenv("NOTEBOOK_OUTPUT_FOLDER", raising=False)
        (tmp_path / "config.yml").write_text("")
        get_config("exp_defout", config_path=tmp_path / "config.yml")
        assert (tmp_path / "output" / "exp_defout").is_dir()

    def test_log_file_is_named_output_log_with_real_sink(self, tmp_path, monkeypatch):
        """A real loguru sink is registered and writes to ``output.log``."""
        monkeypatch.delenv("NOTEBOOK_OUTPUT_FOLDER", raising=False)
        (tmp_path / "config.yml").write_text("")
        get_config("exp_log", config_path=tmp_path / "config.yml")
        log_path = tmp_path / "output" / "exp_log" / "output.log"
        assert log_path.exists()
        key = str(log_path.resolve())
        assert isinstance(setup_mod._FILE_SINKS[key], int)  # logger.add returned a sink id, not None
        content = log_path.read_text()
        assert " - Writing output to:" in content  # message is not wrapped/altered
