
"""
    Avem aplicatia care tine stocul unui depozit (Cap 5-6). Efectuati urmatoarele imbunatatiri:
   Este necesar rezolvati minim 3 din punctele de mai jos:
1. Implementati o solutie care sa returneze o proiectie grafica a intrarilor si iesirilor intr-o
anumita perioada, pentru un anumit produs; --pygal--
2. Implementati o solutie care sa va avertizeze automat cand stocul unui produs este mai mic decat o 
limita minima, predefinita per produs. Limita sa poata fi variabila (per produs). Preferabil sa 
transmita automat un email de avertizare;
3. Creati o metoda cu ajutorul careia sa puteti transmite prin email diferite informatii(
de exemplu fisa produsului) ;  --SMTP--
4. Utilizati Regex pentru a cauta :
    - un produs introdus de utilizator;
    - o tranzactie cu o anumita valoare introdusa de utilizator;   --re--
5. Creati o baza de date care sa cuprinda urmatoarele tabele:  --pymysql--  sau --sqlite3--
    Categoria
        - idc INT NOT NULL AUTO_INCREMENT PRIMARY KEY (integer in loc de int in sqlite3)
        - denc VARCHAR(255) (text in loc de varchar in sqlite3)
    Produs
        - idp INT NOT NULL AUTO_INCREMENT PRIMARY KEY
        - idc INT NOT NULL
        - denp VARCHAR(255)
        - pret DECIMAL(8,2) DEFAULT 0 (real in loc de decimal)
        # FOREIGN KEY (idc) REFERENCES Categoria.idc ON UPDATE CASCADE ON DELETE RESTRICT
    Operatiuni
        - ido INT NOT NULL AUTO_INCREMENT PRIMARY KEY
        - idp INT NOT NULL
        - cant DECIMAL(10,3) DEFAULT 0
        - data DATE
6. Imlementati o solutie cu ajutorul careia sa populati baza de date cu informatiile adecvate.
7. Creati cateva view-uri cuprinzand rapoarte standard pe baza informatiilor din baza de date. --pentru avansati--
8. Completati aplicatia astfel incat sa permita introducerea pretului la fiecare intrare si iesire.
Pretul de iesire va fi pretul mediu ponderat (la fiecare tranzactie de intrare se va face o medie intre
pretul produselor din stoc si al celor intrate ceea ce va deveni noul pret al produselor stocate).
Pretul de iesire va fi pretul din acel moment; --pentru avansati--
9. Creati doua metode noi, testati-le si asigurati-va ca functioneaza cu succes;
"""  #

from datetime import datetime
import pygal
import smtplib


class Stoc:
    """Tine stocul unui depozit"""

    def __init__(self, prod, categ, um='Buc', sold=0):
        self.prod = prod
        self.categ = categ
        self.sold = sold
        self.um = um
        self.i = {}
        self.e = {}
        self.d = {}

    def intr(self, cant, data=str(datetime.now().strftime('%D'))):
        self.data = data
        self.cant = cant
        self.sold += cant
        if self.d.keys():
            cheie = max(self.d.keys()) + 1
        else:
            cheie = 1
        self.i[cheie] = cant
        self.d[cheie] = self.data

    def iesi(self, cant, data=str(datetime.now().strftime('%D'))):

        self.data = data
        self.cant = cant
        self.sold -= self.cant
        if self.d.keys():
            cheie = max(self.d.keys()) + 1
        else:
            cheie = 1
        self.e[cheie] = self.cant
        self.d[cheie] = self.data

    def fisap(self):

        print('Fisa produsului ' + self.prod + ': ' + self.um)
        print(28 * '-')
        print(' Nrc ', '  Data ', 'Intrari', 'Iesiri')
        print(28 * '-')
        for v in self.d.keys():
            if v in self.i.keys():
                print(str(v).rjust(5), self.d[v], str(self.i[v]).rjust(6), str(0).rjust(6))
            else:
                print(str(v).rjust(5), self.d[v], str(0).rjust(6), str(self.e[v]).rjust(6))
        print(28 * '-')
        print('Stoc actual:      ' + str(self.sold).rjust(10))
        print(28 * '-' + '\n')

    def proiectie(self):    #1,#9
        """Proiectie grafica a intrarilor si a iesirilor --- Stacked Bar"""

        self.x=[]
        for v in self.d.values():
            self.x.append(v)
        self.x1= []
        self.x2= []
        self.h = {}
        self.f = {}
        self.c=0
        for v in self.d.keys():
            self.c+=1
        for v in range (1,self.c+1):
            self.h[v]=0
            self.f[v]=0
        for v in self.i.keys():
            self.h[v] = self.i[v]
        for v in self.e.keys():
            self.f[v] = self.e[v]
        for v in self.h.values():
            self.x1.append(v)
        for v in self.f.values():
            self.x2.append(v)

        ob = pygal.StackedBar()
        ob.title = 'Proiectie grafica a intrarilor si a iesirilor pentru ' + self.prod
        ob.add('Intrari',self.x1)
        ob.add('Iesiri', self.x2)
        ob.x_labels = self.l
        ob.render_to_file('Proiectie.svg')
        print('Vei gasi proiectia grafica a intrarilor si a iesirilor sub numele de Proiectie.svg')

    def minim(self, min=0):
        """Atentionarea prin email in cazul depasirii unui minim la un produs"""

        if self.sold < min:
            print('Miimul', min, 'la', self.prod, 'a fost depasit!')
            self.expeditor = 'introduMail@email.com'
            self.destinatar = input('Introduceti adresa la care doriti sa trimiteti mail de atentionare pentru depasirea minimului')
            self.parola = 'introduParola'
            self.mesaj = """ACESTA ESTE DOAR UN MESAJ DE ATENTIONARE
               Minimul """+str(min)+' la '+self.prod+' a fost depasit!!'
            self.ob = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            self.ob.login(self.expeditor, self.parola)
            self.ob.sendmail(self.expeditor, self.destinatar, self.mesaj)

        else:
            print('Minimul ', min, 'la', self.prod, 'nu a fost depasit!!')

    def info(self):
        """Trimiterea prin email a fisei unui produs"""

        self.mesaj = 'Fisa produsului' + self.prod + ': ' + self.um+'\n'
        self.mesaj+=55 * '-'+'\n'
        self.mesaj+=' Nrc '+ '\t    Data '+ 'Intrari'+ ' Iesiri'+'\n'
        for v in self.d.keys():
            if v in self.i.keys():
                self.mesaj+=str(v).rjust(5)+'| '+ self.d[v]+'  '+ str(self.i[v]).rjust(6)+' '+ str(0).rjust(6)+'\n'
            else:
                self.mesaj+=str(v).rjust(5)+'| '+ self.d[v]+'  '+ str(0).rjust(6)+' '+ str(self.e[v]).rjust(6)+'\n'
        self.mesaj+=35 * '-'+'\n'
        self.mesaj+='Stoc actual:      ' + str(self.sold).rjust(10)+'\n'
        self.mesaj+=35 * '-' + '\n'
        self.expeditor = 'introduMail@email.com'
        self.destinatar = input('Introdu adresa la care doresti sa primesti fisa produsului:')
        self.parola = 'introduParola'
        self.ob = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        self.ob.login(self.expeditor, self.parola)
        self.ob.sendmail(self.expeditor, self.destinatar, self.mesaj)


fragute = Stoc('fragute', 'fructe', 'kg')
lapte = Stoc('lapte', 'lactate', 'litru')


fragute.intr(100)
fragute.iesi(73)
fragute.intr(100)
fragute.iesi(85)
fragute.intr(100)
fragute.iesi(101)
fragute.intr(500)
fragute.intr(79)
fragute.iesi(520)

fragute.fisap()


lapte.intr(1500)
lapte.iesi(975)
lapte.intr(1200)
lapte.iesi(1490)
lapte.intr(1000)
lapte.iesi(1200)

lapte.fisap()


fragute.proiectie()
fragute.minim(35)
fragute.info()