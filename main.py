import re
import time

# Decorador para medir el tiempo de ejecución de funciones
# Complejidad Computacional: O(1)
# Razon: El decorador no afecta la complejidad de la funcion decorada, solo mide el tiempo de ejecucion.
def medir_tiempo(func):
    def wrapper(*args, **kwargs):
        inicio = time.perf_counter()
        resultado = func(*args, **kwargs)
        fin = time.perf_counter()
        print(f"{func.__name__} tardó {fin - inicio:.4f} segundos")
        return resultado
    return wrapper

# Función para mostrar un mensaje de finalización
# Complejidad Computacional: O(1)
# Razon: La funcion solo imprime un mensaje y espera una entrada del usuario.
def finalizador_Programa():
    """Función que se ejecuta al finalizar el programa"""
    input("Presiona Enter para salir...")

# Mapeo de extensiones a secciones en expresiones.txt
LANGUAGE_MAP = {
    "py": "python",
    "rkt": "racket",
    "asm": "asm"
}


# Funcion para leer archivos y procesar expresiones
# Complejidad Computacional: O(n), n siendo numero de caracteres en el archivo.
# Razon: La lectura del archivo se realiza linea por linea, lo que quiere decir que si hay n caracteres en el archivo, el tiempo es lineal con respecto al tamaño del archivo.
@medir_tiempo
def read_file(file_path):
    """Lee un archivo y devuelve sus líneas preservando espacios y saltos de línea"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.readlines()


# Funcion para leer expresiones desde un archivo de configuracion
# Complejidad Computacional: O(E * R), E siendo el numero de secciones de lenguaje en el archivo `expresiones.txt` y R numero de patrones en las listas keywords, operators, literals y comments.
# Razon: Lee E secciones y para cada seccion recorre R patrones para crear la lista de expresiones. En el peor de los casos, todos los tokens estan en la misma linea.
@medir_tiempo
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

# Funcion para resaltar el codigo
# Complejidad Computacional: O(L * (T + R)), L siendo el numero de lineas del codigo, T el numero de tokens en cada linea y R el numero de patrones en las listas keywords, operators, literals y comments.
# Razon: Para cada linea, se procesan T tokens y se comparan con R patrones. En el peor de los casos, todos los tokens estan en la misma linea.
@medir_tiempo
def highlight_code(code_lines, language, expressions):
    """Versión corregida que preserva saltos de línea y espacios originales"""
    lang_data = expressions.get(LANGUAGE_MAP.get(language, ""), {})
    comment_pattern = lang_data.get('comments', ['#.*'])[0]
    
    # Funcion para resaltar una línea de código
    # Complejidad Computacional: O(T * R), T siendo el numero de tokens en la linea y R el numero de patrones en las listas keywords, operators, literals y comments.
    # Razon: Por cada token, se comparan R patrones. En el peor de los casos, todos los tokens estan en la misma linea.
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

# Funcion para generar el HTML
# Complejidad Computacional: O(N), N siendo el numero de caracteres en el codigo resaltado.
# Razón: El HTML se genera con una plantilla fija y una sola operación de inserción de texto.
@medir_tiempo
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

# Funcion principal para procesar archivos
# Complejidad Computacional: O(L * (T + R)), T siendo el numero de tokens en la linea y R el numero de patrones en las listas keywords, operators, literals y comments.
# Razon: El procesamiento de cada archivo implica leer el archivo, resaltar el código y generar el HTML. Cada paso tiene una complejidad lineal con respecto al tamaño del archivo.
@medir_tiempo
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
# Complejidad: O(Z * L * (T + R)), Z siendo el numero de archivos a procesar, L el numero de lineas, T el numero de tokens en cada linea y R el numero de patrones en las listas keywords, operators, literals y comments.
# Razon: Se procesan Z archivos, cada uno con L lineas, T tokens y R patrones. La complejidad total es la suma de las complejidades de cada archivo.
@medir_tiempo
def main():
    process_file("1.py", "salida_python.html")
    process_file("2.rkt", "salida_racket.html")
    process_file("3.asm", "salida_asm.html")
    
# se ejecuta el programa
if __name__ == "__main__":
    main()
    finalizador_Programa()