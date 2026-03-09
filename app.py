import tkinter as tk
from tkinter import messagebox
import random
import os
from googletrans import Translator

class PutsieWorldApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Putsie World - Multi-User")
        self.root.geometry("500x700") # Iets kleiner gemaakt voor overzichtelijkheid
        
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
        for widget in self.root.winfo_children():
            widget.destroy()

    def maak_putsie_balk(self):
        frame = tk.Frame(self.root, bg="#ffeb3b", pady=5)
        frame.pack(fill="x")
        self.label_putsie = tk.Label(frame, text=f"Putsie: Welkom {self.username}!", font=("Arial", 10, "italic"), bg="#ffeb3b")
        self.label_putsie.pack(side="left", padx=10)
        tk.Button(frame, text="🔍 Hint (€50)", command=self.zoek_hint, bg="#ff9800").pack(side="right", padx=10)

    def zoek_hint(self):
        if self.geld >= 50 and self.laatste_woord:
            self.geld -= 50
            self.save_stats()
            betekenis = self.woorden_lijst.get(self.laatste_woord, "Geen details.")
            self.label_putsie.config(text=f"Putsie: Hint: '{betekenis[:3]}...'")
        else:
            messagebox.showwarning("Putsie", "Te weinig geld of geen vraag!")

    # --- DATABEHEER (Maakt automatisch nieuwe bestanden) ---
    def laad_data(self):
        self.woorden_lijst = {}
        self.werkwoorden_lijst = {}
        
        # Maak bestanden aan als ze niet bestaan
        if not os.path.exists(self.user_words_file):
            open(self.user_words_file, "w").close()
        if not os.path.exists(self.user_stats_file):
            with open(self.user_stats_file, "w") as f: f.write("0;0")

        # Lees woorden
        with open(self.user_words_file, "r", encoding="utf-8") as f:
            for regel in f:
                d = regel.strip().split(";")
                if len(d) == 2: self.woorden_lijst[d[0]] = d[1]
                elif len(d) == 7: self.werkwoorden_lijst[d[0]] = d[1:]

        # Lees stats
        with open(self.user_stats_file, "r", encoding="utf-8") as f:
            line = f.read().split(";")
            if len(line) >= 2:
                self.geld = int(line[0])
                self.land_grootte = int(line[1])

    def save_stats(self):
        with open(self.user_stats_file, "w", encoding="utf-8") as f:
            f.write(f"{self.geld};{self.land_grootte}")

    def hoofdmenu(self):
        self.clear_screen()
        self.maak_putsie_balk()
        tk.Label(self.root, text=f"💰 €{self.geld} | 🗺️ {self.land_grootte} km²", font=("Arial", 14, "bold")).pack(pady=10)
        
        tk.Button(self.root, text="Woord Quiz", width=25, command=self.start_woord_quiz).pack(pady=5)
        tk.Button(self.root, text="Werkwoord Quiz", width=25, command=self.start_werkwoord_quiz).pack(pady=5)
        tk.Button(self.root, text="Toevoegen", width=25, command=self.toevoegen_menu, bg="#E1F5FE").pack(pady=5)
        tk.Button(self.root, text="🏰 Koop Land (€500)", width=25, bg="#8BC34A", command=self.koop_land).pack(pady=20)
        tk.Button(self.root, text="Uitloggen", command=self.login_scherm, fg="red").pack(side="bottom", pady=10)

    def koop_land(self):
        if self.geld >= 500:
            self.geld -= 500
            self.land_grootte += 10
            self.save_stats()
            self.hoofdmenu()
        else:
            messagebox.showwarning("Geld", "Je hebt €500 nodig!")

    # --- QUIZ LOGICA ---
    def start_woord_quiz(self):
        if not self.woorden_lijst:
            messagebox.showinfo("Leeg", "Voeg eerst woorden toe!")
            return
        self.clear_screen()
        self.maak_putsie_balk()
        w = random.choice(list(self.woorden_lijst.keys()))
        self.laatste_woord = w
        tk.Label(self.root, text=f"Vertaal naar Frans:\n\n{self.woorden_lijst[w]}", font=("Arial", 12)).pack(pady=20)
        e = tk.Entry(self.root, font=("Arial", 14)); e.pack(pady=10); e.focus_set()
        tk.Button(self.root, text="Check", command=lambda: self.check_w(w, e.get())).pack(pady=10)

    def check_w(self, w, p):
        if p.strip().lower() == w.lower():
            self.geld += 100
            self.save_stats()
            messagebox.showinfo("Top!", "+€100!")
        else:
            messagebox.showerror("Fout", f"Het was: {w}")
        self.hoofdmenu()

    # --- LOGIN ---
    def login_scherm(self):
        self.clear_screen()
        tk.Label(self.root, text="🌍 Putsie World", font=("Arial", 24, "bold")).pack(pady=30)
        tk.Label(self.root, text="Wie ben je?").pack()
        self.entry_user = tk.Entry(self.root, font=("Arial", 12)); self.entry_user.pack(pady=10)
        tk.Button(self.root, text="Start Avontuur", command=self.verwerk_login, width=20, bg="#2196F3", fg="white").pack(pady=10)

    def verwerk_login(self):
        naam = self.entry_user.get().strip().lower()
        if not naam: return
        self.username = naam
        self.user_words_file = f"woorden_{self.username}.txt"
        self.user_stats_file = f"stats_{self.username}.txt"
        self.laad_data()
        self.hoofdmenu()

    def toevoegen_menu(self):
        self.clear_screen()
        tk.Label(self.root, text="Frans woord:").pack()
        f_entry = tk.Entry(self.root); f_entry.pack()
        tk.Label(self.root, text="Nederlandse betekenis:").pack()
        n_entry = tk.Entry(self.root); n_entry.pack()
        tk.Button(self.root, text="Opslaan", command=lambda: self.save_word(f_entry.get(), n_entry.get())).pack(pady=10)
        tk.Button(self.root, text="Terug", command=self.hoofdmenu).pack()

    def save_word(self, f, n):
        if f and n:
            with open(self.user_words_file, "a", encoding="utf-8") as file:
                file.write(f"{f.strip().lower()};{n.strip().lower()}\n")
            self.laad_data()
            messagebox.showinfo("Opgeslagen", "Woord toegevoegd!")
            self.hoofdmenu()

    def start_werkwoord_quiz(self):
        messagebox.showinfo("Info", "Werkwoord-sectie werkt hetzelfde als de woord quiz!")
        self.hoofdmenu()

if __name__ == "__main__":
    root = tk.Tk()
    app = PutsieWorldApp(root)
    root.mainloop()
