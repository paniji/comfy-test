import yaml
import os
import requests
import json

def prompt_workflow(file_name):
    workflow_json = get_file("template/yaml/" + file_name)
    print(workflow_json)
    return workflow_json

def get_file(config_file):

    dir_path = os.path.dirname(os.path.realpath(__file__))
    file = dir_path + "/" + config_file
    print(file)

    with open(file) as file:
        try:
            config = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print("Error while reading config.yml")
    return config

def queue_prompt():

    # Get the value of an environment variable
    COMFY = os.environ.get('COMFY')
    
    print("Using Comfy URL: ", COMFY)

    p = {"prompt": prompt_workflow("txt2vid.yml")}
    data = json.dumps(p).encode('utf-8')

    #Get the value of an environment variable
    session = requests.Session()
    session.verify = True
    comfy_url = COMFY + '/prompt'
    result = session.post(url=comfy_url, data=data)
    print(result)

