#!/usr/bin/env python3
"""
Post-installation setup script for Cortex Linux.
Automatically installs and configures Ollama for local LLM support.

Author: Cortex Linux Team
License: Apache 2.0
"""

import logging
import os
import shutil
import subprocess
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_ollama_installed() -> bool:
    """Check if Ollama is already installed."""
    return shutil.which("ollama") is not None


def install_ollama() -> bool:
    """
    Install Ollama using the official installation script.
    
    Returns:
        True if installation succeeded, False otherwise
    """
    if is_ollama_installed():
        logger.info("✅ Ollama already installed")
        return True

    logger.info("📦 Installing Ollama for local LLM support...")
    logger.info("   This enables privacy-first, offline package management")
    
    try:
        # Download installation script
        logger.info("   Downloading Ollama installer...")
        result = subprocess.run(
            ["curl", "-fsSL", "https://ollama.com/install.sh"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        
        if result.returncode != 0:
            logger.error(f"❌ Failed to download Ollama installer: {result.stderr}")
            return False

        # Execute installation script
        logger.info("   Running Ollama installer...")
        install_result = subprocess.run(
            ["sh", "-c", result.stdout],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if install_result.returncode == 0:
            logger.info("✅ Ollama installed successfully")
            return True
        else:
            logger.warning(f"⚠️  Ollama installation encountered issues: {install_result.stderr}")
            # Don't fail the entire setup if Ollama fails
            return False

    except subprocess.TimeoutExpired:
        logger.warning("⚠️  Ollama installation timed out")
        return False
    except Exception as e:
        logger.warning(f"⚠️  Ollama installation failed: {e}")
        return False


def start_ollama_service() -> bool:
    """
    Start the Ollama service.
    
    Returns:
        True if service started, False otherwise
    """
    if not is_ollama_installed():
        return False

    logger.info("🚀 Starting Ollama service...")
    
    try:
        # Start Ollama in background
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        
        # Give it a moment to start
        time.sleep(2)
        logger.info("✅ Ollama service started")
        return True

    except Exception as e:
        logger.warning(f"⚠️  Failed to start Ollama service: {e}")
        return False


def pull_default_model() -> bool:
    """
    Pull a lightweight default model for Cortex.
    
    Returns:
        True if model pulled successfully, False otherwise
    """
    if not is_ollama_installed():
        return False

    logger.info("📥 Pulling default model (phi3:mini) - this may take a few minutes...")
    logger.info("   You can skip this and it will auto-download on first use")
    
    try:
        result = subprocess.run(
            ["ollama", "pull", "phi3:mini"],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes for model download
        )
        
        if result.returncode == 0:
            logger.info("✅ Default model ready")
            return True
        else:
            logger.warning("⚠️  Model pull failed, will auto-download on first use")
            return False

    except subprocess.TimeoutExpired:
        logger.warning("⚠️  Model download timed out, will auto-download on first use")
        return False
    except Exception as e:
        logger.warning(f"⚠️  Model pull failed: {e}")
        return False


def setup_ollama():
    """Main setup function for Ollama integration."""
    logger.info("=" * 60)
    logger.info("Cortex Linux - Setting up local LLM support")
    logger.info("=" * 60)
    
    # Check if we should skip Ollama setup
    if os.getenv("CORTEX_SKIP_OLLAMA_SETUP") == "1":
        logger.info("⏭️  Skipping Ollama setup (CORTEX_SKIP_OLLAMA_SETUP=1)")
        return
    
    # Check if running in CI/automated environment
    if os.getenv("CI") or os.getenv("GITHUB_ACTIONS"):
        logger.info("⏭️  Skipping Ollama setup in CI environment")
        return

    # Install Ollama
    if not install_ollama():
        logger.warning("⚠️  Ollama installation skipped")
        logger.info("ℹ️  You can install it later with: curl -fsSL https://ollama.com/install.sh | sh")
        logger.info("ℹ️  Cortex will fall back to cloud providers (Claude/OpenAI) if configured")
        return

    # Start service
    if not start_ollama_service():
        logger.info("ℹ️  Ollama service will start automatically on first use")
        return

    # Pull default model (optional, non-blocking)
    logger.info("ℹ️  Pulling default model (optional)...")
    pull_default_model()
    
    logger.info("=" * 60)
    logger.info("✅ Cortex Linux setup complete!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Quick Start:")
    logger.info("  1. Run: cortex install nginx --dry-run")
    logger.info("  2. No API keys needed - uses local Ollama by default")
    logger.info("  3. Optional: Set ANTHROPIC_API_KEY or OPENAI_API_KEY for cloud fallback")
    logger.info("")


if __name__ == "__main__":
    setup_ollama()
