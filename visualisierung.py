
"""
=========================================================
PROJEKT:        Schnittgrößen-Solver
DATEI:          visualisierung.py
BESCHREIBUNG:   Grafik-Modul des Projekts. Nutzt Matplotlib, 
                um das Freikörperbild (Skizze) sowie die 
                Diagramme für Querkraft und Biegemoment 
                dynamisch zu zeichnen.
---------------------------------------------------------
ENTWICKLER:     [Dein Name]
VERSION:        v1.0.0 (Final)
=========================================================
"""




import matplotlib.pyplot as plt
import numpy as np


class Diagramm_Zeichner:
    """
    Klasse zur grafischen Darstellung des statischen Systems und der Schnittgrößen.
    """


    def __init__(self, x_werte, q_werte, m_werte, balken_objekt):
        """
        Initialisiert den Diagramm-Zeichner mit den Berechnungsdaten.

        Speichert die x-Achse, die Arrays für Querkraft und Biegemoment 
        sowie das Balken-Objekt (für die Geometrie und Lasten) als Attribute.
        """
        self.x_Werte = x_werte
        self.q_Werte = q_werte
        self.m_Werte = m_werte
        self.Balkenobjekt = balken_objekt



    def zeichne(self):
        """
        Erstellt die komplette grafische Ausgabe (Freikörperbild, Querkraft, Biegemoment).

        Baut ein Fenster mit drei vertikal gekoppelten Diagrammen (Subplots) auf. 
        Die x-Achsen sind synchronisiert (sharex=True), um die Lasten im FKB 
        direkt über den zugehörigen Schnittgrößenverläufen ablesen zu können. 
        
        Returns:
            fig: Das fertige Matplotlib-Figure-Objekt zur Einbindung in Streamlit.
        """


        fig, (ax_skizze,ax1,ax2) = plt.subplots(3,1,figsize=(8,6), sharex = True)
        
        fig.suptitle("Schnittgrößenverläufe", fontsize=18, fontweight="bold")


        self.zeichne_FKB(ax_skizze) #Methode zur Freikörperbild Zeichnung wird aufgerufen
        

        #Oberes Diagramm (Querkraft)
        ax1.plot(self.x_Werte, self.q_Werte, color="red", linewidth=2)
        ax1.set_ylabel("Querkraft Q [kN]")
        ax1.axhline(0,color="black",linewidth=1.5) #beim Nulldurchgang wird ein schwarzer Strich gezogen
        ax1.grid(True, linestyle=':', alpha=0.7) # Hilfsgitter mit : als Zeichen, leicht durchsichtig (alpha=0.7)

        #unteres Diagramm (Biegemoment)
        ax2.plot(self.x_Werte, self.m_Werte, color="blue", linewidth=2, linestyle='--')
        ax2.set_xlabel("Balkenlänge x [m]") # durch sharex=True gibt es im gesamten Fenster nur eine einzige X Achse
        ax2.set_ylabel("Biegemoment M [kNm]")
        ax2.axhline(0,color="black", linewidth=1.5)
        ax2.grid(True, linestyle=':', alpha=0.7)

        #Layout optimieren
        plt.tight_layout() #Diagramme werden so zurecht geschoben dass sich keine Texte überschneiden



        return fig
    
    
    def zeichne_FKB(self, ax_skizze):
        """
        Zeichnet das statische System (Freikörperbild) in das oberste Diagramm.

        Skizziert den Balken, die Auflager (Fest- und Loslager) sowie alle 
        angreifenden Punktlasten, Streckenlasten und freien Momente mit den 
        entsprechenden Richtungen, Vorzeichen und Beschriftungen.
        """


        #Rahmen der Skizze:
        ax_skizze.set_ylim(-4.0, 4.0)
        #set_ylim --> Funktion setzt Grenzen der Y-Achse

        #rechtes Auflager --> Loslager:
        ax_skizze.plot(self.Balkenobjekt.Balkenlaenge, -0.7, marker='^', markersize=12, color='gray')
        #x|y Koordinaten --> x = Balkenlaenge, y=-0.5 --> Dreieck soll etwas unter dem Balken angreifen
        
        #Rolle um Loslager zu kennzeichnen:
        ax_skizze.plot(self.Balkenobjekt.Balkenlaenge, -1.9, marker='_', markersize=25, markeredgewidth=3, color='gray')
        #x|y Koordinaten --> x = Balkenlaenge, y=-1.0 --> Rolle soll etwas unter dem Dreieck angreifen
        #marker '_' --> Befehl/Funktion für Strich zeichnen
        #markeredgewidth=6 --> macht Strich dicker

        #linkes Auflager --> Festlager:
        ax_skizze.plot(0,-0.9,marker='^',markersize=15, color='gray')
        #x|y Koordinaten --> x = 0, y=-0.5 --> Dreieck soll etwas unter dem Balken angreifen
        #marker='^' --> Befehl/Funktion für Dreieck
        #markersize = 15 --> Größe des Dreieck
        

        #waagerechter Träger (Linie)
        ax_skizze.plot([0, self.Balkenobjekt.Balkenlaenge], [0,0], color ='black', linewidth = 5)
        #Matplotlib arbeit in Achsen Listen --> erster Block [] x Werte --> von O bis Balkenlänge
        #                                   --> zweiter Block [] y Werte Höhe der Punkte

        #Punktlasten
        for last in self.Balkenobjekt.punktlasten:
            abstand = last[0]
            kraft = last[1]

            #wenn Kraft positiv ist soll Pfeil auf den Träger von unten drücken
            if kraft > 0:
                ax_skizze.annotate(             #annotate Funktion bindet eine Information an einen bestimmten Punkt
                    f"{kraft} kN",              #Betrag der Kraft wird auf den Pfeil geschrieben
                    xy=(abstand,0),             #Koordinaten für Pfeilspitze --> x = Abstand der Punktlast zum linken Lager, y = 0 --> Pfeilspitze soll direkt auf Träger angreifen
                    xytext=(abstand,-3.0),      #Position des Textes & und Länge des Pfeils
                    arrowprops=dict(facecolor='red', width=3, headwidth=10), #Pfeil Eigenschaften: width=3 Dicke des Pfeilstamms, headwidth=10 Breite der Pfeilspitze
                    ha='center',                #ha='center' --> Text steht zentriert über dem Pfeil
                    va='top',                    #Text ist sauber unter dem Pfeilende
                    color='red'
                    )

            #wenn Kraft negativ ist soll Pfeil auf den Träger von oben drücken
            if kraft < 0:
                ax_skizze.annotate(             #annotate Funktion bindet eine Information an einen bestimmten Punkt
                    f"{kraft} kN",              #Betrag der Kraft wird auf den Pfeil geschrieben
                    xy=(abstand,0),             #Koordinaten für Pfeilspitze --> x = Abstand der Punktlast zum linken Lager, y = 0 --> Pfeilspitze soll direkt auf Träger angreifen
                    xytext=(abstand,3.0),       #Startpunkt des Pfeils /Koordinate für Textfeld
                    arrowprops=dict(facecolor='red', width=3, headwidth=10), #Pfeil Eigenschaften: width=3 Dicke des Pfeilstamms, headwidth=10 Breite der Pfeilspitze
                    ha='center',                #ha='center' --> Text steht zentriert über dem Pfeil
                    va='bottom',                #Text ist sauber über dem Pfeilende
                    color='red'
                    )
                

        #Streckenlasten
        for last in self.Balkenobjekt.streckenlasten:
            start = last[0]
            ende = last[1]
            q = last[2]
        
            if q < 0: #wenn Streckenlast negativ ist muss Pfeil von oben auf Träger drücken --> y Koordinaten = 1,5
                y_Koordinate = 1.5
                text_y = 2.5 #y Koordinate für q welches auf dem Streckenlast Block steht

            else:#wenn Streckenlast positiv ist genau das Gegenteil
                y_Koordinate = -1.5
                text_y = -2.5 #y Koordinate für q welches auf dem Streckenlast Block steht

            ax_skizze.plot([start, ende], [y_Koordinate, y_Koordinate], color='blue') #horizontale Linie als obere/untere Begrenzung

            #da die Länge des Balkens stark varrieren kann darf es keinen statischen Abstand zwischen den einzelnen Pfeilen geben.
            #--> durch np.linspace werden 5 Werte geliefert welche alle den gleichen Abstand zwischen Start und Ende haben
            x_Koordinaten_Pfeile= np.linspace(start,ende,5)

            for x_Koordinate in x_Koordinaten_Pfeile:
                ax_skizze.annotate(
                    "",                                 #Nutzen der Hinweis Pfeil Funktion ohne Text bzw. mit leerem string ""
                    xy=(x_Koordinate,0),                #Koordinaten für Pfeilspitze
                    xytext=(x_Koordinate,y_Koordinate), #Startpunkt des Pfeils /Koordinate für Textfeld
                    arrowprops=dict(arrowstyle="->",color='blue') #Eigenschaften des Pfeils --> arrowstyle="->" ergibt eindimensionale Linie mit v förmigen Abschluss
                )

            ax_skizze.text(               # Befehl um beliebigen Text ins Diagramm zu schreiben
                (ende - start)/2 + start, # x Koordinate für Textfeld über dem Streckenlast Block --> von Lager A und bis start des Blocks + Mitte des BLocks
                text_y,                   # y_Koordinate in if else oben festgelegt
                f"{q} kN", 
                ha='center',              # Zentriert den Text horizontal auf der X-Koordinate
                va='center',              # Zentriert den Text vertikal auf der Y-Koordinate
                color='blue'
            )


        # freie Momente
        for moment in self.Balkenobjekt.einzelmomente:
            abstand = moment[0]
            m_wert = moment[1]
                
            # in Abhängigkeit des Vorzeichen der Kraft wird das jeweilige Unicode zeichen ausgewählt
            if m_wert > 0:
                moment_symbol = "↺"  # Positiv: Gegen den Uhrzeigersinn
            else:
                moment_symbol = "↻"  # Negativ: Im Uhrzeigersinn


            ax_skizze.text(          # Befehl um beliebigen Text ins Diagramm zu schreiben
                abstand, 0,          # Koordinaten, x --> Abstand von linken Lager, y --> Mittelpunkt des Kreis auf dem Balken
                moment_symbol,       # vorausgewähltes Unicode Zeichen
                ha='center',         # Symbol wird exakt auf der X-Koordinate zentriert
                va='center',         # Zentriert das Symbol exakt auf der Y-Koordinate
                color='purple', 
                fontsize=25,         # frontsize steuert die Größe des Text/Symbol
                fontweight='bold'    # Linien des Kreises werden dicker
            )
                
            #Beschriftung über dem Symbol
            ax_skizze.text(          # Befehl um beliebigen Text ins Diagramm zu schreiben
                abstand, 1.5,        # Koordinaten, x --> Abstand von linken Lager, y --> Text soll über dem Symbol stehen
                f"{m_wert} kNm", # Kraft wird angezeigt
                ha='center',         # Symbol wird exakt auf der X-Koordinate zentriert
                va='center',         # Zentriert das Symbol exakt auf der Y-Koordinate
                color='purple', 
            )


        ax_skizze.axis('off')#Koordinatensystem ausschalten