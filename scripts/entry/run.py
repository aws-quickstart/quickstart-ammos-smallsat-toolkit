from app import EntryTemplateFactory

main_template_filepath = 'input/main.yaml'
config_filepath = 'input/config.json'


factory = EntryTemplateFactory.new(
    main_template_filepath,
    config_filepath
)

factory.get_entry_template()
