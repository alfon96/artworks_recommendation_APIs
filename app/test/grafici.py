from app.risorse_condivise.classi_condivise import  Config
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib
matplotlib.use('Agg')
from matplotlib.pyplot import figure

class Grafici():
    
    def __init__(self,df : pd.DataFrame, punteggi : np.ndarray = []):
        self.df = df
        self.punteggi = punteggi
        self.tipologie = { '1':"Artigianato", '2':"Biblioteca o Archivio", '3':"Castello", '4':"Chiesa", '5':"Design", '6':"Enogastronomia", '7':"Fotografia", '8':"Installazione multimediale", '9':"Palazzo", '10':"Performance artistica", '11':"Piazza",'12':"Pittura", '13':"Ponte", '14':"Sala",'15':"Scultura", '16':"Strada", '17':"Street art",'18':"Teatro ", '19': "Gioielleria", '20':"Archeologia", '21':"Sport",  '22':"Antiquariato"}
        self.num_righe, self.num_colonne, self.colonne_presenti, self.colonne_mancanti, self.num_duplicates = self.ottieni_info_statiche()
        self.figure_size = (25,22)
        self.figure_size_punteggi = (25,22)
        # Font size
        self.font_title_size = 32
        self.font_axis_size = 28
        self.legenda_font_size = 20
        self.font_righe_oblique_size = 18
        self.soglie_punteggi = [0.1, 0.3, 0.5, 0.7, 0.9]
        self.soglia_intorno = 0.1
        self.prop = fm.FontProperties(fname=r"app/file_statici/fonts/PoppinsLight.ttf")

    def get_colors_vector(self, num_labels):   return [plt.cm.Paired(i / num_labels) for i in range(len(self.df.columns))]

    def ottieni_info_statiche(self):
        # Calcolo righe e colonne del dataframe
        num_righe = self.df.shape[0]
        num_colonne = self.df.shape[1]

        # Tipologie presenti e non nel dataframe
        colonne_presenti = [colonna for colonna in self.df.columns if colonna in self.tipologie]
        colonne_mancanti = {colonna:self.tipologie[colonna] for colonna in self.tipologie if colonna not in self.df.columns}

        # Righe duplicate
        num_duplicates = Config.df_opere.duplicated(subset="Opera").sum()

        return num_righe, num_colonne, colonne_presenti, colonne_mancanti, num_duplicates
    
    def grafico_df_solo_tipologia(self):
        # Rinomina le colonne selezionate utilizzando il dizionario
        df = self.df[Config.liste_colonne_df[1]].rename(columns={colonna: self.tipologie[colonna] for colonna in self.colonne_presenti})
        # Grafico e assi
        num_uno = df.sum()
    
        self.opzioni_visualizzazione(
            num_uno.index, num_uno.values, "Distribuzione delle Tipologie nelle Opere",
            "Tipologie Opere", "Numero Opere"
            )
        
        # Salva
        plt.savefig(f"{Config.path_analisi_db}/dati_statistici_database_tipologia.png")
        plt.close()
    
    def grafico_df_completo(self):
        # Crea il grafico
        ones_per_col = self.df[Config.liste_colonne_df[1] + Config.liste_colonne_df[2]].sum()
        bins = [0, 10, 20, 30, 40, 50, 60, 70, 100, float("inf")]
        labels = ["<10", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70-100", ">100"]
        counts, _ = np.histogram(ones_per_col, bins=bins)
        
        self.opzioni_visualizzazione(
            labels, counts, "Numero di presenze del tag nelle opere",
            "Numero di colonne", "Distribuzione dei tag nelle opere"
            )
        
        plt.savefig(f"{Config.path_analisi_db}/dati_statistici_database_completo.png")
        plt.close()

    def grafico_df_utenti_opere(self):
        # Crea il grafico
        ones_per_col = self.df.sum()
        print(self.df)
        bins = [0, 1, 4, 7,10, float("inf")]
        labels = ["0", "1-3", "4-6", "7-9", ">10"]
        counts, _ = np.histogram(ones_per_col, bins=bins)
        
        self.opzioni_visualizzazione(
            labels, counts, "Distribuzione dei like degli utenti per le opere",
            "Numero di like", "Numero di opere", tipologie_non_presenti=False
            )
        
        plt.savefig(f"{Config.path_analisi_db}/dati_statistici_database_utenti_opere.png")
        plt.close()

    def opzioni_visualizzazione(self, labels, count, titolo : str, asse_x  : str, asse_y  : str, tipologie_non_presenti=True):
        figure(figsize=self.figure_size, dpi=80)
        # Variabili per lo stile del grafico

        plt.rcParams.update({
            'font.family': 'Poppins',
            'font.size': self.font_axis_size,
        })
        
        font_title = {'fontsize': self.font_title_size, 'fontproperties':self.prop}
        font_axis  = {'fontsize': self.font_axis_size, 'fontproperties':self.prop}
        colors = self.get_colors_vector(len(labels))

        # Grafico e assi
        plt.bar(labels, count, 0.98,color=colors)
        plt.title(titolo, font_title)
        plt.xlabel(asse_x, font_axis)
        plt.ylabel(asse_y, font_axis)
        plt.xticks(rotation=45, ha='right', fontsize=self.font_righe_oblique_size)

        # Legenda
        legenda = f"Numero di righe: {self.num_righe}\nNumero di colonne: {self.num_colonne}"
        if tipologie_non_presenti:
            legenda += "\nOpere con lo stesso nome: {self.num_duplicates}\n\nTipologie non presenti:\n"
            for valore in self.colonne_mancanti.values(): legenda += f"{valore}\n"
        plt.text(0.95, 0.95, legenda, transform=plt.gca().transAxes, ha='right', va='top', fontsize= self.legenda_font_size, fontproperties=self.prop)

        # Aggiungi il valore di ogni istogramma
        for i, valore in enumerate(count):      plt.text(i, valore, str(valore), ha='center', va='bottom')


    def grafico_punteggi(self, nome: str = None, info : list = None):

       # Contare il numero di elementi per ogni soglia
        
        num_elements = [np.sum(np.logical_and(self.punteggi >= soglia-self.soglia_intorno , self.punteggi <= soglia+self.soglia_intorno)) for soglia in self.soglie_punteggi]

        # Creare il vettore di legenda
        legend_labels = ['({} - {})% ({}/{})'.format(int((self.soglie_punteggi[i]-self.soglia_intorno) * 100),int((self.soglie_punteggi[i] + self.soglia_intorno) * 100), np.sum(np.logical_and(self.punteggi >= self.soglie_punteggi[i]-self.soglia_intorno , self.punteggi <= self.soglie_punteggi[i]+self.soglia_intorno)), len(self.punteggi)) for i in range(len(self.soglie_punteggi))]
        plt.rcParams.update({
            'font.family': 'Poppins',
            'font.size': self.font_axis_size,
        })
        

        # Creare il grafico a barre
        figure(figsize=self.figure_size_punteggi, dpi=80)
        plt.bar(self.soglie_punteggi, num_elements, width=0.095, color=self.get_colors_vector(len(num_elements)), tick_label=[str(soglia) for soglia in self.soglie_punteggi], label=legend_labels)

        # Aggiungere i numeri precisi dei dati su ogni rettangolo del grafico
        for i, num in enumerate(num_elements):
            plt.text(self.soglie_punteggi[i], num, str(num), ha='center', va='bottom')
        plt.legend(loc='upper right',fontsize= self.legenda_font_size)
        # Mostrare il grafico
        tipo_di_raccomandazione = "Contenuto" if self.df.columns.to_list() == Config.df_opere.columns.to_list() else "Utente"
        interessi = "insieme di caratteristiche contenuto multimediale e preferenze utente" if self.df.columns.to_list() == Config.df_opere.columns.to_list() else "interessi utente"
        

        font_title = {'fontsize': self.font_title_size, 'fontproperties':self.prop}
        font_axis  = {'fontsize': self.font_axis_size, 'fontproperties':self.prop}

        # Grafico e assi
        plt.title(f'Uscita del Modello di raccomandazione per {tipo_di_raccomandazione}', font_title)
        plt.xlabel(f'Percentuale di somiglianza con {interessi} (%)', font_axis)
        plt.ylabel('Opere', font_axis)
        plt.xticks(rotation=45, ha='right', fontsize=self.font_righe_oblique_size)

        legenda = "\nInteressi utente:\n"
        if info:
            info = [str(x) for x in info]
            m = int(len(info)/40) + 1

            for i in range(0, len(info), m):
                gruppo = info[i:i+m]
                legenda += ",".join(gruppo) + "\n"
            plt.text(0.95, 0.85, legenda, transform=plt.gca().transAxes, ha='right', va='top', fontsize= self.legenda_font_size, fontproperties=self.prop)

        # Salva
        if not nome:  nome = f'dati_statistici_predizioni_{tipo_di_raccomandazione}.png'
        plt.savefig(nome)
        plt.close()