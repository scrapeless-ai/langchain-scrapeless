import sys
import re
from pathlib import Path
import subprocess


def update_pyproject_version(new_version: str):
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()

    updated_content = re.sub(
        r'version\s*=\s*"[0-9]+\.[0-9]+\.[0-9]+"',
        f'version = "{new_version}"',
        content,
    )
    pyproject_path.write_text(updated_content)
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


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python release.py <new_version>")
        sys.exit(1)

    new_version = sys.argv[1]

    update_pyproject_version(new_version)
    generate_changelog(new_version)
    git_commit_and_tag(new_version)
