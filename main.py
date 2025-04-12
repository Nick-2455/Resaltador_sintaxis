import re

# Leer archivo línea por línea
def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

# Leer expresiones desde un archivo
def read_expressions(file_path):
    raw_content = read_file(file_path)
    parsed_expressions = []
    
    for line in raw_content:
        parts = line.split('=')
        if len(parts) == 2:
            key = parts[0].strip()
            value = parts[1].strip()
            parsed_expressions.append((key, value))
    
    return parsed_expressions

# Guardar las expresiones en una variable
expressions = read_expressions("expresiones.txt")

# Mostrar expresiones cargadas
print(expressions)

# Buscar una clave en la lista
def safe_assoc(key, alist):
    for k, v in alist:
        if k == key:
            return v
    return False

# Resaltar un solo token
def highlight_token(token):
    if re.match(r'^\s+$', token):
        return token
    elif re.match(r'^#.*$', token):
        return f"<span class='comment'>{token}</span>"
    elif re.match(r'^(f)?["\'][^"\']*["\']$', token):  # Corregido aquí
        return f"<span class='literal'>{token}</span>"
    elif re.match(r'^\[.*\]$', token):
        content = token.strip("[]")
        num_pattern = r'\d+(?:\.\d+)?'
        highlighted_content = re.sub(num_pattern, lambda m: f"<span class='literal'>{m.group(0)}</span>", content)
        return f"<span class='literal'>[{highlighted_content}]</span>"
    elif re.match(r'^\d+(?:\.\d+)?$', token):
        return f"<span class='literal'>{token}</span>"
    elif re.match(r'^(' + '|'.join([k for k, _ in expressions]) + r')$', token):
        return f"<span class='keyword'>{token}</span>"
    elif re.match(r'^[+*/=<>!&|%^-]+$', token):
        return f"<span class='operator'>{token}</span>"
    else:
        return token

# Resaltar cada línea del código
def highlight_code(code_lines):
    def highlight_line(line):
        if re.match(r'^\s*#', line):
            return f"<span class='comment'>{line}</span>"
        else:
            tokens = re.findall(r'"[^"]*"|\'[^\']*\'|f"[^"]*"|\[.*?\]|\b\d+(?:\.\d+)?\b|\b[a-zA-Z_]\w*\b|[+*/=<>!&|%^-]+|[(),:]|\s+', line)
            highlighted = [highlight_token(token) for token in tokens]
            return ''.join(highlighted)
    
    return '\n'.join(highlight_line(line) for line in code_lines)

# Crear HTML con estilos y código resaltado
def generate_html(code):
    return f"""<html><head><style>
    body {{ font-family: Arial, sans-serif; }}
    .keyword {{ color: blue; font-weight: bold; }}
    .operator {{ color: green; font-weight: bold; }}
    .literal {{ color: orange; font-style: italic; }}
    .comment {{ color: gray; font-style: italic; }}
    </style></head><body><pre>
    {highlight_code(code)}
    </pre></body></html>"""

# Guardar el HTML generado
def write_html(output_file, content):
    with open(output_file, 'w') as file:
        file.write(content)

# Procesar un archivo y generar su HTML
def process_file(input_file, output_file):
    code = read_file(input_file)
    html_content = generate_html(code)
    write_html(output_file, html_content)

# Ejecutar el programa con archivos de prueba
process_file("1.py", "resaltado_1.html")
process_file("2.rkt", "resaltado_2.html")
process_file("3.asm", "resaltado_3.html")