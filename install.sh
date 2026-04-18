#!/usr/bin/env bash
# Debriefeur — One-Command Installer
#
# Usage:
#   pip install debriefeur
#
# Or from source:
#   curl -fsSL https://raw.githubusercontent.com/aigenteur/debrief/main/install.sh | bash

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'
BOLD='\033[1m'

echo -e "${PURPLE}${BOLD}"
echo "  ╔═══════════════════════════════════════╗"
echo "  ║       Debriefeur Installer     ║"
echo "  ║   Expertise → Agent Configuration     ║"
echo "  ╚═══════════════════════════════════════╝"
echo -e "${NC}"

# Check Python
if command -v python3 >/dev/null 2>&1; then
    PY=python3
elif command -v python >/dev/null 2>&1; then
    PY=python
else
    echo -e "${RED}❌ Python 3.11+ is required.${NC}"
    echo "   Install: https://www.python.org/downloads/"
    exit 1
fi

PY_VERSION=$($PY --version 2>&1 | grep -oP '\d+\.\d+')
echo -e "${GREEN}✅${NC} Python ${PY_VERSION} found"

# Check pip
if ! $PY -m pip --version >/dev/null 2>&1; then
    echo -e "${RED}❌ pip not found. Install: $PY -m ensurepip${NC}"
    exit 1
fi

# Install
echo ""
echo -e "${BLUE}Installing Debriefeur...${NC}"

if [ -d ".git" ] && [ -f "pyproject.toml" ]; then
    # Installing from cloned repo
    $PY -m pip install -e ".[dev]"
else
    # Installing from PyPI (or git)
    $PY -m pip install debriefeur
fi

echo ""
echo -e "${GREEN}${BOLD}✅ Debriefeur installed!${NC}"
echo ""
echo -e "  ${BOLD}Quick start:${NC}"
echo -e "    ${BLUE}debriefeur setup${NC}     Configure your LLM provider"
echo -e "    ${BLUE}debrief${NC}           Start your first interview"
echo ""
echo -e "  ${BOLD}After interview:${NC}"
echo -e "    ${BLUE}debriefeur export <id> --framework openclaw${NC}"
echo -e "    ${BLUE}debriefeur export <id> --framework hermes${NC}"
echo ""
echo -e "  ${PURPLE}Community → https://skool.com/aigenteur${NC}"
echo ""
