"""
 * Copyright 2020, Departamento de sistemas y Computación
 * Universidad de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 """
import config
from DISClib.ADT import list as lt
from DISClib.DataStructures import listiterator as it
from DISClib.ADT import orderedmap as om
from DISClib.DataStructures import mapentry as me
from DISClib.ADT import map as m
import datetime
assert config

"""
En este archivo definimos los TADs que vamos a usar,
es decir contiene los modelos con los datos en memoria

Se define la estructura de un catálogo de libros.
El catálogo tendrá  una lista para los libros.

Los autores, los tags y los años se guardaran en
tablas de simbolos.
"""

# -----------------------------------------------------
# API del TAD Catalogo de Libros
# -----------------------------------------------------


def newAnalyzer():
    """ Inicializa el analizador

    Crea una lista vacia para guardar todos los crimenes
    Se crean indices (Maps) por los siguientes criterios:
    -Fechas

    Retorna el analizador inicializado.
    """
    analyzer = {'crimes': None,
                'dateIndex': None
                }

    analyzer['crimes'] = lt.newList('SINGLE_LINKED', compareIds)
    analyzer['dateIndex'] = om.newMap(omaptype='RBT',
                                      comparefunction=compareDates)
    return analyzer

def hourAnalyzer():
    """ Inicializa el analizador

    Crea una lista vacia para guardar todos los crimenes
    Se crean indices (Maps) por los siguientes criterios:
    -Horas

    Retorna el analizador inicializado.
    """
    analyzer = {'crimes': None,
                'hourIndex': None
                }

    analyzer['crimes'] = lt.newList('SINGLE_LINKED', compareIds)
    analyzer['hourIndex'] = om.newMap(omaptype='RBT',
                                      comparefunction=compareDates)
    return analyzer

# Funciones para agregar informacion al catalogo


def addCrime(analyzer, crime):
    """
    """
    lt.addLast(analyzer['crimes'], crime)
   
    updateHourIndex(analyzer['hourIndex'], crime)
    return analyzer

   

def updateDateIndex(map, crime):
    """
    Se toma la fecha del crimen y se busca si ya existe en el arbol
    dicha fecha.  Si es asi, se adiciona a su lista de crimenes
    y se actualiza el indice de tipos de crimenes.

    Si no se encuentra creado un nodo para esa fecha en el arbol
    se crea y se actualiza el indice de tipos de crimenes
    """
    occurreddate = crime['OCCURRED_ON_DATE']
    crimedate = datetime.datetime.strptime(occurreddate, '%Y-%m-%d %H:%M:%S')
    entry = om.get(map, crimedate.date())
    if entry is None:
        datentry = newDataEntry(crime)
        om.put(map, crimedate.date(), datentry)
    else:
        datentry = me.getValue(entry)
    addDateIndex(datentry, crime)
    return map



def updateHourIndex(map, crime):
    """
    Se toma la hora del crimen y se busca si ya existe en el arbol
    dicha fecha.  Si es asi, se adiciona a su lista de crimenes
    y se actualiza el indice de tipos de crimenes.

    Si no se encuentra creado un nodo para esa hora en el arbol
    se crea y se actualiza el indice de tipos de crimenes
    """
    occurreddate = crime['Start_Time']
    crimedate = datetime.datetime.strptime(occurreddate, '%Y-%m-%d %H:%M:%S')
    if crimedate.time()>=datetime.time(0,0,0) and crimedate.time() < datetime.time(0,15,0):
        crimedate=crimedate.replace(minute=00,second=00)
    elif crimedate.time()>=datetime.time(0,15,0) and crimedate.time() < datetime.time(0,30,0) or crimedate.time()>=datetime.time(0,30,0) and crimedate.time() < datetime.time(0,45,0):
        crimedate=crimedate.replace(minute=30,second=00)
    else:
        sum_hour=1
        new_hour=datetime.timedelta(hours=sum_hour)
        plus_hour=crimedate+ new_hour
        crimedate=plus_hour
        crimedate=crimedate.replace(minute=00,second=00)
   
    entry = om.get(map, crimedate)
    if entry is None:
        hourentry = newDataEntry_hours(crime)
        om.put(map, crimedate, hourentry)
    else:
        hourentry = me.getValue(entry)
    addHourIndex(hourentry, crime)
    return map


def addDateIndex(datentry, crime):
    """
    Actualiza un indice de tipo de crimenes.  Este indice tiene una lista
    de crimenes y una tabla de hash cuya llave es el tipo de crimen y
    el valor es una lista con los crimenes de dicho tipo en la fecha que
    se está consultando (dada por el nodo del arbol)
    """
    lst = datentry['lstcrimes']
    lt.addLast(lst, crime)
    offenseIndex = datentry['offenseIndex']
    offentry = m.get(offenseIndex, crime['Severity'])
    if (offentry is None):
        entry = newOffenseEntry(crime['Severity'], crime)
        lt.addLast(entry['lstoffenses'], crime)
        m.put(offenseIndex, crime['Severity'], entry)
    else:
        entry = me.getValue(offentry)
        lt.addLast(entry['lstoffenses'], crime)
    return datentry


def addHourIndex(hourentry, crime):
    """
    Actualiza un indice de severidad de crimenes.  Este indice tiene una lista
    de crimenes y una tabla de hash cuya llave es la severidad de crimen y
    el valor es una lista con los crimenes de dicho severidad en la hora que
    se está consultando (dada por el nodo del arbol)
    """
    lst = hourentry['lstcrimes']
    lt.addLast(lst, crime)
    offenseIndex = hourentry['offenseIndex']
    offentry = m.get(offenseIndex, crime['Severity'])
    if (offentry is None):
        entry = newOffenseEntry(crime['Severity'], crime)
        lt.addLast(entry['lstoffenses'], crime)
        m.put(offenseIndex, crime['Severity'], entry)
    else:
        entry = me.getValue(offentry)
        lt.addLast(entry['lstoffenses'], crime)
    return hourentry


def newDataEntry(crime):
    """
    Crea una entrada en el indice por fechas, es decir en el arbol
    binario.
    """
    entry = {'offenseIndex': None, 'lstcrimes': None}
    entry['offenseIndex'] = m.newMap(numelements=30,
                                     maptype='PROBING',
                                     comparefunction=compareOffenses)
    entry['lstcrimes'] = lt.newList('SINGLE_LINKED', compareDates)
    return entry



def newDataEntry_hours(crime):
    """
    Crea una entrada en el indice por horas, es decir en el arbol
    binario.
    """
    entry = {'offenseIndex': None, 'lstcrimes': None}
    entry['offenseIndex'] = m.newMap(numelements=30,
                                     maptype='PROBING',
                                     comparefunction=compareOffenses)
    entry['lstcrimes'] = lt.newList('SINGLE_LINKED', compareHours)
    return entry

def newOffenseEntry(offensegrp, crime):
    """
    Crea una entrada en el indice por tipo de crimen, es decir en
    la tabla de hash, que se encuentra en cada nodo del arbol.
    """
    ofentry = {'offense': None, 'lstoffenses': None}
    ofentry['offense'] = offensegrp
    ofentry['lstoffenses'] = lt.newList('SINGLELINKED', compareOffenses)
    return ofentry


# ==============================
# Funciones de consulta
# ==============================


def crimesSize(analyzer):
    """
    Número de crimenes
    """
    return lt.size(analyzer['crimes'])


def indexHeight(analyzer):
    """
    Altura del arbol
    """
    return om.height(analyzer['dateIndex'])

def indexHeight_hours(analyzer):
    """
    Altura del arbol
    """
    return om.height(analyzer['hourIndex'])

def indexSize(analyzer):
    """
    Numero de elementos en el indice
    """
    return om.size(analyzer['dateIndex'])

def indexSize_hours(analyzer):
    """
    Numero de elementos en el indice
    """
    return om.size(analyzer['hourIndex'])

def minKey(analyzer):
    """
    Llave mas pequena
    """
    return om.minKey(analyzer['dateIndex'])

def minKey_hours(analyzer):
    """
    Llave mas pequena
    """
    return om.minKey(analyzer['hourIndex'])

def maxKey(analyzer):
    """
    Llave mas grande
    """
    return om.maxKey(analyzer['dateIndex'])
    
def maxKey_hours(analyzer):
    """
    Llave mas grande
    """
    return om.maxKey(analyzer['hourIndex'])


def getCrimesByRange(analyzer, initialDate, finalDate):
    """
    Retorna el numero de crimenes en un rago de fechas.
    """
    lst = om.values(analyzer['dateIndex'], initialDate, finalDate)
    lstiterator = it.newIterator(lst)
    totcrimes = 0
    while (it.hasNext(lstiterator)):
        lstdate = it.next(lstiterator)
        totcrimes += lt.size(lstdate['lstcrimes'])
    return totcrimes


def getCrimesByRange_hours(analyzer, initialHour, finalHour):
    """
    Retorna el numero de crimenes en un rago de horas.
    """
    lst = om.values(analyzer['hourIndex'], initialHour, finalHour)
    lstiterator = it.newIterator(lst)
    totcrimes = 0
    while (it.hasNext(lstiterator)):
        lsthour = it.next(lstiterator)
        totcrimes += lt.size(lsthour['lstcrimes'])
    return totcrimes


def getCrimesByRangeCode(analyzer, initialDate, offensecode):
    """
    Para una fecha determinada, retorna el numero de crimenes
    de un tipo especifico.
    """
    crimedate = om.get(analyzer['dateIndex'], initialDate)
    if crimedate['key'] is not None:
        offensemap = me.getValue(crimedate)['offenseIndex']
        numoffenses = m.get(offensemap, offensecode)
        if numoffenses is not None:
            return m.size(me.getValue(numoffenses)['lstoffenses'])
        return 0


# ==============================
# Funciones de Comparacion
# ==============================


def compareIds(id1, id2):
    """
    Compara dos crimenes
    """
    if (id1 == id2):
        return 0
    elif id1 > id2:
        return 1
    else:
        return -1


def compareDates(date1, date2):
    """
    Compara dos fechas
    """
    if (date1 == date2):
        return 0
    elif (date1 > date2):
        return 1
    else:
        return -1

def compareHours(hour1,hour2):
    if (hour1 == hour2):
        return 0
    elif (hour1 > hour2):
        return 1
    else:
        return -1


def compareOffenses(offense1, offense2):
    """
    Compara dos tipos de crimenes
    """
    offense = me.getKey(offense2)
    if (offense1 == offense):
        return 0
    elif (offense1 > offense):
        return 1
    else:
        return -1
