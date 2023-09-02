from app.risorse_condivise.classi_condivise import Config
from app.raccomandazione.modello_effettivo import InfoUtente, InfoUtenteConOpere
from app.configurazione.gestore_dataframes import carica_dati_app
from app.raccomandazione.rotte_api_modello import ottieni_breakpoints_maestro
from sklearn.metrics.pairwise import cosine_similarity
from app.test.performance import MisuraPerformance
from itertools import combinations
import numpy as np
import random

carica_dati_app()



def test_accuratezza_raccomandazione_utente():
    id_utente = 1
    print(Config.liste_colonne_df[1] + Config.liste_colonne_df[2])
    preferenze = Config.liste_colonne_df[1]
    coordinate_GPS = []
    ratings_poi = []
    ratings_multimedia = []
    risultati = []
    count = 0

    for m in range(4,5):
        # Genera tutte le possibili permutazioni del vettore x in m 
        combinazioni = list(combinations(preferenze, m))

        # Stampa tutte le permutazioni
        for preferenza in combinazioni:
            id_contenuto_multimediale = random.randint(1, 3)
            dizionario_id_opere_breakpoints = ottieni_breakpoints_maestro(id_contenuto_multimediale)
            user_item = InfoUtenteConOpere(id_utente, preferenza, coordinate_GPS, ratings_poi, ratings_multimedia, dizionario_id_opere_breakpoints,id_contenuto_multimediale)

            # user.insert_opere_breakpoints()
            user_item.ottieni_raccomandazioni()

            MisuraPerformance.ottieni_misure()
            if not risultati    : risultati = [ MisuraPerformance.misure[x] for x in range(len(MisuraPerformance.misure))]
            else                : risultati = [ risultati[x]+MisuraPerformance.misure[x] for x in range(len(MisuraPerformance.misure))]
            temp = MisuraPerformance
            MisuraPerformance.azzera_misurazioni()
            count +=1

            print("Preferenze attuali : ", preferenza)
    risultati = [ risultati[x]/count for x in range(len(risultati))]
    temp.carica_misure(risultati)
    print(temp.formatta_misurazioni())

test_accuratezza_raccomandazione_utente()
