from app.risorse_condivise.classi_condivise import Config
from app.raccomandazione.modello_effettivo import InfoUtente
from app.configurazione.gestore_dataframes import carica_dataframe_opere_solo_tipologia
from sklearn.metrics.pairwise import cosine_similarity
from itertools import combinations
from app.test.performance import MisuraPerformance

carica_dataframe_opere_solo_tipologia()




def test_accuratezza_raccomandazione_utente():
    id_utente = 1
    preferenze = Config.df_opere_solo_tipologia.columns.to_list()
    print(preferenze)
    preferenze.remove(12)
    coordinate_GPS = []
    ratings_poi = []
    ratings_multimedia = []


    for m in range(11):
        # Genera tutte le possibili permutazioni del vettore x
        combinazioni = list(combinations(preferenze, m))

        # Stampa tutte le permutazioni
        for preferenza in combinazioni:
            user = InfoUtente(id_utente, preferenza, coordinate_GPS, ratings_poi, ratings_multimedia)
            user.ottieni_raccomandazioni()
            print("Preferenze attuali : ", preferenza)

test_accuratezza_raccomandazione_utente()



# def create_excel_file():
#     # crea una matrice casuale di 0 e 1 di dimensione 238x21
#     matrix = np.random.randint(low=0, high=2, size=(238, 21))
    
#     # converte la matrice in un dataframe pandas
#     df = pd.DataFrame(matrix)
    
#     # crea un oggetto ExcelWriter e scrive il dataframe in un file Excel
#     writer = pd.ExcelWriter('matrix.xlsx')
#     df.to_excel(writer, sheet_name='Sheet1', index=False)
#     writer.save()
#     print("Saved succesfully")


# from sklearn.metrics.pairwise import cosine_similarity
# import numpy as np

# def calculate_cosine_similarity(data, numero_preferenze_utente):
#     """
#     Calcola la similarità coseno tra una matrice di dimensioni nxn e un insieme di vettori di dimensioni crescenti
#     da 1 a n.
#     Restituisce una lista contenente il massimo valore di similarità per ogni dimensione e il differenziale
#     tra i valori di similarità.
#     """
#     n = data.shape[0]
#     similarities = []
    
#     for dim in range(1, n+1):
#         # crea una matrice Nxdim contenente solo 1 o 0
#         matrix = np.random.randint(2, size=(n, dim))
#         # crea un vettore 1xdim contenente solo 1 o 0
#         n_ones = numero_preferenze_utente if dim>numero_preferenze_utente else dim   # numero di 1 da inserire
#         vector = np.zeros(dim)
#         # genera un array di indici casuali
#         random_indices = np.random.choice(dim, n_ones, replace=False)
#         # imposta gli elementi del vettore agli indici casuali a 1
#         vector[random_indices] = 1

#         # calcola la similarità coseno tra la matrice e il vettore
#         similarity = cosine_similarity(matrix, vector.reshape(1,-1)).mean()
#         similarities.append(similarity)

#     return similarities

# import statistics
# import random
# N = 250
# max_mean = -1
# result = []
# max_cols = 22

# print(f"Numero di colonne ideale per massimizzare la media delle predizioni per una matrice di opere di dim_max = [{N},{max_cols}]  : " )
# for numero_preferenze_utente in range(1,5):
#     for M in range(1, max_cols + 1):
#         X = random.randint(1,10)
#         matrix = np.zeros((N, M))

#         # imposta i valori casuali delle colonne
#         for j in range(M):
#             indices = np.random.choice(N, X, replace=False)
#             matrix[indices, j] = 1
        
#         similarities = calculate_cosine_similarity(matrix, numero_preferenze_utente)

#         best_cols = max(range(len(similarities)), key=similarities.__getitem__) + 1
#         mean = statistics.mean(similarities)
#         max_points = max(similarities)
        
#         if mean> max_mean:
#             result = [best_cols, mean,max_points ]

#     print(f"n_preferenze: {numero_preferenze_utente}, best_n_cols : {result[0]}, media = {result[1]}, max = {result[2]}")