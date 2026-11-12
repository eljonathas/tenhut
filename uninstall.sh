#!/usr/bin/env bash
# Remove o bloqueio do /etc/hosts, o helper e a regra sudo (Linux e macOS).  sudo ./uninstall.sh
set -euo pipefail
if [[ $EUID -ne 0 ]]; then
  echo "Rode com sudo: sudo ./uninstall.sh" >&2
  exit 1
fi
for NAME in tenhut general-foco; do  # general-foco = nome antigo
  HELPER=/usr/local/libexec/$NAME/hosts-helper
  [[ -x "$HELPER" ]] && "$HELPER" clear || true
  rm -f "/etc/sudoers.d/$NAME" "$HELPER"
  rmdir "/usr/local/libexec/$NAME" 2>/dev/null || true
done
if [[ -n "${SUDO_USER:-}" ]]; then
  if command -v getent >/dev/null 2>&1; then
    USER_HOME="$(getent passwd "$SUDO_USER" | cut -d: -f6)"
  else
    USER_HOME="$(dscl . -read "/Users/$SUDO_USER" NFSHomeDirectory | awk '{print $2}')"
  fi
  rm -f "$USER_HOME/.local/share/applications/general-foco.desktop" "$USER_HOME/.local/share/applications/tenhut.desktop"
  rm -f "$USER_HOME"/.local/share/icons/hicolor/*/apps/tenhut.png
fi
echo "Tenhut desinstalado. (config e estado do usuário ficam em ~/.config/tenhut, ~/.local/state/tenhut e ~/.local/share/tenhut)"
