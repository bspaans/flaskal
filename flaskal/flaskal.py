import yaml
import sys
from parser import ColumnParser, ModelParser
from generator import CodeGenerator

def yaml_to_code(yaml_str):
    y = yaml.load(yaml_str)
    return CodeGenerator().output_code(ModelParser().parse_multiple(y))

def yaml_file_to_code(yaml_file):
    with open(yaml_file):
        return yaml_to_code(open(yaml_file).read())

def main():
    print yaml_file_to_code(sys.argv[1])
    
if __name__ == '__main__':
    main()
