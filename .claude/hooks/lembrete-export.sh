#!/usr/bin/env bash
# Hook PostToolUse (Bash) do Claude Code: depois de um "git commit" feito pelo Claude,
# mostra ao usuário o mesmo lembrete de export do .githooks/post-commit.
# Só lê: não exporta, não cria commits, não altera arquivos.
input=$(cat)
cmd=$(jq -r '.tool_input.command // ""' <<<"$input" 2>/dev/null)

# Só reage a comandos que contenham um git commit
grep -qE '(^|[;&|(]|[[:space:]])git([[:space:]]+-C[[:space:]]+[^[:space:]]+)?[[:space:]]+commit([[:space:]]|$)' <<<"$cmd" || exit 0

root=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0

# Commit bloqueado por hook não cria commit: só avisa se o HEAD é recente
head_ts=$(git -C "$root" log -1 --format=%ct 2>/dev/null) || exit 0
[ $(( $(date +%s) - head_ts )) -le 300 ] || exit 0

"$root/.githooks/post-commit" --json
exit 0
