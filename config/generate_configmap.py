import argparse
import os

import ConfigParser
import StringIO

"""
webapp.properties:

allow.textmode=true
color.bad=yellow
color.good=purple

"""


def read_properties_file(file_path):
    with open(file_path) as f:
        config = StringIO.StringIO()
        config.write('[dummy_section]\n')
        config.write(f.read().replace('%', '%%'))
        config.seek(0, os.SEEK_SET)

        cp = ConfigParser.SafeConfigParser()
        cp.readfp(config)

        return dict(cp.items('dummy_section'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates an Openshift (oc) create configmap from literals')
    parser.add_argument('-n', '--name', dest='configmap_name', const='settings', type=str,
                        metavar='configmap_name', nargs='?',
                  help='Defines the name of the generated configmap')

    parser.add_argument('-f', '--file', dest='properties_file', const='webapp.properties', type=str,
                        metavar='properties_file', nargs='?',
                        help='Relative or absolute path to the properties file')

    args = parser.parse_args()

    file_path = 'webapp.properties'

    if args.properties_file:
        file_path = args.properties_file

    try:
        props = read_properties_file(file_path=file_path)

        configmap_name = 'settings'
        if args.configmap_name:
            configmap_name = args.configmap_name

        literals_string = ""
        for key, value in props.iteritems():
            literals_string += "--from-literal={}={} ".format(key, value)

        command = "oc create configmap {configmap_name} {literals}".format(configmap_name=configmap_name,
                                                                           literals=literals_string)
        print("COPY AND RUN THE FOLLOWING COMMAND TO CREATE A CONFIGMAP:")
        print("=============")
        print(command)
        print("=============")
    except IOError as e:
        print("Error: {}".format(e))

    """
    Result: oc create configmap settings --from-literal=allow.textmode=true --from-literal=color.bad=yellow --from-literal=color.good=purple
    """
