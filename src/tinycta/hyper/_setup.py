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
    params: dict[str, Any] | None = None
    optuna: dict[str, Any] | None = None
    data: dict[str, Any] | None = None


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file, returning an empty dict if the file does not exist."""
    if not path.exists():
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def _resolve_base(config_path: Path) -> Path:
    """Return the notebooks directory that paths are resolved relative to.

    This is the grandparent of ``config_path`` when it lives inside a ``config/``
    subdirectory, otherwise its direct parent.
    """
    return config_path.parent.parent if config_path.parent.name == "config" else config_path.parent


def _merge_sections(
    cfg: dict[str, Any], sibling: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Merge the shared ``config.yml`` with the experiment-specific sibling.

    Each of the ``data``, ``params`` and ``optuna`` sections is taken from
    ``cfg`` when present and truthy, else from ``sibling``, else an empty dict.

    Returns:
        tuple: ``(data, params, optuna)`` section dicts.
    """

    def pick(section: str) -> dict[str, Any]:
        """Return ``section`` from ``cfg`` if truthy, else ``sibling``, else an empty dict."""
        return cfg.get(section) or sibling.get(section) or {}

    return pick("data"), pick("params"), pick("optuna")


def _output_dir(base: Path, data: dict[str, Any], name: str) -> Path:
    """Resolve the experiment output directory and create it.

    ``NOTEBOOK_OUTPUT_FOLDER`` is a deliberate operator override and is used
    verbatim. Otherwise the directory is ``base / output_path / name`` and is
    confined under ``base`` so an untrusted ``output_path`` (e.g. ``../../etc``
    or an absolute path) cannot escape the notebooks directory.

    Raises:
        ValueError: When the config-derived path escapes ``base``.
    """
    env_folder = os.environ.get("NOTEBOOK_OUTPUT_FOLDER")
    if env_folder:
        output_dir = Path(env_folder)
    else:
        folder = data.get("output_path", "output")
        base_resolved = base.resolve()
        output_dir = (base_resolved / folder / name).resolve()
        if not output_dir.is_relative_to(base_resolved):
            msg = f"output_path {folder!r} escapes the notebooks directory {base_resolved}"
            raise ValueError(msg)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _ensure_sink(log_path: Path) -> None:
    """Register a loguru file sink for ``log_path`` once, keyed by its resolved path."""
    key = str(log_path.resolve())
    if key not in _FILE_SINKS:
        _FILE_SINKS[key] = logger.add(log_path)


def get_config(name: str, config_path: Path | str | None = None) -> ExperimentConfig:
    """Return logger and config sections for an experiment.

    Accepts either a shared ``config.yml`` or an experiment-specific
    ``config/{name}.yml``.  Paths in the config are resolved relative to the
    notebooks directory (one level above any ``config/`` subdirectory).
    ``NOTEBOOK_OUTPUT_FOLDER`` env var overrides the output directory used for
    the log file sink; otherwise the config-derived output directory is confined
    under the notebooks directory.
    """
    config_path = Path(config_path) if config_path else Path.cwd() / "config.yml"
    cfg = _load_yaml(config_path)
    base = _resolve_base(config_path)
    sibling = _load_yaml(base / "config" / f"{name}.yml")

    data, params, optuna_cfg = _merge_sections(cfg, sibling)

    output_dir = _output_dir(base, data, name)
    _ensure_sink(output_dir / "output.log")
    logger.info(f"Writing output to: {output_dir}\nCurrent working directory: {os.getcwd()}")

    return ExperimentConfig(
        name=name,
        logger=logger,
        params=params,
        optuna=optuna_cfg,
        data=data,
    )
