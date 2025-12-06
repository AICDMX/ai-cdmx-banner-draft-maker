.PHONY: help install run clean lint format check test dev requirements verify-gimp all

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)GIMP Banner Generator - Makefile Commands$(NC)"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Prerequisites:$(NC)"
	@echo "  - Python 3.8+ (usually pre-installed)"
	@echo "  - GIMP 2.10+ must be installed"
	@echo "  - tkinter (usually included with Python)"
	@echo ""

install: ## Verify Python, GIMP, and tkinter are installed
	@echo "$(BLUE)Checking prerequisites...$(NC)"
	@command -v python3 >/dev/null 2>&1 || { \
		echo "$(RED)✗ Python 3 not found!$(NC)"; \
		echo "$(YELLOW)Install Python 3 with:$(NC)"; \
		echo "  Arch Linux: sudo pacman -S python"; \
		echo "  Ubuntu/Debian: sudo apt install python3"; \
		exit 1; \
	}
	@echo "$(GREEN)✓ Python found:$(NC) $$(python3 --version)"
	@python3 -c "import tkinter" 2>/dev/null || { \
		echo "$(RED)✗ tkinter not available!$(NC)"; \
		echo "$(YELLOW)Install tkinter with:$(NC)"; \
		echo "  Arch Linux: sudo pacman -S tk"; \
		echo "  Ubuntu/Debian: sudo apt install python3-tk"; \
		exit 1; \
	}
	@echo "$(GREEN)✓ tkinter available$(NC)"
	@command -v gimp >/dev/null 2>&1 || { \
		echo "$(RED)✗ GIMP not found!$(NC)"; \
		echo "$(YELLOW)Install GIMP with:$(NC)"; \
		echo "  Arch Linux: sudo pacman -S gimp"; \
		echo "  Ubuntu/Debian: sudo apt install gimp"; \
		exit 1; \
	}
	@echo "$(GREEN)✓ GIMP found:$(NC) $$(gimp --version)"
	@echo "$(GREEN)✓ All prerequisites met!$(NC)"

verify-gimp: ## Verify GIMP is installed and available
	@echo "$(BLUE)Checking for GIMP...$(NC)"
	@command -v gimp >/dev/null 2>&1 || { \
		echo "$(RED)✗ GIMP not found!$(NC)"; \
		echo "$(YELLOW)Install GIMP with:$(NC)"; \
		echo "  Arch Linux: sudo pacman -S gimp"; \
		echo "  Ubuntu/Debian: sudo apt install gimp"; \
		exit 1; \
	}
	@echo "$(GREEN)✓ GIMP found:$(NC) $$(gimp --version)"

verify-tkinter: ## Verify tkinter is available
	@echo "$(BLUE)Checking for tkinter...$(NC)"
	@python3 -c "import tkinter" 2>/dev/null || { \
		echo "$(RED)✗ tkinter not available!$(NC)"; \
		echo "$(YELLOW)Install tkinter with:$(NC)"; \
		echo "  Arch Linux: sudo pacman -S tk"; \
		echo "  Ubuntu/Debian: sudo apt install python3-tk"; \
		exit 1; \
	}
	@echo "$(GREEN)✓ tkinter available$(NC)"

run: verify-gimp verify-tkinter ## Run the banner GUI application
	@echo "$(BLUE)Starting Banner Generator GUI...$(NC)"
	@python3 banner_gui.py

run-auto: verify-gimp ## Run automatically using saved configuration (no GUI, no popups)
	@echo "$(BLUE)Running banner generation automatically...$(NC)"
	@python3 banner_gui.py --auto

dev: verify-gimp verify-tkinter ## Run in development mode (same as run for now)
	@echo "$(BLUE)Starting Banner Generator GUI (dev mode)...$(NC)"
	@python3 banner_gui.py

clean: ## Remove generated files and cache
	@echo "$(BLUE)Cleaning up...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

lint: ## Run linting checks (placeholder - add linter if needed)
	@echo "$(YELLOW)No linter configured yet$(NC)"
	@echo "Consider adding: ruff, pylint, or flake8"

format: ## Format code (placeholder - add formatter if needed)
	@echo "$(YELLOW)No formatter configured yet$(NC)"
	@echo "Consider adding: black or ruff format"

check: verify-gimp verify-tkinter ## Check if everything is set up correctly
	@echo "$(BLUE)Running system checks...$(NC)"
	@echo "$(GREEN)✓ Python:$(NC) $$(python3 --version)"
	@echo "$(GREEN)✓ tkinter:$(NC) Available"
	@echo "$(GREEN)✓ GIMP:$(NC) $$(gimp --version)"
	@echo ""
	@echo "$(GREEN)All checks passed! Ready to generate banners.$(NC)"

requirements: ## Show project requirements and setup info
	@echo "$(BLUE)Project Requirements:$(NC)"
	@echo ""
	@echo "$(GREEN)Runtime Requirements:$(NC)"
	@echo "  - Python 3.8+"
	@echo "  - tkinter (Arch: sudo pacman -S tk, Ubuntu: sudo apt install python3-tk)"
	@echo "  - GIMP 2.10+"
	@echo ""
	@echo "$(GREEN)Template Requirements:$(NC)"
	@echo "  - Text layers: Title1, Title2, SpeakerName, SpeakerTitle, Date, Time"
	@echo "  - Photo placeholder: SpeakerPhoto layer"
	@echo ""
	@echo "See TEMPLATE_REQUIREMENTS.md for full details"

all: install verify-gimp check ## Verify everything is set up correctly
	@echo ""
	@echo "$(GREEN)✓ Setup complete! You're ready to go.$(NC)"
	@echo ""
	@echo "$(BLUE)Next steps:$(NC)"
	@echo "  1. Run: make run"
	@echo "  2. Select your template directory"
	@echo "  3. Fill in event details"
	@echo "  4. Generate banners!"
	@echo ""
	@echo "For more info: make help"

test: ## Run tests (placeholder for future testing)
	@echo "$(YELLOW)No tests configured yet$(NC)"
	@echo "Consider adding pytest for testing"

# Aliases for common tasks
setup: all ## Alias for 'all' - full setup
start: run ## Alias for 'run'

