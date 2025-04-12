#lang racket

;; Leer archivo línea por línea
(define (read-file file-path)
  (with-input-from-file file-path
    (lambda () (port->lines (current-input-port)))))

;; Leer expresiones desde un archivo
(define (read-expressions file-path)
  (define raw-content (read-file file-path))
  (define parsed-expressions
    (filter pair?
      (map (lambda (line)
             (define parts (string-split line "="))
             (if (= (length parts) 2)
                 (cons (string-trim (first parts)) (string-trim (second parts)))
                 '()))
           raw-content)))
  parsed-expressions)

;; Guardar las expresiones en una variable
(define expressions (read-expressions "expresiones.txt"))

;; Mostrar expresiones cargadas
(displayln expressions)

;; Buscar una clave en la lista
(define (safe-assoc key alist)
  (define result (assoc key alist))
  (if result
      (cdr result)
      #f))

;; Resaltar un solo token
(define (highlight-token token)
  (cond
    ;; Espacios
    [(regexp-match? (regexp "^\\s+$") token) token]
    ;; Comentarios
    [(regexp-match? (regexp "^#.*$") token)
     (string-append "<span class='comment'>" token "</span>")]
    ;; Cadenas
    [(regexp-match? #px"^(f)?[\"'][^\"']*[\"']$" token)
     (string-append "<span class='literal'>" token "</span>")]
    ;; Listas con números
    [(regexp-match? #px"^\\[.*\\]$" token)
     (let ([content (string-trim token "[]")]
           [num-pattern #px"\\d+(?:\\.\\d+)?"])
       (string-append "<span class='literal'>[" 
                     (regexp-replace* num-pattern content
                                    (lambda (m) 
                                      (string-append "<span class='literal'>" m "</span>")))
                     "]</span>"))]
    ;; Números sueltos
    [(regexp-match? #px"^\\d+(?:\\.\\d+)?$" token)
     (string-append "<span class='literal'>" token "</span>")]
    ;; Palabras clave
    [(regexp-match? (regexp (string-append "^(" (or (safe-assoc "keywords" expressions) "") ")$")) token)
     (string-append "<span class='keyword'>" token "</span>")]
    ;; Operadores
    [(regexp-match? (regexp "^[+*/=<>!&|%^-]+$") token)
     (string-append "<span class='operator'>" token "</span>")]
    ;; Todo lo demás
    [else token]))

;; Resaltar cada línea del código
(define (highlight-code code-lines)
  (define (highlight-line line)
    (if (regexp-match? (regexp "^\\s*#") line)
        ;; Línea que empieza con comentario
        (string-append "<span class='comment'>" line "</span>")
        ;; Resaltar tokens en la línea
        (let* ([tokens (regexp-match* #px"\"[^\"]*\"|'[^']*'|f\"[^\"]*\"|\\[.*?\\]|\\b\\d+(?:\\.\\d+)?\\b|\\b[a-zA-Z_]\\w*\\b|[+*/=<>!&|%^-]+|[(),:]|\\s+" line)]
               [highlighted (map highlight-token tokens)])
          (string-join highlighted ""))))
  (string-join (map highlight-line code-lines) "\n"))

;; Crear HTML con estilos y código resaltado
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

;; Guardar el HTML generado
(define (write-html output-file content)
  (with-output-to-file output-file
    (lambda () (display content))
    #:exists 'replace))

;; Procesar un archivo y generar su HTML
(define (process-file input-file output-file)
  (define code (read-file input-file))
  (define html-content (generate-html code))
  (write-html output-file html-content))

;; Ejecutar el programa con archivos de prueba
(process-file "1.py" "resaltado_1.html")
(process-file "2.rkt" "resaltado_2.html")
(process-file "3.js" "resaltado_3.html")
