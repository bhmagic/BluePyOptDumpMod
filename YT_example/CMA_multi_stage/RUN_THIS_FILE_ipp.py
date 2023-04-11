
import os
# os.system("nrnivmodl mechanisms")

import bluepyopt
import json
import pprint
import local_model
import local_evaluator_v7
import glob
import sys
import time
import logging
logger = logging.getLogger()
from datetime import datetime



pp = pprint.PrettyPrinter(indent=2)


def main(command_line_input_index):
    ### Settings
    input_dir = 'all_input'
    config_folder = 'config_v8'

    offspring_size = 4096
    max_ngen = [40, 200]
    documenting_step_size = max_ngen
    timeout = 10

    seed = command_line_input_index[2]

    stage_parameter_updating_ratio = [0.5,   1.0 ]
    soma_threashhold = -20
    dend_threashhold = -55

    file_id = get_file_id(command_line_input_index, input_dir)

    output_dir = file_id+'_seed_'+ seed +'_Outputs'
    if not (os.path.isdir(output_dir)): 
        os.mkdir(output_dir)




    os.system('cp '+config_folder+'/*'+ ' '+ output_dir)
    config_folder = str(output_dir)

    making_parameter_files(output_dir)

    morphology_filename, feature_filename, protocal_filename, mechanisms_filename, parameter_filename = get_file_names(file_id, input_dir, config_folder)

    os.system('cp '+morphology_filename +' '+ output_dir)
    for each_file in protocal_filename:
        os.system('cp '+each_file +' '+ output_dir)
    for each_file in feature_filename:
        os.system('cp '+each_file +' '+ output_dir)
    
    morphology_filename, feature_filename, protocal_filename, mechanisms_filename, parameter_filename = get_file_names(file_id, output_dir, output_dir)


    total_numner_of_stages = len(mechanisms_filename)

    for stage_number in range(total_numner_of_stages):
        if (max_ngen[stage_number]>0):
            if stage_number>=len(feature_filename):
                maxout_number = len(feature_filename)-1
                os.system('cp '+feature_filename[maxout_number] +' '+ feature_filename[maxout_number].split(str(maxout_number)+'.')[-2]+str(stage_number)+'.json' )
                os.system('cp '+protocal_filename[maxout_number] +' '+ protocal_filename[maxout_number].split(str(maxout_number)+'.')[-2]+str(stage_number)+'.json' )
            else:
                maxout_number = stage_number

            from ipyparallel import Client
            rc = Client(profile=os.getenv('IPYTHON_PROFILE'))

            logger.debug('Using ipyparallel with %d engines', len(rc))

            lview = rc.load_balanced_view()

            def mapper(func, it):
                start_time = datetime.now()
                ret = lview.map_sync(func, it)
                logger.debug('Generation took %s', datetime.now() - start_time)
                return ret

            map_function = mapper

            evaluator = making_evaluator(
                morphology_filename, 
                feature_filename[maxout_number], 
                protocal_filename[maxout_number], 
                mechanisms_filename[stage_number], 
                parameter_filename[stage_number], 
                soma_threashhold, 
                dend_threashhold,
                timeout,
                output_dir)

            
            import deap
            import deap.base
            # import deap.algorithms
            # import deap.tools
            hof = deap.tools.HallOfFame(40)
            # optimizer = bluepyopt.optimisations.DEAPOptimisation(
            #     seed=seed,
            #     evaluator=evaluator,
            #     offspring_size=offspring_size,
            #     map_function=map_function,
            #     hof=hof)
            
            # checkpoint_filename = os.path.join(output_dir,'_statge_'+str(stage_number)+'_checkpoint.pkl')

            # halloffame, log = run_stage(
            #     file_id, 
            #     checkpoint_filename, 
            #     output_dir, max_ngen[stage_number], 
            #     documenting_step_size[stage_number], 
            #     stage_number, 
            #     evaluator, 
            #     optimizer)

            optimiser = bluepyopt.deapext.optimisationsCMA.DEAPOptimisationCMA
            optimisation = optimiser(
                evaluator=evaluator, 
                seed=int(seed),
                offspring_size=offspring_size,
                map_function=map_function,
                hof=hof)
                
            pop, halloffame, log, hist = optimisation.run(
                max_ngen=max_ngen[stage_number],
                dump_location=output_dir)
            out_file_name = file_id +'_statge_'+ str(stage_number)+'_iteration_'+ str(1)+ '_halloffame.json'
            saving_hof(output_dir, evaluator, halloffame, out_file_name)


            if (stage_number != total_numner_of_stages-1):
                edit_next_stage_parameter_bounds(parameter_filename, stage_parameter_updating_ratio, stage_number, evaluator, halloffame)

            json_each_stage(file_id, output_dir, stage_number, evaluator, halloffame, log)

    #os.system('for n in $(qstat -f|grep cscl|grep -v u$|cut -d @ -f 2|cut -d . -f 1|sort -u);do ssh $n pkill -u wuy2;done')

    # crash_it()


def json_each_stage(file_id, output_dir, stage_number, evaluator, halloffame, log):
    out_file_name = file_id +'_statge_'+ str(stage_number)+ '_halloffame.json'
    saving_hof(output_dir, evaluator, halloffame, out_file_name)

    out_file_name = file_id +'_statge_'+ str(stage_number)+ '_log.json'
    making_pretty_json(output_dir, log, out_file_name)

def get_file_id(command_line_input_index, input_dir):
    file_list = sorted(glob.glob(input_dir+'/*_feature_stage_0.json'))
    new_file_list = []
    for files in file_list:
        new_file_list.append( files.split('/')[-1].split('_fea')[0])


    file_id = new_file_list[int(command_line_input_index[1])]
    return file_id


def making_parameter_files(config_folder):
    mechanisms_filename = sorted(glob.glob(config_folder+'/'+'mechanisms_stage_*.json'))
    parameter_filename = config_folder+'/'+'parameters_aim.json'
    for each_mech in mechanisms_filename:
        mech_in = json.load(open(each_mech))
        para_in = json.load(open(parameter_filename))
        keep_list = []
        for ii in range(len(para_in)):
            if ('mech' in list(para_in[ii])) and ('sectionlist' in list(para_in[ii])):
                if (para_in[ii]['mech'] in mech_in["all"]) or (para_in[ii]['mech'] in mech_in[para_in[ii]['sectionlist'] ]):
                    keep_list.append(ii)
            elif  (para_in[ii]['param_name'] == 'ena'):
                if (any(s.lower().startswith('na') for s in mech_in[para_in[ii]['sectionlist']])):
                    keep_list.append(ii)

            elif  (para_in[ii]['param_name'] == 'ek'):
                if (any(s.lower().startswith('k') for s in mech_in[para_in[ii]['sectionlist']])):
                    keep_list.append(ii)
            else:
                keep_list.append(ii)
        para_in = [para_in[ii] for ii in keep_list]
        parameter_out_filename = config_folder + '/' + 'parameters_stage_' + each_mech.split('.')[-2].split('_')[-1] + '.json'
        with open(parameter_out_filename, 'w') as outfile:
            outfile.write(json.dumps(para_in, indent=4, sort_keys=True))





def get_file_names(file_id, input_folder, config_folder):
    morphology_filename = input_folder + '/'+file_id+'_transformed.swc'

    feature_filename = sorted(glob.glob(input_folder+'/'+file_id+'_feature_stage_*.json'))
    protocal_filename = sorted(glob.glob(input_folder+'/'+file_id+'_protocol_stage_*.json'))
    mechanisms_filename = sorted(glob.glob(config_folder+'/'+'mechanisms_stage_*.json'))
    parameter_filename = sorted(glob.glob(config_folder+'/'+'parameters_stage_*.json'))

    # feature_filename = [
    #     os.path.join(input_folder,file_id+'_feature_stage_0.json') ,
    #     os.path.join(input_folder,file_id+'_feature_stage_1.json') ,
    #     os.path.join(input_folder,file_id+'_feature_stage_2.json')
    #     # os.path.join(input_folder,file_id+'_feature_stage_3.json')
    #     ]

    # # protocal_filename = [
    # #     os.path.join(input_folder,file_id+'_protocol_stage_0.json') ,
    # #     os.path.join(input_folder,file_id+'_protocol_stage_1.json') ,
    # #     os.path.join(input_folder,file_id+'_protocol_stage_2.json')
    # #     # os.path.join(input_folder,file_id+'_protocol_stage_3.json')
    # #     ]
    # mechanisms_filename = [
    #     os.path.join(config_folder,'mechanisms_stage_0.json'),
    #     os.path.join(config_folder,'mechanisms_stage_1.json'),
    #     os.path.join(config_folder,'mechanisms_stage_2.json')
    #     # os.path.join(config_folder,'mechanisms_stage_3.json')
    #     ]
    # parameter_filename = [
    #     os.path.join(config_folder,'parameters_stage_0.json'),
    #     os.path.join(config_folder,'parameters_stage_1.json'),
    #     os.path.join(config_folder,'parameters_stage_2.json')
    #     # os.path.join(config_folder,'parameters_stage_3.json')
    #     ]
        
    return morphology_filename,feature_filename,protocal_filename,mechanisms_filename,parameter_filename


def run_stage(file_id, checkpoint_filename, output_dir, max_ngen, documenting_step_size, stage_number, evaluator, opt):
    continue_cp = False
    gens_remaining = max_ngen
    iteration_number = 1
    while (gens_remaining>0):
        tic = time.perf_counter()

        final_pop, halloffame, log, hist = opt.run(
                output_dir,
                max_ngen=iteration_number*documenting_step_size,
#                cp_filename=checkpoint_filename,
                continue_cp=continue_cp)
        continue_cp = True
        out_file_name = file_id +'_statge_'+ str(stage_number)+'_iteration_'+ str(iteration_number)+ '_halloffame.json'
        saving_hof(output_dir, evaluator, halloffame, out_file_name)

        iteration_number = iteration_number+1
        gens_remaining = gens_remaining - documenting_step_size
        toc = time.perf_counter()
        print(f"Iteration done in {toc - tic:0.4f} seconds")

    
    print('stage ' + str(stage_number) + ' is done\n')
    best_params = evaluator.param_dict(halloffame[0])
    pp.pprint(best_params)

    return halloffame,log




def making_pretty_json(output_dir, log, out_file_name):
    json_string = json.dumps(log,indent=4, sort_keys=True)
    with open(os.path.join(output_dir,out_file_name), 'w') as outfile:
        outfile.write(json_string)

def saving_hof(output_dir, evaluator, halloffame, out_file_name):
    para_out = []
    for jj in range(len(halloffame)):
        para_out.append(evaluator.param_dict(halloffame[jj]))
    making_pretty_json(output_dir, para_out, out_file_name)



def edit_next_stage_parameter_bounds(parameter_filename, stage_parameter_updating_ratio, stage_number, evaluator, halloffame):
    param_configs_temp = json.load(open(parameter_filename[stage_number+1]))
    for jj in range(len(halloffame)):
        if (jj == 0):
            best_params = evaluator.param_dict(halloffame[0]) 
            for each_parameter in best_params:
                best_params[each_parameter] = [best_params[each_parameter]]
        else:
            for each_parameter in best_params:
                best_params[each_parameter].append(evaluator.param_dict(halloffame[jj])[each_parameter])
    parameters_max = {}
    parameters_min = {}
    for each_parameter in best_params:
        parameters_max[each_parameter] = max(best_params[each_parameter])
        parameters_min[each_parameter] = min(best_params[each_parameter])

    for jj in range(len(param_configs_temp)):
        try:
            temp_name = (param_configs_temp[jj]['param_name']+'.'+param_configs_temp[jj]['sectionlist'])
        except:
            temp_name = ''

        if ( temp_name in list(best_params)):
            if (param_configs_temp[jj]['bounds'][0] < parameters_min[temp_name] - abs(parameters_min[temp_name]*(stage_parameter_updating_ratio[0]))):
                param_configs_temp[jj]['bounds'][0] = parameters_min[temp_name] - abs(parameters_min[temp_name]*(stage_parameter_updating_ratio[0]))
            if (param_configs_temp[jj]['bounds'][1] > parameters_max[temp_name] + abs(parameters_max[temp_name]*(stage_parameter_updating_ratio[1]))):
                param_configs_temp[jj]['bounds'][1] = parameters_max[temp_name] + abs(parameters_max[temp_name]*(stage_parameter_updating_ratio[1]))
    json_string = json.dumps(param_configs_temp, indent=4, sort_keys=True)
    with open(parameter_filename[stage_number+1], 'w') as outfile:
        outfile.write(json_string)



def making_evaluator(morphology_filename, feature_filename, protocal_filename, mechanisms_filename_0, parameter_filename_0, soma_threashhold, dend_threashhold, timeout, output_dir):


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
            dump_location = output_dir)

    return evaluator

if __name__ == "__main__":

#    for ii in range(int(sys.argv[1]),int(sys.argv[2])):
#        main([sys.argv[0], str(ii), sys.argv[3]])
        main([sys.argv[0], sys.argv[1], sys.argv[2]])


