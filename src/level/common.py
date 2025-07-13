import importlib
import os
import re
import tiktoken


def generate_prompt(
    level,
    system_info,
    allowed_operations,
    restrictions,
    examples,
    operation_levels,
    extra_prompt,
):
    """
    动态生成 Prompt，并让 AI 自行判断权限是否足够。
    """
    main_module = importlib.import_module("main")
    config = getattr(main_module, "config")

    # 使用 config 中的 LANGUAGE
    language_code = config["LANGUAGE"]
    # 构造语言文件路径
    main_dir = os.path.dirname(os.path.abspath(main_module.__file__))

    locale_dir = os.path.join(main_dir, "locale", "prompt", language_code)
    file_path = os.path.join(locale_dir, f"{language_code}.txt")

    # 确保文件存在
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Language template file '{file_path}' not found.")

    # 读取模板文件内容
    with open(file_path, "r", encoding="utf-8") as file:
        prompt_template = file.read()

    # 准备替换的内容
    system_info_text = "\n".join(
        [f"{key}: {value}" for key, value in system_info.items()]
    )
    operation_levels_text = "\n".join(
        [f"{key}: Level {value}" for key, value in operation_levels.items()]
    )

    # 使用格式化方法填充模板
    prompt = prompt_template.format(
        level=level,
        system_info_text=system_info_text,
        operation_levels_text=operation_levels_text,
        allowed_operations=allowed_operations,
        restrictions=restrictions,
        examples=examples,
        extra_prompt=extra_prompt,
    )

    encoding = tiktoken.encoding_for_model("gpt-4o")
    tokens1 = encoding.encode(prompt)
    tokens2 = encoding.encode(prompt.replace("\n", "").replace("\r", ""))
    tokens3 = encoding.encode(
        prompt.replace("\n", "").replace("\r", "").replace(" ", "")
    )
    print("tokens1 " + str(len(tokens1)))
    print("tokens2 " + str(len(tokens2)))
    print("tokens3 " + str(len(tokens3)))

    return prompt.replace("\n", "").replace("\r", "")


def extract_code(ai_response):
    """
    提取 AI 响应中的代码块。
    """
    import re

    match = re.search(r">>>RUN>>>[\s\S]*?<<<RUN<<<", ai_response)
    if match:
        return match.group(0).replace(">>>RUN>>>", "").replace("<<<RUN<<<", "").strip()
    return None


def extract_callback(ai_response):
    """
    提取 AI 响应中的回调块。
    """
    import re

    match = re.search(r">>>CALLBACK>>>[\s\S]*?<<<CALLBACK<<<", ai_response)
    if match:
        return (
            match.group(0)
            .replace(">>>CALLBACK>>>", "")
            .replace("<<<CALLBACK<<<", "")
            .strip()
        )
    return None


import re


def extract_all_code(ai_response):
    """
    提取 AI 响应中的所有代码块
    """
    matches = re.findall(r">>>RUN>>>[\s\S]*?<<<RUN<<<", ai_response)
    return (
        [
            match.replace(">>>RUN>>>", "").replace("<<<RUN<<<", "").strip()
            for match in matches
        ]
        if matches
        else []
    )


def extract_all_callbacks(ai_response):
    """
    提取 AI 响应中的所有回调块
    """
    matches = re.findall(r">>>CALLBACK>>>[\s\S]*?<<<CALLBACK<<<", ai_response)
    return (
        [
            match.replace(">>>CALLBACK>>>", "").replace("<<<CALLBACK<<<", "").strip()
            for match in matches
        ]
        if matches
        else []
    )
