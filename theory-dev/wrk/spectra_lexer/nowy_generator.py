#!/usr/bin/env python3
import argparse
import collections
import time
import os
import re

samogłoski = ['a', 'ą', 'e', 'ę', 'i', 'o', 'ó', 'u', 'y']
tylda = "~"
gwiazdka = "*"
myślnik = "-"
jot = "J"
ee = "E"
ii = "I"
aa = "A"
uu = "U"
nic = ""
tyldogwiazdka = "~*"
# {"Fonem": ("Lewa ręka", "Prawa ręka")}
fonemy_spółgłoskowe = {"b": ("P~", "B"),
                       "bi": ("PJ~", "BW"),
                       "c": ("ZT", "C"),
                       "ci": ("ZTJ", "CW"),
                       "ch": ("X", "CB"),
                       "chi": ("XJ", "CBW"),
                       "cz": ("PV", "CL"),
                       "czi": ("PVJ", "CLW"),
                       "ć": ("TJ", "TW"),
                       "d": ("T~", "BT"),
                       "di": ("TJ~", "BTW"),
                       "dz": ("ZT~", "C"),  # Dodałem
                       "dzi": ("ZTJ~", "CW"),  # Dodałem
                       "dź": ("ZTJ~", "LST"),
                       "dż": ("PV~", "CLW"),
                       "f": ("F", "W"),
                       "fi": ("FJ", "W"),
                       "g": ("K~", "G"),
                       "gi": ("KJ~", "GW"),
                       "h": ("X~", "CBW"),  # Zamieniłem z XK~
                       "hi": ("XJ~", "CBW"),  # Zamieniłem z XKJ~
                       "j": ("J", "CR"),
                       "ji": ("J", "CRW"),
                       "k": ("K", "GW"),
                       "ki": ("KJ", "GW"),
                       "l": ("L", "L"),
                       "li": ("LJ", "LW"),
                       "ł": ("LJ", "LB"),
                       "łi": ("LJ", "LBW"),
                       "m": ("KP", "CS"),
                       "mi": ("KPJ", "CSW"),
                       "n": ("TV", "CL"),
                       "ni": ("TVJ", "CLW"),
                       "ń": ("TVJ", "CLW"),
                       # Tu zmieniłem prawą, bo nie ma "P" po prawej stronie
                       "p": ("P", "RG"),
                       "pi": ("PJ", "RGW"),
                       "q": ("KV", "GWY"),
                       "r": ("R", "R"),
                       "ri": ("RJ", "RW"),
                       "rz": ("RJ", "RBW"),
                       "s": ("S", "S"),
                       "si": ("SJ", "SW"),
                       "sz": ("TP", "RB"),
                       "ś": ("SJ", "SW"),
                       "t": ("T", "T"),
                       "ti": ("TJ", "TW"),
                       "v": ("V", "W"),
                       "vi": ("VJ", "W"),
                       "w": ("V", "W"),
                       "wi": ("VJ", "~W"),
                       "x": ("SK", "BSG"),
                       "xi": ("SKJ", "BSGW"),
                       "z": ("Z", "BS"),
                       "zi": ("ZJ", "BSW"),
                       "ź": ("ZJ", "BSW"),
                       "ż": ("TP~", "RBW")}

fonemy_spółgłoskowe_klucze = ["b", "bi", "c", "ci", "ch", "chi", "cz", "czi", "ć",
                              "d", "di", "dz", "dzi", "dź", "dż", "f", "fi", "g",
                              "gi", "h", "hi", "j", "ji", "k", "ki", "l", "li",
                              "ł", "łi", "m", "mi", "n", "ni", "ń", "p", "pi",
                              "q", "r", "ri", "rz", "s", "si", "sz", "ś", "t", 
                              "ti", "v", "vi", "w", "wi", "x", "xi", "z", "zi",
                              "ź", "ż"]

# {"Fonem": ("Środek", "Prawa ręka")}
fonemy_samogłoskowe = {"a": ("A", "TO"),
                       "ą": ("~O", "TW"),
                       "e": ("E", "TWOY"),
                       "ę": ("E~", "OY"),
                       "i": ("I", nic),
                       "o": ("AU", "O"),
                       "ó": ("U", nic),
                       # Tutaj zabrałem prawą rękę z "i"
                       "u": ("U", "WY"),
                       "y": ("IAU", "Y")}
fonemy_samogłoskowe_klucze = ["a", "ą", "e", "ę", "i",
                              "o", "ó", "u", "y",]


def fonemy(string, zmiękczenie = False):
    fonemy_dwuznakowe = {"b": ["i"],
                         "c": ["h", "i", "z"],
                         "d": ["i", "z", "ź", "ż"],
                         "f": ["i"],
                         "g": ["i"],
                         "h": ["i"],
                         "j": ["i"],
                         "k": ["i"],
                         "l": ["i"],
                         "ł": ["i"],
                         "m": ["i"],
                         "n": ["i"],
                         "p": ["i"],
                         "r": ["i", "z"],
                         "s": ["i", "z"],
                         "t": ["i"],
                         "w": ["i"],
                         "z": ["i"]}
    znaki = split(string)
    if zmiękczenie:
        znaki.append("i")

    wynik = []
    i = 0
    ilość_znaków = len(znaki)
    while i < ilość_znaków:
        znak = znaki[i]
        if znak in fonemy_dwuznakowe.keys():
            if (i+1 < ilość_znaków) and znaki[i+1] in fonemy_dwuznakowe[znak]:
                następny_znak = znaki[i+1]
                if zmiękczenie and ((znak == "c" and następny_znak in ["z", "h"])\
                  or (znak == "d" and następny_znak =="z")):
                    if (i+2 < ilość_znaków) and znaki[i+2] == "i":
                        i += 3
                        wynik.append(znak + następny_znak + "i")
                    else:
                        i += 2
                        wynik.append(znak + następny_znak)
                else:
                    i += 2
                    wynik.append(znak + następny_znak)
            else:
                i += 1
                wynik.append(znak)
        else:
            i += 1
            wynik.append(znak)
    return wynik


def odejmij_fonemy(fonemy, do_odjęcia):
    nowe_fonemy = fonemy
    for fonem in do_odjęcia:
        if fonem in nowe_fonemy:
            nowe_fonemy.remove(fonem)
    return nowe_fonemy


def wygeneruj_odjemniki(malejące_lewe, malejące_prawe):
    łączna_waga = 0
    odjemniki = []
    for sylaba in malejące_lewe + malejące_prawe:
        łączna_waga += sylaba[1]
    for sylaba in malejące_lewe:
        odjemniki.append(([sylaba], malejące_prawe, łączna_waga - sylaba[1]))
    for sylaba in malejące_prawe:
        odjemniki.append((malejące_lewe, [sylaba], łączna_waga - sylaba[1]))
    return odjemniki


def dzielniki_dla_słowa_o_długości(n):
    if n == 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    elif n == 3:
        return [1, 2, 0]
    elif n == 4:
        return [2, 1, 3, 0]
    else:
        lista = [n - 2, 1 , n - 1, 0]
        # odj dod odj dod
        z_początku = False
        pozostałe = []
        for i in range(2, n - 2):
            pozostałe.append(i)
        while pozostałe:
            if z_początku:
                lista.append(pozostałe.pop(0))
            else:
                lista.append(pozostałe.pop(-1))
            z_początku = not z_początku
        return lista

# # TODO naprawić to
# def odejmij_fonemy_wg_wagi(fonemy, do_odjęcia, i):
#     # print(f"odejmuję od {fonemy} któryś z tych: {do_odjęcia}")
#     nowe_fonemy = fonemy
#     który_odjąć = do_odjęcia[0]
#     for fonem in do_odjęcia[1:]:
#         if fonem[1] < który_odjąć[1]:
#             który_odjąć = fonem
#     nowe_fonemy.remove(który_odjąć)
#     return nowe_fonemy

# indeksy kolumn po lewej stronie od 0
lewe_indeksy_klawiszy = {"X": 0, "F": 0, "XF": 0, "XZ": 0, "FS": 0, "XFZS": 0,
                         "Z": 1, "S": 1, "ZS": 1,
                         "K": 2, "T": 2, "KT": 2,
                         "P": 3, "V": 3, "PV": 3,
                         "L": 4, "R": 4, "LR": 4,
                         "~": 5, "*": 5,
                         "J": 6}


# indeksy kolumn po prawej stronie od 0
prawe_indeksy_klawiszy = {"~": 5, "*": 5,
                          "C": 6, "R": 6, "CR": 6,
                          "L": 7, "B": 7, "LB": 7,
                          "S": 8, "G": 8, "SG": 8,
                          "T": 9, "W": 9, "TW": 9, "TO": 9, "WY": 9, "TWOY": 9,
                          "O": 10, "Y": 10, "OY": 10}


znaki_środka = ["J", "E",tylda, gwiazdka, "I", "A", "U"]

def klawisze_dla_fonemu(fonem, prawe=False):
    fonem = fonem[0]
    if prawe:
        if fonem in samogłoski:
            return fonemy_samogłoskowe[fonem][1]
        return fonemy_spółgłoskowe[fonem][1]           
    else:
        if fonem in samogłoski:
            return nic
        return fonemy_spółgłoskowe[fonem][0]


def niemalejące(fonemy_lewe, fonemy_prawe, bez_inwersji=False):
    # print(f"Niemalejące?: {fonemy_lewe}|{fonemy_prawe}")
    inwersja_użyta = False
    if bez_inwersji:
        inwersja_użyta = True
    indeksy = lewe_indeksy_klawiszy
    indeksy_fonemów_lewe = [(0, 0, nic)]  # (indeks_klawisza, indeks_pomocniczy, (fonem, waga))
    j = 0
    for i in range(len(fonemy_lewe)):
        fonem = fonemy_lewe[i]
        minimalny_indeks_klawisza = 5
        # print(f"Fonem:{fonem} w {fonemy_lewe}")
        for klawisz in klawisze_dla_fonemu(fonem[0]):
            bieżący_indeks = indeksy[klawisz]
            if bieżący_indeks < minimalny_indeks_klawisza:
                minimalny_indeks_klawisza = bieżący_indeks
        if minimalny_indeks_klawisza != indeksy_fonemów_lewe[-1][0]:
            indeksy_fonemów_lewe.append((minimalny_indeks_klawisza, j, fonem))
            j += 1
    indeksy_fonemów_lewe = indeksy_fonemów_lewe[1:]
    (jest_niemalejący, gdzie_nie_jest) = ciąg_niemalejący(indeksy_fonemów_lewe[1:])
    if not jest_niemalejący:
        if not inwersja_użyta:
            # print(f"nie jest: {gdzie_nie_jest} indeksy: {indeksy_fonemów_lewe}")
            tymczasowy = indeksy_fonemów_lewe[gdzie_nie_jest[1] - 1]
            indeksy_fonemów_lewe[gdzie_nie_jest[1] - 1] = indeksy_fonemów_lewe[gdzie_nie_jest[1]]
            indeksy_fonemów_lewe[gdzie_nie_jest[1]] = tymczasowy
            inwersja_użyta = True
            (jest_niemalejący, gdzie_nie_jest) = ciąg_niemalejący(indeksy_fonemów_lewe)
            if not jest_niemalejący:
                return (False, 0, gdzie_nie_jest)
        else:
            return (False, 0, gdzie_nie_jest)

    indeksy_fonemów_prawe = [(5, 0, nic)]
    # print(f"sprawdzam: {fonemy_lewe}||{fonemy_prawe}")
    indeksy = prawe_indeksy_klawiszy
    j = 0
    for i in range(len(fonemy_prawe)):
        fonem = fonemy_prawe[i]  # ('di', waga)
        minimalny_indeks_klawisza = 10
        for klawisz in klawisze_dla_fonemu(fonem[0], prawe=True):
            bieżący_indeks = indeksy[klawisz]
            if bieżący_indeks < minimalny_indeks_klawisza:
                minimalny_indeks_klawisza = bieżący_indeks
        if minimalny_indeks_klawisza != indeksy_fonemów_prawe[-1][0]:
            indeksy_fonemów_prawe.append((minimalny_indeks_klawisza, j, fonem))
            j += 1
    indeksy_fonemów_prawe = indeksy_fonemów_prawe[1:]
    (jest_niemalejący, gdzie_nie_jest) = ciąg_niemalejący(indeksy_fonemów_prawe)
    if not jest_niemalejący and not inwersja_użyta:
        # print(f"male: {gdzie_nie_jest} - {indeksy_fonemów_prawe}")
        tymczasowy = indeksy_fonemów_prawe[gdzie_nie_jest[1] - 1]
        indeksy_fonemów_prawe[gdzie_nie_jest[1] - 1] = indeksy_fonemów_prawe[gdzie_nie_jest[1]]
        indeksy_fonemów_prawe[gdzie_nie_jest[1]] = tymczasowy
        inwersja_użyta = True
        (jest_niemalejący, gdzie_nie_jest) = ciąg_niemalejący(indeksy_fonemów_prawe)
        if not jest_niemalejący:
            return (False, 1, gdzie_nie_jest)
        return (True, None, None)
    elif jest_niemalejący:
        return (True, None, None)
    return (False, 1, gdzie_nie_jest)


def ciąg_niemalejący(ciąg):
    długość_ciągu = len(ciąg)
    if długość_ciągu < 2:
        return (True, None)
    else:
        for i in range(1, długość_ciągu):
            if ciąg[i][0] < ciąg[i-1][0]:
                return (False, ciąg[i])
    return (True, None)


class Logger:
    def __init__(self, plik_logowania, rozmiar_bufora=1024, pisz_na_ekran=True):
        self.plik_logowania = open(plik_logowania, 'a', buffering=rozmiar_bufora)
        self.pisz_na_ekran = pisz_na_ekran

    def __exit__(self):
        self.plik_logowania.flush()
        self.plik_logowania.close()

    def _loguj(self, poziom_logowania, dane):
        self.plik_logowania.write(f"{poziom_logowania}: {dane}\n")

    def info(self, dane):
        self._loguj("INF", dane)
        if self.pisz_na_ekran:
            print(f"INF: {dane}")

    def debug(self, dane):
        self._loguj("DBG", dane)

    def error(self, dane):
        self._loguj("ERR", dane)
        if self.pisz_na_ekran:
            print(f"ERR: {dane}")


class SłownikDomyślny(collections.UserDict):
    def __init__(self, domyślna_fabryka=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not callable(domyślna_fabryka) and domyślna_fabryka is not None:
            raise TypeError('Pierwszy argument musi być wykonywalny albo None')
        self.domyślna_fabryka = domyślna_fabryka

    def __missing__(self, klucz):
        if self.domyślna_fabryka is None:
            raise KeyError(klucz)
        if klucz not in self:
            self[klucz] = self.domyślna_fabryka(klucz)
        return self[klucz]


class Generator():
    def __init__(self, log, słownik_ostateczny, sylaby_słowa):
        self.log = log
        # {tekst: {"Kombinacja": niedopasowanie}}
        self.słownik = słownik_ostateczny
        self._samogłoski = re.compile(r'[aąeęioóuy]+')
        self.sylaby_słowa = sylaby_słowa
        self.fonemy_sylaby = SłownikDomyślny(lambda x: self.rozłóż_sylabę(x))
        self.wagi_fonemów = SłownikDomyślny(lambda x: self.policz_wagę_fonemu(x))
        self.rozdzielacz = SłownikDomyślny(lambda x: dzielniki_dla_słowa_o_długości(x))
        self.kombinacje = dict()
        self._zainicjalizuj_kombinacje()
        self.loguj_postęp_co = 10000 # Będzie log po tylu wygenerowanych słowach
        self.postęp = 0
        self.minimum_kombinacji_per_słowo = 1
        self.niepowodzenia = []

    def _zainicjalizuj_kombinacje(self):
        self.log.info("Inicjalizuję bazę generatora")
        for (tekst, kombinacje) in self.słownik.items():
            for kombinacja in kombinacje.keys():
                self.kombinacje[kombinacja] = tekst
        self.log.info("Baza zainicjalizowana w pamięci")

    def rozłóż_sylabę(self, sylaba: str):
        m = self._samogłoski.search(sylaba)
        if not m:
            błąd = f"sylaba {sylaba} bez samogłosek"
            self.log.debug(błąd)
            return (sylaba, nic, nic)
        śródgłos = fonemy(m.group(0))

        # Wykryj "i" które tylko zmiękcza, przesuń je do nagłosu
        zmiękczenie = False
        if len(śródgłos) > 1 and śródgłos[0].startswith('i'):
            śródgłos = śródgłos[1:]
            zmiękczenie = True
        nagłos = fonemy(re.split(self._samogłoski, sylaba)[0], zmiękczenie)
        wygłos = fonemy(re.split(self._samogłoski, sylaba)[1])

        # self.log.debug(f"Rozłożyłem {sylaba} na N: {nagłos} Ś: {śródgłos} W: {wygłos}")
        return (nagłos, śródgłos, wygłos)

    def rozbij_sylaby_na_fonemy(self, sylaby_lewe, sylaba_środkowa, sylaby_prawe):
        fonemy_lewe = []
        śródgłosy = []
        fonemy_prawe = []
        for sylaba in sylaby_lewe:
            (nagłos, śródgłos, wygłos) = self.fonemy_sylaby[sylaba]
            for fonem in nagłos + wygłos:
                fonemy_lewe.append(fonem)
        (nagłos, śródgłos, wygłos) = self.fonemy_sylaby[sylaba_środkowa]
        for fonem in nagłos:
            fonemy_lewe.append(fonem)
        for fonem in śródgłos:
            śródgłosy.append(fonem)
        for fonem in wygłos:
            fonemy_prawe.append(fonem)
        if sylaby_prawe:
            for sylaba in sylaby_prawe[:-1]:
                (nagłos, śródgłos, wygłos) = self.fonemy_sylaby[sylaba]
                for fonem in nagłos + wygłos:
                    fonemy_prawe.append(fonem)
            (nagłos, śródgłos, wygłos) = self.fonemy_sylaby[sylaby_prawe[-1]]
            if not wygłos:
                for fonem in nagłos + śródgłos:
                    fonemy_prawe.append(fonem)
            else:
                for fonem in nagłos + wygłos:
                    fonemy_prawe.append(fonem)
        return (self.zważ_fonemy(fonemy_lewe),
                self.zważ_fonemy(śródgłosy),
                self.zważ_fonemy(fonemy_prawe, prawe=True))

    def zważ_fonemy(self, fonemy, prawe=0):
        wagi_fonemów = collections.defaultdict(lambda: 0)
        wyjściowe_fonemy = []
        for fonem in fonemy:
            wagi_fonemów[fonem] += self.wagi_fonemów[fonem][prawe]
            if fonem not in wyjściowe_fonemy:
                wyjściowe_fonemy.append(fonem)
        zważone_fonemy = []
        for fonem in wyjściowe_fonemy:
            zważone_fonemy.append((fonem, wagi_fonemów[fonem]))
        # self.log.info(f"ZWA:{zważone_fonemy}")
        return zważone_fonemy

    def policz_wagę_fonemu(self, x):
        if x in fonemy_samogłoskowe_klucze:
            return (len(fonemy_samogłoskowe[x][0]),
                    len(fonemy_samogłoskowe[x][1]))
        elif x in fonemy_spółgłoskowe_klucze:
            return (len(fonemy_spółgłoskowe[x][0]),
                    len(fonemy_spółgłoskowe[x][1]))

    def waga_fonemu(self, fonem, prawe=False):
        waga = 0
        if fonem in fonemy_spółgłoskowe_klucze:
            waga = fonemy_spółgłoskowe[fonem][0]
            if prawe:
                waga = fonemy_spółgłoskowe[fonem][1]
        elif fonem in fonemy_samogłoskowe_klucze:
            waga = fonemy_samogłoskowe[fonem][0]
            if prawe:
                waga = fonemy_samogłoskowe[fonem][1]
        return waga



    def _dopasuj_kombinacje(self, tekst, kombinacje):
        if tekst == "moc":
            self.log.info(f"Propozycje dla {tekst}: {kombinacje}({len(kombinacje)}")
        kombinacje_dodane = []
        for kombinacja in kombinacje:
            obecny_właściciel = None
            if tekst == "moc":
                self.log.info(f"sprawdzam: {kombinacja[0][0]}")

            if kombinacja[0] not in self.kombinacje.keys():
                self.kombinacje[kombinacja[0][0]] = tekst
                if tekst == "moc":
                    self.log.info(f"co w kombo {kombinacja[0][0]}: {self.kombinacje[kombinacja[0][0]]}")

                kombinacje_dodane.append(kombinacja)
            else:
                obecny_właściciel = self.kombinacje[kombinacja[0][0]]
                if obecny_właściciel == tekst:
                    kombinacje_dodane.append(kombinacja)
                    continue
                kombinacje_właściciela = self.słownik[obecny_właściciel]
                ilość_kombinacji_właściciela = len(kombinacje_właściciela.keys())
                if ilość_kombinacji_właściciela <= self.minimum_kombinacji_per_słowo:
                    continue
                else:
                    obecne_niedopasowanie = kombinacje_właściciela[kombinacja[0][0]]
                    if tekst == "moc":
                        self.log.info(f"2: {kombinacja[0][0]} - niedo: {obecne_niedopasowanie}")

                    minimalne_niedopasowanie_u_właściciela = obecne_niedopasowanie
                    for obca_kominacja, obce_niedopasowanie in kombinacje_właściciela.items():
                        if obce_niedopasowanie < minimalne_niedopasowanie_u_właściciela:
                            minimalne_niedopasowanie_u_właściciela = obce_niedopasowanie
                            break
                        elif obce_niedopasowanie == minimalne_niedopasowanie_u_właściciela and\
                             obca_kombinacja != kombinacja[0][0]:
                            minimalne_niedopasowanie_u_właściciela = obce_niedopasowanie -1
                            break
                    if obecne_niedopasowanie > minimalne_niedopasowanie_u_właściciela:
                        kombinacje_właściciela.pop(kombinacja[0][0])
                        self.słownik(tekst)[kombinacja[0][0]] = niedopasowanie
                        if tekst == "moc":
                            self.log.info(f"3: {kombinacja[0][0]} = {tekst}")

                        self.kombinacje[kombinacja[0][0]] = tekst
                        kombinacje_dodane.append(kombinacja)
        return kombinacje_dodane
                
    def wygeneruj_kombinacje(self, słowo, limit_prób=2):
        self.postęp += 1
        # TODO:
        # - zaimplementować kombinacje z rosnącą liczbą wykluczonych fonemów
        # - przywrócić obliczanie niedopasowania na zasadzie ile brakuje fonemów w kombinacji
        # Wtedy dodawanie wyrazów więcej niż jednosylabowych powinno być prostsze

        # Dla 'w', 'z'
        try:
            sylaby = self.sylaby_słowa[słowo]
        except KeyError as e:
            if len(słowo) == 1:
                sylaby = [słowo]
            else:
                raise KeyError(f"Nie znam sylab, {e}")
        dzielniki_słowa = self.rozdzielacz[len(sylaby)]
        kombinacje = []
        for gdzie_podzielić in dzielniki_słowa:
            (sylaby_lewe,
            sylaba_środkowa,
            sylaby_prawe) = podziel_sylaby_na_strony(sylaby,
                                                     gdzie_podzielić)
            bez_inwersji = True
            malejące_lewe = []
            malejące_prawe = []
            wygenerowano_odjemniki = False
            pozostały_kombinacje_do_przetestowania = True

            indeks_odjemników = -1
            odjemniki_sylab = []
            odejmuj = False
            bez_środka = False

            while limit_prób > 0 and pozostały_kombinacje_do_przetestowania:
                # Wszystkie literki powinny być dopasowane
                # nagłos - lewa, śródgłos - kciuk(i), wygłos - prawa
                # self.log.debug(f"Sylaby: {sylaby_lewe}|{sylaba_środkowa}|{sylaby_prawe}")
                wzrost_niedopasowania = 0
                (fonemy_lewe,
                 śródgłos,
                 fonemy_prawe) = self.rozbij_sylaby_na_fonemy(sylaby_lewe,
                                                            sylaba_środkowa,
                                                            sylaby_prawe)
                # self.log.info(f"{fonemy_lewe} | {śródgłos} | {fonemy_prawe}")
                waga_słowa = 0
                for fonem in fonemy_lewe + śródgłos + fonemy_prawe:
                    waga_słowa += fonem[1]
                if bez_środka:
                    śródgłos = nic
                ręka_lewa = RękaLewa(self.log)
                ręka_prawa = RękaPrawa(self.log)

                kombinacja_środkowa = nic
                if not (malejące_lewe or malejące_prawe or bez_inwersji):
                    fonemy_niemalejące = False
                    while not fonemy_niemalejące:
                        fonemy_lewe = odejmij_fonemy(fonemy_lewe, malejące_lewe)
                        # self.log.info(f"Odjęte lewe: {fonemy_lewe}")
                        fonemy_prawe = odejmij_fonemy(fonemy_prawe, malejące_prawe)
                        (fonemy_niemalejące, który, gdzie) = niemalejące(fonemy_lewe,
                                                                         fonemy_prawe,
                                                                         bez_inwersji)
                        #  Zbieramy informacje o fonemach, które być może
                        #  trzeba będzie wyciszyć aby uzyskać unikalną
                        #  kombinację
                        if not fonemy_niemalejące:
                            if który == 0:
                                malejące_lewe.append(gdzie[2])
                            else:
                                malejące_prawe.append(gdzie[2])

                if not wygenerowano_odjemniki:
                    odjemniki_sylab = wygeneruj_odjemniki(malejące_lewe, malejące_prawe)
                    wygenerowano_odjemniki = True
                if odejmuj:
                    (do_odjęcia_lewe,
                    do_odjęcia_prawe,
                    wzrost_niedopasowania) = odjemniki_sylab[indeks_odejmików]
                    fonemy_lewe = odejmij_fonemy(fonemy_lewe,
                                                 malejące_lewe[indeks_odjemników])
                    fonemy_prawe = odejmij_fonemy(fonemy_prawe,
                                                  malejące_prawe[indeks_odjemników])

                pierwsza = True
                ostatnia = False
                długość_lewych = len(fonemy_lewe)
                for i in range(długość_lewych):
                    fonem = fonemy_lewe[i]
                    if i == długość_lewych -1:
                        ostatnia = True
                    znaki = klawisze_dla_fonemu(fonem)
                    ręka_lewa.zbuduj_kombinację(znaki, pierwsza, ostatnia)
                    pierwsza = False
                for fonem in śródgłos:
                    znaki = fonemy_samogłoskowe[fonem[0]][0]
                    kombinacja_środkowa += znaki
                pierwsza = True
                ostatnia = False
                długość_fonemów_prawych = len(fonemy_prawe)
                for i in range(długość_fonemów_prawych):
                    fonem = fonemy_prawe[i]
                    if i + 1 == długość_fonemów_prawych:
                        ostatnia = True
                    znaki = klawisze_dla_fonemu(fonem, prawe=True)
                    ręka_prawa.zbuduj_kombinację(znaki, pierwsza, ostatnia)
                    pierwsza = False
                # self.log.debug(f"{słowo} {waga_słowa}, Lewa:{ręka_lewa.waga()} Prawa: {ręka_prawa.waga()}")
                niedopasowanie = waga_słowa + wzrost_niedopasowania\
                  - ręka_lewa.waga() - ręka_prawa.waga()
                # self.log.debug(f"{słowo} NPo: {niedopasowanie}")
                # kompletny_akord: ("ZN~*AKI",
                #   ( (dodanie_tyldy_z_lewej, czy_wszystkie_klawisze),
                #     (dodanie_tyldy_z_prawej, czy_wszystkie_klawisze) ),
                #   ( (dodanie_gwiazdki_z_lewej, czy_wszystkie_klawisze),
                #     (dodanie_gwiazdki_z_prawej, czy_wszystkie_klawisze) ),
                #   ( (dodanie_tyldogwiazdki_z_lewej, czy_wszystkie_klawisze),
                #     (dodanie_tyldogwiazdki_z_prawej, czy_wszystkie_klawisze) ) )
                kompletny_akord = self.połącz_kombinacje(ręka_lewa.akord_lewy(),
                                                         kombinacja_środkowa,
                                                         ręka_prawa.akord_prawy())
                kombinacje.append((kompletny_akord, niedopasowanie))
                limit_prób -= 1
                if bez_inwersji:
                    bez_środka = True
                if bez_środka:
                    bez_inwersji = False
                    bez_środka = False
                    odejmuj = True
                if odejmuj:
                    indeks_odjemników += 1
                    if indeks_odjemników >= len(odjemniki_sylab):
                        odejmuj = False
                        pozostały_kombinacje_do_przetestowania = False

        dodane = []
        #  Kombinacja: ("ZNAKI", (dodanie_tyldy_możliwe),
        #               (dodanie_gwiazdki_możliwe), (dodanie_tyl-gwi_możliwe))
        #
        # (dodanie_X_możliwe) == ((z_lewej, czy wszystkie znaki), (z_prawej, czy_wszystkie_znaki))

        if kombinacje:
            if słowo == "moc":
                    self.log.info(f"dopasowuje moc... {kombinacje}")
            dodane = self._dopasuj_kombinacje(słowo, kombinacje)
        else:
            self.log.debug(f"Nie znalazłem kombinacji dla: {słowo}")
        nowe_kombinacje = []
        if len(dodane) == 0 and kombinacje:
            #  Możemy pokombinować z gwiazdkami
            #  Na razie logika minimalistyczna
            # if słowo == "moc":
            #     self.log.info(f"moc: {kombinacje}")
            for kombinacja in kombinacje:
                nowe_podkombinacje = dodaj_znaki_specjalne_do_kombinacji(kombinacja)
                nowe_kombinacje += nowe_podkombinacje
                # if len(dodane) > 0:
                #     break
            if nowe_kombinacje:
                if słowo == "moc":
                    self.log.info(f"dopasowuje moc... {nowe_kombinacje}")
                dodane += self._dopasuj_kombinacje(słowo, nowe_kombinacje)

        if self.postęp % self.loguj_postęp_co == 0:
            self.log.info(f"{self.postęp}: {słowo} - wygenerowano")
        if len(dodane) == 0:
            return False
        else:
            return True

    def połącz_kombinacje(self, ręka_lewa, kombinacja_środkowa, ręka_prawa):
        tylda_lewa = tylda in ręka_lewa[0]
        tylda_prawa = tylda in ręka_prawa[0]
        gwiazdka_lewa = gwiazdka in ręka_lewa[0]
        gwiazdka_prawa = gwiazdka in ręka_prawa[0]
        ptyldogwiazdka = nic
        ręka_lewa_znaki = ręka_lewa[0]
        ręka_prawa_znaki = ręka_prawa[0]
        if tylda_lewa or tylda_prawa:
            ręka_lewa_znaki = ręka_lewa_znaki.replace(tylda, nic)
            ręka_prawa_znaki = ręka_prawa_znaki.replace(tylda, nic)
            kombinacja_środkowa = kombinacja_środkowa.replace(tylda, nic)
            ptyldogwiazdka = tylda

        if gwiazdka_lewa or gwiazdka_prawa:
            ręka_lewa_znaki = ręka_lewa_znaki.replace(gwiazdka, nic)
            ręka_prawa_znaki = ręka_prawa_znaki.replace(gwiazdka, nic)
            kombinacja_środkowa = kombinacja_środkowa.replace(gwiazdka, nic)
            ptyldogwiazdka += gwiazdka
        if len(ptyldogwiazdka) == 0:
            ptyldogwiazdka = "-"
        kombinacja_środkowa += ptyldogwiazdka
        wynik = nic
        for znak in znaki_środka:
            if znak in kombinacja_środkowa:
                wynik += znak
        return (ręka_lewa_znaki + wynik + ręka_prawa_znaki,
                (ręka_lewa[1], ręka_prawa[1]),  # dodanie tyldy możliwe
                (ręka_lewa[2], ręka_prawa[2]),  # dodanie gwiazdki możliwe
                (ręka_lewa[3], ręka_prawa[3]),)  # dodanie tyldogwiazdki możliwe
        
    # Ponieważ sortowanie może trochę zająć, warto zapisać co już mamy
    # w razie gdyby skończył się zapas RAMu
    def generuj_do_pliku(self):
        for (kombinacja, tekst) in self.kombinacje.items():
            if tekst == "moc":
                self.log.info(f"generuje: {kombinacja}: {tekst}")

            yield f'"{kombinacja}": "{tekst}",\n'


def main():
    parser = argparse.ArgumentParser(
        description='Generuj słownik na podstawie słów podzielonych na sylaby',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--log', default='wyniki/generuj_slownik.log',
                        help='log przebiegu generacji słownika')
    parser.add_argument('--frekwencja', default='../../data/frekwencja_Kazojc.csv',
                        help='dane frekwencyjne (w formacie linii csv: "słowo",częstość)')
    parser.add_argument('--slowa', default='../../data/slownik',
                        help='słowa do utworzenia słownika podzielone na sy=la=by')
    parser.add_argument('--baza', default='wyniki/baza.json',
                        help='początkowy plik słownika w formacie JSON')
    parser.add_argument('--slownik', default='wyniki/spektralny-slowik.json',
                        help='wynikowy plik JSON do załadowania do Plovera')
    args = parser.parse_args()

    # Upewnij się że foldery istnieją
    for plik_wyjściowy in [args.log, args.slownik]:
        folder = os.path.dirname(plik_wyjściowy)
        if folder != '':
            os.makedirs(folder, exist_ok=True)

    # Spróbuj otworzyć plik logu
    log = Logger(args.log)
    log.info(f'Argumenty: {str(args)[10:-1]}')

    # Słownik wyjściowy, dane w formie:
    # {tekst: {"Kombinacja": niedopasowanie}}
    słownik = collections.defaultdict(dict)
    numer_linii = 0
    if args.baza:
        log.info(f"Czytam bazę słownika z {args.baza}")
        for linia in czytaj_linie_pliku(args.baza):
            numer_linii += 1
            linia = linia.strip()
            if not linia or linia.startswith('#') or linia.startswith('{') or linia.startswith('}') :
                continue
            (kombinacja, wyraz) = czytaj_znaki_między_cudzysłowem(linia)
            słownik[wyraz] = {kombinacja: 0}
        log.info(f"Baza wczytana")
    linie_bazy = numer_linii

    sylaby_słowa = dict()
    numer_linii = 0
    for linia in czytaj_linie_pliku(args.slowa):
        numer_linii += 1
        linia = linia.strip()
        if linia.startswith('#'):
            continue

        sylaby = linia.split('=')
        tekst = ''.join(sylaby)
        sylaby_słowa[tekst] = sylaby #klawisze_słowa
        if numer_linii % 10000 == 0 and numer_linii != 0:
            log.info(f'Przetwarzanie linii {numer_linii}: {linia}')

    log.info("Wczytałem sylaby, generuję klawisze...")
    istniejące_słowa = słownik.keys()
    generator = Generator(log, słownik, sylaby_słowa)
    numer_generacji = 0
    czas_start = time.time()
    niepowodzenia = []
    for linia in czytaj_linie_pliku(args.frekwencja):
        linia = linia.strip()
        słowo = linia.split('"')[1]
        frekwencja = int(linia.split(',')[1])
        if słowo in istniejące_słowa or słowo.isnumeric():
            continue

        udało_się = generator.wygeneruj_kombinacje(słowo, limit_prób=20)
        if not udało_się:
            niepowodzenia.append((słowo, frekwencja))
        numer_generacji += 1
    log.info(f"Dodano {len(słownik) - linie_bazy} słów.")

    # Na czas developmentu wyłączone
    # log.info("Dodaję słowa bez podanej częstotliwości")
    # for słowo in sylaby_słowa.keys():
    #     generator.wygeneruj_kombinacje(słowo, limit_prób=10)
    #     numer_generacji += 1

    log.info(f"Nie powiodło się dodawanie kombinacji dla {len(niepowodzenia)} słów.")
    log.info(f"Dodano {len(słownik) - linie_bazy} słów w {time.time() - czas_start} sekund.")
    log.info("Słownik utworzony, zapisuję...")
    with open(args.slownik[:-5]+"_niesortowany.json", 'w', buffering=1024000) as plik_wynikowy:
        plik_wynikowy.write('{\n')
        for linia in generator.generuj_do_pliku():
            plik_wynikowy.write(linia)
        # plik_wynikowy.seek(-2, os.SEEK_CUR)
        plik_wynikowy.write('}\n')

    # Posortuj słowa według kolejności klawiszy
    log.info("Zapis niesortowanego słownika zakończony, sortuję...")
    kolejność = '/#XFZSKTPVLR-JE~*IAUCRLBSGTWOY'
    posortowany_słownik = collections.OrderedDict(
        sorted(generator.kombinacje.items(), key=lambda wpis:
               [kolejność.index(k) for k in wpis[0]]))

    log.info("Sortowanie zakończone, zapisuję...")
    with open(args.slownik, 'w', buffering=1024000) as plik_wynikowy:
        plik_wynikowy.write('{\n')
        for klawisze, tekst in posortowany_słownik.items():
            plik_wynikowy.write(f'"{klawisze}": "{tekst}",\n')
        plik_wynikowy.write('}\n')

    plik_z_niepowodzeniami = args.slownik[:-5]+"_porazki.txt"
    log.info(f"Zapisuję niepowodzenia do {plik_z_niepowodzeniami}")
    with open(plik_z_niepowodzeniami, 'w', buffering=1024) as plik_wynikowy:
        for (słowo, frekwencja) in niepowodzenia:
            plik_wynikowy.write(f"{słowo} ({frekwencja})\n")
    log.info("Fajrant")


def czytaj_znaki_między_cudzysłowem(wiersz):
    lista = []
    token = nic
    cudzysłów_otwarty = False
    poprzedni_backslash = False
    for znak in wiersz:
        if cudzysłów_otwarty and znak != '"':
            token+=znak
            poprzedni_backslash = False
        elif cudzysłów_otwarty and znak == '"' and not poprzedni_backslash:
            lista.append(token)
            token = nic
            cudzysłów_otwarty = False
        elif cudzysłów_otwarty and znak == '"' and poprzedni_backslash:
            token+=znak
            poprzedni_backslash = False
        elif cudzysłów_otwarty and znak == '\\':
            token+=znak
            poprzedni_backslash = True
        elif not cudzysłów_otwarty and znak == '"':
            cudzysłów_otwarty = True
            poprzedni_backslash = False
        elif not cudzysłów_otwarty and znak != '"':
            poprzedni_backslash = False
            continue
    return lista


def split(word):
    return [char for char in word]


def czytaj_linie_pliku(plik):
    for linia in open(plik, "r"):
        yield linia
            

class Klawisz:
    def __init__(self, znak, indeks, kombinacja_id, waga=1, samodzielny=0, początkowy=False, końcowy=False):
        self.znak = znak
        self.waga = waga
        # if początkowy or końcowy:
        #     self.waga += 1
        self.indeks = indeks
        self.kombinacja = set()
        self.kombinacja.add(kombinacja_id)
        self.początkowy = początkowy
        self.końcowy = końcowy
        self.samodzielny = samodzielny

    def aktualizuj(self, inny_klawisz, id_kombinacji, długość_kombinacji):
        self.kombinacja.add(id_kombinacji)
        samodzielny = 0
        if długość_kombinacji == 1:
            samodzielny = 1
        self.samodzielny += samodzielny
        if inny_klawisz.początkowy:
            self.początkowy = True
        if inny_klawisz.końcowy:
            self.końcowy = True


class Kombinacja:
    def __init__(self, id_kombinacji,
                 znaki,
                 waga=1,
                 prawa=False,
                 pierwsza_kombinacja=False,
                 ostatnia_kombinacja=False):
        self.indeksy = lewe_indeksy_klawiszy
        if prawa:
            self.indeksy = prawe_indeksy_klawiszy
        self.id_kombinacji = id_kombinacji
        self.klawisze = dict()
        self.długość_kombinacji = len(znaki)
        for znak in znaki:
            indeks = self.indeksy[znak]
            samodzielny = 0
            if self.długość_kombinacji == 1:
                samodzielny = 1
            self.klawisze[znak] = Klawisz(znak,
                                          indeks,
                                          id_kombinacji,
                                          waga,
                                          samodzielny,
                                          pierwsza_kombinacja,
                                          ostatnia_kombinacja)
    def zwróć_klawisze(self):
        for klawisz in self.klawisze.values():
            yield klawisz
            
lewe_wszystkie = "LR~*-"
prawe_wszystkie = "~*-CR"
def dodaj_znaki_specjalne_do_kombinacji(kombinacja):
    #   ( (dodanie_tyldy_z_lewej, czy_wszystkie_klawisze),
    #     (dodanie_tyldy_z_prawej, czy_wszystkie_klawisze) ),
    #   ( (dodanie_gwiazdki_z_lewej, czy_wszystkie_klawisze),
    #     (dodanie_gwiazdki_z_prawej, czy_wszystkie_klawisze) ),
    #   ( (dodanie_tyldogwiazdki_z_lewej, czy_wszystkie_klawisze),
    #     (dodanie_tyldogwiazdki_z_prawej, czy_wszystkie_klawisze) ) )
    nowe_kombinacje = []
    (kombo, niedopasowanie) = kombinacja
    #('TLE~GO', ((False, False), (False, False)), ((False, False), (False, False)), ((False, False), (True, False)))
    (znaki, ((l_tylda, lt_wszystko),(p_tylda, pt_wszystko)),
            ((l_gwiazdka, lg_wszystko), (p_gwiazdka, pg_wszystko)),
            ((l_tyldogwiazdka, ltg_wszystko), (p_tyldogwiazdka, ptg_wszystko))) = kombo
    # print(f"kombo: {kombo}")
    if myślnik in znaki:
        znaki_lewe, znaki_prawe = znaki.split(myślnik)
    elif tylda in znaki:
        znaki_lewe, znaki_prawe = znaki.split(tylda)
        znaki_prawe = tylda + znaki_prawe
    elif gwiazdka in znaki:
        znaki_lewe, znaki_prawe = znaki.split(gwiazdka)
        znaki_prawe = gwiazdka + znaki_prawe
    elif jot in znaki:
        znaki_lewe, znaki_prawe = znaki.split(jot)
        znaki_lewe = znaki_lewe + jot
    elif ee in znaki:
        znaki_lewe, znaki_prawe = znaki.split(ee)
        znaki_lewe = znaki_lewe + ee
    elif ii in znaki:
        znaki_lewe, znaki_prawe = znaki.split(ii)
        znaki_prawe = ii + znaki_prawe
    elif aa in znaki:
        znaki_lewe, znaki_prawe = znaki.split(aa)
        znaki_prawe = aa + znaki_prawe
    elif uu in znaki:
        znaki_lewe, znaki_prawe = znaki.split(uu)
        znaki_prawe = uu + znaki_prawe
    else:
        print(f"ERR: Nie wiem jak podzielić {znaki} w {kombo}")
        return []
    if l_tylda or p_tylda:
        if lt_wszystko:
            for znak in lewe_wszystkie:
                znaki_lewe = znaki_lewe.replace(znak, nic)
            nowe_kombinacje.append(znaki_lewe + lewe_wszystkie + znaki_prawe)
        elif pt_wszystko:
            for znak in prawe_wszystkie:
                znaki_prawe = znaki_prawe.replace(znak, nic)
            nowe_kombinacje.append(znaki_lewe + prawe_wszystkie + znaki_prawe)
        else:
            nowe_kombinacje.append(znaki_lewe.replace(tylda, nic)\
                                   + tylda\
                                   # + myślnik\
                                   + znaki_prawe.replace(tylda, nic))

    if l_gwiazdka or p_gwiazdka:
        if lg_wszystko:
            for znak in lewe_wszystkie:
                znaki_lewe = znaki_lewe.replace(znak, nic)
            nowe_kombinacje.append(znaki_lewe + lewe_wszystkie + znaki_prawe)
        elif pg_wszystko:
            for znak in prawe_wszystkie:
                znaki_prawe = znaki_prawe.replace(znak, nic)
            nowe_kombinacje.append(znaki_lewe + prawe_wszystkie + znaki_prawe)
        else:
            nowe_kombinacje.append(znaki_lewe.replace(gwiazdka, nic)\
                                   + gwiazdka\
                                   # + myślnik\
                                   + znaki_prawe.replace(gwiazdka, nic))

    if l_tyldogwiazdka or p_tyldogwiazdka:
        if ltg_wszystko:
            for znak in lewe_wszystkie:
                znaki_lewe = znaki_lewe.replace(znak, nic)
            nowe_kombinacje.append(znaki_lewe + lewe_wszystkie + znaki_prawe)
        elif ptg_wszystko:
            for znak in prawe_wszystkie:
                znaki_prawe = znaki_prawe.replace(znak, nic)
            nowe_kombinacje.append(znaki_lewe + prawe_wszystkie + znaki_prawe)
        elif l_tyldogwiazdka:
            nowe_prawe = znaki_prawe.replace(tylda, nic)
            nowe_prawe = nowe_prawe.replace(gwiazdka, nic)
            nowe_kombinacje.append(znaki_lewe\
                                   + tyldogwiazdka\
                                   # + myślnik\
                                   + nowe_prawe)
        elif p_tyldogwiazdka:
            nowe_lewe = znaki_lewe.replace(tylda, nic)
            nowe_lewe = nowe_lewe.replace(gwiazdka, nic)
            nowe_kombinacje.append(nowe_lewe\
                                   + tyldogwiazdka\
                                   # + myślnik\
                                   + znaki_prawe)
    output = []
    for nowa in nowe_kombinacje:
        output.append( (
            (nowa, ((False, False),
                    (False, False)),
             ((False, False),
              (False, False)),
                             ((False, False),
                              (True, False))), niedopasowanie))
    return output
    

class RękaLewa:
    def __init__(self, log):
        self.log = log
        self.palec_mały = Palec(log, ["X", "F", "Z", "S"])
        self.palec_serdeczny = Palec(log, ["K", "T"])
        self.palec_środkowy = Palec(log, ["P", "V"])
        self.palec_wskazujący = Palec(log, ["L", "R", "~", "*"])
        self.kciuk_lewy = Palec(log, ["J", "E"])  # tutaj do logiki ważne jest tylko "J"
        self.kombinacje = []  # Można tylko dodawać elementy do kombinacji, żeby IDki się zgadzały!!!
        self.dostępne_id_kombinacji = 0

    def waga(self):
        waga = 0
        for palec in [self.palec_mały, self.palec_serdeczny, self.palec_środkowy,
                      self.palec_wskazujący, self.kciuk_lewy]:
            waga += palec.waga()
        return waga

    def palec_dla_indeksu(self, indeks):
        if indeks in [0, 1]:
            return self.palec_mały
        elif indeks == 2:
            return self.palec_serdeczny
        elif indeks == 3:
            return self.palec_środkowy
        elif indeks in [4, 5]:
            return self.palec_wskazujący
        elif indeks == 6:
            return self.kciuk_lewy
        else:
            self.log.error(f"Lewa ręka nie ma palca dla indeksu: {indeks}")

    def zbuduj_kombinację(self, znaki, pierwsza=False, ostatnia=False):
        id_kombinacji = self.dostępne_id_kombinacji
        self.dostępne_id_kombinacji += 1
        kombinacja = Kombinacja(id_kombinacji,
                                znaki,
                                prawa=False,
                                pierwsza_kombinacja=pierwsza,
                                ostatnia_kombinacja=ostatnia)
        self.dodaj_kombinację(kombinacja)

    def dodaj_kombinację(self, kombinacja):
        self.kombinacje.append(kombinacja)
        for klawisz in kombinacja.zwróć_klawisze():
            palec = self.palec_dla_indeksu(klawisz.indeks)
            if klawisz.znak not in palec.wspierane_kombinacje:
                self.log.error(f"Nie mogę dodać klawisza {klawisz.znak} {klawisz.indeks}")
            else:
                palec.dodaj_klawisz(klawisz, kombinacja.id_kombinacji, kombinacja.długość_kombinacji)

    def akord_lewy(self):
        tekst = self.palec_mały.tekst()
        tekst += self.palec_serdeczny.tekst()
        tekst += self.palec_środkowy.tekst()
        tekst += self.palec_wskazujący.tekst()
        tekst += self.kciuk_lewy.tekst()
        dodanie_tyldy = self.palec_wskazujący.dodanie_tyldy_możliwe()
        dodanie_gwiazdki = self.palec_wskazujący.dodanie_gwiazdki_możliwe()
        dodanie_tyldogwiazdki = self.palec_wskazujący.dodanie_tyldy_i_gwiazdki_możliwe()
        return (tekst, dodanie_tyldy, dodanie_gwiazdki, dodanie_tyldogwiazdki)


class RękaPrawa:
    def __init__(self, log):
        self.log = log
        self.palec_wskazujący = Palec(log, ["~", "*", "C", "R"])
        self.palec_środkowy = Palec(log, ["L", "B"])
        self.palec_serdeczny = Palec(log, ["S", "G"])
        self.palec_mały = Palec(log, ["T", "W", "O", "Y"])
        self.kombinacje = []  # Można tylko dodawać elementy do kombinacji, żeby IDki się zgadzały!!!
        self.dostępne_id_kombinacji = 0

    def waga(self):
        waga = 0
        for palec in [self.palec_mały, self.palec_serdeczny, self.palec_środkowy,
                      self.palec_wskazujący]:
            waga += palec.waga()
        return waga

    def palec_dla_indeksu(self, indeks):
        if indeks in [5, 6]:
            return self.palec_wskazujący
        elif indeks == 7:
            return self.palec_środkowy
        elif indeks == 8:
            return self.palec_serdeczny
        elif indeks in [9, 10]:
            return self.palec_mały
        else:
            self.log.error(f"Prawa ręka nie ma palca dla indeksu: {indeks}")

    def zbuduj_kombinację(self, znaki, pierwsza=False, ostatnia=False):
        id_kombinacji = self.dostępne_id_kombinacji
        self.dostępne_id_kombinacji += 1
        kombinacja = Kombinacja(id_kombinacji,
                                znaki,
                                prawa=True,
                                pierwsza_kombinacja=pierwsza,
                                ostatnia_kombinacja=ostatnia)
        self.dodaj_kombinację(kombinacja)

    def dodaj_kombinację(self, kombinacja):
        self.kombinacje.append(kombinacja)
        for klawisz in kombinacja.zwróć_klawisze():
            palec = self.palec_dla_indeksu(klawisz.indeks)
            if klawisz.znak not in palec.wspierane_kombinacje:
                self.log.error(f"Nie mogę dodać klawisza {klawisz.znak} {klawisz.indeks}")
            else:
                palec.dodaj_klawisz(klawisz, kombinacja.id_kombinacji, kombinacja.długość_kombinacji)

    def akord_prawy(self):
        tekst = self.palec_wskazujący.tekst()
        tekst += self.palec_środkowy.tekst()
        tekst += self.palec_serdeczny.tekst()
        tekst += self.palec_mały.tekst()
        dodanie_tyldy = self.palec_wskazujący.dodanie_tyldy_możliwe()
        dodanie_gwiazdki = self.palec_wskazujący.dodanie_gwiazdki_możliwe()
        dodanie_tyldogwiazdki = self.palec_wskazujący.dodanie_tyldy_i_gwiazdki_możliwe()
        return (tekst, dodanie_tyldy, dodanie_gwiazdki, dodanie_tyldogwiazdki)
        

class Palec:
    def __init__(self, log, obsługiwane_klawisze):
        self.log = log
        self.wspierane_kombinacje = [obsługiwane_klawisze[0],
                                     obsługiwane_klawisze[1],
                                     obsługiwane_klawisze[0]+obsługiwane_klawisze[1]]
        if len(obsługiwane_klawisze) == 4:
            self.wspierane_kombinacje += [obsługiwane_klawisze[2],
                                          obsługiwane_klawisze[3],
                                          obsługiwane_klawisze[2]+obsługiwane_klawisze[3],
                                          obsługiwane_klawisze[0]+obsługiwane_klawisze[2],
                                          obsługiwane_klawisze[1]+obsługiwane_klawisze[3],
                                          obsługiwane_klawisze[0]+obsługiwane_klawisze[1]+\
                                          obsługiwane_klawisze[2]+obsługiwane_klawisze[3]]
        self.obsługiwane_klawisze = obsługiwane_klawisze
        self.klawisze = {}

    def dodaj_klawisz(self, klawisz, id_kombinacji, długość_kombinacji):
        if klawisz.znak not in self.obsługiwane_klawisze:
            self.log.error(f"{klawisz.znak} nieobsługiwany ({self.obsługiwane_klawisze})")
        elif klawisz.znak not in self.klawisze.keys():
            self.klawisze[klawisz.znak] = klawisz
        else:
            self.klawisze[klawisz.znak].aktualizuj(klawisz, id_kombinacji, długość_kombinacji)

    def pierwszy_lub_ostatni_klawisz(self):
        for klawisz in self.klawisze.values():
            if klawisz.początkowy or klawisz.końcowy:
                return klawisz.znak
        return False

    def tekst(self):
        ile_klawiszy_użytych = len(self.klawisze)
        tekst = nic
        if ile_klawiszy_użytych == 3:
            # Musimy coś wywalić, pierwszy i ostatni musi zostać
            musi_zostać = self.pierwszy_lub_ostatni_klawisz()
            if not musi_zostać:
                usuwany_klawisz = Klawisz('', -1, -1, 100)
                for klawisz in self.klawisze.values():
                    if klawisz.waga < usuwany_klawisz.waga:
                        usuwany_klawisz = klawisz
                self.klawisze.pop(usuwany_klawisz.znak)
            else:
                for klawisz in self.klawisze.values():
                    if klawisz.znak == musi_zostać:
                        continue
                    if musi_zostać+klawisz.znak in self.wspierane_kombinacje:
                        return musi_zostać+klawisz.znak
                    elif klawisz.znak+musi_zostać in self.wspierane_kombinacje:
                        return klawisz.znak+musi_zostać
                self.log.error(f"Nie znalazłem prawidłowej kombinacji dla {self.klawisze.keys()}")
        for klawisz in self.obsługiwane_klawisze:
            if klawisz in self.klawisze.keys():
                tekst += klawisz
        return tekst

    def waga(self):
        waga = 0
        for klawisz in self.klawisze.values():
            waga += klawisz.waga
        return waga

    def dodanie_tyldy_możliwe(self):
        if tylda not in self.obsługiwane_klawisze:
            return (False, False)
        elif tylda in self.klawisze.keys():
            return (False, False)
        elif len(self.klawisze) == 3:
            # return (True, self.wspierane_kombinacje[-1])
            return (True, True)  # tylda wspierana, wtedy wszystkie klawisze palca aktywne
        elif len(self.klawisze) == 1\
          and "L" in self.klawisze.keys():
            return (True, False)
        elif len(self.klawisze) == 1\
          and "C" in self.klawisze.keys():
            # return (True, "~C")
            return (True, False)  # tylda wspierana, wtedy nie wszystkie klawisze palca aktywne
        elif len(self.klawisze) == 0:
            return (True, False)
        return (False, False)

    def dodanie_gwiazdki_możliwe(self):
        if gwiazdka not in self.obsługiwane_klawisze:
            return (False, False)
        elif gwiazdka in self.klawisze.keys():
            return (False, False)
        elif len(self.klawisze) == 3:
            # return (True, self.wspierane_kombinacje[-1])
            return (True, True)  # Gwiazdka wspierana, wtedy wszystkie klawisze aktywowane
        elif len(self.klawisze) == 1\
          and "R" in self.klawisze.keys():
            # if self.obsługiwane_klawisze[0] == "L"
            #     return (True, "R*")
            # else:
            #     return (True, "*R")
            return (True, False)  # Gwiazdka wspierana, wtedy nie wszystkie klawisze aktywowane
        elif len(self.klawisze) == 0:
            return (True, False)
        return (False, False)

    def dodanie_tyldy_i_gwiazdki_możliwe(self):
        if tylda not in self.obsługiwane_klawisze or\
          gwiazdka not in self.obsługiwane_klawisze:
            return (False, False)
        elif tylda in self.klawisze.keys() or\
          gwiazdka in self.klawisze.keys():
            return (False, False)
        elif len(self.klawisze) == 2:
            return (True, True)
        elif len(self.klawisze) == 0:
            return (True, False)
        return (False, False)

#  Jeśli sam(a) podajesz wartość gdzie_podzielić,
#  musisz zadbać o poprawność.
def podziel_sylaby_na_strony(sylaby, gdzie_podzielić=-2):
    # TODO sparametryzować definicję podziału
    ilość_sylab = len(sylaby)
    if gdzie_podzielić < 0:
        gdzie_podzielić = ilość_sylab + gdzie_podzielić
        if gdzie_podzielić < 0:
            gdzie_podzielić = 0
    if gdzie_podzielić > ilość_sylab -1:
        gdzie_podzielić = ilość_sylab -1
    sylaby_lewe = []
    sylaby_prawe = []
    if ilość_sylab == 1:
        return (sylaby_lewe, sylaby[0], sylaby_prawe)
    else:
        for i in range(gdzie_podzielić):
            sylaby_lewe.append(sylaby[i])
        if gdzie_podzielić == ilość_sylab - 1:
            sylaby_prawe = []
        else:
            sylaby_prawe = [sylaby[gdzie_podzielić + 1]]
        return (sylaby_lewe,
                sylaby[gdzie_podzielić],
                sylaby_prawe)


if __name__ == '__main__':
    main()

