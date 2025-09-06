# 嵌入式Linux软件框架

## 项目结构
- `src/`：C语言主程序及模块
- `go_mod/`：Go语言模块示例
- `python_mod/`：Python模块示例
- `.github/`：Copilot instructions

## 快速开始
1. 构建C主程序：`make -C src`
2. 运行Go模块：`go run go_mod/main.go`
3. 运行Python模块：`python3 python_mod/main.py`

## 依赖
- GCC (C编译器)
- Go 1.18+
- Python 3.7+

## 说明
本框架适合嵌入式Linux环境，支持多语言扩展。
