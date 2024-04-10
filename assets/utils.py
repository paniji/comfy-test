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

    print(workflow_json)
    return workflow_json

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

def set_prompt(workflow_json, node, prompt):
    prompt_node = workflow_json[node]

    prompt_node[INPUT][TEXT] = prompt

def set_file_name(workflow_json, node, name):
    file_node = workflow_json[node]

    file_node[INPUT][FILE_NAME] = name

def get_file(config_file):

    dir_path = os.path.dirname(os.path.realpath(__file__))
    file = dir_path + "/" + config_file
    print(file)

    with open(file) as file:
        try:
            config = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print("Error while loading template file")
    return config

def queue_prompt(template):

    # Get the value of an environment variable
    COMFY = os.environ.get('COMFY')
    
    print("Using Comfy URL: ", COMFY)

    p = {"prompt": prompt_workflow(template)}
    data = json.dumps(p).encode('utf-8')

    #Get the value of an environment variable
    session = requests.Session()
    session.verify = True
    comfy_url = COMFY + '/prompt'
    result = session.post(url=comfy_url, data=data)
    print(result)

