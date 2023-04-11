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
            if (each_profile[1] == str(4)):
                each_profile[1] = str(3)




        with open(( output_dir + '/'+  each_swc_file.split('/')[-1] ), 'w', newline='') as csvfile_out:
            spamwriter = csv.writer(csvfile_out, delimiter=' ')
            for row in file_list_csv_content:
                spamwriter.writerow(row)
            
    except:
        print(each_swc_file.split('/')[-1] + ' is bad')
