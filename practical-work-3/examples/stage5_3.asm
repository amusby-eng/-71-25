; Обработка третьего вектора из шести элементов

; Записываем исходные значения в память
load_const r20, -100
load_const r21, 500
write r20, r21

load_const r20, -20
load_const r21, 501
write r20, r21

load_const r20, 15
load_const r21, 502
write r20, r21

load_const r20, 0
load_const r21, 503
write r20, r21

load_const r20, -1
load_const r21, 504
write r20, r21

load_const r20, 50
load_const r21, 505
write r20, r21

; Загружаем базовый адрес вектора
load_const r29, 500

; Вычисляем модули элементов и записываем на место исходных
load_const r20, 500
read r20, r8
abs r8, 0, r29

load_const r20, 501
read r20, r8
abs r8, 1, r29

load_const r20, 502
read r20, r8
abs r8, 2, r29

load_const r20, 503
read r20, r8
abs r8, 3, r29

load_const r20, 504
read r20, r8
abs r8, 4, r29

load_const r20, 505
read r20, r8
abs r8, 5, r29
