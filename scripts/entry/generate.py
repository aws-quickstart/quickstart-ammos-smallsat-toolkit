from app import EntryTemplateFactory
import cli

def main():
    params = cli.load()

    factory = EntryTemplateFactory.new(**params)
    factory.get_entry_template(**params)

if __name__ == '__main__':
    main()



