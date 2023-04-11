


from scoop import futures

# if __name__ == "__main__":
    # returnValues = list(futures.map(helloWorld, range(16)))
    # print("\n".join(returnValues))




import os
# os.system("nrnivmodl mechanisms")

import bluepyopt
import json
import pprint
import local_model
import local_evaluator_v7
import glob
import sys


pp = pprint.PrettyPrinter(indent=2)





def evaluate_each_json_and_document(each_iteration):
    timeout = 20

    soma_threashhold = -20
    dend_threashhold = -55

    morphology_filename, feature_filename, protocal_filename, mechanisms_filename, parameter_filename = get_file_names(each_iteration)

        
    evaluator = making_evaluator(
            morphology_filename, 
            feature_filename, 
            protocal_filename, 
            mechanisms_filename, 
            parameter_filename, 
            soma_threashhold, 
            dend_threashhold,
            timeout)
    hof_list = json.load(open(each_iteration['file_name']))
        

    each_hof_response = []
    for each_hof_para in hof_list:

        responses = evaluator.run_protocols(protocols=local_evaluator_v7.define_protocols(protocal_filename).values(), param_values=each_hof_para)
        scores = evaluator.fitness_calculator.calculate_scores(responses)
        values = evaluator.fitness_calculator.calculate_values(responses)

        for each_trace in responses:
            responses[each_trace] = {'time':responses[each_trace]['time'].tolist(), 'voltage':responses[each_trace]['voltage'].tolist()}
            
        each_hof_response.append({'responses':responses, 'scores':scores, 'values': values})


        # import scipy.io
        # out_file_name = each_iteration['cell_id']+'_stage_'+each_iteration['stage_id']+'_iteration_'+each_iteration['iteration_id']+'hof_responses.mat'
        # out_file_name = os.path.join(log_dir,out_file_name) 
        # scipy.io.savemat(out_file_name, mdict={'whatever_data': each_hof_response})

    out_file_name = each_iteration['cell_id']+'_stage_'+each_iteration['stage_id']+'_iteration_'+each_iteration['iteration_id']+'_hof_responses.json'
    making_pretty_json(os.path.dirname(each_iteration['file_name']), each_hof_response, out_file_name)



def making_pretty_json(output_dir, log, out_file_name):
    json_string = json.dumps(log,indent=4, sort_keys=True)
    with open(os.path.join(output_dir,out_file_name), 'w') as outfile:
        outfile.write(json_string)



def get_log_file_id( input_dir):
    file_list = sorted(glob.glob(input_dir+'/*iteration*_halloffame.json'))
    file_dict = []
    for files in file_list:
        cell_id = files.split('/')[-1].split('_')[0]
        stage_id = files.split('/')[-1].split('_')[2]
        iteration_id = files.split('/')[-1].split('_')[4]

        file_dict.append({
            'file_name':files, 
            'cell_id':cell_id,
            'stage_id':stage_id,
            'iteration_id':iteration_id,
            'input_dir': input_dir
        })

    return file_dict




def get_file_id(command_line_input_index, input_dir):
    file_list = sorted(glob.glob(input_dir+'/*_feature_stage_0.json'))
    new_file_list = []
    for files in file_list:
        new_file_list.append( files.split('/')[-1].split('_')[0])


    file_id = new_file_list[int(command_line_input_index[1])]
    return file_id




def get_file_names(each_iteration):
    morphology_filename = each_iteration['input_dir'] + '/'+each_iteration['cell_id']+'_transformed.swc'
    feature_filename = os.path.join(each_iteration['input_dir'],each_iteration['cell_id']+'_feature_stage_' + each_iteration['stage_id'] + '.json') 
    protocal_filename = os.path.join(each_iteration['input_dir'],each_iteration['cell_id']+'_protocol_stage_' + each_iteration['stage_id'] + '.json') 
    mechanisms_filename = os.path.join(each_iteration['input_dir'],'mechanisms_stage_' + each_iteration['stage_id'] + '.json') 
    parameter_filename = os.path.join(each_iteration['input_dir'],'parameters_stage_' + each_iteration['stage_id'] + '.json') 
        
    return morphology_filename,feature_filename,protocal_filename,mechanisms_filename,parameter_filename


def making_evaluator(morphology_filename, feature_filename, protocal_filename, mechanisms_filename_0, parameter_filename_0, soma_threashhold, dend_threashhold, timeout):


    # 'do_replace_axon' -> replace the axon with a AIS.
    morphology = bluepyopt.ephys.morphologies.NrnFileMorphology(morphology_filename, do_replace_axon=True)
    parameters = local_model.define_parameters(parameter_filename_0)
    mechanisms = local_model.define_mechanisms(mechanisms_filename_0)
    local_cell = bluepyopt.ephys.models.CellModel(
        'cell_'+morphology_filename.split("/")[-1].split(".")[0], 
        morph=morphology, 
        mechs=mechanisms, 
        params=parameters)

    print(local_cell)

    ### Building Evaluator: Protocols and eFeatures (objectives)

    fitness_protocols = local_evaluator_v7.define_protocols(protocal_filename)
    fitness_calculator = local_evaluator_v7.define_fitness_calculator(fitness_protocols, feature_filename, soma_threashhold, dend_threashhold)

    print('\n'.join('%s' % protocol for protocol in fitness_protocols.values()))
    feature_configs = json.load(open(feature_filename))
    pp.pprint(feature_configs)


    evaluator = bluepyopt.ephys.evaluators.CellEvaluator( 
            cell_model=local_cell, 
            param_names=[param.name for param in local_cell.params.values() if not param.frozen], 
            fitness_protocols=fitness_protocols, 
            fitness_calculator=fitness_calculator, 
            sim=bluepyopt.ephys.simulators.NrnSimulator(),
            timeout = timeout,
            isolate_protocols = True)
            
    return evaluator

if __name__ == "__main__":
    ### Settings

    input_dir = 'Exc_L2-3_LINC00507_FREM3_features_v8'
    command_line_input_index = sys.argv

    for ii in range(int(command_line_input_index[1]), int(command_line_input_index[2])):
        file_id = get_file_id(['0', str(ii), command_line_input_index[3] ], input_dir)

        output_dir = file_id+'_seed_'+ command_line_input_index[3] +'_Outputs'
        if not (os.path.isdir(output_dir)):
            print(output_dir)
            raise()

        file_dict = get_log_file_id(output_dir)
        pp.pprint(file_dict)
        aaa = list(futures.map(evaluate_each_json_and_document,file_dict))
    os.system('for n in $(qstat -f|grep cscl|grep -v u$|cut -d @ -f 2|cut -d . -f 1|sort -u);do ssh $n pkill -u wuy2;done')

