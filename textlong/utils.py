import re
import os
import hashlib
from typing import List, Union, Any
from langchain_core.documents import Document
from .config import get_env

def raise_not_install(packages):
    print(f"please install package: '{packages}' with pip or poetry")
    # auto install package
    # subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

def raise_not_supply_all(info: str, *args):
    if all(arg is None for arg in args):
        raise ValueError(info)

def extract_text(resp_md: str, start_marker: str=None, end_marker: str=None):
    """
    如果指定开始和结束的标记，就提取标记中间的文本，并移除标记所在的行。
    一旦文本出现Markdown标题（若干个#开头的行），之后的内容就都不要进行start_marker匹配。
    """
    if start_marker and end_marker:
        start_lines = resp_md.split('\n')
        # 查找第一个Markdown标题的索引
        markdown_title_index = next((i for i, line in enumerate(start_lines) if line.strip().startswith('#')), len(start_lines))
        
        # 在第一个Markdown标题之前查找start_marker
        start_index = next((i for i, line in enumerate(start_lines[:markdown_title_index]) if start_marker in line), None)
        end_index = next((i for i, line in enumerate(reversed(start_lines), 1) if end_marker in line), None)

        if start_index is not None and end_index is not None and start_index < len(start_lines) - end_index:
            return '\n'.join(start_lines[start_index+1:len(start_lines)-end_index]).strip()

    return resp_md

def hash_text(text):
    text_bytes = text.encode('utf-8')
    hash_object = hashlib.md5(text_bytes)
    return hash_object.hexdigest()

def clean_filename(filename: str):
    """
    先将除字母、数字、中文、下划线和短横线之外的字符替换为下划线;
    再将多个连续的下划线或短横线替换为单个下划线。
    """
    cleaned_filename = re.sub(r'[^\w\s-]', '_', filename)
    cleaned_filename = re.sub(r'[-_ ]+', '_', cleaned_filename)
    return cleaned_filename

def safety_path(path: str):
    return os.path.normpath(re.sub(r"\.\.+", ".", path)) if path else ''

def compress_text(text: str, start_limit: int=100, end_limit: int=100, delta: int=50) -> str:
    """
    压缩文本，如果文本长度超过指定限制，则只保留前后部分，并用省略号连接。
    """
    if len(text) <= start_limit + end_limit + delta:
        # 如果文本长度小于或等于前后限制之和，则直接返回原文本
        return text
    else:
        # 否则，保留前后部分并用省略号连接
        return text[:start_limit] + f"\n...(省略{len(text)-start_limit-end_limit}字)\n" + text[-end_limit:]

def stream_log(call, *args, **kwargs):
    """
    打印流式日志。
    """

    output_text = ""
    last_block_type = ""

    for block in call(*args, **kwargs):
        if block.block_type in ['text', 'final', 'front_matter']:
            output_text += block.text

        if block.block_type in ['chunk']:
            print(block.text_with_print_color, end="")
            last_block_type = block.block_type

        if block.block_type in ['info', 'warn', 'text']:
            if last_block_type == "chunk":
                print("\n")
                last_block_type = ""
            print(f'>-[{block.block_type.upper()}]>> {block.text_with_print_color}')
            last_block_type = block.block_type
    
    if last_block_type == "chunk":
        print("\n")
        last_block_type = ""

    # 生成哈希值
    # 移除前后空格以确保唯一性
    trimmed_output_text = output_text.strip()
    hash_object = hashlib.sha256(trimmed_output_text.encode())
    hash_hex = hash_object.hexdigest()  # 获取十六进制哈希值
    # 转换为8位数字哈希值
    hash_code = int(hash_hex, 16) % (10 ** 8)  # 取模运算得到8位数字

    tail = f'>-[END]>> 【{get_env("TEXTLONG_AIGC_INFO_DECLARE")}，{get_env("TEXTLONG_AIGC_INFO_CHK")} {hash_code}】'
    print(tail)
    
    return output_text
