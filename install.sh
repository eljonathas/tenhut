#!/usr/bin/env bash
# Instala o helper root do Tenhut e a regra sudo que permite ao app (sem senha)
# reescrever APENAS o bloco "tenhut" do /etc/hosts. Linux e macOS.
# (Quem usa o app empacotado pode fazer o mesmo pelo botão CONFIG > INSTALAR BLOCK
#  ou por `tenhut --install-helper`.)
#
#   sudo ./install.sh
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "Rode com sudo: sudo ./install.sh" >&2
  exit 1
fi
USER_NAME="${SUDO_USER:-}"
if [[ -z "$USER_NAME" || "$USER_NAME" == "root" ]]; then
  echo "Rode via sudo a partir do seu usuário (SUDO_USER vazio)." >&2
  exit 1
fi

if [[ "$(uname -s)" == "Darwin" ]]; then GROUP=wheel; else GROUP=root; fi
if [[ ! "$USER_NAME" =~ ^[a-z_][a-z0-9_-]*\$?$ ]]; then
  echo "Nome de usuário não suportado: $USER_NAME" >&2
  exit 1
fi

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HELPER=/usr/local/libexec/tenhut/hosts-helper
SUDOERS=/etc/sudoers.d/tenhut

# versão antiga (general-foco): remove o helper e a regra sudo de antes
rm -f /etc/sudoers.d/general-foco /usr/local/libexec/general-foco/hosts-helper
rmdir /usr/local/libexec/general-foco 2>/dev/null || true

install -d -o root -g "$GROUP" -m 0755 /usr/local/libexec/tenhut
install -o root -g "$GROUP" -m 0755 "$HERE/helper/hosts-helper" "$HELPER"

TMP="$(mktemp /tmp/tenhut-sudoers.XXXXXX)"
echo "$USER_NAME ALL=(root) NOPASSWD: $HELPER" > "$TMP"
visudo -cf "$TMP" >/dev/null
install -o root -g "$GROUP" -m 0440 "$TMP" "$SUDOERS"
rm -f "$TMP"

# ícone + atalho no menu de aplicativos (instalados para o usuário, sem root)
if command -v getent >/dev/null 2>&1; then
  USER_HOME="$(getent passwd "$USER_NAME" | cut -d: -f6)"
else
  USER_HOME="$(dscl . -read "/Users/$USER_NAME" NFSHomeDirectory | awk '{print $2}')"
fi
UV="$(sudo -u "$USER_NAME" -H bash -lc 'command -v uv' || true)"
UV="${UV:-$USER_HOME/.local/bin/uv}"
sudo -u "$USER_NAME" -H "$UV" sync --inexact --project "$HERE" --quiet  # --inexact: não desinstala o extra da câmera
sudo -u "$USER_NAME" -H "$UV" run --project "$HERE" tenhut --install-desktop >/dev/null

echo "OK: helper em $HELPER, regra em $SUDOERS; Tenhut instalado no menu de aplicativos"
echo "Teste: sudo -n $HELPER status"
