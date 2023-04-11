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


        for each_profile in file_list_csv_content:
            if (each_profile[1] != str(2)):
                useful_idx.append(each_profile[0])

#        useful_idx = sorted(useful_idx)

        new_file_list_csv_content = []
        for each_inx in useful_idx:
            for each_profile in file_list_csv_content:
                if (each_profile[0] == str(each_inx)):
                    new_file_list_csv_content.append(each_profile)

        with open(( output_dir + '/'+  each_swc_file.split('/')[-1] ), 'w', newline='') as csvfile_out:
            spamwriter = csv.writer(csvfile_out, delimiter=' ')
            for row in new_file_list_csv_content:
                spamwriter.writerow(row)

        print(each_swc_file.split('/')[-1] + ' is done')


            
    except:
        print(each_swc_file.split('/')[-1] + ' is bad')
