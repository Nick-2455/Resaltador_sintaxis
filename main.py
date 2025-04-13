import re

# Mapeo de extensiones a secciones en expresiones.txt
LANGUAGE_MAP = {
    "py": "python",
    "rkt": "racket",
    "asm": "asm"
}

def read_file(file_path):
    """Lee un archivo y devuelve sus líneas preservando espacios y saltos de línea"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.readlines()

def read_expressions(config_file):
    """Parsea el archivo de configuración correctamente"""
    sections = {}
    current_section = None
    
    for line in read_file(config_file):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('[') and line.endswith(']'):
            current_section = line[1:-1].lower()
            sections[current_section] = {
                'keywords': [],
                'operators': [],
                'literals': [],
                'comments': []
            }
        elif current_section and '=' in line:
            key, value = line.split('=', 1)
            key = key.strip().lower()
            sections[current_section][key] = [v.strip() for v in value.split('|')]
            
    return sections

def highlight_code(code_lines, language, expressions):
    """Versión corregida que preserva saltos de línea y espacios originales"""
    lang_data = expressions.get(LANGUAGE_MAP.get(language, ""), {})
    comment_pattern = lang_data.get('comments', ['#.*'])[0]
    
    def highlight_line(line):
        """Procesa una línea de código para resaltar sintaxis"""
        # Preserva el salto de línea original
        original_line_ending = '\n' if line.endswith('\n') else ''
        
        if re.match(comment_pattern, line.rstrip('\n')):
            return f"<span class='comment'>{line.rstrip('\n')}</span>{original_line_ending}"
            
        # Regex para capturar tokens y espacios
        token_re = re.compile(
            r'(\s+)|'                                  # Espacios
            r'("[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\')|'  # Strings
            r'(\d+\.?\d*)|'                            # Números
            r'(\b\w+\b)|'                              # Palabras
            r'([=+*/\-<>!&|%^.,:;()\[\]{}])|'          # Operadores
            r'(#.*)'                                    # Comentarios
        )
        
        highlighted = []
        for match in token_re.finditer(line.rstrip('\n')):
            spaces, string_lit, number, word, operator, comment = match.groups()
            
            if spaces:
                highlighted.append(spaces)
            elif comment:
                highlighted.append(f"<span class='comment'>{comment}</span>")
            else:
                token = next(item for item in [string_lit, number, word, operator] if item is not None)
                token_clean = token.strip()
                
                css_class = None
                if token_clean in lang_data.get('keywords', []):
                    css_class = 'keyword'
                elif token_clean in lang_data.get('operators', []):
                    css_class = 'operator'
                elif any(re.fullmatch(pat, token) for pat in lang_data.get('literals', [])):
                    css_class = 'literal'
                
                if css_class:
                    highlighted.append(f"<span class='{css_class}'>{token}</span>")
                else:
                    highlighted.append(token)
        
        return ''.join(highlighted) + original_line_ending
    
    return ''.join(highlight_line(line) for line in code_lines)

def generate_html(highlighted_code):
    """Genera el HTML con estilos integrados"""
    return f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: monospace; }}
        .keyword {{ color: #0000FF; font-weight: bold; }}
        .operator {{ color: #008000; }}
        .literal {{ color: #FF8C00; }}
        .comment {{ color: #808080; font-style: italic; }}
    </style>
</head>
<body>
    <pre>{highlighted_code}</pre>
</body>
</html>"""

def process_file(input_file, output_file):
    """Procesa un archivo y genera el HTML final"""
    lang = input_file.split('.')[-1].lower()
    expressions = read_expressions('expresiones.txt')
    code = read_file(input_file)
    highlighted = highlight_code(code, lang, expressions)
    html = generate_html(highlighted)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

# Ejecución
if __name__ == "__main__":
    process_file("1.py", "salida_python.html")
    process_file("2.rkt", "salida_racket.html")
    process_file("3.asm", "salida_asm.html")