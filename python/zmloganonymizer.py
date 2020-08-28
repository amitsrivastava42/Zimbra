#!/usr/bin/python

import re
import hashlib
import optparse
import logging
import sys
import random
import string

def hashing_func(to_hash, salt):
    """ Calculates hash """
    return hashlib.sha256(to_hash + salt).hexdigest()

def random_char(y):
    """ Random character generation for salt """
    return ''.join(random.choice(string.ascii_letters) for x in range(y))

class MultiRegex(object):
    """ See: https://code.activestate.com/recipes/576710 """
    flags = re.DOTALL
    regexes = ()

    def __init__(self):
        """ compile a disjunction of regexes, in order """
        self._regex = re.compile("|".join(self.regexes), self.flags)

    def sub(self, s):
        return self._regex.sub(self._sub, s)

    def _sub(self, mo):
        """
        determine which partial regex matched, and
        dispatch on self accordingly.
        """
        for k, v in mo.groupdict().iteritems():
            if v:
                sub = getattr(self, k)
                if callable(sub):
                    return sub(mo)
                return sub
        raise AttributeError, \
             'nothing captured, matching sub-regex could not be identified'


class AnonymizeLog(MultiRegex):
    email_regex_patt = (r'(?P<uname>[a-zA-Z0-9._+-]+)'
                        r'(@|%40)'
                        r'(?P<domain1>[a-zA-Z0-9.-]+'
                        r'(\.[a-zA-Z0-9]{2,4}))')

    ipadd_regex_patt = (r'(?P<ipadd>\b(?:'
                        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
                        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b)')

    # To capture activesync patterns in nginx access logs,
    # which take the form of domain%5Cuser or domain\x5Cuser
    nginx_async_patt1 = (r'(?P<async_dom>\b[a-zA-Z0-9.-]+)'
                         r'(\x5C|%5C)'
                         r'(?P<async_uname>[a-zA-Z0-9._+-]+\b)')

    # Activesync pattern again, with only username
    nginx_async_patt2 = (r'(User=)(?P<async_nodom>'
                         r'(.[^@^%]*))(&DeviceId)')

    # sasl_username, when it's only the username without domain
    postfix_sasl_patt = (r'\b(sasl_username=)(?P<sasl_nodom>'
                         r'(.[^@]*)\b)')

    # usernames with 'auth_zimbra', when it's only the username
    postfix_auth_patt = (r'\b(auth_zimbra: )(?P<auth_nodom>'
                         r'(.[^@ ]*)\b)')

    regexes = (
        email_regex_patt,
        ipadd_regex_patt,
        nginx_async_patt1,
        nginx_async_patt2,
        postfix_sasl_patt,
        postfix_auth_patt
    )

    def uname(self, mo):
        """
        Anonymize username@example.com. Append username with 'USN_'
        and domain with 'DOM_' for easier regexing and visual grepping
        """
        username_hash = hashing_func(mo.group('uname'), salt)
        domain_hash = hashing_func(mo.group('domain1'), salt)

        trunc_uname_hash = 'USN_' + username_hash[:13]
        trunc_dom_hash = 'DOM_' + domain_hash[:10]

        logging.debug('Email %s@%s is %s@%s' %
                     (mo.group('uname'),
                      mo.group('domain1'),
                      trunc_uname_hash,
                      trunc_dom_hash))

        return "%s@%s" % (trunc_uname_hash, trunc_dom_hash)

    def ipadd(self, mo):
        """
        Anonymize IP address. Append it with 'IP_'.
        """
        ipaddr_hash = hashing_func(mo.group(0), salt)

        trunc_ipadd_hash = 'IP_' + ipaddr_hash[:11]

        logging.debug('IP %s is %s' %
                     (mo.group(0),
                      trunc_ipadd_hash))

        return trunc_ipadd_hash

    def async_dom(self, mo):
        """
        Anonymize nginx activesync logs, which may look like "domain\username"
        """
        async_dom_hash = hashing_func(mo.group('async_dom'), salt)
        async_uname_hash = hashing_func(mo.group('async_uname'), salt)

        trunc_adom_hash = 'DOM_' + async_dom_hash[:10]
        trunc_ausn_hash = 'USN_' + async_uname_hash[:13]

        logging.debug('Activesync domain and user %s\%s is %s\%s' %
                      (mo.group('async_dom'),
                       mo.group('async_uname'),
                       trunc_adom_hash,
                       trunc_ausn_hash))

        return ("%s\%s" %
                (trunc_adom_hash, trunc_ausn_hash))

    def async_nodom(self, mo):
        """
        Same as above, but when no domain is present"
        """
        async_uname_hash2 = hashing_func(mo.group('async_nodom'), salt)

        trunc_usn_nodom_hash = 'USN_' + async_uname_hash2[:13]

        logging.debug('Activesync user %s is %s' %
                      (mo.group('async_nodom'),
                       trunc_usn_nodom_hash))

        return "User=%s&DeviceId" % (trunc_usn_nodom_hash)

    def sasl_nodom(self, mo):
        """
        Anonymize sasl_username in zimbra.log, when it's only the username"
        """
        sasl_uname_hash = hashing_func(mo.group('sasl_nodom'), salt)

        trunc_sasl_hash = 'USN_' + sasl_uname_hash[:13]

        logging.debug('sasl user %s is %s' %
                      (mo.group('sasl_nodom'),
                       trunc_sasl_hash))

        return "sasl_username=%s" % (trunc_sasl_hash)

    def auth_nodom(self, mo):
        """
        Anonymize auth_zimbra username, when it's only username"
        """
        auth_uname_hash = hashing_func(mo.group('auth_nodom'), salt)
        trunc_azimbra_hash = 'USN_' + auth_uname_hash[:13]

        logging.debug('auth_zimbra user %s is %s' %
                      (mo.group('auth_nodom'),
                       trunc_azimbra_hash))
        return "auth_zimbra: %s" % (trunc_azimbra_hash)


def main():

    global salt

    desc = (r"Replace usernames, email addresses and IP addresses "
           r"with random characters. "
           r"Usernames are appended with 'USN_', domains with "
           r"'DOM_' and IP addresses with 'IP_'. "
           r"SHA-256 with salt is used for hashing, and "
           r"hashes are truncated for better readability."
    )

    parser = optparse.OptionParser(
            usage='Usage: %prog -l <log file> -o <output log file> <options>',
            description=desc,
            version='%prog version 1.0')

    parser.add_option('-i', '--inputfile',
                      help='File to anonymize.',
                      dest='input_file',
                      action='store',
                      metavar='zimbra.log')

    parser.add_option('-o', '--outputfile',
                      help='File to store the anonymized logs.',
                      dest='output_file',
                      action='store',
                      metavar='zimbra.anonymized.log')

    parser.add_option('-l', '--logfile',
                      help='Log file storing script operations.',
                      dest='log_file',
                      action='store',
                      metavar='/opt/zimbra/log/zmloganonymizer.log',
                      default='/opt/zimbra/log/zmloganonymizer.log')

    parser.add_option('-s', '--salt',
                      help=(r'Salt to use for hashing. If none is specified,'
                            r'it will be randomly generated.'),
                      dest='salt',
                      action='store',
                      metavar='ak3lz1')

    parser.add_option('-v', '--verbose',
                      help=(r"Log verbosity. Default is 'INFO'. Specifying "
                            r"this enables 'DEBUG' logging, which shows the "
                            r"mapping between the original and hashes. This "
                            r"leads to large log files, almost as large as "
                            r"the original, so use with care."),
                      dest='log_level',
                      action='store_true',
                      default=False)

    (opts, args) = parser.parse_args()

    if not opts.input_file:
        sys.exit("Error: Specify an input file")
    if not opts.output_file:
        sys.exit("Error: Specify an output file")

    if opts.log_level:
        log_level = 10
    else:
        log_level = 20

    # Enable logging. Change to INFO/DEBUG as necessary
    log_file = opts.log_file
    logging.basicConfig(level=log_level,
                        filename=log_file,
                        format='%(asctime)s %(levelname)s %(message)s')
    print "Starting script. Logging at %s" % log_file

    if opts.salt:
        logging.debug('Salt specified by user')
        salt = opts.salt
    else:
        logging.debug('Generating random salt')
        salt = random_char(6)

    logging.info('Salt is %s' % salt)
    logging.info('Input file is %s' % opts.input_file)
    logging.debug('Output file is %s' % opts.output_file)

    with open(opts.output_file, 'w') as new_file:
        with open(opts.input_file) as old_file:
            for line in old_file:
                # logging.debug('Modifying %s' % line)
                new_line = AnonymizeLog().sub(line)
                # logging.debug('Modified to %s' % new_line )
                new_file.write(new_line)

    logging.info('Completed anonymizing %s' % opts.input_file)
    print "Completed. Salt is %s" % salt
    print (r"To generate the same hashes for other log files, "
           r"specify the same salt using '-s'")


if __name__ == '__main__':
    main()
