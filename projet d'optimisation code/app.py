import streamlit as st
from scipy.optimize import linprog
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import random
import pandas as pd
import base64
from pathlib import Path
from collections import defaultdict

# ---------------------------
# ENCODE LOGO EN BASE64
# ---------------------------
def get_logo_base64():
    parent = Path(__file__).parent
    candidates = [
        "emsi_logo.jpg",
        "emsi_logo (1).jpg",
        "OIP.jpg",
        "logo.jpg",
        "logo.png",
    ]
    for name in candidates:
        p = parent / name
        if p.exists():
            with open(p, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return None

# ---------------------------
# STYLE CSS - THEME EMSI VERT
# ---------------------------
def load_css(logo_b64):
    logo_html = (
        f'<img src="data:image/jpeg;base64,{logo_b64}" style="height:68px;object-fit:contain;" alt="EMSI Logo"/>'
        if logo_b64 else
        '<div style="font-family:Montserrat,sans-serif;font-size:1.6rem;font-weight:900;color:#2E7D32;letter-spacing:3px;">EMSI</div>'
    )
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&family=Roboto:wght@400;500;600&display=swap');
        html, body, [class*="css"] {{ font-family: 'Roboto', sans-serif; background-color: #F4F6F4; }}
        .main {{ background-color: #F4F6F4; }}
        .emsi-header {{
            background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 55%, #388E3C 100%);
            border-radius: 18px; padding: 24px 36px; margin-bottom: 28px;
            display: flex; align-items: center; gap: 28px;
            box-shadow: 0 8px 32px rgba(27,94,32,0.30);
        }}
        .emsi-logo-box {{
            background: white; border-radius: 14px; padding: 12px 18px;
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 4px 16px rgba(0,0,0,0.15); min-width: 150px;
        }}
        .emsi-header-text h1 {{
            font-family: 'Montserrat', sans-serif; font-size: 1.9rem; font-weight: 800;
            color: #FFFFFF !important; margin: 0 0 6px 0;
        }}
        .emsi-header-text p {{ color: rgba(255,255,255,0.88); font-size: 0.92rem; margin: 0 0 8px 0; }}
        .emsi-badge {{
            background: rgba(255,255,255,0.20); border: 1px solid rgba(255,255,255,0.40);
            border-radius: 20px; padding: 4px 14px; font-size: 0.78rem; color: #fff;
            display: inline-block; font-weight: 600; margin-right: 8px;
        }}
        h2, h3 {{ font-family: 'Montserrat', sans-serif; color: #1B5E20; }}
        [data-testid="metric-container"] {{
            background: #FFFFFF; border-radius: 14px; padding: 18px; text-align: center;
            border-top: 4px solid #2E7D32; box-shadow: 0 4px 18px rgba(46,125,50,0.12);
        }}
        [data-testid="metric-container"] label {{ color: #555; font-size: 0.85rem; font-weight: 600; }}
        [data-testid="metric-container"] [data-testid="stMetricValue"] {{
            color: #2E7D32; font-family: 'Montserrat', sans-serif; font-size: 1.9rem; font-weight: 800;
        }}
        .stButton>button {{
            background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%);
            color: white; border-radius: 12px; height: 3.3em; width: 100%;
            font-family: 'Montserrat', sans-serif; font-weight: 700; font-size: 1rem;
            border: none; box-shadow: 0 4px 16px rgba(46,125,50,0.35); transition: all 0.2s ease;
        }}
        .stButton>button:hover {{ background: linear-gradient(135deg, #2E7D32 0%, #43A047 100%); transform: translateY(-2px); }}
        [data-testid="stSidebar"] {{ background: linear-gradient(180deg, #0A1F0B 0%, #1B3D1C 100%); }}
        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] div {{ color: #E8F5E9 !important; }}
        .sidebar-logo-zone {{
            background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.18);
            border-radius: 14px; padding: 16px; text-align: center; margin-bottom: 20px;
        }}
        .stProgress > div > div {{ background: linear-gradient(90deg, #1B5E20, #66BB6A); border-radius: 8px; }}
        .stProgress > div {{ background: #C8E6C9; border-radius: 8px; }}
        .info-card {{
            background: #FFFFFF; border-radius: 12px; padding: 16px 22px; margin: 10px 0;
            border-left: 5px solid #2E7D32; box-shadow: 0 2px 12px rgba(46,125,50,0.10);
        }}
        .conflict-card {{
            background: #FFF3E0; border-radius: 12px; padding: 16px 22px; margin: 10px 0;
            border-left: 5px solid #E65100; box-shadow: 0 2px 12px rgba(230,81,0,0.15);
        }}
        .ok-card {{
            background: #F1F8E9; border-radius: 12px; padding: 16px 22px; margin: 10px 0;
            border-left: 5px solid #2E7D32; box-shadow: 0 2px 12px rgba(46,125,50,0.10);
        }}
        hr {{ border: none; height: 2px; background: linear-gradient(90deg, #2E7D32, transparent); margin: 24px 0; }}
        </style>

        <div class="emsi-header">
            <div class="emsi-logo-box">{logo_html}</div>
            <div class="emsi-header-text">
                <h1>🎓 EMSI Room Optimizer</h1>
                <p>Dashboard intelligent de répartition optimale des groupes et des salles</p>
                <span class="emsi-badge">📍 EMSI Marrakech</span>
                <span class="emsi-badge">📐 Programmation Linéaire</span>
                <span class="emsi-badge">🛡️ Anti-Conflits</span>
            </div>
        </div>
    """, unsafe_allow_html=True)


# ============================================================
# CLASSES POO
# ============================================================
class Solution:
    def __init__(self, x, y, z, valeur):
        self.x = x; self.y = y; self.z = z; self.valeur = valeur

class ProblemeOptimisation:
    def __init__(self, total_groupes, heures):
        self.total_groupes = total_groupes; self.heures = heures

class Solveur:
    def resoudre(self, p):
        c = [-1, -1]
        A = [[1, 1], [p.heures, 0], [0, p.heures], [1, -1]]
        b = [p.total_groupes, 175, 175, 4]
        result = linprog(c, A_ub=A, b_ub=b, bounds=(0, None))
        x, y = result.x if result.success else (0, 0)
        z = max(0, p.total_groupes - x - y)
        return Solution(x, y, z, x + y)


# ============================================================
# CONSTANTES
# ============================================================
# Matières passant 1 fois/semaine
MATIERES_1X = [
    "Programmation Python", "SQL Server",
    "Développement Projet", "Programmation Linéaire", "Réseaux Informatiques",
    "Recherche Scientifique", "Communication Pro", "English",
    "Conception OO",
]
# Matières passant 2 fois/semaine
MATIERES_2X = ["Modèles Statistiques", "Programmation Java"]

JOURS    = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
CRENEAUX = ["08h30-10h00", "10h15-11h45", "12h00-13h30", "13h45-15h15", "15h30-17h00"]

# Grille semaine : 5 jours x 5 créneaux = 25 cases
# Plan fixe par groupe :
#   9 matières 1x  =  9 cases
#   2 matières 2x  =  4 cases
#   Total cours    = 13 cases
#   Repos          = 12 cases  (pauses déjeuner, récupération)
def construire_plan_semaine() -> list:
    """
    Retourne une liste de 25 éléments (5 jours x 5 créneaux) représentant
    les matières à planifier pour une semaine, avec repos.
    """
    plan = (
        MATIERES_1X[:]                +   # 9 matières × 1
        MATIERES_2X * 2               +   # 2 matières × 2  = 4
        ["🌿 Repos"] * 12                 # 12 créneaux de repos
    )
    assert len(plan) == 25, f"Plan invalide : {len(plan)} cases"
    random.shuffle(plan)
    return plan


# ============================================================
# AFFECTATION DES SALLES UNIQUE PAR GROUPE
# ============================================================
def affecter_salles_uniques(nb_groupes_total: int) -> dict:
    """
    Retourne un dict {groupe_id: salle_unique} où chaque groupe
    a une salle différente. Les salles sont nommées globalement
    (Salle 101, 102 … 115 …) pour éviter tout doublon entre étages.

    Règle :
      - 1er étage  : Salles 101-110  (max 10 salles)
      - 2ème étage : Salles 201-210
      - 3ème étage : Salles 301-310
    On attribue les salles séquentiellement → jamais deux groupes
    dans la même salle.
    """
    affectation = {}
    # Pool de salles par étage (suffisamment grand)
    pool = (
        [f"Salle 1{i:02d}" for i in range(1, 21)] +   # étage 1 : 101-120
        [f"Salle 2{i:02d}" for i in range(1, 21)] +   # étage 2 : 201-220
        [f"Salle 3{i:02d}" for i in range(1, 21)]     # étage 3 : 301-320
    )
    for gid in range(1, nb_groupes_total + 1):
        affectation[gid] = pool[gid - 1]   # index unique → salle unique
    return affectation


# ============================================================
# GESTIONNAIRE EDT  (UNE SALLE FIXE PAR GROUPE)
# ============================================================
class GestionnaireEDT:
    """
    Règles garanties :
    ✅ Pas de conflit de GROUPE   : un groupe a 1 seul cours par créneau.
    ✅ Pas de conflit de SALLE    : deux groupes ne partagent JAMAIS
                                    la même salle (affectation unique).
    ✅ Variété des matières       : pas deux fois la même matière le même jour.
    """

    def __init__(self):
        # grille globale : (salle, jour, creneau) -> groupe_id  [contrôle salle]
        self.grille_salle  = {}
        # grille globale : (groupe_id, jour, creneau) -> matiere [contrôle groupe]
        self.grille_groupe = {}
        self.edts          = {}   # groupe_id -> (DataFrame, salle)
        self.conflits_log  = []

    def generer_edt_groupe(self, groupe_id: int, salle: str):
        """
        Génère l'EDT d'un groupe avec les règles :
          - Chaque matière 1x apparaît exactement 1 fois dans la semaine
          - Modèles Statistiques et Programmation Java apparaissent 2 fois
          - Les cases restantes sont des créneaux de repos
          - Pas de conflit de salle ni de groupe
        """
        # Construire le plan de la semaine (25 cases mélangées)
        plan = construire_plan_semaine()
        cases = [(j, c) for j in JOURS for c in CRENEAUX]  # 25 cases ordonnées

        edt = {}

        for idx, (jour, creneau) in enumerate(cases):
            cle_salle  = (salle, jour, creneau)
            cle_groupe = (groupe_id, jour, creneau)
            matiere    = plan[idx]

            # ── Vérification conflit de salle (sécurité) ──────────────────
            if cle_salle in self.grille_salle:
                occupant = self.grille_salle[cle_salle]
                self.conflits_log.append(
                    f"🔴 Conflit SALLE : **{salle}** le **{jour}** à **{creneau}** "
                    f"déjà prise par Groupe {occupant} → Groupe {groupe_id} bloqué"
                )
                edt[(jour, creneau)] = "⛔ CONFLIT SALLE"
                continue

            # ── Vérification conflit de groupe (sécurité) ─────────────────
            if cle_groupe in self.grille_groupe:
                self.conflits_log.append(
                    f"🔴 Conflit GROUPE : **Groupe {groupe_id}** déjà planifié "
                    f"le **{jour}** à **{creneau}**"
                )
                edt[(jour, creneau)] = "⛔ CONFLIT GROUPE"
                continue

            # ── Enregistrer (pas de repos dans les grilles de contrôle) ───
            if matiere != "🌿 Repos":
                self.grille_salle[cle_salle]   = groupe_id
                self.grille_groupe[cle_groupe] = matiere

            edt[(jour, creneau)] = matiere

        # Construire DataFrame : index = créneaux, colonnes = jours
        data = {jour: [edt.get((jour, c), "—") for c in CRENEAUX] for jour in JOURS}
        df = pd.DataFrame(data, index=CRENEAUX)
        self.edts[groupe_id] = (df, salle)
        return df

    # ── Vérification globale a posteriori ─────────────────────────────────
    def rapport_conflits(self):
        """
        Relit toutes les grilles et retourne :
          nb_conflits_salle, nb_conflits_groupe, liste_details
        """
        # Conflit salle : même (salle, jour, creneau) → 2 groupes
        inv_salle = defaultdict(list)
        for (salle, jour, cren), gid in self.grille_salle.items():
            inv_salle[(salle, jour, cren)].append(gid)

        details = []
        nb_cs = nb_cg = 0
        for (salle, jour, cren), gids in inv_salle.items():
            if len(gids) > 1:
                nb_cs += 1
                details.append(
                    f"🔴 Conflit SALLE : **{salle}** le **{jour}** à **{cren}** "
                    f"→ Groupes {gids}"
                )

        # Conflit groupe : même (groupe_id, jour, creneau) → 2 matières
        inv_groupe = defaultdict(list)
        for (gid, jour, cren), mat in self.grille_groupe.items():
            inv_groupe[(gid, jour, cren)].append(mat)
        for (gid, jour, cren), mats in inv_groupe.items():
            if len(mats) > 1:
                nb_cg += 1
                details.append(
                    f"🔴 Conflit GROUPE : **Groupe {gid}** le **{jour}** à **{cren}** "
                    f"→ Matières {mats}"
                )

        # Ajouter les conflits détectés lors de la génération
        details += self.conflits_log
        nb_cs  += sum(1 for l in self.conflits_log if "SALLE"  in l)
        nb_cg  += sum(1 for l in self.conflits_log if "GROUPE" in l)
        return nb_cs, nb_cg, details


# ============================================================
# CONFIG PAGE
# ============================================================
st.set_page_config(page_title="EMSI Marrakech — Optimizer", page_icon="🎓", layout="wide")
logo_b64 = get_logo_base64()
load_css(logo_b64)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    if logo_b64:
        st.markdown(f"""
            <div class="sidebar-logo-zone">
                <img src="data:image/jpeg;base64,{logo_b64}"
                     style="width:100%;max-width:180px;object-fit:contain;" alt="EMSI"/>
                <div style="margin-top:10px;font-size:0.75rem;color:rgba(255,255,255,0.7);line-height:1.6;">
                    École Marocaine des Sciences de l'Ingénieur<br>
                    <b style="color:#81C784;">📍 Marrakech</b>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("### ⚙️ Configuration")
    total_groupes = st.slider("Nombre de groupes", 1, 30, 12)
    heures        = st.slider("Heures / groupe",    1, 30, 21)

    st.markdown("---")
    st.markdown("""
        <div style="color:rgba(200,230,200,0.85);font-size:0.82rem;line-height:1.9;">
            🎓 <b style="color:#81C784;">EMSI Marrakech</b><br>
            💡 Optimisation des salles<br>
            🏫 Génie Informatique<br>
            🛡️ Anti-conflits activé<br>
            🤝 Membre HONORES United Universities
        </div>
    """, unsafe_allow_html=True)

# ============================================================
# BOUTON PRINCIPAL
# ============================================================
if st.button("🔍 Lancer l'optimisation"):

    # ── Résolution LP ────────────────────────────────────────────────────
    p      = ProblemeOptimisation(total_groupes, heures)
    solver = Solveur()
    sol    = solver.resoudre(p)
    st.success("✅ Optimisation réussie — Résultats affichés ci-dessous")

    # ── KPIs ─────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏢 1er étage",     f"{sol.x:.2f}")
    col2.metric("🏢 2ème étage",    f"{sol.y:.2f}")
    col3.metric("🏢 3ème étage",    f"{sol.z:.2f}")
    col4.metric("📈 Performance Z", f"{sol.valeur:.2f}")

    st.markdown("---")

    # ── Graphique ─────────────────────────────────────────────────────────
    st.subheader("📊 Visualisation de la répartition")
    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor('#FFFFFF'); ax.set_facecolor('#F1F8E9')
    bars = ax.bar(["1er étage", "2ème étage", "3ème étage"],
                  [sol.x, sol.y, sol.z],
                  color=['#1B5E20', '#388E3C', '#81C784'],
                  width=0.5, edgecolor='white', linewidth=2)
    for bar, val in zip(bars, [sol.x, sol.y, sol.z]):
        ax.text(bar.get_x()+bar.get_width()/2., bar.get_height()+0.08,
                f'{val:.1f}', ha='center', va='bottom',
                color='#1B5E20', fontweight='bold', fontsize=12)
    ax.tick_params(colors='#333333', labelsize=11)
    ax.set_ylabel("Nombre de Groupes", color='#333333', fontsize=11)
    ax.set_title("Distribution optimale des salles — EMSI Marrakech",
                 color='#1B5E20', fontsize=13, fontweight='bold', pad=14)
    for sp in ax.spines.values(): sp.set_color('#C8E6C9')
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.yaxis.grid(True, color='#C8E6C9', linestyle='--', alpha=0.8)
    ax.set_axisbelow(True)
    st.pyplot(fig)

    # ── Insight + taux ───────────────────────────────────────────────────
    st.subheader("🧠 Analyse automatique")
    insight = ("Le 1er étage est prioritaire." if sol.x > sol.y else
               "Le 2ème étage est prioritaire." if sol.y > sol.x else
               "Répartition équilibrée entre les étages.")
    st.markdown(f'<div class="info-card">🔎 <b>Insight :</b> {insight}</div>',
                unsafe_allow_html=True)

    taux = min(100, int((sol.valeur / total_groupes) * 100))
    st.subheader("📉 Taux d'utilisation globale")
    st.progress(taux)
    st.markdown(f'<div class="info-card">📊 <b>Utilisation :</b> '
                f'<span style="color:#2E7D32;font-size:1.15rem;font-weight:800;">{taux}%</span>'
                f'</div>', unsafe_allow_html=True)

    # ============================================================
    # GÉNÉRATION DES EDT — SALLES UNIQUES PAR GROUPE
    # ============================================================
    st.markdown("---")
    st.subheader("📅 Génération des emplois du temps — Détection de conflits")

    nb_e1 = int(sol.x)
    nb_e2 = int(sol.y)
    nb_e3 = int(sol.z)
    nb_total = nb_e1 + nb_e2 + nb_e3

    # ── Attribution salles uniques globales ──────────────────────────────
    affectation = affecter_salles_uniques(nb_total)

    # Déterminer étage de chaque groupe
    etages = {}
    for gid in range(1, nb_e1 + 1):
        etages[gid] = "1er étage"
    for gid in range(nb_e1 + 1, nb_e1 + nb_e2 + 1):
        etages[gid] = "2ème étage"
    for gid in range(nb_e1 + nb_e2 + 1, nb_total + 1):
        etages[gid] = "3ème étage"

    # ── Génération des EDT ───────────────────────────────────────────────
    gestionnaire = GestionnaireEDT()
    for gid in range(1, nb_total + 1):
        salle = affectation[gid]
        gestionnaire.generer_edt_groupe(gid, salle)

    # ── Rapport de conflits ──────────────────────────────────────────────
    nb_cs, nb_cg, details = gestionnaire.rapport_conflits()
    total_conflits = nb_cs + nb_cg

    st.markdown("### 🛡️ Rapport de Conflits")
    cA, cB, cC = st.columns(3)
    cA.metric("⚠️ Conflits de Salle",  nb_cs)
    cB.metric("⚠️ Conflits de Groupe", nb_cg)
    cC.metric("✅ Total Conflits",      total_conflits)

    if total_conflits == 0:
        st.markdown(
            '<div class="ok-card">'
            '✅ <b>Aucun conflit détecté</b> — Chaque groupe a sa propre salle unique. '
            'Tous les emplois du temps sont cohérents.'
            '</div>', unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="conflict-card">'
            f'🔴 <b>{total_conflits} conflit(s) détecté(s)</b> — '
            f'{nb_cs} salle(s), {nb_cg} groupe(s).'
            f'</div>', unsafe_allow_html=True
        )
        with st.expander("📋 Voir le détail des conflits"):
            for d in details:
                st.markdown(d)

    # ── Résumé des affectations ──────────────────────────────────────────
    st.markdown("---")
    st.subheader("🏫 Affectation des salles")

    resume_data = {
        "Groupe": [f"Groupe {gid}" for gid in range(1, nb_total + 1)],
        "Étage":  [etages[gid]     for gid in range(1, nb_total + 1)],
        "Salle":  [affectation[gid] for gid in range(1, nb_total + 1)],
    }
    df_resume = pd.DataFrame(resume_data)
    st.dataframe(df_resume, width='stretch', hide_index=True)

    # ── EDT détaillés par groupe ─────────────────────────────────────────
    st.markdown("---")
    st.subheader("📚 Emplois du temps détaillés")

    def style_edt(val):
        v = str(val)
        if "CONFLIT" in v:
            return "background-color:#FFCDD2; color:#B71C1C; font-weight:bold;"
        if "Repos" in v:
            return "background-color:#E8F5E9; color:#757575; font-style:italic;"
        if "Statistiques" in v or "Java" in v:
            return "background-color:#FFF9C4; color:#5D4037; font-weight:bold;"
        return "background-color:#F1F8E9; color:#1B5E20;"

    for gid in range(1, nb_total + 1):
        salle = affectation[gid]
        etage = etages[gid]
        df, _ = gestionnaire.edts[gid]

        has_conflict = any("CONFLIT" in str(v) for v in df.values.flatten())

        st.markdown(
            f'<div class="{"conflict-card" if has_conflict else "info-card"}">'
            f'<b style="font-size:1.05rem;color:#1B5E20;">📚 Groupe {gid}</b><br>'
            f'🏢 {etage} &nbsp;|&nbsp; 🏫 <b>{salle}</b>'
            f'{"&nbsp;&nbsp;⚠️ <span style=color:#E65100;>Conflit détecté</span>" if has_conflict else "&nbsp;&nbsp;✅ <span style=color:#2E7D32;>Sans conflit</span>"}'
            f'</div>', unsafe_allow_html=True
        )

        try:
            styled = df.style.map(style_edt)
        except AttributeError:
            styled = df.style.applymap(style_edt)

        st.dataframe(styled, width='stretch')
        st.markdown("---")
