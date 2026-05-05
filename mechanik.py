
"""
=========================================================
PROJEKT:        Schnittgrößen-Solver
DATEI:          mechanik.py
BESCHREIBUNG:   Physik-Engine des Projekts. Enthält die 
                Klassen 'Balken' und 'SchnittgroessenRechner' 
                zur Ermittlung von Auflagerkräften und 
                Schnittgrößenverläufen (Q, M).
---------------------------------------------------------
ENTWICKLER:     [Linus Schiel]
VERSION:        v1.0.0 (Final)
=========================================================
"""


import numpy as np

class Balken:
    """Repräsentiert einen Einfeldträger und speichert alle angreifenden Lasten."""
    

    
    def __init__(self, laenge):
        """
        Initialisiert den Balken mit einer bestimmten Länge
        
        Setzt die Länge fest und erstellt leere Listen für Punktlasten, Streckenlasten und freie Momente
        """

        #Laenge wird als Attribut gespeichert
        self.Balkenlaenge = laenge

        #leere Liste um Punktlasten zu speichern
        self.punktlasten = []

        #leere Liste um Streckenlasten zu speichern
        self.streckenlasten = []

        #leere Liste um freie Momente zu speichern
        self.einzelmomente = []


    
    def zeige_Daten(self):
        """Hilfsmethode um beim Debuggen den erstellten Balken und die eingespeicherten Lasten zu überprüfen"""

        print(f"Balken erfolgreich erstellt! Länge: {self.Balkenlaenge}m")

        print(f"Aktuelle Punktlasten: {len(self.punktlasten)}")#len() steht für length --> es zählt wie viele Elemente in der Liste sind

    

    def speichere_Punktlast(self, abstand,kraft):
        """
        Methode um Punktlasten zu speichern/anzuhängen
        
        Achtung: Hier wird nicht auf Falscheingaben (Bsp: Position liegt nicht auf Balken) geprüft
        --> wird in app.py bei der Eingabe gemacht
        """


        #wenn Nutzer Kraft und Abstand der pUnktlast angibt werden diese Werte an die Liste angehängt
        # Punktlast mit Abstand 4 und Kraft 10 --> self.punktlasten = [[4,10]]
        #--> später ist ein einfaches abrufen möglich
        self.punktlasten.append([abstand,kraft])

   
    def speicher_Streckenlast(self, start, ende, q):
        """
        Methode um Streckenlasten zu speichern/anzuhängen
        
        Achtung: Hier wird nicht auf Falscheingaben (Bsp: Position liegt nicht auf Balken) geprüft
        --> wird in app.py bei der Eingabe gemacht
        """

        #analoges System wie in Punktlast Methode
        self.streckenlasten.append([start, ende, q])


    def speicher_freie_Momente(self,abstand, moment):
        """
        Methode um freie Momente zu speichern/anzuhängen
        
        Achtung: Hier wird nicht auf Falscheingaben (Bsp: Position liegt nicht auf Balken) geprüft
        --> wird in app.py bei der Eingabe gemacht
        """

        #analoges System wie in Punktlast Methode
        self.einzelmomente.append([abstand,moment])



    #Methode um Lagerkraefte zu berechnen
    def berechne_Lagerkraefte(self):

        """
        Berechnet die Auflagerkräfte A und B für einen Einfeldträger.

        Verwendet die globalen Gleichgewichtsbedingungen:
        1. Summe M_A = 0 (um B zu berechnen)
        2. Summe F_y = 0 (um A zu berechnen)
        Achtung: Äußere Lasten nach unten müssen negativ eingegeben werden.
        Herleitung siehe Notizen: Herleitung_Schnittgroessen.pdf
        """

        #lokale Variablen (ohne Vorsatz self.) Nutzung welche nur einmalig in der Methode erhalten sind
        Moment_um_A = 0.0
        Summe_aller_Kraefte_y = 0.0


        #for Schleife Punktlast
        for last in self.punktlasten: #Interpret durchläuft Liste der Punktlasten und nimmt jedes angehängte "Paket" [4,10]
                                      #--> als Abstand wird der erste Wert genommen, als Kraft zweiter Wert
                                      #danach wird nächstes "Paket" genommen....
            abstand = last[0]
            kraft = last[1]

            # Kräfte in y Richtung werden alle aufaddiert
            # durch einhalten der richtigen Vzw. Konventionen kann hier aufaddiert werden
            Summe_aller_Kraefte_y += kraft

            # Moment um A durch Kraft mal Hebelarm zum Lager A
            # auch hier werden Vzw. Konventionen eingehalten
            Moment_um_A += kraft * abstand

        # for Schleife Streckenlast
        for last in self.streckenlasten:
            start = last[0]
            ende = last[1]
            q = last[2]

            # Ersatzkraft_q aus der Streckenlast und Fläche berechnen
            Ersatzkraft_Q = (ende - start) * q

            # Kräfte in y Richtung werden alle aufaddiert, notwendig für Lagerkraftberechnung
            # durch einhalten der richtigen Vzw. Konventionen kann hier aufaddiert werden
            Summe_aller_Kraefte_y += Ersatzkraft_Q

            # Schwerpunkt der Fläche über der die Streckenlast wirkt berechnen --> Hebelarm
            hebelarm = start + 1/2*(ende - start) #zuerst wird Länge bis zur Streckenlast Fläche genutzt und dann Hälfte der Fläche

            # Moment um A durch Ersatzkraft mal Hebelarm zum Lager A
            # auch hier werden Vzw. Konventionen eingehalten
            Moment_um_A += Ersatzkraft_Q * hebelarm


        # for Schleife freie Momente
        for last in self.einzelmomente:
            M = last[1]

            # für Summe aller Kräfte in y Richtung ist Moment irrelevant

            # Summe M = 0 --> M = -freies Moment
            # auch hier werden Vzw. Konventionen eingehalten
            Moment_um_A += M

        # durch die drei for Schleifen sind alle Punktlasten, Streckenlasten sowie freie Momente in den beiden lokalen Variablen berücksichtigt
        # --> Berechnung der Lagerkräfte

        # Lagerkraft B: Summe M_A = 0 --> Lagerkraft_B_y * self.Balkenlaenge + Moment_um_A = 0
        self.Lagerkraft_B_y = -Moment_um_A / self.Balkenlaenge

        # Lagerkraft A: Summe F_y = 0 --> Lagerkraft A + Lagerkraft B + Summe_aller_Kraefte_y = 0
        self.Lagerkraft_A_y = -Summe_aller_Kraefte_y - self.Lagerkraft_B_y




class SchnittgroessenRechner:
    """Erstellung der Arrays des Biegemomenten_Verlaufs sowie der Querkraft"""

    

    def __init__(self, uebergebener_balken):
        """
        Initialisiert den Rechner und bereitet die Arrays für die Schnittgrößen vor.
        
        Speichert das übergebene Balken-Objekt ab und erstellt eine hochauflösende 
        x-Achse (1000 Punkte) für präzise Diagramme. Zudem werden leere Null-Arrays 
        für die spätere Berechnung von Querkraft (Q) und Biegemoment (M) generiert.
        """ 


        self.balken = uebergebener_balken
        self.x_werte = np.linspace(0, self.balken.Balkenlaenge, 1000)

        #np.zeros_like baut Array, das exakt so lang ist wie x_werte, aber voll mit Nullen
        self.q_werte = np.zeros_like(self.x_werte)
        self.m_werte = np.zeros_like(self.x_werte)
    
    

    def berechne_linien(self):
        """
        Berechnet die Verläufe von Querkraft und Biegemoment entlang des gesamten Balkens.

        Iteriert über die x-Achse (das Schnittufer) und summiert an jedem 
        Punkt die Einflüsse der linken Lagerkraft, der Punktlasten, Streckenlasten 
        und freien Momente auf Basis der statischen Gleichgewichtsbedingungen auf.

        Herleitung siehe Notizen: Herleitung_Schnittgroessen.pdf

        Returns:
            Ein Tuple (x_werte, q_werte, m_werte) zur grafischen Darstellung.
        """


        for i, x in enumerate(self.x_werte): # enumerate liefert den Index (i) und den echten x-Wert des Schnittufers gleichzeitig
            # der Index geht von 0 bis 999 (Balken wurde in tausend Teile zerteilt) durch die ganzzahligen i werte können die passenden Arrays befüllt werden

            #Lagerkraft als Startwert gegeben:
            
            # Summe F_y = 0 --> A - Q = 0
            aktuelle_querkraft = self.balken.Lagerkraft_A_y
            
            # Summe M = 0 --> M = Ax
            aktuelles_moment = self.balken.Lagerkraft_A_y * x


            #Punktlasten
            for last in self.balken.punktlasten: #Interpret durchläuft Liste der Punktlasten und nimmt jedes angehängte "Paket" [4,10]
                                                 #--> als Abstand wird der erste Wert genommen, als Kraft zweiter Wert
                                                 #danach wird nächstes "Paket" genommen....
                abstand = last[0]
                kraft = last[1]

                # wenn die Punktlast links von dem Schnittufer ist muss der Wert für die Querkraft und das Moment aktualisiert werden
                if abstand <= x: #Abstand geht vom Balkenanfang bis zur Punktlast, x geht vom Balkenanfang bis zum Schnittufer
                    
                    # F_y = 0 --> A + F -Q = 0 --> Lagerkraft ist schon als Startwert gegeben siehe oben
                    aktuelle_querkraft += kraft #Punktlast wird von aktueller Querkraft abgezogen


                    Hebelarm_Punktlast = x - abstand

                    #Summe M = 0 --> 0 = M - kraft * Hebelarm
                    aktuelles_moment += kraft * Hebelarm_Punktlast


            #Streckenlasten
            for last in self.balken.streckenlasten: #analoges Vorgehen siehe Punktlast
                start = last[0]
                ende = last[1]
                q = last[2]

                #1. Fall --> Schnittufer vor der Streckenlast x < start --> keine Beachtung

                #2. Fall --> Schnittufer MITTEN IN der Streckenlast start <= x <0 ende
                if start <= x <= ende:
                    wirksame_Laenge = x - start
                    Ersatzkraft_q = q * wirksame_Laenge
                    Hebelarm = wirksame_Laenge / 2

                    #Summe F_y = 0 --> 0= -Q q*(x-start)
                    aktuelle_querkraft += Ersatzkraft_q

                    #Summe M = 0 --> 0 = M -Ersatzkraft*Hebelarm
                    aktuelles_moment += Ersatzkraft_q * Hebelarm

                #3. Fall --> Schnittufer hinter der Streckenlast x > ende
                elif x > ende:
                    wirksame_Laenge = ende - start
                    Ersatkraft_q = q * wirksame_Laenge
                    Hebelarm = wirksame_Laenge / 2 + (x - ende)

                    #Summe F_y = 0 --> 0= -Q -Ersatzkraft
                    aktuelle_querkraft += Ersatkraft_q

                    #Summe M = 0 --> 0 = M -Ersatzkraft*Hebelarm
                    aktuelles_moment += Ersatkraft_q * Hebelarm

            #freie Momente
            for last in self.balken.einzelmomente:
                abstand = last[0]
                M = last[1]

                if abstand <= x: # wenn das Moment hinter oder auf dem Schnittufer liegt --> Schnittgrößen Aktualisierung
                #für Querkraft ist Moment irrelevant

                    # Summe M = 0 --> M = -freies Moment
                    aktuelles_moment -= M


            # nun Einspeicherung der beiden lokalen Variablen welche aufsummiert wurden
            # hierbei wird der index i (ganzzahlige Werte) genutzt
            self.q_werte[i] = aktuelle_querkraft
            self.m_werte[i] = aktuelles_moment

        #Rückgabe der fertigen Arrays welche für die graphische Darstellung in der weiteren Klasse benötigt werden
        return self.x_werte, self.q_werte, self.m_werte
    



    def berechne_extremwerte(self):
        """
        Ermittelt die betragsmäßig größten Schnittgrößen und deren x-Koordinaten.
        
        Sucht in den numerischen Arrays nach den maximalen Werten für Querkraft 
        und Biegemoment. Gibt diese zusammen mit den Lagerkräften zurück.
        """


        # 1. Lagerkräfte (bereits berechnet)
        Lagerkraft_A = self.balken.Lagerkraft_A_y
        Lagerkraft_B = self.balken.Lagerkraft_B_y

        # 2. Betragsmäßiges Maximum der Querkraft

        # np.abs() Befehl nimmt den Betrag --> alle Zahlen werden positiv
        # np.argmax() sucht Index (Position) der größten Zahl
        Index_max_Q = np.argmax(np.abs(self.q_werte))

        # mit Index kann x Koordinate und echter Wert erlangt werden
        # Achtung hierbei kann es zu minimalen Abweichungen der wirklichen Extremstellen kommen. 
        # Da Balken in 1000 gleich große Teile zerlegt wurde kann tatsächliches Maximum zwischen einem der Punkte liegen
        
        max_Q_Wert = self.q_werte[Index_max_Q]
        X_Koordinate_max_Q_Wert = self.x_werte[Index_max_Q]

        # 3.Betragsmäßiges Maximum des Biegemoment

        # analoges Vorgehen wie in Maximum der Querkraft
        # Achtung hierbei kann es zu minimalen Abweichungen der wirklichen Extremstellen kommen. 
        # Da Balken in 1000 gleich große Teile zerlegt wurde kann tatsächliches Maximum zwischen einem der Punkte liegen
        # Für eine analytisch exakte Lösung des Biegemoments müsste künftig die Nullstelle der Querkraftfunktion berechnet werden, da M'(x) = Q(x)

        Index_max_M = np.argmax(np.abs(self.m_werte))

        max_M_Wert = self.m_werte[Index_max_M]
        X_Koordinate_max_M_Wert = self.x_werte[Index_max_M]

        #Rückgabe sämtlicher Extremwerte in einem Dictionary
        return{
            "A": Lagerkraft_A,
            "B": Lagerkraft_B,
            "max_Q": max_Q_Wert,
            "x_Q": X_Koordinate_max_Q_Wert,
            "max_M": max_M_Wert,
            "x_M": X_Koordinate_max_M_Wert
        }



      










        
