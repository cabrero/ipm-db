# -*- coding: utf-8 -*-

import random
import datetime
import calendar
from db.CouchDBEvents import SubjectVO, EventVO, UserVO

class GeneratorSimple(object):
    """
    Generador simple:
      - eventos: entre dos fechas dadas
      - asignaturas: todas las disponibles
      - usuarios: todos los disponibles (ver L{users})
    """
    def __init__(self, start, end, filedata):
        """
        Inicializa el generador para un rango de fechas.

        @param start: Primer día del rango. Ese día pertenece al intervalo.
        @type  start: datetime.date
        @param end:   Último día del rango. Ese día pertenece al intervalo.
        @type  end:   datetime.date
        @param filedata: Adaptador para acceso a los datos en ficheros.
        @type  filedata: data.FileData
        """
        self._start = start
        self._end = end
        self._filedata = filedata

    def _random_date(self):
        while True:
            delta = self._end - self._start
            secs = random.randrange(0, delta.total_seconds(), 24*60*60)
            date = self._start + datetime.timedelta(seconds=secs)
            if calendar.weekday(date.year, date.month, date.day) < 6:
                break
        return date

    _whats = [u'Examen', u'Entrega de prácticas', u'Prueba de evaluación continua',
              u'Seminario']
    _subjects = [u"IPM", u"AS"]
    def _random_description(self):
        return u"[{0}] {1} {2}".format(subject[1], description[1], tags)
        
    def eventos(self, number):
        """
        Genera el número indicado de eventos aleatorios.

        @param number: Número de eventos a generar.
        @type  number: int
        @return: Lista de eventos.
        @rtype: list(tuple())
        """
        for i in range(number):
            teacher = random.choice(self._filedata['teachers'])[1]
            subject = random.choice(self._filedata['subjects'])
            description = random.choice(self._filedata['descriptions'])
            tags = subject[0] + description[0]
            yield EventVO(description[1], teacher, tags, self._random_date())

    def users(self):
        """
        Genera una lista de usuarios con un número aleatorio de
        asignaturas asociadas para los estudiantes y una asignatura
        para los profesores.

        @return: Lista de usuarios.
        @rtype: list(tuple())
        """
        for user in self._filedata['users']:
            if 'teacher' in user[0]:
                yield UserVO(user[0][0], user[1], [random.choice(self._filedata['subjects'][0][0])])
            else:
                yield UserVO(user[0][0], user[1], [subject[0][0] for subject in self._filedata['subjects'] if random.getrandbits(1)])
                

    def subjects(self):
        """
        Genera una lista de asignaturas.

        @return: Lista de asignaturas
        @rtype: list(tuple())
        """
        for subject in self._filedata['subjects']:
            yield SubjectVO(subject[1], subject[0])
