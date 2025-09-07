#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EC200M 实时短信接收示例
硬件连接：模块 UART_TXD → PC/RPI UART_RXD
          模块 UART_RXD → PC/RPI UART_TXD
          共地
"""

import serial, re, time

PORT = "/dev/ttyUSB2"   # 在 Windows 改为 COM3 等
BAUD = 115200
TIMEOUT = 0.5

# 短信存储器，防止重复读取
read_index = set()

def send(cmd, wait=0.2):
    """发 AT 并返回响应列表"""
    ser.write((cmd + "\r\n").encode())
    time.sleep(wait)
    lines = []
    while ser.in_waiting:
        lines.append(ser.readline().decode(errors="ignore").strip())
    return lines

def parse_cmt(lines):
    """解析 +CMT 实时文本短信"""
    head = lines[0]
    m = re.match(r'\+CMT: "(\+?\d+)",.*,"(.+)"', head)
    if not m:
        print("[WARN] 无法解析 CMT 头:", head)
        return
    num, ts = m.groups()
    # 剩余行是内容
    text = "\n".join(lines[1:]).strip()
    print("\n[实时文本短信]")
    print("  来自 :", num)
    print("  时间 :", ts)
    print("  内容 :", text)

def parse_cmti(line):
    """解析 +CMTI，读取并删除"""
    m = re.match(r'\+CMTI: "(\w+)",(\d+)', line)
    if not m:
        return
    mem, idx = m.groups()
    idx = int(idx)
    if idx in read_index:
        return
    read_index.add(idx)
    # 读短信
    lines = send(f"AT+CMGR={idx}")
    for l in lines:
        if l.startswith("+CMGR:"):
            print("\n[存储短信]")
            print("  索引 :", idx)
            # 简单打印整行
            print("  原始行:", l)
            # 内容在下一行
            if len(lines) > 1:
                print("  内容 :", lines[1])
            break
    # 删除已读
    send(f"AT+CMGD={idx}")

def main():
    global ser
    ser = serial.Serial(PORT, BAUD, timeout=TIMEOUT)
    print("串口打开:", ser.name)

    # 1. 基本检查
    if not any("OK" in l for l in send("AT")):
        raise RuntimeError("模块未响应")

    # 2. 文本模式 + UTF-8 + 主动上报
    send("AT+CMGF=1")          # 文本
    send('AT+CSCS="UTF-8"')    # 字符集
    send("AT+CNMI=1,2,0,1,0")  # +CMT 实时；+CMTI 存储提示
    print("初始化完成，等待短信...\n")

    buf = ""
    while True:
        if ser.in_waiting:
            chunk = ser.read(ser.in_waiting).decode(errors="ignore")
            buf += chunk
        if "\n" not in buf:
            time.sleep(0.1)
            continue
        line, buf = buf.split("\n", 1)
        line = line.strip()
        if not line:
            continue

        # 实时文本短信
        if line.startswith("+CMT: "):
            # 把剩余行一次性读完
            time.sleep(0.2)
            tail = []
            while ser.in_waiting:
                tail.append(ser.readline().decode(errors="ignore").strip())
            parse_cmt([line] + tail)
            continue

        # 存储短信提示
        if line.startswith("+CMTI: "):
            parse_cmti(line)
            continue

        # 数据短信（DCS=4）示例：11 字节十六进制
        if len(line) == 22 and all(c in "0123456789ABCDEFabcdef" for c in line):
            print("\n[数据短信 11 字节]")
            print("  payload :", line)
            # 这里你可以按自己的协议再解
            continue

        # 其他调试信息可选打印
        # print("[DBG]", line)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n用户中断，退出。")
    finally:
        ser.close()