from itertools import combinations

import numpy as np
import plotly
import plotly.graph_objs as go

with open('matrix_electre.txt') as f:  # зчитування матриці та інформацію про ваги та c i d з файлу matrix_electre.txt
    data = f.readlines()
    matrix = [list(map(int, row.split())) for row in data[:-2]]
    array_c_and_d = data.pop()
    array_c_and_d = list(map(float, array_c_and_d.split(' ')))
    array_w = data.pop()
    array_w = list(map(float, array_w.split(' ')))
    c = array_c_and_d[0]
    d = array_c_and_d[1]


def vnutrishnya_stiykist(X, matrix_R):  # перевірка чи відповідає розв’язок властивості внутрішньої стійкості
    flag = False
    for k in X:
        gen = (l for l in X if l != k)  # перевіряємо чи є у кожному рядку з X одиниці на позиціях елементів з множини X
        for j in gen:
            if matrix_R[k][j] == 1 or matrix_R[j][k] == 1:
                flag = True
                break
    if not flag:
        return True


def zovnishna_stiykist(X, matrix_R):  # перевірка чи відповідає розв’язок властивості зовнішньої стійкості
    mnoshina = []

    for j in range(len(matrix_R)):
        if j not in X:
            mnoshina.append(j)   # множина усіх елементів, що не входять в X
    for k in mnoshina:
        flag = False
        for j in range(len(matrix_R)):
            if matrix_R[j][k] == 1 and j in X:  # якщо є хоча б одна одиниця в рядках з множини X
                flag = True
        if not flag:
            return False
    return True


def print_matrix(array):  # вивід матриці на екран
    for i in range(len(array)):
        for j in range(len(array[0])):
            print(array[i][j], end=' ')
        print()


def find_P(array_K): #знаходимо множину P
    P = 0
    if array_K:
        for k in array_K:
            P += array_w[k]
    return P


def dfs(vertex, matrix_R, color):  # перевірка на ациклічність
    color[vertex] = "grey"
    for j in range(len(matrix_R)):
        if matrix_R[vertex][j] == 1:
            if color[j] == "white":
                dfs(j, matrix_R, color)
            if color[j] == "grey":
                return True
    color[vertex] = "black"


def check_cycle(matrix_R, color):  # перевірка на ациклічність
    cycle = False
    for i in range(len(matrix_R)):
        color[i] = "white"
    for i in range(len(matrix_R)):
        if dfs(i, matrix_R, color):
            cycle = True
            break
    return cycle


def Electre1(c, d):  # виконуємо метод ELECTRE 1
    Kplus = []
    Kminus = []
    Kdorivnuye = []
    matrixCab = [[0] * len(matrix) for _ in range(len(matrix))]
    matrixDab = [[1] * len(matrix) for _ in range(len(matrix))]
    matrix_R = [[0] * len(matrix) for _ in range(len(matrix))]
    max_vidhilennia = []

    for i in range(len(matrix[0])):
        col = [r[i] for r in matrix]
        max_vidhilennia.append(array_w[i] * (max(col) - min(col)))
    # print("Максимальне відхилення:", max_vidhilennia)
    for i in range(len(matrix)):
        for l in range(i + 1, len(matrix)):
            count = -1
            count_simetr = -1
            array = []
            array_simetr = []
            for j in range(len(matrix[0])):
                if matrix[i][j] > matrix[l][j]:
                    Kplus.append(j)
                    count_simetr += 1
                    for k in range(count_simetr, len(Kplus)):
                        array_simetr.append(array_w[Kplus[k]] * (matrix[i][j] - matrix[l][j]))
                if matrix[i][j] == matrix[l][j]:
                    Kdorivnuye.append(j)
                if matrix[i][j] < matrix[l][j]:
                    Kminus.append(j)
                    count += 1
                    for k in range(count, len(Kminus)):
                        array.append(array_w[Kminus[k]] * (matrix[l][j] - matrix[i][j]))

            try:
                matrixDab[i][l] = round(max(array) / max(max_vidhilennia[m] for m in Kminus), 3)
            except:
                matrixDab[i][l] = 0
            try:
                matrixDab[l][i] = round(max(array_simetr) / max(max_vidhilennia[m] for m in Kplus), 3)
            except:
                matrixDab[l][i] = 0
            Pplus = find_P(Kplus)
            Pminus = find_P(Kminus)
            Pdorivnue = find_P(Kdorivnuye)
            Pplus_simetric = Pminus
            matrixCab[i][l] = round((Pdorivnue + Pplus) / (sum(array_w)), 3)
            matrixCab[l][i] = round((Pdorivnue + Pplus_simetric) / (sum(array_w)), 3)
            Kplus.clear()
            Kdorivnuye.clear()
            Kminus.clear()
    # print("Матриця індексів узгодження:")
    # print_matrix(matrixCab)
    # print("Матриця індексів неузгодження:")
    # print_matrix(matrixDab)

    for i in range(len(matrixCab)):
        for j in range(len(matrixCab)):
            if matrixCab[i][j] >= c and matrixDab[i][j] <= d:
                matrix_R[i][j] = 1
    # print("Відношення на множині альтернатив: ")
    # print_matrix(matrix_R)
    color = [0] * len(matrix_R)

    if not check_cycle(matrix_R, color):
        for j in range(1, len(matrix_R)+1):
            for i in combinations([k for k in range(0, len(matrix_R))], j):
                if vnutrishnya_stiykist(i, matrix_R) and zovnishna_stiykist(i, matrix_R):
                    # print("Ядро для відношення", list(k+1 for k in i))
                    return list(i)
    else:
        return 0


def change_c_and_d_simultaneously():  # змінюємо с та d одночасно та будуємо графіки
    array_d = []
    array_c = []
    array_len_rozviazok = []
    n_d = list(np.arange(0, 0.51, 0.01))
    for i in range(len(n_d)):
        n_d[i] = round(n_d[i], 2)

    n_c = list(np.arange(1, 0.49, -0.01))
    for i in range(len(n_c)):
        n_c[i] = round(n_c[i], 2)
    counter = 0
    array_numberiter=[]
    for d, c in zip(n_d, n_c):
        rozviazok = Electre1(c, d)
        if type(rozviazok) == list:
            counter +=1
            array_numberiter.append(counter)
            array_len_rozviazok.append(len(rozviazok))
        else:
            continue

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=array_numberiter, y=array_len_rozviazok))
    fig.update_layout(legend_orientation="h",
                      legend=dict(x=.5, xanchor="center"),
                      title="Залежність розміру ядра від c та d",
                      xaxis_title="номер ітерації",
                      yaxis_title="Розмір ядра",
                      margin=dict(l=0, r=0, t=30, b=0))
    fig.write_image("figs.png")


def change_c_and_d(): # змінюємо с та d та будуємо графіки для кожного випадку
    c_const = 0.5
    array_d = []
    array_c = []
    d_const = 0.49
    array_len_rozviazok=[]
    n = list(np.arange(0, 0.51, 0.01))
    for i in range(len(n)):
        n[i] = round(n[i], 2)

    for d in n:
        rozviazok = Electre1(c_const, d)
        if type(rozviazok) == list:
            array_d.append(d)
            array_len_rozviazok.append(len(rozviazok))
        else:
            continue
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=array_d, y=array_len_rozviazok))
    fig.update_layout(legend_orientation="h",
                      legend=dict(x=.5, xanchor="center"),
                      title="Залежність розміру ядра від d",
                      xaxis_title="d",
                      yaxis_title="Розмір ядра",
                      margin=dict(l=0, r=0, t=30, b=0))
    fig.write_image("fig1.png")

    array_len_rozviazok.clear()
    n = list(np.arange(0.5, 1.01, 0.01))
    for i in range(len(n)):
        n[i] = round(n[i], 2)

    for c in n:
        rozviazok = Electre1(c, d_const)
        if type(rozviazok) == list:
            array_c.append(c)
            array_len_rozviazok.append(len(rozviazok))
        else:
            continue

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=array_c, y=array_len_rozviazok))
    fig.update_layout(legend_orientation="h",
                      legend=dict(x=.5, xanchor="center"),
                      title="Залежність розміру ядра від c",
                      xaxis_title="с",
                      yaxis_title="Розмір ядра",
                      margin=dict(l=0, r=0, t=30, b=0))
    fig.write_image("fig2.png")


Electre1(c, d)
change_c_and_d()
change_c_and_d_simultaneously()


