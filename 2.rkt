#lang racket

(define (suma x y)
  (+ x y))

(define resultado (suma 3 5))

; Esto es un comentario

(if (> resultado 5)
    (display "Mayor a 5")
    (display "Menor o igual a 5"))
