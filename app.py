
"""
=========================================================
PROJEKT:        Schnittgrößen-Solver
DATEI:          app.py
BESCHREIBUNG:   Hauptdatei der Streamlit-App. Steuert die 
                Benutzeroberfläche (Dashboard), validiert 
                Nutzereingaben und koordiniert die Module 
                für Statik-Berechnung und Visualisierung.
---------------------------------------------------------
ENTWICKLER:     [Linus Schiel]
VERSION:        v1.0.0 (Final)
=========================================================
"""


import streamlit as st
import pandas as pd

#Import der Klassen
from mechanik import Balken, SchnittgroessenRechner
from visualisierung import Diagramm_Zeichner


st.title("Schnittgrößenrechner")# Überschrift

# ====================================================================
# 1. ZWISCHENSPEICHER (SESSION STATE) INITIALISIEREN
# ====================================================================
# sodass Nutzer beim erstmaligen öffnen des Solvers direkt Schnittgrößen in Kombi mit eingegebenen Lasten sieht wird session state genutzt
# da Schlüssel 'beispiel_geladen' beim ersten öffnen noch nicht im Speicher ist muss dieser erstmalig "befüllt" werden

#Erklärung zur Merker Logik ("beispiel_geladen"):
# 'not in' prüft hier NICHT auf True oder False
# es fragt Python lediglich: "Gibt es im "Aktenschrank" (session_state) überhaupt schon eine "Schublade" mit dem Etikett 'beispiel_geladen'?
#
# beim allerersten Start der App ist der Schrank leer --> Bedingung erfüllt, Python springt in den if Block

if 'beispiel_geladen' not in st.session_state:
    # jetzt "klebt" Python das "Etikett" 'beispiel_geladen' auf die Schublade und "legt" den Wert True hinein (True ist hierbei völlig irrelevant)
    st.session_state.beispiel_geladen = True
    #wenn Streamlit bei Nutzereingabe neu startet, sieht Python:
    # das "Etikett" 'beispiel_geladen' existiert schon --> if Block wird übersprungen und Nutzereingaben bleiben sicher

    #Beispiel Länge
    st.session_state.aktuelle_laenge = 10.0

    #Beispiel Lasten in den "Tresor legen":
    #Punktlasten
    st.session_state.punktlasten = pd.DataFrame([{"Position x [m]": 5, "Kraft F [kN]": 50.0}]) # hier wird kein columns davor benötigt weil Python ein dictionary übergeben bekommt
    # hierbei nimmt es die Schlüssel (Texte vor dem Doppelpunkt) und verwendet diese als Spaltenüberschriften

    #Streckenlasten
    st.session_state.streckenlasten = pd.DataFrame([{"Start x [m]": 0.0, "Ende x [m]": 10.0, "Last q [kN/m]": -15.0}]) #analog zu Punktlasten

    #freie Momente
    st.session_state.freie_momente = st.session_state.df_moment = pd.DataFrame([{"Position x [m]": 3.0, "Kraft M [kNm]": -20.0}])


# ====================================================================
# 2. Reset Funktion und Button
# ====================================================================
# diese Funktion überschreibt den Zwischenspeicher gezielt, wenn der Nutzer den roten Button klickt

def setze_auf_standard_zurueck():
    st.session_state.aktuelle_laenge = 10.0
    st.session_state.punktlasten = pd.DataFrame(columns=["Position x [m]", "Kraft F [kN]"])
    st.session_state.streckenlasten = pd.DataFrame(columns=["Start x [m]", "Ende x [m]", "Last q [kN/m]"])
    st.session_state.freie_momente = pd.DataFrame(columns=["Position x [m]", "Kraft M [kNm]"])
    #da Pandas (Tabellen) hier leer sind (keine Startwerte) muss columns=[] davorstehen

    # Die nachfolgenden Zeilen machen Folgendes:
    # Wenn das interne Widget-Gedächtnis (Key) eines Eingabefeldes oder einer 
    # Tabelle bereits im session_state existiert, wird dieser Key gezielt gelöscht
    if "eingabe_laenge" in st.session_state:
        del st.session_state["eingabe_laenge"]
    if "tabelle_punktlasten" in st.session_state:
        del st.session_state["tabelle_punktlasten"]
    if "tabelle_strecken" in st.session_state:
        del st.session_state["tabelle_strecken"]
    if "tabelle_momente" in st.session_state:
        del st.session_state["tabelle_momente"]

        # Warum "Gedächtnis" (session state) löschen
        # 1. Das Problem: Die Tabellen haben durch ihren eigenen key ihr eigenes "Kurzzeitgedächtnis" 
        # --> sie behalten alte Eingaben, selbst wenn Hauptdatenbank session_state geleert wird
        # 2. Folge: Ohne Löschung würden alte Werte als "Geister-Daten" wieder in der Eingabemaske auftauchen
        # 3. Lösung: Mit 'del' werden diese Daten ("GEdächtnisse") gelöscht
        # --> beim Neustart (rerun) werden Tabellen gezwungen leere Standard Tabellen zu akzeptieren



st.sidebar.subheader("Neues Projekt")

# wenn Button gedrückt wird wird Reset Funktion und App neu gestartet
if st.sidebar.button("Eigener Balken (Alles löschen)", type="primary"):
    setze_auf_standard_zurueck()#Funktion welche davor definiert wird wird aufgerufen
    st.rerun()
    # --- WARUM st.rerun()? ---
    # Wenn Speicher im Hintergrund geleert wird, indem einfach session state überschrieben wird, checkt die Tabelle auf dem 
    # Bildschirm das nicht sofort. Sie "wehrt" sich und behält stur die alten Zahlen.
    # st.rerun() drückt quasi hart "F5" (Seite neu laden). 
    # Code beginnt wieder von oben:
    # Interpreter prüft ob in session state 'beispiel_geladen' enthalten ist --> ist enthalten durch den allerersten Durchlauf
    # --> daher werden keine Beispielwerte mehr gesetzt und die session states sind mit den leeren Pandas befüllt welche beim Button drücken in der Funktion aufgerufen worden sind
    # Nutzer kann selbst Eingaben vornehmen


st.sidebar.divider() # Optischer Trennstrich


# ====================================================================
# 3. BALKENLÄNGE
# ====================================================================

st.sidebar.subheader("Balkenlänge definieren")
Balken_Laenge = st.sidebar.number_input(
    "Balkenlänge [m]:",         
    min_value=0.1,                          # Darf nicht 0 oder negativ sein
    value=st.session_state.aktuelle_laenge, # Startwert wird aus dem Zwischenspeicher geholt
    key="eingabe_laenge"
)

# Falls Nutzer Länge per Hand ändert, wird Speicher sofort akutalisiert
st.session_state.aktuelle_laenge = Balken_Laenge

#Konstruktor der Klasse Balken wird aufgerufen und die zuvor abgefragte Balken Länge wird übergeben
neuer_Balken = Balken(Balken_Laenge)


# ====================================================================
# 4. LASTEN DEFINIEREN
# ====================================================================

st.sidebar.subheader("Lasten definieren")



# ---------------------------------------------------
# Punktlasten
# ---------------------------------------------------

st.sidebar.markdown("**Punktlasten (F in kN, x in m)**") #Normaler Text, Sternchen machen diesen fett


#um Falscheingaben abzufangen werden Regeln festgelegt
regeln_Punktlasten={

    # Erste Spalte: Position/Abstand (mit Grenzen)
    "Position x [m]":                       #dieser Text muss genauso heißen wie die Spalte im Data Frame welche eingeschränkt werden soll
        st.column_config.NumberColumn(      #dieser Befehl ändert Zelle in spezielles Zahlenfeld, in das kein Text eingegeben werden kann
          min_value=0.0,                    #absolute Untergrenze, bei Eingabe von -2 wird Zahl auf 0.0 geändert
          max_value=Balken_Laenge,          #absolute Obergrenze
        ),

    # Zweite Spalte: Kraft
    "Kraft F [kN]":
        st.column_config.NumberColumn(
        )

}

punktlasten_eingabe_neu = st.sidebar.data_editor(
    st.session_state.punktlasten,           # Data Editor erhält Data Frame aus session state
    column_config=regeln_Punktlasten,       # fertiges Dictionary regeln_x wird an column_config übergeben --> vorher festgelegte Regeln werden für die Spalten berücksichtigt
    num_rows="dynamic",                     # Nutzer kann Zeilen hinzufügen und löschen
    use_container_width=True,               # Zieht Tabelle ausreichend breit
    hide_index=True,                        # Index vor der Zeile wird nicht angezeigt
    key="tabelle_punktlasten"               # interner einmaliger Name
)


#speichern der eingegeben Tabellenwerten --> Punktlasten
for index, row in punktlasten_eingabe_neu.iterrows(): #iterrows --> Tabelle wird Zeile für Zeile durchgegangen
                                                      # index ist Zeilennummer
                                                      # row enthält alle Daten
    
    #Python aktualisiert bei jeder Eingabe in die Tabelle die Diagramme --> Problem: wenn Werte wie die Kraft fehlen kann Diagramm nicht berechnet werden --> Fehlermeldung
    #um dies zu vermeiden --> try except Funktion
    try:
        # Python versucht die einzelnen Zellen durch float in eine Kommazahl umzuwandeln (wenn das nicht funktioniert wird ein Type Error ausgelöst --> Programm stürzt ab)
        abstand_Punktlast = float(row["Position x [m]"])#mit exaktem Namen wird auf Wert der Zelle zugegriffen
        kraft = float(row["Kraft F [kN]"])
        
        # Falscheingabe: Balkenlänge wird nachträglich angepasst --> Position der Punktlast liegt in der Luft
        if abstand_Punktlast > Balken_Laenge:
          st.sidebar.error(f"Fehler Punktlast (Zeile {index+1}): Position x = {abstand_Punktlast}m liegt außerhalb des Balken!\n\n Punktlast wird nicht berücksichtigt!")
          
          continue  #durch diesen Befehl springt Python direkt zum Start der Schleife und macht mit nächster Zeile der Tabelle weiter --> Falsche Werte werden nicht als Punktlast in der Klasse Balken gespeichert


        # Wenn alles echte Zahlen sind & keine Falscheingabe vorhanden ist --> Speicherung im Balken
        neuer_Balken.speichere_Punktlast(abstand_Punktlast, kraft)
        
    except (ValueError, TypeError):
        # ValueError --> Falscher Inhalt float("Hallo")
        # TypeError --> Zelle ist leer float(None)

        # --> FEHLER ABGEFANGEN: Wenn Zelle leer ist (None) oder jemand Text tippt Code landet hier --> pass bedeutet mache nichts/gehe zur nächsten Zeile
        pass



# ---------------------------------------------------
# STRECKENLASTEN
# ---------------------------------------------------

st.sidebar.markdown("**Streckenlasten (q in kN/m, x in m)**")


#um Falscheingaben abzufangen werden Regeln festgelegt
regeln_Streckenlasten = {

    "Start x [m]":
        st.column_config.NumberColumn(      # dieser Befehl ändert Zelle in spezielles Zahlenfeld, in das kein Text eingegeben werden kann
           min_value=0.0,                   # Untergrenze
           max_value=Balken_Laenge,         # Obergrenze
        ),
    
    "Ende x [m]":
        st.column_config.NumberColumn(      # dieser Befehl ändert Zelle in spezielles Zahlenfeld, in das kein Text eingegeben werden kann
           min_value=0.0,                   # Untergrenze
           max_value=Balken_Laenge,         # Obergrenze
        ),

    "Last q [kN/m]":
        st.column_config.NumberColumn(      # dieser Befehl ändert Zelle in spezielles Zahlenfeld, in das kein Text eingegeben werden kann
        )
}

streckenlasten_eingabe_neu = st.sidebar.data_editor(
    st.session_state.streckenlasten,        # Data Editor erhält Data Frame aus session state
    column_config=regeln_Streckenlasten,    # fertiges Dictionary regeln_x wird an column_config übergeben --> vorher festgelegte Regeln werden für die Spalten berücksichtigt
    num_rows="dynamic",                     # Nutzer kann Zeilen hinzufügen und löschen
    use_container_width=True,               # Zieht Tabelle ausreichend breit
    hide_index=True,                        # Index vor der Zeile wird nicht angezeigt
    key="tabelle_strecken"                  # interner einmaliger Name
)


#speichern der eingegeben Tabellenwerten --> Streckenlasten
for index, row in streckenlasten_eingabe_neu.iterrows(): #iterrows --> Tabelle wird Zeile für Zeile durchgegangen
                                                      # index ist Zeilennummer
                                                      # row enthält alle Daten

   #Python aktualisiert bei jeder Eingabe in die Tabelle die Diagramme --> Problem: wenn Werte wie die Kraft fehlen kann Diagramm nicht berechnet werden --> Fehlermeldung
   #um dies zu vermeiden --> try except Funktion
   try:
        # Python versucht die einzelnen Zellen durch float in eine Kommazahl umzuwandeln (wenn das nicht funktioniert wird ein Type Error ausgelöst --> Programm stürzt ab)
        start_Streckenlast = float(row["Start x [m]"])#mit exaktem Namen wird auf Wert der Zelle zugegriffen
        ende_Streckenlast = float(row["Ende x [m]"])
        q_wert = float(row["Last q [kN/m]"])


        # Falscheingabe: Ende der Streckenlast liegt vor oder auf dem Startpunkt
        if start_Streckenlast >= ende_Streckenlast:

            #Rote Fehlermeldung für den Nutzer
            st.sidebar.error(f"Fehler Streckenlast (Zeile {index+1}): Start ({start_Streckenlast}m) muss vor Ende ({ende_Streckenlast}m) liegen!\n\n Streckenlast wird nicht berücksichtigt!")

            continue #durch diesen Befehl springt Interpret direkt zum Start der Schleife und macht mit nächster Zeile der Tabelle weiter --> Falsche Werte werden nicht als Streckenlast in der Klasse Balken gespeichert

        
        # Falscheingabe: Balkenlänge wird nachträglich angepasst --> Streckenlast Ende liegt in der Luft
        if ende_Streckenlast > Balken_Laenge:
            
            #Rote Fehlermeldung für den Nutzer
            st.sidebar.error(f"Fehler Streckenlast (Zeile {index+1}): Ende ({ende_Streckenlast}m) ist länger als der Balken!\n\n Streckenlast wird nicht berücksichtigt!")

            continue #durch diesen Befehl springt Python direkt zum Start der Schleife und macht mit nächster Zeile der Tabelle weiter --> Falsche Werte werden nicht als Streckenlast in der Klasse Balken gespeichert


         # Wenn alles echte Zahlen sind & beide Falscheingaben als nicht vorhanden erkannt sind --> Speicherung der Streckenlast im Balken
        neuer_Balken.speicher_Streckenlast(start_Streckenlast, ende_Streckenlast, q_wert)
        
   except (ValueError, TypeError):
       # ValueError --> Falscher Inhalt float("Hallo")
       # TypeError --> Zelle ist leer float(None)

       # --> FEHLER ABGEFANGEN: Wenn Zelle leer ist (None) oder jemand Text tippt Code landet hier --> pass bedeutet mache nichts/gehe zur nächsten Zeile
        pass
   


# ---------------------------------------------------
# Freie Momente
# ---------------------------------------------------

st.sidebar.markdown("**Freie Momente (M in kNm, x in m)**")


#um Falscheingaben abzufangen werden Regeln festgelegt
regeln_freie_Momente = {

    "Position x [m]":
        st.column_config.NumberColumn(      # dieser Befehl ändert Zelle in spezielles Zahlenfeld, in das kein Text eingegeben werden kann
           min_value=0.0,                   # Untergrenze
           max_value=Balken_Laenge,         # Obergrenze
        ),

    "Kraft M [kNm]":
        st.column_config.NumberColumn(      # dieser Befehl ändert Zelle in spezielles Zahlenfeld, in das kein Text eingegeben werden kann
        )   
}

freie_Momente_eingabe_neu = st.sidebar.data_editor(
    st.session_state.freie_momente,        # Data Editor erhält Data Frame aus session state
    column_config=regeln_freie_Momente,    # fertiges Dictionary regeln_x wird an column_config übergeben --> vorher festgelegte Regeln werden für die Spalten berücksichtigt
    num_rows="dynamic",                    # Nutzer kann Zeilen hinzufügen und löschen
    use_container_width=True,              # Zieht Tabelle ausreichend breit
    hide_index=True,                       # Index vor der Zeile wird nicht angezeigt
    key="tabelle_momente"                  # interner einmaliger Name
)



#speichern der eingegeben Tabellenwerten --> Streckenlasten
for index, row in freie_Momente_eingabe_neu.iterrows(): #iterrows --> Tabelle wird Zeile für Zeile durchgegangen
                                                      # index ist Zeilennummer
                                                      # row enthält alle Daten

   #Python aktualisiert bei jeder Eingabe in die Tabelle die Diagramme --> Problem: wenn Werte wie die Kraft fehlen kann Diagramm nicht berechnet werden --> Fehlermeldung
   #um dies zu vermeiden --> try except Funktion
   try:
        # Python versucht die einzelnen Zellen durch float in eine Kommazahl umzuwandeln (wenn das nicht funktioniert wird ein Type Error ausgelöst --> Programm stürzt ab)
        abstand_freies_Moment = float(row["Position x [m]"])#mit exaktem Namen wird auf Wert der Zelle zugegriffen
        kraft= float(row["Kraft M [kNm]"])

        # Falscheingabe: Balkenlänge wird nachträglich angepasst --> Position des freiens Moments liegt in der Luft
        if abstand_freies_Moment > Balken_Laenge:
            
            #Rote Fehlermeldung für den Nutzer
            st.sidebar.error(f"Fehler Freies Moment (Zeile {index+1}): Position x = {abstand_freies_Moment}m liegt außerhalb des Balken!\n\n Freies Moment wird nicht berücksichtigt!")

            continue #durch diesen Befehl springt Python direkt zum Start der Schleife und macht mit nächster Zeile der Tabelle weiter --> Falsche Werte werden nicht als freies Moment in der Klasse Balken gespeichert


         # Wenn alles echte Zahlen sind & keine Falscheingabe vorhanden ist --> Speicherung im Balken
        neuer_Balken.speicher_freie_Momente(abstand_freies_Moment, kraft)
        
   except (ValueError, TypeError):
       # ValueError --> Falscher Inhalt float("Hallo")
       # TypeError --> Zelle ist leer float(None)

       # --> FEHLER ABGEFANGEN: Wenn Zelle leer ist (None) oder jemand Text tippt Code landet hier --> pass bedeutet mache nichts/gehe zur nächsten Zeile
        pass
   


# ====================================================================
# 5. BERECHNUNG
# ====================================================================
#Methode zur Lagerkraftberechnung wird aufgerufen
neuer_Balken.berechne_Lagerkraefte()

#Konstruktor der Klasse SchnittgroessenRechner wird aufgerufen
rechner = SchnittgroessenRechner(neuer_Balken)

# Methode des SchnittgroessenRechner um die einzelnen Arrays zu berechnen wird aufgerufen --> durch return in der Methode können die Arrays hier "aufgesammelt" werden
x_Werte, Q_Werte, M_Werte = rechner.berechne_linien()


# ====================================================================
# Visualisierung und Präsentation der Extremwerte
# ====================================================================


#Konstruktor der Klasse Diagramm_Zeichner wird aufgerufen
visualisierung = Diagramm_Zeichner(x_Werte, Q_Werte, M_Werte, neuer_Balken)

#Methode des Diagramm_Zeichner wird aufgerufen um die das komplette Diagramm zu erstellen
fertiges_bild = visualisierung.zeichne()

#Befehl um fertiges Diagramm in Streamlit zu integrieren
st.pyplot(fertiges_bild)

#Methode des Diagramm_Zeichner wird aufgerufen um Extremwerte zu berechnen
Ergebnisse_Extremwerte= rechner.berechne_extremwerte()


st.divider() #Trennstrich
st.subheader("Analyse der Extremwerte")

col1,col2,col3 = st.columns(3) #Erstellen von 3 Spalten (Lager, Querkraft, Moment)

#einzelne Extremwerte werden durch ihre jeweilige Bezeichnung in der Methode nachfolgend integriert: Ergebnisse_Extremwerte['A'] --> "A": Lagerkraft_A
with col1:
    st.markdown("**Lagerkräfte**")
    st.metric("Lager A", f"{Ergebnisse_Extremwerte['A']:.2f} kN")
    st.metric("Lager B", f"{Ergebnisse_Extremwerte['B']:.2f} kN")

with col2:
    st.markdown("**Querkraft**")
    st.metric("max |Q|", f"{Ergebnisse_Extremwerte['max_Q']:.2f} kN")
    st.caption(f"an Stelle x = {Ergebnisse_Extremwerte['x_Q']:.2f} m")

with col3:
    st.markdown("**Biegemoment**")
    st.metric("max |M|", f"{Ergebnisse_Extremwerte['max_M']:.2f} kNm")
    st.caption(f"an Stelle x = {Ergebnisse_Extremwerte['x_M']:.2f} m")

# f"{...:.2f}" --> Ergebnisse mit nur zwei Nachkommastellen

