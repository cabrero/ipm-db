# -*- coding: utf-8 -*-

import sys
import locale
import getopt
import couchdb
import datetime
from helpers.generators.GeneratorSimple import GeneratorSimple
from db.CouchDBEvents import CouchdbDAO

# @stererotype{Command}
class DBHelper(object):
    """
    Helper para realizar operaciones típicas sobre la base de datos
    durante el testing de las aplicaciones.

    Helper === command
    """

    # @stereotype{Factory method}
    @staticmethod
    def createHelper(name, server, filedata):
        """
        Crea una instancia del subtipo de helper correspondiente al
        nombre inidicado.

        @param name: Nombre del helper deseado
        @type  name: string
        
        @param server: Servidor de base de datos
        @type  server: object

        @return: Una instancia del helper solicitado
        @rtype:  DBHelper

        @raise LookupError: Si no existe ninún tipo de helper adecuado
                            para el nombre indicado
        """
        for helper in DBHelper.__subclasses__():
            if name == helper._cmdStr:
                return helper(server, filedata)
        raise LookupError()


    @staticmethod
    def cliHelp():
        """
        Devuelve la ayuda con las opciones de los helpers.
        """
        helpStrs = []
        for helper in DBHelper.__subclasses__():
            helpStrs.append((helper._cmdStr, helper._argsHelp))
        return helpStrs
            

    def __init__(self, server, filedata):
        self._server = server
        self._filedata = filedata

    def run(self, args):
        """
        Lanza la operación definida por el Helper concreto con las
        opciones indicadas.

        @param args: Lista de argumentos para el Helper
        @type  args: list(string)
        """
        pass

class Badarg(Exception):
    """
    Excepción: uno de los argumentos pasados al helper no es válido.
    """
    pass


class DBHelperList(DBHelper):
    """
    Helper para obtener la lista de bases de datos existentes.
    """
    _cmdStr = "list"
    _argsHelp = [""]

    def __init__(self, server, filedata):
        DBHelper.__init__(self, server, filedata)

    def run(self, args):
        """
        Lista (stdout) las bases de datos existentes.
        """
        for bd in self._server:
            print bd



class DBHelperDelete(DBHelper):
    """
    Helper para borrar bases de datos existentes.
    """
    _cmdStr = "delete"
    _argsHelp = ["databasename [databasename ...]"]

    def __init__(self, server, filedata):
        DBHelper.__init__(self, server, filedata)

    def run(self, args):
        """
        Borra las bases de datos cuyos nombres se indican.

        @param args: Lista de nombres de BBDD a borrar
        @type  args: list(string)
        """
        for dbname in args:
            try:
                self._server.delete(dbname)
            except couchdb.ResourceNotFound:
                print >> sys.stderr, "La base de datos '{0}' no existe.".format(dbname)
        pass


class DBHelperCreate(DBHelper):
    """
    Helper para crear bases de datos con contenido inicial aleatorio.
    """
    _cmdStr = "create"
    _argsHelp = ["databasename -y año",
                 "             -q cuatrimestre (1 ó 2)",
                 "             [-n nº de eventos (default: 30)]"]
    DEFAULT_N = 30

    def __init__(self, server, filedata):
        DBHelper.__init__(self, server, filedata)

    def run(self, args):
        """
        Crea una base de datos con las características inidicadas.

        @param args: Lista de opciones al estilo de la línea de comandos
                     (ver L{_argsHelp})
        @type  args: list(string)
        """
        try:
            dbname = args[0]
            opts, args = getopt.getopt(args[1:], "y:q:n:", ["year=","quarter=","number="])
        except (getopt.GetoptError, IndexError):
            raise Badarg()

        number = None
        year = None
        quarter = None
        for o, a in opts:
            if o in ("-y", "--year"):
                try:
                    year = int(a)
                except ValueError:
                    raise Badarg()
            elif o in ("-q", "--quarter"):
                try:
                    quarter = int(a)
                except ValueError:
                    raise Badarg()
                if quarter != 1 and quarter != 2:
                    print >> sys.stderr, "ERROR: Los cuatrimestres válidos son 1 ó 2."
                    raise ValueError()
            elif o in ("-n", "--number"):
                try:
                    number = int(a)
                except ValueError:
                    raise Badarg()
            else:
                raise Badarg()
        if not(year) or not(quarter):
            raise Badarg()
        if not(number):
            number = self.DEFAULT_N
        # Miramos en algún servicio o BD las fechas de inicio y fin del cuatrimestre
        if year == 2013 and quarter == 1:
            start = datetime.date(2013,9,9)
            end = datetime.date(2014,1,24)
        elif year == 2013 and quarter == 2:
            start = datetime.date(2014,1,28)
            end = datetime.date(2014,6,6)
        elif year == 2012 and quarter == 1:
            start = datetime.date(2012,9,10)
            end = datetime.date(2013,1,25)
        elif year == 2012 and quarter == 2:
            start = datetime.date(2013,1,29)
            end = datetime.date(2013,6,7)
        elif year == 2011 and quarter == 1:
            start = datetime.date(2011,9,19)
            end = datetime.date(2012,1,31)
        elif year == 2011 and quarter == 2:
            start = datetime.date(2012,2,1)
            end = datetime.date(2012,7,8)
        else:
            print >>sys.stderr, "ERROR: El curso {0}/{1} no está en la BD.".format(year, year+1)
            raise ValueError()


        try:
            db = self._server.create(dbname)
            dao = CouchdbDAO(db)
        except couchdb.PreconditionFailed:
            print >> sys.stderr, "ERROR: La base de datos '{0}' ya existe.".format(dbname)
            raise ValueError()

        generator = GeneratorSimple(start, end, self._filedata)
        for event in generator.eventos(number):
            dao.insert(event)

        for user in generator.users():
            dao.insert(user)

        for subject in generator.subjects():
            dao.insert(subject)
