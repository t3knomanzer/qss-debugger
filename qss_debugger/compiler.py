# *********************************************************************
# +++ IMPORTS
# *********************************************************************
import os
import re


# *********************************************************************
# +++ CLASS
# *********************************************************************
class VisualCompilerBase(object):
    @staticmethod
    def compile(qss_folder_path, qss_vars_folder_path, qss_out_file_path):
        raise NotImplementedError()


# *********************************************************************
# +++ CLASS
# *********************************************************************
class VisualCompilerDefault(VisualCompilerBase):
    @staticmethod
    def compile(qss_folder_path, qss_vars_folder_path, qss_out_file_path):
        VisualCompilerDefault._compile_qss(qss_folder_path, qss_out_file_path)
        VisualCompilerDefault._inject_vars(qss_out_file_path, qss_vars_folder_path)

    @staticmethod
    def _compile_qss(input_folder_path, output_file_path):
        result = ''
        for file_name in os.listdir(input_folder_path):
            file_path = os.path.join(input_folder_path, file_name)
            extension = os.path.splitext(file_name)[1]

            if extension in ['.css', '.qss']:
                with open(file_path, 'r') as file_handle:
                    result += file_handle.read() + '\n'

        with open(output_file_path, "w") as output_file:
            output_file.write(result)

    @staticmethod
    def _inject_vars(input_file_path, vars_path):
        vars_map = {}

        for file_name in os.listdir(vars_path):
            file_path = os.path.join(vars_path, file_name)

            with open(file_path, 'r') as file_handle:
                for line in file_handle.readlines():
                    line = line.strip('\n')
                    line = line.replace(' ', '')
                    line = line.split(':')

                    if len(line) == 2:
                        vars_map[line[0]] = line[1]
                    else:
                        print('Error in line {} from file {}'.format(line, file_name))

        with open(input_file_path, 'r') as file_handle:
            content = file_handle.read()

            for key, value in vars_map.iteritems():
                re_value = re.compile(key, re.IGNORECASE)
                content = re_value.sub(value, content)

        with open(input_file_path, 'w') as file_handle:
            file_handle.write(content)
