import datetime
import tkinter as tk
from tkinter import ttk, messagebox

def calcul_heures_travaillees(horaires):
    """
    Calcule le total d'heures travaillées sur les jours déjà effectués.
    Pour chaque jour, si la durée (entre arrivée et départ) est d'au moins 6 heures,
    on soustrait 1 heure de pause déjeuner.
    Les horaires doivent être au format "HH:MM".
    """
    total = 0
    for jour in horaires:
        arrivee = datetime.datetime.strptime(jour['arrivee'], "%H:%M")
        depart = datetime.datetime.strptime(jour['depart'], "%H:%M")
        diff = (depart - arrivee).seconds / 3600
        if diff >= 6:
            diff -= 1  # pause déjeuner d'1h
        total += diff
    return total

def distribution_minimale(extra_total, nb_jours):
    """
    Répartit de manière concentrée les heures supplémentaires à ajouter sur
    les jours restants pour atteindre le total hebdomadaire de 35 heures.
    
    Chaque jour dispose d'un créneau obligatoire de 9h à 15h (6h).
    Si des heures en extra sont nécessaires, on les affecte en priorité sur
    un jour (max 5h par jour, réparties en 2h maximum le matin et 3h maximum le soir).
    
    Pour un jour donné :
      - Si l'extra nécessaire est ≤ 3, on ajoute tout en fin de journée (départ retardé).
      - Si l'extra est > 3, on complète d'abord 3h en fin de journée et le reste en avance le matin.
    """
    suggestions = []
    for _ in range(nb_jours):
        if extra_total > 0:
            extra_for_day = min(extra_total, 5)  # maximum 5h en extra par jour
            extra_total -= extra_for_day
            if extra_for_day <= 3:
                extra_matin = 0
                extra_soir = extra_for_day
            else:
                extra_soir = 3
                extra_matin = extra_for_day - 3
            arrivee_dt = datetime.datetime.strptime("09:00", "%H:%M") - datetime.timedelta(hours=extra_matin)
            depart_dt  = datetime.datetime.strptime("15:00", "%H:%M") + datetime.timedelta(hours=extra_soir)
            suggestions.append({
                'arrivee': arrivee_dt.time().strftime("%H:%M"),
                'depart': depart_dt.time().strftime("%H:%M")
            })
        else:
            suggestions.append({'arrivee': "09:00", 'depart': "15:00"})
    return suggestions

def minutes_to_time(m):
    hours = m // 60
    minutes = m % 60
    return f"{hours:02d}:{minutes:02d}"

def update_arrival_label(val, idx):
    m = int(float(val))
    labels_arrivee[idx].config(text=minutes_to_time(m))

def update_departure_label(val, idx):
    m = int(float(val))
    labels_depart[idx].config(text=minutes_to_time(m))

def calculer_horaires():
    try:
        jours_travailles = int(jours_travailles_spinbox.get())
    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer un nombre valide pour le nombre de jours déjà travaillés.")
        return
    horaires = []
    for i in range(jours_travailles):
        arr_minutes = scales_arrivee[i].get()  # Valeur en minutes
        dep_minutes = scales_depart[i].get()
        arrival_str = minutes_to_time(arr_minutes)
        departure_str = minutes_to_time(dep_minutes)
        horaires.append({'jour': day_names[i], 'arrivee': arrival_str, 'depart': departure_str})
    try:
        heures_travaillees = calcul_heures_travaillees(horaires)
    except Exception as e:
        messagebox.showerror("Erreur", "Erreur dans la saisie des horaires.")
        return
    
    # Calcul du nombre de jours restants (sur la semaine totale)
    jours_restants = total_jours - jours_travailles
    # En travaillant seulement le créneau obligatoire (9h-15h) sur les jours restants, on aurait :
    heures_mandatoires_restantes = jours_restants * 6
    # Si on ajoute ces heures aux heures déjà effectuées, le total serait :
    total_sans_extra = heures_travaillees + heures_mandatoires_restantes
    # Le nombre d'heures en extra à ajouter sur les jours restants pour atteindre 35h :
    extra_total = max(0, 35 - total_sans_extra)
    
    suggestions = distribution_minimale(extra_total, jours_restants)
    total_restant = 35 - heures_travaillees  # total d'heures à réaliser sur les jours restants (incluant les 6h obligatoires)
    result = "Il vous reste {:.2f} heures à travailler au total sur les jours restants (en comptant les 6h obligatoires par jour).\n".format(total_restant)
    result += "Pour minimiser les heures supplémentaires, voici les suggestions :\n"
    for idx, s in enumerate(suggestions):
        result += "{} -> Arrivée : {}, Départ : {}\n".format(day_names[jours_travailles + idx] if (jours_travailles + idx) < len(day_names) else f"Jour {jours_travailles+idx+1}", s['arrivee'], s['depart'])
    result_text.set(result)

# --- Interface graphique avec curseurs ---
root = tk.Tk()
root.title("Planification des horaires avec curseurs - Minimum Extra")

mainframe = ttk.Frame(root, padding="10")
mainframe.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Titre de la fenêtre
ttk.Label(mainframe, text="Utilisez les curseurs pour définir vos horaires (HH:MM) :").grid(row=0, column=0, columnspan=7, pady=5)

day_names = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
total_jours = 5  # Total des jours de travail dans la semaine

scales_arrivee = []
labels_arrivee = []
scales_depart = []
labels_depart = []

# Création des curseurs pour chaque jour
for i, jour in enumerate(day_names):
    ttk.Label(mainframe, text=jour).grid(row=i+1, column=0, sticky=tk.W)
    
    ttk.Label(mainframe, text="Arrivée:").grid(row=i+1, column=1, sticky=tk.W)
    scale_arr = tk.Scale(mainframe, from_=420, to=540, orient=tk.HORIZONTAL, resolution=5,
                         command=lambda val, idx=i: update_arrival_label(val, idx))
    scale_arr.set(540)  # Par défaut 9:00
    scale_arr.grid(row=i+1, column=2, sticky=tk.W)
    scales_arrivee.append(scale_arr)
    lab_arr = ttk.Label(mainframe, text=minutes_to_time(scale_arr.get()))
    lab_arr.grid(row=i+1, column=3, sticky=tk.W)
    labels_arrivee.append(lab_arr)
    
    ttk.Label(mainframe, text="Départ:").grid(row=i+1, column=4, sticky=tk.W)
    scale_dep = tk.Scale(mainframe, from_=900, to=1080, orient=tk.HORIZONTAL, resolution=5,
                         command=lambda val, idx=i: update_departure_label(val, idx))
    scale_dep.set(900)  # Par défaut 15:00
    scale_dep.grid(row=i+1, column=5, sticky=tk.W)
    scales_depart.append(scale_dep)
    lab_dep = ttk.Label(mainframe, text=minutes_to_time(scale_dep.get()))
    lab_dep.grid(row=i+1, column=6, sticky=tk.W)
    labels_depart.append(lab_dep)

# Saisie du nombre de jours déjà travaillés (0 à 5)
ttk.Label(mainframe, text="Nombre de jours déjà travaillés:").grid(row=7, column=0, columnspan=2, pady=5, sticky=tk.W)
jours_travailles_spinbox = tk.Spinbox(mainframe, from_=0, to=5, width=5)
jours_travailles_spinbox.delete(0, tk.END)
jours_travailles_spinbox.insert(0, "0")
jours_travailles_spinbox.grid(row=7, column=2, sticky=tk.W)
# Pour la suite, on utilisera la variable 'jours_travailles' dans le calcul
def get_jours_travailles():
    try:
        return int(jours_travailles_spinbox.get())
    except ValueError:
        return 0

# Bouton de calcul
calculer_btn = ttk.Button(mainframe, text="Calculer", command=calculer_horaires)
calculer_btn.grid(row=8, column=0, columnspan=2, pady=10)

# Zone d'affichage du résultat
result_text = tk.StringVar()
result_label = ttk.Label(mainframe, textvariable=result_text, foreground="blue")
result_label.grid(row=9, column=0, columnspan=7, sticky=tk.W)

root.mainloop()