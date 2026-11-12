# Security policy

## Reporting a vulnerability

Please do not open a public issue for security problems. Use GitHub's private
reporting: **Security → Report a vulnerability** on this repository.

## What is security-sensitive here

Tenhut blocks sites by rewriting the system hosts file, which needs elevated rights:

- **Linux / macOS:** a small root-owned script (`helper/hosts-helper`) is installed at
  `/usr/local/libexec/tenhut/hosts-helper`, and a sudoers rule lets your user run exactly that file
  without a password. The script only rewrites its own marked block in `/etc/hosts`, validates every
  domain against a strict pattern, and must never import the `tenhut` package or trust environment
  variables, because it runs as root.
- **Windows:** the app asks for administrator rights at launch and writes the hosts file itself.

Changes to the helper, the sudoers rule, or the install flow get extra review. Reports about
privilege escalation through the helper are the most valuable ones.

## Supported versions

Only the latest release receives fixes.
