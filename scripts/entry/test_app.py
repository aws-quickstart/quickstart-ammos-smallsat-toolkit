from app import EntryTemplateFactory

main_template_filepath = 'input/main.yaml'


factory = EntryTemplateFactory.new(
    main_template_filepath,
)

factory.get_entry_template()
