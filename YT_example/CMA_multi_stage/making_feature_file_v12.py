
import os

import pickle
import numpy
import json

import glob

def main():

    feature_filename = [
        'features_stage_0.json',
        'features_stage_2_correction.json',
        'features_stage_2_correction.json'
    ]

    feature_filename_negative = 'features_negative.json'

    file_name_append = [
        '_stage_0',
        '_stage_1',
        '_stage_2'
    ]

    check_AIS = [
        False, 
        False, 
        False]

    tracie_picking_method = [
        'Negative_plus_one', 
        'Six_each', 
        'Six_each']

    protocol_filename = [
        'protocols.json',
        'protocols.json',
        'protocols.json'] 
        
    input_dir = 'all_ephys'
    output_dir = 'all_input'
    swc_fir = 'all_swc'

    if not (os.path.isdir(output_dir)): 
        os.mkdir(output_dir)

    for ii in range(len(feature_filename)):
        making_files_feature_protocol(feature_filename[ii], file_name_append[ii], protocol_filename[ii], input_dir, output_dir,check_AIS[ii],tracie_picking_method[ii], feature_filename_negative)

    os.system('cp '+swc_fir+'/*'+ ' '+ output_dir)



def making_files_feature_protocol(feature_filename, file_name_append, protocol_filename, input_dir, output_dir, check_AIS, tracie_picking_method, feature_filename_negative):

    feature_configs = json.load(open(feature_filename))
    feature_config_negative = json.load(open(feature_filename_negative))


    protocol_configs = json.load(open(protocol_filename))

    feature_configs = feature_configs[list(feature_configs)[0]]
    feature_config_negative = feature_config_negative[list(feature_config_negative)[0]]
    protocol_configs = protocol_configs[list(protocol_configs)[0]]


    all_cells_data = read_all_cell_data(input_dir)

    selected_features = find_seleted_feature(feature_configs)
    
    # feature_std = getting_std(all_cells_data, selected_features)
    feature_std = json.load(open('std_out.json'))

    all_sweep_time = extract_time(all_cells_data)

    for each_cell in all_cells_data:
        
        try:
        
            all_current = []
            all_spike = []

            for sweep in all_cells_data[each_cell]:
                if not (all_cells_data[each_cell][sweep]['00_custom_extra_current_mean'] in all_current):
                    all_current.append(all_cells_data[each_cell][sweep]['00_custom_extra_current_mean'])
                    all_spike.append(len(all_cells_data[each_cell][sweep]['peak_time']))

            
            # all_current_want = list(set(all_current))
            if tracie_picking_method == 'Negative': 
                all_current_want = current_picker_negative_only(all_current,all_spike)

            if tracie_picking_method == 'All': 
                all_current_want = all_current


            elif tracie_picking_method == 'Negative_plus_one': 
                all_current_want = current_picker_negative_only(all_current,all_spike)
                all_current_want.append(current_picker_highest_not_firing(all_current,all_spike))
                all_current_want = list(set(all_current_want))


            elif tracie_picking_method == "Spike": 
                all_current_want = current_picker_firing_only(all_current,all_spike)

            elif tracie_picking_method == "Five_each": 
                all_current_want = [current_picker_lowest(all_current,all_spike),
                                current_picker_highest_not_firing(all_current,all_spike),
                                current_picker_lowest_firing(all_current,all_spike),
                                current_picker_send_lowest_firing(all_current,all_spike),
                                current_picker_highest_firing(all_current,all_spike)]
                all_current_want = list(set(all_current_want))
                if (len(all_current_want) != 5):
                    print(each_cell+ ' has less than 5 usful trace')


            elif tracie_picking_method == "Six_each": 
                all_current_want = [current_picker_lowest(all_current,all_spike),
                                current_picker_highest_not_firing(all_current,all_spike),
                                current_picker_lowest_firing(all_current,all_spike),
                                current_picker_send_lowest_firing(all_current,all_spike),
                                current_picker_3rd_lowest_firing(all_current,all_spike),
                                current_picker_highest_firing(all_current,all_spike)]        

                all_current_want = list(set(all_current_want))
                if (len(all_current_want) != 6):
                    print(each_cell+ ' has less than 6 usful trace')


            elif tracie_picking_method == "Seven_each": 
                all_current_want = [current_picker_lowest(all_current,all_spike),
                                current_picker_sec_highest_not_firing(all_current,all_spike),
                                current_picker_highest_not_firing(all_current,all_spike),
                                current_picker_lowest_firing(all_current,all_spike),
                                current_picker_send_lowest_firing(all_current,all_spike),
                                current_picker_3rd_lowest_firing(all_current,all_spike),
                                current_picker_highest_firing(all_current,all_spike)]    
                all_current_want = list(set(all_current_want))
                if (len(all_current_want) != 7):
                    print(each_cell+ ' has less than 7 usful trace')


            else: 
                raise()



            all_current_want = list(set(all_current_want))




            feature_for_this_cell = {}
            protocol_for_this_cell = {}


            for current_target in all_current_want:
                list_of_useful_sweep = []
                for sweep in all_cells_data[each_cell]:
                    if (all_cells_data[each_cell][sweep]['00_custom_extra_current_mean'] == current_target) :
                        list_of_useful_sweep.append(sweep)
                
                feature_for_this_current = {'soma':{}}
                protocol_for_this_current = {'stimuli':[{}]}                    
                
                if (current_target>0):
                    for each_feature in feature_configs['soma']:
                        data_temp = []
                        for sweep in list_of_useful_sweep:
                            still_good = True
                            if not (all_cells_data[each_cell][sweep][each_feature] is not None):
                                still_good = False
                            elif not (len(all_cells_data[each_cell][sweep][each_feature]) !=0 ):
                                still_good = False
                            if still_good:
                                data_temp.append(all_cells_data[each_cell][sweep][each_feature][0])
                        if (len(data_temp) !=0 ):
                            feature_for_this_current['soma'][each_feature] = [0.0, 0.0]
                            feature_for_this_current['soma'][each_feature][0] = float(numpy.mean(data_temp))
                            if float(numpy.absolute(numpy.mean(data_temp)))  == 0 :
                                feature_for_this_current['soma'][each_feature][1] = 0.05
                            elif (feature_std[each_feature] == 0.0) or not (float('-inf') < float(feature_std[each_feature]) < float('inf') ):
                                feature_for_this_current['soma'][each_feature][1] = float(numpy.absolute(numpy.mean(data_temp)))*0.05 
                            else:
                                feature_for_this_current['soma'][each_feature][1] = feature_std[each_feature] 
                else:
                    for each_feature in feature_config_negative['soma']:
                        data_temp = []
                        for sweep in list_of_useful_sweep:
                            still_good = True
                            if not (all_cells_data[each_cell][sweep][each_feature] is not None):
                                still_good = False
                            elif not (len(all_cells_data[each_cell][sweep][each_feature]) !=0 ):
                                still_good = False
                            if still_good:
                                data_temp.append(all_cells_data[each_cell][sweep][each_feature][0])
                        if (len(data_temp) !=0 ):
                            feature_for_this_current['soma'][each_feature] = [0.0, 0.0]
                            feature_for_this_current['soma'][each_feature][0] = float(numpy.mean(data_temp))
                            if float(numpy.absolute(numpy.mean(data_temp)))  == 0 :
                                feature_for_this_current['soma'][each_feature][1] = 0.05
                            elif (feature_std[each_feature] == 0.0) or not (float('-inf') < float(feature_std[each_feature]) < float('inf') ):
                                feature_for_this_current['soma'][each_feature][1] = float(numpy.absolute(numpy.mean(data_temp)))*0.05 
                            else:
                                feature_for_this_current['soma'][each_feature][1] = feature_std[each_feature] 


                first_sweep_for_the_current = list_of_useful_sweep[0]
                if check_AIS:
                    still_good = True

                    if not (all_cells_data[each_cell][first_sweep_for_the_current]["AP_begin_time"] is not None):
                        still_good = False
                    elif not (len(all_cells_data[each_cell][first_sweep_for_the_current]["AP_begin_time"]) !=0 ):
                        still_good = False
                    if still_good:
                        feature_for_this_current['AIS'] = {"check_AISInitiation": [1.0, 0.05]}
            
                protocol_for_this_current['stimuli'][0]['delay'] = round(all_cells_data[each_cell][first_sweep_for_the_current]['00_custom_extra_stim_start'])
                protocol_for_this_current['stimuli'][0]['amp'] = all_cells_data[each_cell][first_sweep_for_the_current]['00_custom_extra_current_mean'].tolist()*0.001
                protocol_for_this_current['stimuli'][0]['duration'] = all_sweep_time[0]
                protocol_for_this_current['stimuli'][0]['totduration'] = 3000


                if (len(protocol_configs)>1):
                    for each_extra in protocol_configs:
                        if (each_extra != 'stimuli'): 
                            protocol_for_this_current[each_extra] = protocol_configs[each_extra]
                    
                    # protocol_for_this_sweep.update({'extra_recordings':  protocol_configs['extra_recordings']})

                feature_for_this_cell.update({first_sweep_for_the_current : feature_for_this_current})
                protocol_for_this_cell.update({first_sweep_for_the_current : protocol_for_this_current})





            json_string = json.dumps(feature_for_this_cell,indent=4, sort_keys=True)
            out_file_name = each_cell +'_feature'+file_name_append+'.json'
            with open(os.path.join(output_dir,out_file_name), 'w') as outfile:
                outfile.write(json_string)

            json_string = json.dumps(protocol_for_this_cell,indent=4, sort_keys=True)
            out_file_name = each_cell +'_protocol'+file_name_append + '.json'
            with open(os.path.join(output_dir,out_file_name), 'w') as outfile:
                outfile.write(json_string)
        except:
            print(each_cell+ ' is bad')






def read_all_cell_data(input_dir):
    file_list = glob.glob(input_dir+'/*pickle')

    all_cells_data = {}
    for files in file_list:
        with (open(files, "rb")) as openfile:
            all_cells_data.update({files.split('/')[-1].split('.')[-2]:pickle.load(openfile)})
    return all_cells_data

def find_seleted_feature(feature_configs):
    all_features = []
    for each_feature in list(feature_configs['soma']):
        all_features.append(each_feature)
    selected_features = list(set(all_features))
    return selected_features    

def getting_std(all_cells_data, selected_features):
    feature_std = {}
    for each_feature in selected_features:
        std_temp = []
        avg_temp = []

        for cells in all_cells_data:
            all_current = []
            for sweep in all_cells_data[cells]:
                all_current.append(all_cells_data[cells][sweep]['00_custom_extra_current_mean'])
            all_current_list = list(set(all_current))
            duplicated_current = []
            for each_current in all_current_list:
                if (all_current.count(each_current) > 1):
                    duplicated_current.append(each_current)
        
            for each_current in duplicated_current:
                number_temp = []
                for sweep in all_cells_data[cells]:
                    if (all_cells_data[cells][sweep]['00_custom_extra_current_mean'] == each_current) and (all_cells_data[cells][sweep][each_feature] is not None):
                        
                        
                        if (type(all_cells_data[cells][sweep][each_feature]) == numpy.ndarray) | (type(all_cells_data[cells][sweep][each_feature]) == numpy.float32) :
                            feature_temp = all_cells_data[cells][sweep][each_feature].tolist()
                        else:
                            feature_temp = all_cells_data[cells][sweep][each_feature]
                        
                        if isinstance(feature_temp, list):
                            for item in all_cells_data[cells][sweep][each_feature]:
                                number_temp.append(item)
                        else:
                            number_temp.append(all_cells_data[cells][sweep][each_feature])

                if (len(number_temp)>1):
                    std_temp.append(numpy.std(number_temp))

        if (each_feature == 'steady_state_voltage'):
            feature_std.update({each_feature : float(numpy.mean(std_temp))*0.25})
        elif (each_feature == 'steady_state_voltage_stimend'):
            feature_std.update({each_feature : float(numpy.mean(std_temp))*0.125})
        elif (each_feature == 'voltage_base'):
            feature_std.update({each_feature : float(numpy.mean(std_temp))*0.25})
        elif (each_feature == 'sag_amplitude'):
            feature_std.update({each_feature : float(numpy.mean(std_temp))*0.25})
        elif (each_feature == 'decay_time_constant_after_stim'):
            feature_std.update({each_feature : float(numpy.mean(std_temp))*0.25})
        else:
            feature_std.update({each_feature : float(numpy.mean(std_temp))})


    return feature_std

def extract_time(all_cells_data):
    all_sweep_time = []
    for cells in all_cells_data:
        for sweep in all_cells_data[cells]:
            all_sweep_time.append(round(all_cells_data[cells][sweep]['00_custom_extra_stim_end'] - all_cells_data[cells][sweep]['00_custom_extra_stim_start']))
    all_sweep_time = list(set(all_sweep_time))

    if not (len(all_sweep_time) == 1):
        raise()



    for cells in all_cells_data:
        for sweep in all_cells_data[cells]:
            if (round(all_cells_data[cells][sweep]['00_custom_extra_current_std']) != 0.0):
                raise()
    return all_sweep_time

def current_picker_lowest(all_current,all_spike):
    return min(all_current)

def current_picker_highest_firing(all_current,all_spike):
    c_temp = []
    for ii in range(len(all_spike)):
        if (all_spike[ii]>0):
            c_temp.append(all_current[ii])
    return max(c_temp)

def current_picker_lowest_firing(all_current,all_spike):
    c_temp = []
    for ii in range(len(all_spike)):
        if (all_spike[ii]>0) and (all_current[ii]>0):
            c_temp.append(all_current[ii])
    return min(c_temp)

def current_picker_highest_not_firing(all_current,all_spike):
    lnf = current_picker_lowest_firing(all_current,all_spike)
    c_temp = []
    for ii in range(len(all_spike)):
        if (all_spike[ii]==0) and (all_current[ii]<lnf): 
            c_temp.append(all_current[ii])
    if (len(c_temp)>0):
        return max(c_temp)
    else:
        return lnf

def current_picker_sec_highest_not_firing(all_current,all_spike):
    lnf = current_picker_highest_not_firing(all_current,all_spike)
    c_temp = []
    for ii in range(len(all_spike)):
        if (all_spike[ii]==0) and (all_current[ii]<lnf):
            c_temp.append(all_current[ii])
    if (len(c_temp)>0):
        return max(c_temp)
    else:
        return lnf


def current_picker_send_lowest_firing(all_current,all_spike):
    lnf = current_picker_lowest_firing(all_current,all_spike)
    c_temp = []
    for ii in range(len(all_spike)):
        if (all_spike[ii]>0) and (all_current[ii]>lnf):
            c_temp.append(all_current[ii])
    if (len(c_temp)>0):
        return min(c_temp)
    else:
        return lnf


def current_picker_3rd_lowest_firing(all_current,all_spike):
    lnf = current_picker_send_lowest_firing(all_current,all_spike)
    c_temp = []
    for ii in range(len(all_spike)):
        if (all_spike[ii]>0) and (all_current[ii]>lnf):
            c_temp.append(all_current[ii])
    if (len(c_temp)>0):
        return min(c_temp)
    else:
        return lnf

def current_picker_negative_only(all_current,all_spike):
    c_temp = []
    for ii in range(len(all_spike)):
        if (all_current[ii]<0):
            c_temp.append(all_current[ii])
    return c_temp

def current_picker_firing_only(all_current,all_spike):
    c_temp = []
    for ii in range(len(all_spike)):
        if (all_spike[ii]>0):
            c_temp.append(all_current[ii])
    return c_temp



if __name__ == "__main__":
    main()

            



