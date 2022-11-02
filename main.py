from Helpers.comparison import compare_all_exp

# It is nessesary to install pandas, numpy, scipy, and plotly libs, 
# use 'pip3 install *lib_title' in terminal 
# Telops lib will be installed automaticaly if it is not

#Folder with results of experiment from 2BARG
path = 'C:/Users/dflws/Desktop/Like_a_new/mech_part/Denal920/'

#Folder with IR movie for chosen experiment
# It is nessesary that the numbers of IR files is equal with number of experiments
# of "EXP #1" in folder 'path' IR file should br titled like 
# "sometitle_you_want_1.hcc" use only "_" as a space between words
IR_path = 'C:/Users/dflws/Desktop/Like_a_new/thermal_part/Denal920/'

# IF you use another sample rate in oscilscope put it here:
sample_rate = 2e6
# Material title for report
material = 'Material'

# Th for IR filtration if you have IR movies
tr_c = 0.8


fig, table= compare_all_exp(path = path, 
                            mat = material, 
                            IR = IR_path, 
                            sr = sample_rate, 
                            th = tr_c)

# write here any path you whant to save mechanical report 
path = path
fig.write_html(f'{path}all_exp_mech.html')
table.to_csv(f'{path}all_exp_mech.csv')

    #IR Results will put in folder with IR movie. Enjoy it.