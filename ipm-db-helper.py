#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import locale
import re
import couchdb
from helpers.DBHelper import DBHelper, Badarg
from data.FileData import FileData

if __name__ == '__main__':
    """
    Script que toma los parámetros de la línea de comandos y lanza el
    helper correspondiente.
    """

    def usage():
        print ("Modo de empleo: " + os.path.basename(sys.argv[0]) +
               " [ServerURL] command [args]")
        print ("Programa de ayuda que asiste en la realización de "
               "las operaciones típicas sobre bases de datos durante "
               "el testing de aplicaciones.")
        print
        print "Instrucciones (command) y sus argumentos: "
        for cmd in DBHelper.cliHelp():
            name = "  " + cmd[0]
            tab = " " * len(name)
            print name + " " + cmd[1][0]
            for opt in cmd[1][1:]:
                print tab + " " + opt

    cmdIdx = 1
    if re.match('http[s]?://.*', sys.argv[1]):
        server = couchdb.Server(sys.argv[1])
        print >> sys.stderr, "INFO: I will try to use couchdb server at " + sys.argv[1]
        cmdIdx = 2
    else:
        print >> sys.stderr, "INFO: I will try to use default couchdb server"
        server = couchdb.Server()

    filedata = FileData(os.path.join(os.path.dirname(sys.argv[0]), 'data'))

    try:
        DBHelper.createHelper(sys.argv[cmdIdx], server, filedata).run(sys.argv[cmdIdx+1:])
    except (LookupError, Badarg):
        usage()
        sys.exit(2)
    except ValueError:
        sys.exit(2)





