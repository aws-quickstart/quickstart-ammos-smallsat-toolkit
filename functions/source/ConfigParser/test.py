from params import Params
import json

params_dict = {
    'word1': 'Watch',
    'word2': 'before',
    'word3': 'you',
    'word4': 'leap'
}


params = Params(params=params_dict)


main_stack_params =  params.get_query_string()
main_stack_params = '["word1=Watch", "word2=before", "word3=you", "word4=leap"]'
main_stack_params = 's3://jjen-configurator-test/my_params.json'
main_stack_params = 's3%3A%2F%2Fjjen-configurator-test%2Fmy_params.json'
data_dict = Params.get_dict_from_params_input_agnostic(main_stack_params)
print(data_dict)
