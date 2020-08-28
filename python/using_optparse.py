import optparse
import sys


def main():
    desc = '''This script deletes the index folder for all users who haven't logged into
    their accounts for over a year. It also places these users in a COS created
    specifically for them. The COS needs to be specified.'''

    parser = optparse.OptionParser(usage='Usage: %prog -c <COS name> <options>',
                                   description=desc,
                                   version='%prog version 1.1')
    parser.add_option('-c', '--cosname',
                      help='''Use the COS name here. This is the
                       special COS created only for abandoned users.''',
                      dest='cos_name',
                      action='store',
                      metavar='abandoned_users')
    parser.add_option('-l', '--logfile',
                      help='''Log file location. Default is
                       /opt/zimbra/log/zimbra_delete_index.log''',
                      dest='log_file',
                      action='store',
                      metavar='/tmp/zimbra_delete_index.log',
                      default='/opt/zimbra/log/zimbra_delete_index.log')
    parser.add_option('-v', '--verbose',
                      help='''Log verbosity. Default is 'INFO'. Specifying this
                       enables 'DEBUG' logging.''',
                      dest='log_level',
                      action='store_true',
                      default=False)
    (opts, args) = parser.parse_args()

    if not opts.cos_name:
        print "\nError: Specify a COS name\n"
        sys.exit(1)

    print opts.log_file, opts.log_level, opts.cos_name


if __name__ == '__main__':
    main()
