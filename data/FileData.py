# -*- coding: utf-8 -*-

import sys
import os
import locale
import codecs
import re

class FileData(object):
    """
    Abstrae el acceso a los ficheros de datos: users, subjects,
    descriptions.

    El acceso es al estilo de los diccionarios: filedata['users'],
    filedata['subjects'], ...

    El formato de los ficheros es texto plano, una entrada por línea:  [id]:string

    El significado de los ids depende del fichero: listas de tags o subtipo.
    """

    def __init__(self, datadir):
        self._datadir = datadir
        self._data = dict()


    def __getitem__(self, key):
        if not key in ['users', 'subjects', 'descriptions', 'teachers', 'students']:
            raise KeyError()
        if not key in self._data:
            if key in ['teachers', 'students']:
                # Remove plural from 'teachers', 'students' for individual keys
                self._data[key] = [user for user in self['users'] if key[:-1] in user[0]]
            else:
                self._data[key] = self._load(key+'.txt')
        return self._data[key]


    def _load(self, filename):
        data = []
        datafile = codecs.open(os.path.join(self._datadir, filename), 'r',
                               encoding='utf-8')

        for line in datafile.readlines():
            matchLine = re.search(r'^([^:]*):(.*)$', line, re.U)
            if matchLine:
                tags = []
                for tag in matchLine.group(1).split(','):
                    if tag:
                        tags.append(tag)
                data.append([tags,matchLine.group(2)])
            else:
                print >>sys.stderr, "ERROR: En {0} la línea no es correcta -- {1}".format(filename, line.strip().encode(locale.getpreferredencoding()))
        datafile.close()

        return data
