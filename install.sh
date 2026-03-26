#!/usr/bin/env bash

CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
RESET='\033[0m'

REPO_USER="Szabomate1111"
REPO_ZIP="https://github.com/${REPO_USER}/mxtools/archive/refs/heads/main.zip"
INSTALL_DIR="$HOME/.local/share/mxtools"
BIN_DIR="$HOME/.local/bin"
BIN_NAME="mxtools"

echo -e "${CYAN}"
echo " __  __      _              _     "
echo "|  \\/  |    | |            | |    "
echo "| \\  / |_  _| |_ ___   ___ | |___ "
echo "| |\\/| \\ \\/ / __/ _ \\ / _ \\| / __|"
echo "| |  | |>  <| || (_) | (_) | \\__ \\"
echo "|_|  |_/_/\\_\\\\__\\___/ \\___/|_|___/"
echo -e "${RESET}"
echo -e "  Installer — mxtools"
echo ""

_step() { echo -e "  ${CYAN}→${RESET}  $1"; }
_ok()   { echo -e "  ${GREEN}✓${RESET}  $1"; }
_warn() { echo -e "  ${YELLOW}!${RESET}  $1"; }
_fail() { echo -e "  ${RED}✗${RESET}  $1"; exit 1; }

_detect_pm() {
    for pm in apt dnf pacman zypper brew; do
        command -v "$pm" &>/dev/null && echo "$pm" && return
    done
    echo "unknown"
}

_install_pkg() {
    local pkg="$1" pm
    pm=$(_detect_pm)
    _step "Installing: $pkg ($pm)"
    case "$pm" in
        apt)    sudo apt-get install -y "$pkg" ;;
        dnf)    sudo dnf install -y "$pkg" ;;
        pacman) sudo pacman -S --noconfirm "$pkg" ;;
        zypper) sudo zypper install -y "$pkg" ;;
        brew)   brew install "$pkg" ;;
        *)      _fail "Unknown package manager. Install manually: $pkg" ;;
    esac
}

if ! command -v python3 &>/dev/null; then
    _warn "python3 not found, installing..."
    _install_pkg python3 || _fail "Failed to install python3."
fi
PY=$(command -v python3)
PY_VER=$("$PY" -c 'import sys; print(sys.version_info.minor)')
[ "$PY_VER" -lt 8 ] && _fail "Python 3.8+ required. Current: 3.${PY_VER}"
_ok "Python $("$PY" --version 2>&1 | cut -d' ' -f2)"

if ! "$PY" -m pip --version &>/dev/null 2>&1; then
    _warn "pip not found, installing..."
    _install_pkg python3-pip || _fail "Failed to install pip."
fi
_ok "pip available"

for tool in curl unzip; do
    command -v "$tool" &>/dev/null || _install_pkg "$tool"
done

_step "Downloading mxtools..."
TMP_ZIP=$(mktemp /tmp/mxtools_XXXXXX.zip)
curl -fsSL "$REPO_ZIP" -o "$TMP_ZIP" || _fail "Download failed. Check your internet connection."

TMP_DIR=$(mktemp -d /tmp/mxtools_XXXXXX)
unzip -q "$TMP_ZIP" -d "$TMP_DIR"
EXTRACTED=$(find "$TMP_DIR" -mindepth 1 -maxdepth 1 -type d | head -1)

rm -rf "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cp -r "$EXTRACTED/." "$INSTALL_DIR/"
rm -rf "$TMP_ZIP" "$TMP_DIR"
_ok "Installed to: $INSTALL_DIR"

mkdir -p "$BIN_DIR"
cat > "$BIN_DIR/$BIN_NAME" <<EOF
#!/usr/bin/env bash
export PYTHONPATH="$INSTALL_DIR"
exec python3 -m mxtools "\$@"
EOF
chmod +x "$BIN_DIR/$BIN_NAME"
_ok "Launcher: $BIN_DIR/$BIN_NAME"

_add_to_path() {
    local rc="$1" line='export PATH="$HOME/.local/bin:$PATH"'
    grep -q '\.local/bin' "$rc" 2>/dev/null && return
    echo "" >> "$rc"
    echo "$line" >> "$rc"
    _ok "PATH updated: $rc"
}

ADDED_PATH=0
case "$(basename "$SHELL")" in
    bash) [ -f "$HOME/.bashrc"       ] && _add_to_path "$HOME/.bashrc"       && ADDED_PATH=1
          [ -f "$HOME/.bash_profile" ] && _add_to_path "$HOME/.bash_profile" ;;
    zsh)  [ -f "$HOME/.zshrc"        ] && _add_to_path "$HOME/.zshrc"        && ADDED_PATH=1 ;;
    fish) FISH_CFG="$HOME/.config/fish/config.fish"
          mkdir -p "$(dirname "$FISH_CFG")"
          grep -q '\.local/bin' "$FISH_CFG" 2>/dev/null || {
              echo 'fish_add_path $HOME/.local/bin' >> "$FISH_CFG"
              _ok "PATH updated: $FISH_CFG"; ADDED_PATH=1; } ;;
    *)    for rc in "$HOME/.profile" "$HOME/.bashrc"; do
              [ -f "$rc" ] && _add_to_path "$rc" && ADDED_PATH=1 && break
          done ;;
esac

echo ""
_ok "mxtools installed!"
echo ""
echo -e "  Run: ${CYAN}mxtools${RESET}"
[ "$ADDED_PATH" -eq 1 ] && echo -e "  ${YELLOW}!${RESET}  Works immediately in a new terminal.\n     Or: ${CYAN}source ~/.bashrc${RESET}"
echo ""
