import yaml
import os
import requests
import json

# Define constants
INPUT = "inputs"
TEXT = "text"
FILE_NAME = "filename_prefix"

def prompt_workflow(tmplt):

    # Load Root supported template property file
    root_template = get_file("template/yaml/template.yml")
    # Get corresponding worklow file name
    workflow = root_template[tmplt]['workflow']
    # Load corresponding worklow file
    workflow_json = get_file("template/yaml/workflow/" + tmplt + "/" + workflow)
    # Update environment specifc properties
    workflow_json = set_env_props(workflow_json, tmplt)

    # Update scene and trigger comfy (scene by scene)
    scene_data(workflow_json, tmplt)
    #return workflow_json

def set_env_props(wf, tmplt):
    ret_wf = wf
    # Get Environment
    ENV = os.environ.get('ENV')
    # Load ENV config file
    env_config = get_file("template/yaml/" + ENV + "/" + tmplt + "-config.yml")
    config = env_config[tmplt]

    for key in config:
        config2 = config[key]
        for key2 in config2:
            ret_wf[key][INPUT][key2] = config2[key2]

    return ret_wf

def scene_data(wf_data, tmplt):
    project_config = get_file("project/template.yml")

    #if 'scenes' in project_config:
    scenes = project_config['scenes']

    for scn in scenes:

        scn_config = get_file("project/scenes/" + scn + "/template.yml")

        scenes2 = scn_config['scenes']

        for scn2 in scenes2:
            scn2_config = get_file("project/scenes/" + scn + "/scenes/" + scn2 + "/template.yml") # + ".yml")

            #print(scn2_config)
            scenes3 = scn2_config['scenes']
            for scn3 in scenes3:
                #print(scn3)
                scene = get_file("project/scenes/" + scn + "/scenes/" + scn2 + "/" + scn3 + ".yml")
                #print(scene)
                pos_promt = project_config['pre_positive_prompt'] + ", " + scene['positive_prompt'] + ", " + project_config['post_positive_prompt']
                neg_promt = project_config['pre_negative_prompt'] + ", " + scene['negative_prompt'] + ", " + project_config['post_negative_prompt']
                length = scene['length_in_secs']
                ## work on hard code for txt2vid
                if tmplt == 'txt2vid':
                    context_length = length * project_config[tmplt]['101']['frame_rate']
                    wf_data['94'][INPUT]['context_length'] = context_length
                    wf_data['3'][INPUT]['text'] = pos_promt
                    wf_data['6'][INPUT]['text'] = neg_promt
                    wf_data['101'][INPUT]['frame_rate'] = project_config[tmplt]['101']['frame_rate']

                    file_name = scn + "/" + scn2 + "/" + scn3
                    print(project_config[tmplt]['101']['filename_prefix'] + "/" + file_name)
                    wf_data['101'][INPUT]['filename_prefix'] = project_config[tmplt]['101']['filename_prefix'] + "/" + file_name
                    # print("-----------------")
                    # print(wf_data)
                    # print("-----------------")

                    p = {"prompt": wf_data}
                    data = json.dumps(p).encode('utf-8')

                    # Trigger comfy
                    queue_prompt(data)

def set_prompt(workflow_json, node, prompt):
    prompt_node = workflow_json[node]

    prompt_node[INPUT][TEXT] = prompt

def set_file_name(workflow_json, node, name):
    file_node = workflow_json[node]

    file_node[INPUT][FILE_NAME] = name

def get_file(config_file):

    dir_path = os.path.dirname(os.path.realpath(__file__))
    file = dir_path + "/" + config_file
    #print(file)

    try:
        with open(file) as file:
            try:
                config = yaml.safe_load(file)
                return config
            except yaml.YAMLError as exc:
                print("Error while loading template file")
                return exc

    except FileNotFoundError as exc:
        print("File not found.")
        return exc
        

def queue_prompt(data):

    # Get the value of an environment variable
    COMFY = os.environ.get('COMFY')
    print("Using Comfy URL: ", COMFY)

    #Get the value of an environment variable
    session = requests.Session()
    session.verify = True
    comfy_url = COMFY + '/prompt'
    result = session.post(url=comfy_url, data=data)
    print(result)

# def trigger_workflow(template):
#     p = {"prompt": prompt_workflow(template)}
#     data = json.dumps(p).encode('utf-8')
