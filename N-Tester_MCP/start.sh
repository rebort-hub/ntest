#!/bin/bash
# N-Tester MCP 主启动脚本
# 调用 scripts/start/start-enhanced.sh

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

bash scripts/start/start-enhanced.sh
