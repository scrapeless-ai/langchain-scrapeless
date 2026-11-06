"""Release preparation tests use temporary metadata and never create tags."""

import importlib.util
from pathlib import Path
from unittest.mock import Mock

import pytest

spec = importlib.util.spec_from_file_location(
    "release_helper", Path(__file__).parents[2] / "scripts" / "release.py"
)
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


@pytest.mark.parametrize("old", ["0.1.3", "0.1.4.dev1", "0.1.4rc1"])
@pytest.mark.parametrize("quote", ['"', "'"])
def test_release_updates_only_poetry_version(tmp_path, monkeypatch, old, quote):
    monkeypatch.chdir(tmp_path)
    metadata = Path("pyproject.toml")
    before = (
        "[tool.poetry]\nname = 'langchain-scrapeless'\n"
        f"version = {quote}{old}{quote} # package version\n\n"
        "[tool.other]\nversion = '7.8.9'\n"
    )
    metadata.write_text(before)
    release.update_pyproject_version("0.1.4")
    assert metadata.read_text() == before.replace(
        f"version = {quote}{old}{quote}", f"version = {quote}0.1.4{quote}"
    )
    release.verify_pyproject_version("0.1.4")


@pytest.mark.parametrize("content", [
    "[tool.other]\nversion = '0.1.3'\n",
    "[tool.poetry]\nname = 'sample'\n",
    "[tool.poetry]\nversion = '0.1.3'\nversion = '0.1.2'\n",
])
def test_missing_or_duplicate_version_stops_before_release_actions(
    tmp_path, monkeypatch, content
):
    monkeypatch.chdir(tmp_path)
    Path("pyproject.toml").write_text(content)
    actions = Mock()
    monkeypatch.setattr(release.subprocess, "run", actions)
    with pytest.raises(ValueError):
        release.main(["0.1.4"])
    actions.assert_not_called()
    assert Path("pyproject.toml").read_text() == content


def test_version_changed_during_changelog_stops_before_commit_and_tag(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    metadata = Path("pyproject.toml")
    metadata.write_text('[tool.poetry]\nversion = "0.1.4.dev1"\n')

    def change_version(_):
        metadata.write_text('[tool.poetry]\nversion = "0.1.3"\n')

    monkeypatch.setattr(release, "generate_changelog", change_version)
    commit = Mock()
    monkeypatch.setattr(release, "git_commit_and_tag", commit)
    with pytest.raises(ValueError, match="does not match"):
        release.main(["0.1.4"])
    commit.assert_not_called()


def test_noop_version_update_stops_before_commit_and_tag(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("pyproject.toml").write_text('[tool.poetry]\nversion = "0.1.4.dev1"\n')
    monkeypatch.setattr(release, "update_pyproject_version", lambda _: None)
    monkeypatch.setattr(release, "generate_changelog", lambda _: None)
    commit = Mock()
    monkeypatch.setattr(release, "git_commit_and_tag", commit)
    with pytest.raises(ValueError, match="does not match"):
        release.main(["0.1.4"])
    commit.assert_not_called()


def test_invalid_version_leaves_metadata_unchanged(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    metadata = Path("pyproject.toml")
    before = '[tool.poetry]\nversion = "0.1.4.dev1"\n'
    metadata.write_text(before)
    with pytest.raises(ValueError):
        release.update_pyproject_version('0.1.4"\nname = "other')
    assert metadata.read_text() == before
