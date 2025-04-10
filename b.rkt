 #lang racket

;; Función para leer el contenido de un archivo línea por línea
(define (read-file file-path)
  (with-input-from-file file-path
    (lambda () (port->lines (current-input-port)))))

;; Función para leer y procesar las expresiones regulares desde el archivo
(define (read-expressions file-path)
  (define raw-content (read-file file-path))  ; Leer todas las líneas del archivo
  (define parsed-expressions
    (filter pair?  ; Filter out empty lists
      (map (lambda (line)
             (define parts (string-split line "="))  ; Divide la línea por el signo igual (=)
             (if (= (length parts) 2)  ; Si la línea tiene el formato esperado, la procesa
                 (cons (string-trim (first parts)) (string-trim (second parts)))  ; Crea un par clave-valor
                 '()))  ; Si no tiene el formato esperado, devuelve una lista vacía
           raw-content)))
  parsed-expressions)  ; Devuelve la lista de expresiones

;; Leer las expresiones del archivo 'expresiones.txt'
(define expressions (read-expressions "expresiones.txt"))

;; Mostrar el contenido leído para verificar
(displayln expressions)

;; Función para acceder a las expresiones de forma segura
(define (safe-assoc key alist)
  (define result (assoc key alist))
  (if result
      (cdr result)  ; Use cdr instead of second since we're using cons pairs
      #f))  ; Devuelve #f si la clave no se encuentra

;; Función para resaltar los tokens en el código
(define (highlight-token token)
  (cond
    ; Preserve whitespace as-is
    [(regexp-match? (regexp "^\\s+$") token) token]
    ; Comments (keep as is, working well)
    [(regexp-match? (regexp "^#.*$") token)
     (string-append "<span class='comment'>" token "</span>")]
    
    ; Full string literals (including f-strings)
    [(regexp-match? #px"^(f)?[\"'][^\"']*[\"']$" token)
     (string-append "<span class='literal'>" token "</span>")]
    
    ; List literals with nested highlighting
    [(regexp-match? #px"^\\[.*\\]$" token)
     (let ([content (string-trim token "[]")]
           [num-pattern #px"\\d+(?:\\.\\d+)?"])
       (string-append "<span class='literal'>[" 
                     (regexp-replace* num-pattern content
                                    (lambda (m) 
                                      (string-append "<span class='literal'>" m "</span>")))
                     "]</span>"))]
    
    ; Numbers
    [(regexp-match? #px"^\\d+(?:\\.\\d+)?$" token)
     (string-append "<span class='literal'>" token "</span>")]
    
    ; Keywords
    [(regexp-match? (regexp (string-append "^(" (or (safe-assoc "keywords" expressions) "") ")$")) token)
     (string-append "<span class='keyword'>" token "</span>")]
    
    ; Operators
    [(regexp-match? (regexp "^[+*/=<>!&|%^-]+$") token)
     (string-append "<span class='operator'>" token "</span>")]
    
    ; Default case: return token as-is
    [else token]))  ; Si no es ninguna categoría, no lo resalta

;; Función para leer y resaltar el código fuente
(define (highlight-code code-lines)
  (define (highlight-line line)
    (if (regexp-match? (regexp "^\\s*#") line)
        ; If line starts with #, treat entire line as comment
        (string-append "<span class='comment'>" line "</span>")
        ; Otherwise process tokens with a direct pattern that preserves formatting
        (let* ([tokens (regexp-match* #px"\"[^\"]*\"|'[^']*'|f\"[^\"]*\"|\\[.*?\\]|\\b\\d+(?:\\.\\d+)?\\b|\\b[a-zA-Z_]\\w*\\b|[+*/=<>!&|%^-]+|[(),:]|\\s+" line)]
               [highlighted (map highlight-token tokens)])
          ; Join without adding extra spaces to preserve formatting
          (string-join highlighted ""))))
  (string-join (map highlight-line code-lines) "\n"))

;; Función para generar el archivo HTML con el código resaltado
(define (generate-html code)
  (string-append "<html><head><style>"
                 "body { font-family: Arial, sans-serif; }"
                 ".keyword { color: blue; font-weight: bold; }"
                 ".operator { color: green; font-weight: bold; }"
                 ".literal { color: orange; font-style: italic; }"
                 ".comment { color: gray; font-style: italic; }"
                 "</style></head><body><pre>"
                 (highlight-code code)
                 "</pre></body></html>"))

;; Función para escribir el HTML resaltado en un archivo
(define (write-html output-file content)
  (with-output-to-file output-file
    (lambda () (display content))   ; Escribe el contenido en el archivo
    #:exists 'replace))           ; Usa el keyword argument #:exists

;; Función principal para procesar el archivo
(define (process-file input-file output-file)
  (define code (read-file input-file))     ; Leer el código fuente
  (define html-content (generate-html code)) ; Generar HTML con el código resaltado
  (write-html output-file html-content))    ; Guardar el HTML en un archivo

;; Ejemplo de uso: Procesar un archivo de código fuente y generar el HTML
(process-file "codigo_fuente.py" "resaltado.html")
