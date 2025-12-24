import os
import sys

from setuptools import find_packages, setup
from setuptools.command.develop import develop
from setuptools.command.install import install


class PostInstallCommand(install):
    """Post-installation setup for Ollama."""
    def run(self):
        install.run(self)
        # Run Ollama setup after installation
        try:
            import subprocess
            subprocess.run([sys.executable, "scripts/setup_ollama.py"], check=False)
        except Exception as e:
            print(f"⚠️  Ollama setup encountered an issue: {e}")
            print("ℹ️  You can run it manually later with: python scripts/setup_ollama.py")


class PostDevelopCommand(develop):
    """Post-development setup for Ollama."""
    def run(self):
        develop.run(self)
        # Run Ollama setup after development install
        try:
            import subprocess
            subprocess.run([sys.executable, "scripts/setup_ollama.py"], check=False)
        except Exception as e:
            print(f"⚠️  Ollama setup encountered an issue: {e}")
            print("ℹ️  You can run it manually later with: python scripts/setup_ollama.py")


with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

# Try to read requirements from root, fallback to LLM directory
requirements_path = "requirements.txt"
if not os.path.exists(requirements_path):
    requirements_path = os.path.join("LLM", "requirements.txt")

if os.path.exists(requirements_path):
    with open(requirements_path, encoding="utf-8") as fh:
        requirements = [
            line.strip()
            for line in fh
            if line.strip() and not line.startswith("#") and not line.startswith("-r")
        ]
else:
    requirements = ["anthropic>=0.18.0", "openai>=1.0.0", "requests>=2.32.4"]

setup(
    name="cortex-linux",
    version="0.1.0",
    author="Cortex Linux",
    author_email="mike@cortexlinux.com",
    description="AI-powered Linux command interpreter with local LLM support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cortexlinux/cortex",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "cortex=cortex.cli:main",
            "cortex-setup-ollama=scripts.setup_ollama:setup_ollama",
        ],
    },
    cmdclass={
        'install': PostInstallCommand,
        'develop': PostDevelopCommand,
    },
    include_package_data=True,
)

