#!/usr/bin/env bash
set -euo pipefail
echo "Switching default GitHub CLI account to Alef..."
gh auth switch -h github.com -u sushmita-mukherjee-alef
gh auth status -h github.com
