// --- Configuration de base ---
const dayNames = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"];
const TOTAL_JOURS = 5;   // 5 jours de travail dans la semaine
const TOTAL_HEBDO = 35;  // 35 heures par semaine

// Convertit un nombre de minutes (depuis minuit) en format "HH:MM"
function minutesToTime(m) {
  const hours = Math.floor(m / 60);
  const minutes = m % 60;
  return String(hours).padStart(2, '0') + ":" + String(minutes).padStart(2, '0');
}

// Calcule le total d'heures travaillées (en soustrayant 1h si >= 6h)
function calculHeuresTravaillees(horaires) {
  let total = 0;
  horaires.forEach((jour) => {
    let duree = (jour.depart - jour.arrivee) / 60; // conversion en heures
    if (duree >= 6) {
      duree -= 1; // pause déjeuner d'1h
    }
    total += duree;
  });
  return total;
}

// Répartit les heures supplémentaires (extraTotal) sur nbJours restants
// Chaque jour a un créneau obligatoire 09:00 - 15:00 (6h)
function distributionMinimale(extraTotal, nbJours) {
  const suggestions = [];
  for (let i = 0; i < nbJours; i++) {
    if (extraTotal > 0) {
      // Max 5h par jour (2h matin + 3h soir)
      const extraForDay = Math.min(extraTotal, 5);
      extraTotal -= extraForDay;

      let extraMatin = 0;
      let extraSoir = 0;
      if (extraForDay <= 3) {
        extraSoir = extraForDay;
      } else {
        extraSoir = 3;
        extraMatin = extraForDay - 3;
      }

      // 09:00 = 540 min, 15:00 = 900 min
      const arrivee = 540 - extraMatin * 60;
      const depart = 900 + extraSoir * 60;

      suggestions.push({
        arrivee: minutesToTime(arrivee),
        depart: minutesToTime(depart)
      });
    } else {
      // Pas d'extra nécessaire
      suggestions.push({
        arrivee: "09:00",
        depart: "15:00"
      });
    }
  }
  return suggestions;
}

// Met à jour dynamiquement les curseurs selon le nombre de jours déjà travaillés
function updateWorkedDays() {
  const nb = parseInt(document.getElementById("jours_travailles").value) || 0;
  const container = document.getElementById("workedDays");
  container.innerHTML = ""; // On vide le conteneur

  for (let i = 0; i < nb; i++) {
    const div = document.createElement("div");
    div.className = "day-row";
    div.innerHTML = `
      <h3>${dayNames[i] || "Jour " + (i + 1)}</h3>
      <div class="slider-container">
        <label class="slider-label">Arrivée:</label>
        <input type="range" id="arrivee_${i}" min="420" max="540" step="5" value="540"
               oninput="document.getElementById('arr_label_${i}').innerText = minutesToTime(parseInt(this.value))" />
        <span id="arr_label_${i}">${minutesToTime(540)}</span>
      </div>
      <div class="slider-container">
        <label class="slider-label">Départ:</label>
        <input type="range" id="depart_${i}" min="900" max="1080" step="5" value="900"
               oninput="document.getElementById('dep_label_${i}').innerText = minutesToTime(parseInt(this.value))" />
        <span id="dep_label_${i}">${minutesToTime(900)}</span>
      </div>
    `;
    container.appendChild(div);
  }
}

// Calcule les horaires et affiche les suggestions
function calculerHoraires() {
  const joursTravailles = parseInt(document.getElementById("jours_travailles").value) || 0;
  const horaires = [];

  // Récupère les curseurs pour chaque jour déjà travaillé
  for (let i = 0; i < joursTravailles; i++) {
    const arr = parseInt(document.getElementById("arrivee_" + i).value);
    const dep = parseInt(document.getElementById("depart_" + i).value);
    horaires.push({ arrivee: arr, depart: dep });
  }

  // 1) Heures déjà effectuées
  const heuresTravaillees = calculHeuresTravaillees(horaires);

  // 2) Jours restants
  const joursRestants = TOTAL_JOURS - joursTravailles;

  // 3) Heures mandatoires = 6h par jour restant
  const heuresMandatoiresRestantes = joursRestants * 6;

  // 4) Total sans extra
  const totalSansExtra = heuresTravaillees + heuresMandatoiresRestantes;

  // 5) Extra à répartir pour atteindre 35h
  const extraTotal = Math.max(0, TOTAL_HEBDO - totalSansExtra);

  // 6) Propositions d'horaires
  const suggestions = distributionMinimale(extraTotal, joursRestants);

  // 7) Affichage
  const totalRestant = TOTAL_HEBDO - heuresTravaillees;
  let resultHTML = `
    Il vous reste ${totalRestant.toFixed(2)} heures à travailler 
    (en comptant 6h obligatoires par jour restant).<br><br>
    Suggestions pour les jours restants :<br>
  `;
  suggestions.forEach((s, idx) => {
    const nomJour = (joursTravailles + idx < dayNames.length)
      ? dayNames[joursTravailles + idx]
      : "Jour " + (joursTravailles + idx + 1);
    resultHTML += `${nomJour} -> Arrivée : ${s.arrivee}, Départ : ${s.depart}<br>`;
  });

  document.getElementById("result").innerHTML = resultHTML;
}

// On met à jour l'interface dès que l'utilisateur change le nombre de jours
document.getElementById("jours_travailles").addEventListener("change", updateWorkedDays);

// On appelle une première fois au chargement
updateWorkedDays();

// On rend la fonction de conversion accessible pour l'attribut oninput
window.minutesToTime = minutesToTime;
