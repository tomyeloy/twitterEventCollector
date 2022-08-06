from dateutil.relativedelta import *
from datetime import datetime
import dateutil.parser as dparser
import spacy
import re
from operator import indexOf
from cgi import print_directory
from asyncio.proactor_events import _ProactorSocketTransport
import os


class Tweet:
    def __init__(self, id_tweet, date, author, text, app, id_user, followers, following, stauses, location,	urls,	geolocation, RT_count,	favorite_count, url_media, type_media, quoted, relation, replied_id, user_replied, retweeted_id, user_retweeted, quoted_id, user_quoted, first_HT, lang, link, tipo_evento, lugar_evento, fecha_evento):
        self.id_tweet = id_tweet
        self.date = date
        self.author = author
        self.text = text
        self.app = app
        self.id_user = id_user
        self.followers = followers
        self.following = following
        self.stauses = stauses
        self.location = location
        self.urls = urls
        self.geolocation = geolocation
        self.RT_count = RT_count
        self.favorite_count = favorite_count
        self.url_media = url_media
        self.type_media = type_media
        self.quoted = quoted
        self.relation = relation
        self.replied_id = replied_id
        self.user_replied = user_replied
        self.retweeted_id = retweeted_id
        self.user_retweeted = user_retweeted
        self.quoted_id = quoted_id
        self.user_quoted = user_quoted
        self.first_HT = first_HT
        self.lang = lang
        self.link = link
        self.tipo_evento = tipo_evento
        self.lugar_evento = lugar_evento
        self.fecha_evento = fecha_evento


def pertenece(autor, tweet):
    if(autor in tweet):
        return True
    return False


def filtro_palabras_clave(frase, palabras):
    for palabra in palabras:
        if palabra in frase:
            return True
    return False


def filtro_combinacion_palabras(frase, palabra):
    if palabra in frase:
        return True
    return False


def remove_emoji(string):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u'\U00010000-\U0010ffff'
                               u"\u200d"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\u3030"
                               u"\ufe0f"
                               u"\u23f0"
                               u"\u23f3"
                               u"\ufe0f"
                               u"\u20e3"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)


def preprocesamiento(tweet):
    tweet = remove_emoji(tweet)
    # tweet = re.sub(r'[^\w\s]', '', tweet)
    # Eliminate duplicate whitespaces using wildcards
    tweet = re.sub(r'\s+', ' ', tweet)
    # elimina caracteres especiales
    tweet = re.sub("\[|\]|\@|\#|\?|\¿|\¡|\!|\||\(|\)", "", tweet)
    tweet = re.sub(r'http\S+', '', tweet)   # elimina url
    # tweet = tweet.lower()  # pasa a minusculas
    return tweet


def detector_patron(patrones, texto):
    for patron in patrones:
        if re.search(patron, texto):
            return True
        return False


def descarte_posiciones(palabras):
    count = 0
    for palabra in palabras:
        count = count+1
        try:
            if(palabras.index(palabra) != palabras.index("@EVENTO@") and palabras.index(palabra) != palabras.index("@EVENTO@")-1 and palabras.index(palabra) != palabras.index("@FECHA@") and palabras.index(palabra) != palabras.index("@FECHA@")-1 and palabras.index(palabra) != palabras.index("@LOCALIZACION@") and palabras.index(palabra) != palabras.index("@LOCALIZACION@")-1):
                palabras.pop(palabras.index(palabra))
                break
        except Exception:
            return None
    if(count < len(palabras)):
        descarte_posiciones(palabras)
    return palabras


comunidades_autonomas = ["Andalucía", "Aragón", "Islas Baleares", "Canarias", "Cantabria", "Castilla-La Mancha", "Castilla y León", "Cataluña", "Comunidad de Madrid",
                         "Comunidad Foral de Navarra", "Comunidad Valenciana", "Extremadura", "Galicia", "País Vasco", "Principado de Asturias", "Región de Murcia", "La Rioja"]

provincias = ["A Coruña", "Alava", "Albacete", "Alicante", "Almería", "Asturias", "Avila", "Badajoz", "Barcelona", "Burgos", "Cáceres", "Cádiz", "Cantabria", "Castellón", "Ceuta", "Ciudad Real", "Córdoba", "Cuenca", "Formentera", "Girona", "Granada", "Guadalajara", "Guipuzcoa", "Huelva", "Huesca", "Ibiza", "Jaén", "La Rioja", "Las Palmas de Gran Canaria", "Gran Canaria",
              "Fuerteventura", "Lanzarote", "León", "Lérida", "Lugo", "Madrid", "Málaga", "Mallorca", "Menorca", "Murcia", "Navarra", "Orense", "Palencia", "Pontevedra", "Salamanca", "Santa Cruz de Tenerife", "Tenerife", "La Gomera", "La Palma", "El Hierro", "Segovia", "Sevilla", "Soria", "Tarragona", "Teruel", "Toledo", "Valencia", "Valladolid", "Vizcaya", "Zamora", "Zaragoza"]

palabras_clave = ["partidos", "partido", "encuentros", "encuentro", "manifestaciones", "manifestación",
                  "concentración", "obras", "obra", "conciertos", "concierto", "espectáculos", "espectáculo", "presentaciones", "presentación"]

fechas = ["hoy", "mañana", "pasado mañana"]
contador = 0
lista_tweets = []
lista_tweets_cortada = []
filtrados = []
descartados = []

with open("tweets/AytoLeganes_tweets.txt", encoding="utf8") as tweets_txt:
    # pasamos los tweets a una lista
    for linea in tweets_txt:
        data = linea.split('\t')
        tweet = Tweet(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11], data[12], data[13],
                      data[14], data[15], data[16], data[17], data[18], data[19], data[20], data[21], data[22], data[23], data[24], data[25], data[26], None, None, None)
        lista_tweets.append(tweet)


# filtrar por palabras clave
for tweet in lista_tweets:
    if filtro_palabras_clave(tweet.text, palabras_clave):
        filtrados.append(tweet)
        # print(tweet.text)
    else:
        descartados.append(tweet)

# print(len(filtrados))
# print(len(descartados))

# PREPROCESADO
# eliminar los tweets que sean RT -> si user retweeted distinto de None es RT
no_RT_lista = []
for tweet in filtrados:
    if(tweet.user_retweeted == "None"):
        no_RT_lista.append(tweet)

# print(len(no_RT_lista))

# Eliminamos en cada tweet corchetes, los símbolos @ y #, símbolos de exclamación e interrogación, emoticonos y URLs.

for tweet in no_RT_lista:
    tweet.text = preprocesamiento(tweet.text)
    # print("")
    # print(tweet.text)

# usar https: // spacy.io /, soporte para gallego: http: // nlp.lsi.upc.edu/freeling/

nlp = spacy.load("es_core_news_sm")
# nlp2 = spacy.load("es_core_news_lg")
# nlpEN = spacy.load("en_core_web_sm")

tweet_sust_loc = []
tweet_sust_eve = []
tweet_sust = []

for tweet in no_RT_lista:
    doc = nlp(tweet.text)

    # print("********************************************")
    # print(tweet.text)
    # # Part-of-speech tags and dependencies
    # for token in doc:
    #     # Text: The original word text.
    #     # Lemma: The base form of the word.
    #     # POS: The simple UPOS part-of-speech tag.
    #     # ADJ: adjective
    #     # ADP: adposition
    #     # ADV: adverb
    #     # AUX: auxiliary
    #     # CCONJ: coordinating conjunction
    #     # DET: determiner
    #     # INTJ: interjection
    #     # NOUN: noun
    #     # NUM: numeral
    #     # PART: particle
    #     # PRON: pronoun
    #     # PROPN: proper noun
    #     # PUNCT: punctuation
    #     # SCONJ: subordinating conjunction
    #     # SYM: symbol
    #     # VERB: verb
    #     # X: other
    #     # Tag: The detailed part-of-speech tag.
    #     # Dep: Syntactic dependency, i.e. the relation between tokens.
    #     # Shape: The word shape – capitalization, punctuation, digits.
    #     # is alpha: Is the token an alpha character?
    #     # is stop: Is the token part of a stop list, i.e. the most common words of the language?

    #     # Aplicar una lematizacion para los verbos
    #     if(token.pos_ == "VERB"):
    #         # print(token.text, token.pos_, token.dep_,
    #         #       token.lemma_)
    #         tweet.text = re.sub(token.text, "@"+token.lemma_, tweet.text)
    #         # print("********************************************")

    # # detector de entidades con nombre
    for ent in doc.ents:
        # print(ent.text, ent.label_)

        if(ent.label_ == "LOC"):  # falta tener en cuenta varias LOC
            tweet.lugar_evento = ent.text

    tweet_sust_loc.append(tweet)

for tweet in tweet_sust_loc:
    for palabra in palabras_clave:
        if palabra in tweet.text:
            tweet.tipo_evento = palabra
    tweet_sust_eve.append(tweet)
    # print(tweet)

# patron que recoge cualquier palabra de mas de 3 caracteres despues de un numero, nos quedamos solo con una fecha (los espacios en blanco presentes son importantes)
regex = re.compile(
    '(\d{1,2}).[de]{2} ([ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic]{3})[a-z]*|([a-z]{3})[a-z]*(\d{1,2})', re.I)

for tweet in tweet_sust_eve:
    for x in regex.findall(tweet.text):
        mes = ""
        if x[0] == '':
            date = '-'.join(filter(None, x))
        else:
            date = '%s/%s/%s' % (x[0], x[1], 22)

            if(x[1] == "ene"):
                mes = "enero"
            elif (x[1] == "feb"):
                mes = "febrero"
            elif (x[1] == "mar"):
                mes = "marzo"
            elif (x[1] == "abr"):
                mes = "abril"
            elif (x[1] == "may"):
                mes = "mayo"
            elif (x[1] == "jun"):
                mes = "junio"
            elif (x[1] == "jul"):
                mes = "julio"
            elif (x[1] == "ago"):
                mes = "agosto"
            elif (x[1] == "sep"):
                mes = "septiembre"
            elif (x[1] == "oct"):
                mes = "octubre"
            elif (x[1] == "nov"):
                mes = "noviembre"
            elif (x[1] == "dic"):
                mes = "diciembre"

            if(mes != ""):
                tweet.fecha_evento = x[0] + " de " + mes

            else:
                if filtro_palabras_clave(tweet.text, fechas):
                    for palabra in fechas:
                        if palabra in tweet.text:
                            tweet.fecha_evento = palabra

    tweet_sust.append(tweet)
    # print("")
    # print(tweet)


# filtrar tweets que no contengan todos los elementos
lista_tweets_sustituidos = []

for tweet in tweet_sust:
    if tweet.tipo_evento != None and tweet.lugar_evento != None and tweet.fecha_evento != None:
        lista_tweets_sustituidos.append(tweet)


for tweet in lista_tweets_sustituidos:
    print("")
    print(tweet.text)
    print("- EVENTO: ", tweet.tipo_evento)
    print("- LOCALIZACION: ", tweet.lugar_evento)
    print("- FECHA: ", tweet.fecha_evento)

print(len(lista_tweets_sustituidos))
# # escribir patrones en un fichero .txt
# file = open("c:/Users/Tomy/Desktop/tfg/patrones.txt", "w")
# for patron in lista_patrones_seleccionados:
#     patron_str = " ".join(patron.patron_recortado)
#     file.write(patron_str + os.linesep)
# file.close()
# print("Patrones almacenados en patrones.txt")
