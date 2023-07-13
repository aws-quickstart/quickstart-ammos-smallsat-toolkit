from dataclasses import dataclass
from typing import Dict
import cfn_flip
import json
import subprocess

class Utils:
    @staticmethod
    def get_dict_from_template(filepath):
        with open(filepath) as f:
            template_raw = f.read()
        template_flat_json = cfn_flip.to_json(template_raw)
        template_dict = json.loads(template_flat_json)
        return template_dict

@dataclass
class EntryTemplateFactory:
    boilerplate: Dict
    main:        Dict
    entry:       Dict = None


    @staticmethod
    def new(
        main_filepath,
        boilerplate_filepath = 'input/boilerplate.yaml'

    ):
        main_dict = Utils.get_dict_from_template(main_filepath)
        boilerplate_dict = Utils.get_dict_from_template(boilerplate_filepath)

        params = {
            'boilerplate': boilerplate_dict,
            'main': main_dict,
        }

        factory = EntryTemplateFactory(**params)
        factory._update_entry()
        return factory

    def get_entry_template(self,filename='entry'):
        entry_dict = self.entry
        with open(f"output/{filename}.json",'w') as f:
            f.write(json.dumps(entry_dict))

        command = f"cfn-flip output/{filename}.json output/{filename}.yaml"
        subprocess.run(command, shell=True)



    #######################################
    ##  Methods used in _update_entry()  ##
    #######################################

    def _update_entry(self):
        entry = self.boilerplate.copy()

        # Main Stack Parameters
        main_params = self._get_entry_main_params()
        entry['Resources']['MainStack']['Properties']['Parameters'] = main_params

        self.entry= entry


    def _get_entry_main_params(self, custom_resource_name = 'Config'):
        cr = custom_resource_name
        keys = list(self.main['Parameters'].keys())
        main_params = { k: {"Fn::GetAtt": [cr, k]} for k in keys }
        return main_params
