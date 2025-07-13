import ast
import importlib
import os
import shutil
import subprocess
import tempfile
import sys

def estimate_timeout(code):
    """
    根据代码复杂度动态计算超时时间，优化简单语句和重复语句的权重
    """
    try:
        # 解析代码为 AST（抽象语法树）
        tree = ast.parse(code)

        # 基础时间和权重
        base_timeout = 5  # 基础超时时间
        statement_weight = 0.5  # 默认语句权重
        simple_call_weight = 0.1  # 简单函数调用权重
        loop_weight = 2  # 循环结构权重
        total_complexity = base_timeout

        # 定义常见简单函数集合
        simple_functions = {
            "print",
            "len",
            "input",
            "range",
            "str",
            "int",
            "float",
            "bool",
            "list",
            "dict",
            "set",
            "tuple",
        }

        # 遍历 AST，计算复杂度
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                total_complexity += loop_weight
            elif isinstance(node, (ast.If, ast.FunctionDef)):
                total_complexity += statement_weight
            elif isinstance(node, ast.Call):
                # 如果是简单的调用（如 print），降低权重
                if isinstance(node.func, ast.Name) and node.func.id in simple_functions:
                    total_complexity += simple_call_weight
                else:
                    total_complexity += statement_weight
            elif isinstance(node, ast.Assign):
                total_complexity += statement_weight

        # 返回计算的超时时间，确保至少为 5 秒
        return max(5, total_complexity)
    except Exception as e:
        # 如果代码解析失败，返回默认超时时间
        return 10


def get_main_directory():
    """
    获取主程序 main.py 的运行目录。
    """
    try:
        # 遍历模块，找到 main 的运行目录
        main_module = importlib.import_module("main")
        if hasattr(main_module, "MAIN_DIRECTORY"):
            return getattr(main_module, "MAIN_DIRECTORY")
        else:
            # 如果 MAIN_DIRECTORY 没有被定义，获取 main.py 所在目录
            return os.path.dirname(os.path.abspath(main_module.__file__))
    except Exception as e:
        # 返回默认目录（当前工作目录）
        return os.getcwd()


def execute_in_subprocess(code, config, output_handler):
    """
    在主程序运行目录的 temp_scripts 文件夹中创建临时文件并执行代码，支持全局超时设置。
    """
    try:
        # 获取主程序运行目录
        main_dir = get_main_directory()

        # 确定超时时间
        if config["RETURN_TIMEOUT"] < 0:
            timeout = estimate_timeout(code)  # 自适应超时
        else:
            timeout = config["RETURN_TIMEOUT"]  # 使用固定超时

        # 构造 temp_scripts 文件夹路径
        temp_scripts_dir = os.path.join(main_dir, "temp_scripts")
        if not os.path.exists(temp_scripts_dir):
            os.makedirs(temp_scripts_dir)

        # 创建临时 Python 文件
        temp_file_path = os.path.join(
            temp_scripts_dir, next(tempfile._get_candidate_names()) + ".py"
        )
        with open(temp_file_path, "w", encoding="utf-8") as temp_file:
            temp_file.write("# -*- coding: utf-8 -*-\n")
            temp_file.write(code)

        # 执行临时文件

        print("解释器路径:", sys.executable)
        process = subprocess.Popen(
            [sys.executable, temp_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )


        try:
            # 设置超时并等待输出
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            # process.kill()
            timeout_message = output_handler.get_translation(
                "error_timeout", timeout=f"{timeout:.2f}"
            )
            return None, timeout_message

        # 返回输出和错误信息
        if stderr.strip():
            return stdout.strip(), stderr.strip()
        return stdout.strip(), None
    except Exception as e:
        return None, f"[ERROR] {str(e)}"


def cleanup_temp_dir():
    """
    清理主程序运行目录下的 temp_scripts 文件夹
    """
    main_dir = get_main_directory()
    temp_dir = os.path.join(main_dir, "temp_scripts")

    # 检查文件夹是否存在
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
