"""Experiment setup helpers: logger configuration."""

import os
from pathlib import Path
from typing import Any, NamedTuple

import yaml
from loguru import logger

_FILE_SINKS: dict[str, int] = {}


class ExperimentConfig(NamedTuple):
    """Resources bundled for a notebook experiment run."""

    name: str
    logger: Any
    params: dict | None = None
    optuna: dict | None = None
    data: dict | None = None


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def get_config(name: str, config_path: Path | str | None = None) -> ExperimentConfig:
    """Return logger and config sections for an experiment.

    Accepts either a shared ``config.yml`` or an experiment-specific
    ``config/{name}.yml``.  Paths in the config are resolved relative to the
    notebooks directory (one level above any ``config/`` subdirectory).
    ``NOTEBOOK_OUTPUT_FOLDER`` env var overrides the output directory used for
    the log file sink.
    """
    config_path = Path(config_path) if config_path else Path.cwd() / "config.yml"
    cfg = _load_yaml(config_path)
    # Resolve paths relative to the notebooks dir, not the config subdir.
    base = config_path.parent.parent if config_path.parent.name == "config" else config_path.parent
    sibling = _load_yaml(base / "config" / f"{name}.yml")

    data = cfg.get("data") or sibling.get("data") or {}
    params = cfg.get("params") or sibling.get("params") or {}
    optuna_cfg = cfg.get("optuna") or sibling.get("optuna") or {}

    env_folder = os.environ.get("NOTEBOOK_OUTPUT_FOLDER")
    if env_folder:
        output_dir = Path(env_folder)
    else:
        folder = data.get("output_path", "output")
        output_dir = (base / folder / name).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    log_path = output_dir / "output.log"
    key = str(log_path.resolve())
    if key not in _FILE_SINKS:
        _FILE_SINKS[key] = logger.add(log_path)
    logger.info(f"Writing output to: {output_dir}\nCurrent working directory: {os.getcwd()}")

    return ExperimentConfig(
        name=name,
        logger=logger,
        params=params,
        optuna=optuna_cfg,
        data=data,
    )
