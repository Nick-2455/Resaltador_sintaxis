section .data
    msg db 'Hello, World!', 0
    msg_len equ $ - msg

section .bss
    result resd 1

section .text
    global _start

_start:
    ; Inicializar valores
    mov eax, 5
    mov ebx, 10

    ; Operaciones
    add eax, ebx
    sub ebx, 3
    imul eax, ebx               ; usar imul explícito

    ; Guardar resultado
    mov [result], eax

    ; Imprimir mensaje
    mov rax, 1                  ; syscall: write
    mov rdi, 1                  ; stdout
    mov rsi, msg
    mov rdx, msg_len
    syscall

    ; Salir
    mov rax, 60                 ; syscall: exit
    xor rdi, rdi
    syscall
