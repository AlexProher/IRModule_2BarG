import os

from plotly.subplots import make_subplots

import plotly.graph_objects as go
import pandas as pd
import numpy as np
import Helpers.cut_temperature as ct

try:
    from TelopsToolbox.hcc.readIRCam import read_ircam
    import TelopsToolbox.utils.image_processing as ip
except:
    os.system("pip3 install PythonTelopsToolbox-0.0.1/TelopsToolbox-0.0.1-py3-none-any.whl")
    from TelopsToolbox.hcc.readIRCam import read_ircam
    import TelopsToolbox.utils.image_processing as ip
    print('Sorry I installed TelopsToolbox in your PC, I really need it')


def IR_calculation(way_to_file, stress, strain, exp_time, tr_c = 0.9, material = 'Material', specimen = 'Specimen', th_stress = 0.1, th_temperature = 0.055):

    """
       This function create the *.html in folder with *.hcc file
       one html contain raw IR movie
       another contain movie after substraction mean of first five
       frames and binarisation with tr_c (default 0.9), it means hat
       all points less the 0.9*max(current_frame) is "0" other "1"
       each new movie with another tr_c saves to new html   
    """
    
    data, header, specialPixel, nonSpecialPixel = read_ircam(way_to_file)
    
    header_df = pd.DataFrame(header)
       
    numero_header = 0
    this_header = header_df.iloc[numero_header]
    frame_rate = this_header[20]

    movie = [ip.form_image(header, item)[0]-273.15 for item in data]

    initial_movie = wrapper(movie, material, specimen, frame_rate)


    mean_frame = np.array(movie[0])
    for item in movie[1:5]:
        mean_frame+=np.array(item)
    mean_frame = mean_frame/5

    zeroed_movie = [item - mean_frame for item in movie]
    masks = [bin_image(item, item.max()*tr_c) for item in movie]
    bin_movie = [zeroed_movie[item]*masks[item] for item in range(len(masks))]

    treated_movie = wrapper(bin_movie, material, specimen, frame_rate)

    treated_movie.write_html(way_to_file[:-4]+f'treated_movie_tr-{tr_c}.html')
    initial_movie.write_html(way_to_file[:-4]+'_raw_movie.html')


    temperature = []
    time = []
    for ind in range(len(bin_movie)):
        if np.array(masks[ind]).sum():
            temperature.append(bin_movie[ind].sum()/np.array(masks[ind]).sum())
        else:
            temperature.append(0)
        time.append(ind/this_header[20])

    temperature, ir_time, eq_strain = ct.cut_signal(strain, temperature, exp_time, time, th_stress, th_temperature)
    temperature_data = pd.DataFrame({'Strain': eq_strain,
                                    'Temperature': temperature})
    temperature_data.to_csv(f'{way_to_file[:-4]}_data.csv')

    figure = plot_subplot(stress, strain, eq_strain, temperature, material, specimen)
    
    return figure

def bin_image(image, tresh):
    image = [list(map(lambda x: 1 if (x > tresh) else 0, line)) for line in image]
    return image
  
    
def plot_subplot(stress, strain, eq_strain, temperature, material, specimen):

    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    fig2.update_layout(template = 'plotly_white', width=800, height=600,
                    title = f'True Strain vs Temperature, {material} specimen {specimen}')
    fig2.add_trace(go.Scatter(x = strain, 
                                y = stress,
                                name = 'True Stress'),
                                secondary_y=False)
    fig2.add_trace(go.Scatter(x = eq_strain, 
                                y = temperature, 
                                name = 'Temperature',
                                mode = 'markers'),
                                secondary_y=True)

    fig2.update_xaxes(title_text="Strain")

    fig2.update_yaxes(title_text="Stress, MPa", secondary_y=False)
    fig2.update_yaxes(title_text="Temperature, C", secondary_y=True)  

    return fig2
def wrapper(data, material, specimen, frame_rate):
    fig_dict = {
        "data": [],
        "layout": { 'yaxis': dict(domain=[0.25, 1]),
                    'yaxis2': dict(domain=[0, 0.2]),
                    'width' : 1000,
                    'height': 800,
                    'title': 'Matetial: ' + material + ' specimen №' + specimen
                    },
        "frames": [],
        "annotation": {}
    }


    fig_dict["layout"]["hovermode"] = "closest"
    fig_dict["layout"]["updatemenus"] = [
        {
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 500, "redraw": True},
                                    "fromcurrent": True, "transition": {"duration": 300,
                                                                        "easing": "quadratic-in-out"}}],
                    "label": "Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": True},
                                    "mode": "immediate",
                                    "transition": {"duration": 0}}],
                    "label": "Pause",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top"
        }
    ]

    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 20},
            "prefix": "",
            "visible": True,
            "xanchor": "right"
        },
        "transition": {"duration": 300, "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": []
    }

    #make data
    first_image = data[0]

    frame_zero = go.Heatmap(z = first_image)
    plot_zero = go.Scatter(y = np.array(first_image).max(axis=0), yaxis ='y2')

    fig_dict['data'].append(frame_zero)
    fig_dict['data'].append(plot_zero)


    # make frames
    for pic in range(len(data)):
        
        current_image = data[pic]
        vertical_temp = np.array(current_image).max(axis=0)

        trace2 = go.Scatter(y = vertical_temp, yaxis ='y2',)
        trace1 = go.Heatmap(z = current_image, yaxis="y1")

        frame_n = {"data": [trace1, trace2], "name": str(pic)}

        slider_step = {"args": [[pic],
                                {"data": {"duration": 300, "redraw": False},
                                "mode": "immediate",
                                "transition": {"duration": 300}}
                                ],
                        "label": f'{round(pic/frame_rate*1e+6,3)} mks',
                        "method": "animate"}
                    
        fig_dict['layout']['yaxis2']['range'] = [0,max(vertical_temp)]
        fig_dict["frames"].append(frame_n)   
        sliders_dict["steps"].append(slider_step)

    fig_dict["layout"]["sliders"] = [sliders_dict]

    fig = go.Figure(fig_dict)
    return fig