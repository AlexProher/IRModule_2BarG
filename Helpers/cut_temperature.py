import numpy as np
from scipy import interpolate

##
#Идея следующая Передаются два сигнала и соответствующие массивы времени
#Первый сигнал - сигнал деформаций он короче чем второй, но он лучше дескитезирован
#
#Второй сигнал - синал температуры его нужно интерполировать и обрезать по длине первого сигнала


def find_slope(sign1, sign2, th_stress, th_temperature): #sign1 - Сигнал деформаций (опорный), sign2 - Сигнал температуры
    #Функция ищет восходящий фронт сигнала по порогу чувствительности 0.01 от максимальной величины сигнала
    tr1 = sign1.max()*th_stress
    tr2 = sign2.max()*th_temperature

    return (np.where(sign1 > tr1)[0][0], 
            np.where(sign2 > tr2)[0][0])

def my_interpolation(t, data):
    xnew = np.arange(0,max(t),500*1e-9) #500 нс - величина обратная Частоте дискретизации 2ГГц
    f = interpolate.interp1d(t, data, kind = 'quadratic')
    ynew = f(xnew)
    return (xnew, ynew)

def cut_signal(signal1, signal2, time1, time2, th_stress, th_temperature):
    #Функция отрезвет сигнал температуры в соответствии с длиной сигнала деформаций
    #сначала интерполируем второй синал чтобы его можно было двигать плавно
    newTime2, newSignal2 = my_interpolation(time2, signal2)   
    p1, p2 = find_slope(np.array(signal1), newSignal2, th_stress, th_temperature)
    #Сдвигаем сигнал температуры влево так чтобы время обнаруженного подъема р1 совпало со временем р1
    newTime2 = time2 - newTime2[p2] + time1[p1]
    #new_signal2.time = new_signal2.time - 107e-6
    #отрезвем сигнал температуры сначала так чтобы были только положительные времена
    zero = np.where(newTime2 >= 0)[0][0]
    last = np.where(newTime2 >= time1[-1])[0][0]
    newTime2 = newTime2[zero-1:last]
    newSignal2 = signal2[zero-1:last]
    newTime2[0] = 0
    newSignal2[0] = 0
    eq_strain = [signal1[np.where(time1 >= item)[0][0]] for item in newTime2]

    
    return (newSignal2, newTime2, eq_strain)