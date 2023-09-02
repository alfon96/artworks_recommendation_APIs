import time

class MisuraPerformance():

    tempi_start = []
    tempi_stop  = []
    tempi_descrizione_start = []
    tempi_descrizione_stop = []
    titoli = {}
    misure  = []


    def start(descrizione: str = None):
        MisuraPerformance.tempi_start.append(time.time())
        MisuraPerformance.tempi_descrizione_start.append(descrizione)

    def inserisci_titolo(titolo : str):
        MisuraPerformance.titoli.update({len(MisuraPerformance.tempi_descrizione_start):titolo})

    def stop(descrizione: str = None):        
        MisuraPerformance.tempi_stop.append(time.time())
        MisuraPerformance.tempi_descrizione_stop.append(descrizione)

    def ottieni_misure():
       MisuraPerformance.misure = [ MisuraPerformance.tempi_stop[x] - MisuraPerformance.tempi_start[x] for x in range(len(MisuraPerformance.tempi_start)) ]

    def carica_misure(misure : list = []):
        MisuraPerformance.misure = misure


    def formatta_misurazioni():
        testo = []
        break_id = 0

        for x in range(len(MisuraPerformance.tempi_start)):
            if x > 0 and MisuraPerformance.titoli.get(x,False):  
                testo.append(f"[Totale] = {sum(MisuraPerformance.misure[:x])}s")
                break_id = x
            if MisuraPerformance.titoli.get(x,False):
                testo.append("-----------------------------")
                testo.append(MisuraPerformance.titoli.get(x))
                testo.append("-----------------------------")
            testo.append(f"{MisuraPerformance.tempi_descrizione_start[x]} : {MisuraPerformance.misure[x]}s")

        testo.append(f"[Totale] = {sum(MisuraPerformance.misure[break_id:])}s")
        return testo

    def azzera_misurazioni():
        MisuraPerformance.tempi_start = []
        MisuraPerformance.tempi_stop  = []
        MisuraPerformance.tempi_descrizione_start = []
        MisuraPerformance.tempi_descrizione_stop = []
        MisuraPerformance.misure  = []
        MisuraPerformance.misure_formattate = []