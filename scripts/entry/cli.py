import argparse


def load():
    ###########################
    ##  Setting up ArgParse  ##
    ###########################

    ## Setup ##
    parser = argparse.ArgumentParser()

    # Positional
    help_text = "Main template filepath. Expects YAML."
    parser.add_argument("main_filepath", type=str, help=help_text)

    # Optional
    help_text = "Filepath of ouput. Defaults to 'output/entry.yaml'"
    parser.add_argument("-o", "--output", type=str, help=help_text)

    help_text = (
        "Filepath of boilerplate template fragment. Defaults to input/boilerplate.yaml"
    )
    parser.add_argument("-b", "--boilerplate", type=str, help=help_text)

    ###########################
    ##  Processing ArgParse  ##
    ###########################

    args = parser.parse_args()

    params = {}
    params.update({"main_filepath": args.main_filepath})
    if bool(args.boilerplate):
        params.update({"boilerplate_filepath": args.boilerplate})
    if bool(args.output):
        params.update({"entry_filepath": args.output})

    return params
