import os
import glob
import csv



output_dir = 'all_input'
swc_fir = 'all_swc'


swc_file_list = sorted(glob.glob(swc_fir + '/*.swc'))

for each_swc_file in swc_file_list:

    try:
        file_list_csv_content = []
        with open(each_swc_file, newline='') as f:
            reader = csv.reader(f,delimiter=' ')
            for row in reader:
                file_list_csv_content.append(row)

        useful_idx = []

        useful_idx.append([])

        for each_profile in file_list_csv_content:
            if (each_profile[6] == str(-1)):
                useful_idx[0].append(each_profile[0])


        for ii in range(25):
            useful_idx.append([])
            for each_last_level_idx in useful_idx[ii]:
                for each_profile in file_list_csv_content:
                    if (each_profile[6] == str(each_last_level_idx)):
                        useful_idx[ii+1].append(each_profile[0])

        new_useful_idx = []
        for each_list in useful_idx:
            new_useful_idx = new_useful_idx + each_list

        useful_idx = []
        for each_list in new_useful_idx:
            useful_idx.append( int(each_list))

        useful_idx = sorted(useful_idx)

        new_file_list_csv_content = []
        for each_inx in useful_idx:
            for each_profile in file_list_csv_content:
                if (each_profile[0] == str(each_inx)):
                    new_file_list_csv_content.append(each_profile)

        with open(( output_dir + '/'+  each_swc_file.split('/')[-1] ), 'w', newline='') as csvfile_out:
            spamwriter = csv.writer(csvfile_out, delimiter=' ')
            for row in new_file_list_csv_content:
                spamwriter.writerow(row)
            
    except:
        print(each_swc_file.split('/')[-1] + ' is bad')
