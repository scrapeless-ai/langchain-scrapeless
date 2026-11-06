import sys
import re
from pathlib import Path
import subprocess


def poetry_version_match(content: str):
    """Locate exactly one quoted version in the Poetry metadata table."""
    tables = list(re.finditer(
        r"(?ms)^\[tool\.poetry\][ \t]*\n(?P<body>.*?)(?=^\[|\Z)", content
    ))
    if len(tables) != 1:
        raise ValueError("Expected exactly one [tool.poetry] table.")
    table = tables[0]
    matches = list(re.finditer(
        r'''(?m)^[ \t]*version[ \t]*=[ \t]*(["'])(?P<version>[^"'\n]+)\1[ \t]*(?:\#.*)?$''',
        table.group("body"),
    ))
    if len(matches) != 1:
        raise ValueError("Expected exactly one quoted Poetry version.")
    match = matches[0]
    return (
        table.start("body") + match.start("version"),
        table.start("body") + match.end("version"),
        match.group("version"),
    )


def verify_pyproject_version(expected_version: str):
    """Stop release preparation if the package version does not match."""
    _, _, actual = poetry_version_match(Path("pyproject.toml").read_text())
    if actual != expected_version:
        raise ValueError("Package version does not match the requested release version.")


def update_pyproject_version(new_version: str):
    if not re.fullmatch(
        r"[0-9]+\.[0-9]+\.[0-9]+(?:(?:a|b|rc)[0-9]+)?"
        r"(?:\.post[0-9]+)?(?:\.dev[0-9]+)?", new_version
    ):
        raise ValueError("Enter a numeric release, prerelease, or development version.")
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()
    start, end, _ = poetry_version_match(content)

    updated_content = content[:start] + new_version + content[end:]
    pyproject_path.write_text(updated_content)
    verify_pyproject_version(new_version)
    print(f"✅ Updated pyproject.toml to version {new_version}")


def generate_changelog(version: str):
    print("📝 Generating CHANGELOG.md...")
    try:
        subprocess.run(
            [
                "npx",
                "standard-version",
                "--release-as",
                version,
                "--tag-prefix",
                "",
                "--skip.tag",
                "--skip.commit",
            ],
            check=True,
        )
        print("✅ CHANGELOG.md generated")
    except subprocess.CalledProcessError:
        print("❌ Failed to generate changelog")
        sys.exit(1)


def git_commit_and_tag(new_version: str):
    print("📦 Committing and tagging release...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"chore(release): v{new_version}"], check=True
        )
        subprocess.run(["git", "tag", f"v{new_version}"], check=True)
        print(f"🏷️  Git tag v{new_version} created")
    except subprocess.CalledProcessError:
        print("❌ Git commit/tag failed")
        sys.exit(1)


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        raise SystemExit("Usage: python release.py <new_version>")
    new_version = args[0]
    update_pyproject_version(new_version)
    generate_changelog(new_version)
    verify_pyproject_version(new_version)
    git_commit_and_tag(new_version)


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        raise SystemExit(str(error))
