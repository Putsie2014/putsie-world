import tkinter as tk

from tkinter import messagebox

import random

import os

from googletrans import Translator



class PutsieWorldApp:

    def __init__(self, root):

        self.root = root

        self.root.title("Putsie World - Volledig Werkend")

        self.root.geometry("800x1000")

        

        self.translator = Translator()

        self.username = None

        self.user_words_file = ""

        self.user_stats_file = ""

        

        self.woorden_lijst = {}

        self.werkwoorden_lijst = {}

        self.geld = 0

        self.land_grootte = 0

        self.laatste_woord = ""

        

        self.login_scherm()



    def clear_screen(self):

        for widget in self.root.winfo_children(): widget.destroy()



    def maak_putsie_balk(self):

        frame = tk.Frame(self.root, bg="#ffeb3b", pady=5)

        frame.pack(fill="x")

        self.label_putsie = tk.Label(frame, text="Putsie: Welkom in Putsie World!", font=("Arial", 10, "italic"), bg="#ffeb3b")

        self.label_putsie.pack(side="left", padx=10)

        tk.Button(frame, text="🔍 Zoek Hint (€50)", command=self.zoek_hint, bg="#ff9800").pack(side="right", padx=10)



    def zoek_hint(self):

        if self.geld >= 50 and self.laatste_woord:

            self.geld -= 50; self.save_stats()

            betekenis = self.woorden_lijst.get(self.laatste_woord, "Geen details.")

            self.label_putsie.config(text=f"Putsie: Hint: '{betekenis[:10]}...'")

        else: self.label_putsie.config(text="Putsie: Te weinig geld of geen vraag actief!")



    # --- DATABEHEER ---

    def laad_data(self):

        self.woorden_lijst = {}; self.werkwoorden_lijst = {}

        if os.path.exists(self.user_words_file):

            with open(self.user_words_file, "r", encoding="utf-8") as f:

                for regel in f:

                    d = regel.strip().split(";")

                    if len(d) == 2: self.woorden_lijst[d[0]] = d[1]

                    elif len(d) == 7: self.werkwoorden_lijst[d[0]] = d[1:]

        if os.path.exists(self.user_stats_file):

            with open(self.user_stats_file, "r", encoding="utf-8") as f:

                line = f.read().split(";")

                if len(line) >= 2: self.geld, self.land_grootte = int(line[0]), int(line[1])



    def save_stats(self):

        with open(self.user_stats_file, "w", encoding="utf-8") as f: f.write(f"{self.geld};{self.land_grootte}")



    # --- HOOFDMENU ---

    def hoofdmenu(self):

        self.clear_screen(); self.maak_putsie_balk()

        tk.Label(self.root, text=f"💰 Saldo: €{self.geld} | 🗺️ Land: {self.land_grootte} km²", font=("Arial", 18, "bold")).pack(pady=20)

        

        # Quizzen

        tk.Button(self.root, text="Woord Quiz", width=30, command=self.start_woord_quiz).pack(pady=5)

        tk.Button(self.root, text="AI Zin Quiz", width=30, command=self.start_zin_quiz).pack(pady=5)

        tk.Button(self.root, text="Werkwoord Quiz", width=30, command=self.start_werkwoord_quiz).pack(pady=5)

        tk.Button(self.root, text="Studie Modus", width=30, command=self.start_studie_modus).pack(pady=5)

        tk.Button(self.root, text="Toevoegen", width=30, command=self.toevoegen_menu).pack(pady=5)

        

        # Land uitbreiden - Duidelijk zichtbaar

        tk.Label(self.root, text="--------------------------------").pack(pady=10)

        tk.Button(self.root, text="🏰 Koop Land (+10 km² voor €500)", width=40, bg="#8BC34A", fg="white", font=("Arial", 10, "bold"), command=self.koop_land).pack(pady=10)



    def koop_land(self):

        if self.geld >= 500:

            self.geld -= 500

            self.land_grootte += 10

            self.save_stats()

            messagebox.showinfo("Gefeliciteerd!", "Je koninkrijk is gegroeid!")

            self.hoofdmenu()

        else:

            messagebox.showwarning("Te weinig geld", "Je hebt €500 nodig om land te kopen.")



    # --- HULP FUNCTIES (QUIZZEN/FLASHCARDS/ETC) ---

    def start_zin_quiz(self):

        self.clear_screen(); self.maak_putsie_balk()

        zin = "La pomme est rouge"

        tk.Label(self.root, text=f"Vertaal deze zin: {zin}").pack()

        e = tk.Entry(self.root); e.pack()

        tk.Button(self.root, text="Check", command=lambda: self.check_zin(zin, e.get())).pack()



    def check_zin(self, zin, poging):

        vertaling = self.translator.translate(zin, src='fr', dest='nl').text

        if poging.lower() == vertaling.lower(): self.geld += 200; self.save_stats(); messagebox.showinfo("Goed!", "+€200")

        self.hoofdmenu()



    def start_studie_modus(self):

        if not self.woorden_lijst: return

        self.toon_flashcard(list(self.woorden_lijst.items()), 0)



    def toon_flashcard(self, woorden, index):

        if index >= len(woorden): self.hoofdmenu(); return

        self.clear_screen(); self.maak_putsie_balk()

        fr, nl = woorden[index]

        tk.Label(self.root, text=f"Frans: {fr}", font=("Arial", 20)).pack(pady=20)

        lbl_n = tk.Label(self.root, text="???", font=("Arial", 16))

        lbl_n.pack(pady=20)

        tk.Button(self.root, text="Omdraaien", command=lambda: lbl_n.config(text=f"NL: {nl}")).pack()

        tk.Button(self.root, text="Volgende", command=lambda: self.toon_flashcard(woorden, index + 1)).pack()

        tk.Button(self.root, text="Stoppen & Terug", command=self.hoofdmenu, fg="red").pack(pady=20)



    def start_woord_quiz(self):

        if not self.woorden_lijst: return

        self.clear_screen(); self.maak_putsie_balk()

        w = random.choice(list(self.woorden_lijst.keys()))

        self.laatste_woord = w

        tk.Label(self.root, text=f"Vertaal: {w}").pack()

        e = tk.Entry(self.root); e.pack()

        tk.Button(self.root, text="Check", command=lambda: self.check_w(w, e.get())).pack()



    def check_w(self, w, p):

        if p.strip().lower() == self.woorden_lijst[w]: self.geld += 100; self.save_stats()

        self.hoofdmenu()



    def start_werkwoord_quiz(self):

        if not self.werkwoorden_lijst: return

        self.clear_screen(); self.maak_putsie_balk()

        inf = random.choice(list(self.werkwoorden_lijst.keys()))

        self.laatste_woord = inf

        correct = self.werkwoorden_lijst[inf]

        tk.Label(self.root, text=f"Vervoeg {inf}").pack()

        entries = {p: tk.Entry(self.root) for p in ["je", "tu", "il", "nous", "vous", "ils"]}

        for p, e in entries.items(): tk.Label(self.root, text=p).pack(); e.pack()

        tk.Button(self.root, text="Check", command=lambda: self.check_wk(correct, entries)).pack()



    def check_wk(self, correct, entries):

        if all(entries[p].get().lower() == correct[i].lower() for i, p in enumerate(["je", "tu", "il", "nous", "vous", "ils"])):

            self.geld += 300; self.save_stats()

        self.hoofdmenu()



    # --- LOGIN & TOEVOEGEN ---

    def login_scherm(self):

        self.clear_screen()

        tk.Label(self.root, text="🌍 Putsie World", font=("Arial", 30)).pack(pady=50)

        self.entry_user = tk.Entry(self.root); self.entry_user.pack()

        tk.Button(self.root, text="Start", command=self.verwerk_login).pack()



    def verwerk_login(self):

        self.username = self.entry_user.get().strip().lower()

        self.user_words_file = f"woorden_{self.username}.txt"

        self.user_stats_file = f"stats_{self.username}.txt"

        self.laad_data(); self.hoofdmenu()



    def toevoegen_menu(self):

        self.clear_screen()

        tk.Button(self.root, text="Voeg Woord toe", command=self.voeg_woord_toe_scherm).pack()

        tk.Button(self.root, text="Voeg Werkwoord toe", command=self.voeg_werkwoord_toe_scherm).pack()

        tk.Button(self.root, text="Terug", command=self.hoofdmenu).pack()



    def voeg_woord_toe_scherm(self):

        self.clear_screen()

        f = tk.Entry(self.root); f.pack(); n = tk.Entry(self.root); n.pack()

        tk.Button(self.root, text="Opslaan", command=lambda: self.save_word(f.get(), n.get())).pack()



    def save_word(self, f, n):

        with open(self.user_words_file, "a", encoding="utf-8") as file: file.write(f"{f.lower()};{n.lower()}\n")

        self.laad_data(); self.hoofdmenu()



    def voeg_werkwoord_toe_scherm(self):

        self.clear_screen()

        self.inf_e = tk.Entry(self.root); self.inf_e.pack()

        self.v_ents = {p: tk.Entry(self.root) for p in ["je", "tu", "il", "nous", "vous", "ils"]}

        for p, e in self.v_ents.items(): tk.Label(self.root, text=p).pack(); e.pack()

        tk.Button(self.root, text="Opslaan", command=self.save_werkwoord).pack()



    def save_werkwoord(self):

        vals = [self.v_ents[p].get() for p in ["je", "tu", "il", "nous", "vous", "ils"]]

        with open(self.user_words_file, "a", encoding="utf-8") as file: file.write(f"{self.inf_e.get()};{';'.join(vals)}\n")

        self.laad_data(); self.hoofdmenu()



if __name__ == "__main__":

    root = tk.Tk(); app = PutsieWorldApp(root); root.mainloop()
