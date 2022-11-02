import pandas as pd
import plotly.graph_objects as go
import os
import numpy as np
from Helpers.IR_calc import IR_calculation


def compare_all_exp(path, mat = 'Material', IR = False, sr = 2e6, th = 0.8, th_stress = 0.1, th_temperature = 0.055):

    dir = os.listdir(path)
    exp = [item for item in dir if '#' in item.split()[-1]]

    fig1 = go.Figure()
    fig1.update_layout(template = 'none', 
                        font=dict(size=16),
                        title = f'Stress-Strain curves for {mat}')
    fig1.update_xaxes(title = 'Strain')
    fig1.update_yaxes(title = 'Stress, [MPa]')

    fig2 = go.Figure()
    fig2.update_layout(template = 'none', 
                        font=dict(size=16),
                        title = f'Temperatures for {mat},',
                        )
    fig2.update_xaxes(title = 'Time, [mks]')
    fig2.update_yaxes(title = 'Temperature rise, [C]')

    result = []

    for item in exp:
        num = item.split('#')[1]
        exp_path = path + item + '/'
        exp_data = pd.read_csv(exp_path+'Stress-Strain True.csv')
        parameters = pd.read_csv(exp_path+'Parameters.txt', sep = ' ', header = None)
        fig1.add_trace(add_data_to_report(exp_data, item))

        result.append(pd.DataFrame({'specimen': item,
                            'diameter[m]': parameters.iloc[0][2],
                            'length[m]': parameters.iloc[1][2],
                            'Ult_Stress': exp_data[' Stress'].max(),
                            'Strain4Ult_Stress': exp_data['# Strain'][exp_data[' Stress'].idxmax()]}, index = [num]))
        if IR:
            files = os.listdir(IR)
            files = [file for file in files if file.split('.')[-1]=='hcc']
            for file in files:
                if num == file.split('_')[2].split('.')[0]:
                    print(f"imagine {file}")
                    subplot = IR_calculation(IR + file, 
                        np.array(exp_data[' Stress']),
                        np.array(exp_data['# Strain']),
                        np.arange(0,(len(exp_data)-1)/sr, 1/sr),
                        tr_c = th,                                 # This is a parameter of IR movie filtration
                        material = mat,                      # This is a title of Material for the plot title
                        specimen = item,                      # This is a title of Specimen for the plot title
                        th_stress = th_stress,
                        th_temperature = th_temperature)

                    subplot.write_html(f'{IR}Specimen_{num}_Stress_and_temperature.html')
                

    fin_table = pd.concat(result)

    return fig1, fin_table

def add_data_to_report(data, title):
    trace_mech = go.Scatter(x = data['# Strain'], y = data[' Stress'], name = f'{title} ')
    return trace_mech    