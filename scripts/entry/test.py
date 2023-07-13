import app

config_entry_stack = app.ConfigEntryStack.new(
    'jjen-configurator-test',
    'data/real.config.json',
    'foobar.yaml',
)

config_entry_stack.get_entry_yaml()
