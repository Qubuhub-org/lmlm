#!/usr/bin/env sh
set -eu

if [ -z "${KAGGLE_API_TOKEN:-}" ]; then
  echo "Set KAGGLE_API_TOKEN in your environment before running this script." >&2
  exit 1
fi

umask 077
mkdir -p "$HOME/.kaggle"
printf '%s' "$KAGGLE_API_TOKEN" > "$HOME/.kaggle/access_token"
chmod 600 "$HOME/.kaggle/access_token"
echo "Kaggle token saved with owner-only permissions."
