import sys
import os
import re
import math as py_math
import random


def run_vfc_language(code_text):
    lines = code_text.splitlines()
    i = 0

    # Хранилище подключенных библиотек, переменных и флаг отладки
    imported_modules = {}
    variables = {}
    debug_mode = True  # По умолчанию отладка включена

    # Вспомогательная функция для служебных сообщений
    def debug_print(text):
        if debug_mode:
            print(text)

    # Функция для подстановки переменных вида ${var_name} в текст
    def parse_vars(text):
        for v_name, v_val in variables.items():
            text = text.replace(f"${{{v_name}}}", str(v_val))
        return text

    while i < len(lines):
        line = lines[i].strip()

        # Пропуск пустых строк
        if not line:
            i += 1
            continue

        # vce::nakonec - полный выход из программы
        if line == "vce::nakonec":
            break

        # vce::ne - мягкая пауза (ожидание Enter)
        if line == "vce::ne":
            input("[VFC Pause] Нажмите Enter для продолжения...")
            i += 1
            continue

        # eto::xz - мусорная команда для запутывания
        if line == "eto::xz":
            i += 1
            continue

        # o::tlad::ka otkl / vkly - управление отладкой
        if line.startswith("o::tlad::ka"):
            arg = line.replace("o::tlad::ka", "").strip().lower()
            if arg == "otkl":
                debug_mode = False
            elif arg == "vkly":
                debug_mode = True
            i += 1
            continue

        # import::use - подключение библиотек
        if line.startswith("import::use"):
            lib_name = line.replace("import::use", "").strip()
            if lib_name:
                if lib_name == "math":
                    imported_modules["math"] = "loaded_base"
                    debug_print("[VFC System] Подключена обязательная базовая библиотека: math")
                elif lib_name == "mathp":
                    imported_modules["mathp"] = py_math
                    debug_print("[VFC System] Подключена математическая библиотека: mathp")
                elif lib_name == "jam":
                    imported_modules["jam"] = random
                    debug_print("[VFC System] Подключена универсальная библиотека: jam")
                else:
                    try:
                        imported_modules[lib_name] = __import__(lib_name)
                        debug_print(f"[VFC System] Загружена внешняя библиотека: {lib_name}")
                    except ImportError:
                        print(f"[VFC Error] Библиотека '{lib_name}' не найдена.")
            i += 1
            continue

        # va::rik: - объявление переменных
        if line == "va::rik:":
            i += 1
            while i < len(lines) and lines[i].strip() != "vce":
                v_line = lines[i].strip()
                match_var = re.search(r'\[(.*?)\]', v_line)
                if match_var:
                    content = match_var.group(1)
                    if "=" in content:
                        parts = content.split("=", 1)
                        variables[parts[0].strip()] = parts[1].strip()
                i += 1
            i += 1
            continue

        # v::opros: - интерактивный вопрос пользователю
        if line == "v::opros:":
            i += 1
            prompt_lines = []
            while i < len(lines) and lines[i].strip() != "vce":
                prompt_lines.append(lines[i])
                i += 1

            prompt_content = "\n".join(prompt_lines)
            match = re.search(r'\[(.*?)\]', prompt_content, re.DOTALL)
            question_text = match.group(1) if match else "Введите значение: "

            user_input = input(parse_vars(question_text))
            variables["user_input"] = user_input
            i += 1
            continue

        # z::ikl: N - цикл выполнения блока команд N раз
        if line.startswith("z::ikl:"):
            try:
                count = int(line.replace("z::ikl:", "").strip())
            except ValueError:
                count = 1

            i += 1
            loop_lines = []
            while i < len(lines) and lines[i].strip() != "vce":
                loop_lines.append(lines[i])
                i += 1

            for _ in range(count):
                sub_code = "\n".join(loop_lines)
                run_vfc_language(sub_code)

            i += 1
            continue

        # k::a::k: - умная проверка
        if line == "k::a::k:":
            i += 1
            block_lines = []
            while i < len(lines) and lines[i].strip() != "vce":
                block_lines.append(lines[i])
                i += 1

            target_file = ""
            check_mode = ""
            check_param = ""

            for b_line in block_lines:
                b_trimmed = b_line.strip()
                if (b_trimmed.startswith("[") or b_trimmed.startswith("{")) and not target_file:
                    target_file = b_trimmed[1:-1].strip()
                elif b_trimmed.startswith("--{"):
                    match_m = re.search(r'--\{(.*?)\}', b_trimmed)
                    if match_m:
                        check_mode = match_m.group(1).strip()
                elif b_trimmed.startswith("---["):
                    match_p = re.search(r'---\[(.*?)\]', b_trimmed)
                    if match_p:
                        check_param = match_p.group(1).strip()

            debug_print(f"[VFC Check] Проверка файла '{target_file}' [Режим: {check_mode}]...")
            if check_mode == "exist" or check_mode == "m":
                exists = os.path.exists(target_file)
                debug_print(f"  └─ Результат существования: {exists}")
            elif check_mode == "stroki":
                if os.path.exists(target_file):
                    with open(target_file, "r", encoding="utf-8") as f:
                        lines_count = sum(1 for _ in f)
                    debug_print(f"  └─ Проверка строк. Ожидалось: '{check_param}', в файле строк: {lines_count}")
                else:
                    debug_print(f"  └─ Файл {target_file} не найден для проверки строк.")
            elif check_mode == "razmer":
                if os.path.exists(target_file):
                    size_bytes = os.path.getsize(target_file)
                    debug_print(f"  └─ Размер файла: {size_bytes} байт (Ожидался критерий: {check_param})")
                else:
                    debug_print(f"  └─ Файл {target_file} не найден.")

            i += 1
            continue

        # vot::tut::vivod: - вывод текста
        if line == "vot::tut::vivod:":
            i += 1
            block_lines = []
            while i < len(lines) and lines[i].strip() != "vce":
                block_lines.append(lines[i])
                i += 1

            content = "\n".join(block_lines)
            match = re.search(r'\[(.*?)\]', content, re.DOTALL)
            raw_text = match.group(1) if match else content
            print(parse_vars(raw_text))
            i += 1
            continue

        # p::apka: - создание папок и файлов
        if line == "p::apka:":
            i += 1
            block_lines = []
            while i < len(lines) and lines[i].strip() != "vce":
                block_lines.append(lines[i])
                i += 1

            file_type = ""
            sub_files = []
            target_name = ""
            file_contents = {}
            current_target_file = None

            for b_line in block_lines:
                b_trimmed = b_line.strip()
                if b_trimmed.startswith("[") and b_trimmed.endswith("]") and not file_type:
                    file_type = b_trimmed[1:-1].strip()
                elif b_trimmed.startswith("---["):
                    match_files = re.search(r'---\[(.*?)\]', b_trimmed)
                    if match_files:
                        content_inside = match_files.group(1)
                        if content_inside and content_inside != "[]":
                            sub_files = [f.strip() for f in content_inside.split(",")]
                elif b_trimmed.startswith("----["):
                    match_name = re.search(r'----\[(.*?)\]', b_trimmed)
                    if match_name:
                        target_name = parse_vars(match_name.group(1).strip())
                elif b_trimmed.startswith("-=[") and b_trimmed.endswith("]"):
                    current_target_file = parse_vars(b_trimmed[3:-1].strip())
                    if current_target_file not in file_contents:
                        file_contents[current_target_file] = []
                elif b_trimmed.startswith("{") and b_trimmed.endswith("}"):
                    text_line = parse_vars(b_trimmed[1:-1])
                    if current_target_file:
                        file_contents[current_target_file].append(text_line)

            if target_name:
                is_folder = (file_type.lower() == "folder" or file_type == "" or "папка" in file_type.lower())
                if is_folder:
                    os.makedirs(target_name, exist_ok=True)
                    debug_print(f"[VFC FS] Создана папка: {os.path.abspath(target_name)}")
                    for sf in sub_files:
                        if sf and sf != "[]":
                            sf_path = os.path.join(target_name, sf)
                            if sf not in file_contents and not os.path.exists(sf_path):
                                with open(sf_path, "w", encoding="utf-8") as sf_obj:
                                    sf_obj.write("")
                                debug_print(f"  └─ Создан пустой файл: {sf}")
                    for fname, lines_list in file_contents.items():
                        fname_path = os.path.join(target_name, fname)
                        with open(fname_path, "w", encoding="utf-8") as f_obj:
                            f_obj.write("\n".join(lines_list))
                        debug_print(f"  └─ Создан файл: {fname}")
                else:
                    default_text = "\n".join(list(file_contents.values())[0]) if file_contents else ""
                    with open(target_name, "w", encoding="utf-8") as f_obj:
                        f_obj.write(default_text)
                    debug_print(f"[VFC FS] Создан файл: {os.path.abspath(target_name)}")

            i += 1
            continue

        if line == "vce":
            i += 1
            continue

        i += 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование в терминале: python vfc.py <файл.vfc>")
        sys.exit(1)

    filename = sys.argv[1]
    if not os.path.exists(filename):
        print(f"[VFC Error] Файл '{filename}' не найден!")
        sys.exit(1)

    with open(filename, "r", encoding="utf-8") as f:
        code = f.read()

    run_vfc_language(code)