import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Loi de Hardy-Weinberg - Mission Oiseaux", layout="wide", page_icon="🦅")

# --- CSS POUR BOÎTES COLORÉES ET ANIMATIONS ---
st.markdown("""
<style>
@keyframes blink-warning {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

.big-warning-box {
    animation: blink-warning 2s ease-in-out infinite;
    padding: 25px;
    border-radius: 15px;
    border: 4px solid #ff9800;
    background-color: #fff3e0;
    color: #e65100;
    font-size: 1.4em;
    font-weight: bold;
    margin: 20px 0;
    text-align: center;
}

.big-success-box {
    padding: 25px;
    border-radius: 15px;
    border: 4px solid #4caf50;
    background-color: #e8f5e9;
    color: #1b5e20;
    font-size: 1.3em;
    font-weight: bold;
    margin: 20px 0;
}

.attention-box {
    padding: 20px;
    border-radius: 10px;
    border: 3px solid #f44336;
    background-color: #ffebee;
    color: #b71c1c;
    font-size: 1.2em;
    font-weight: bold;
    margin: 15px 0;
}
</style>
""", unsafe_allow_html=True)

# --- FONCTIONS DE CALLBACK ---
def appliquer_fix(n_rr, n_vert):
    """Applique les valeurs théoriques et prépare l'affichage de confirmation"""
    st.session_state['pop_RR'] = n_rr
    st.session_state['pop_rr'] = n_vert
    st.session_state['nb_essais'] = 0
    st.session_state['show_confirmation_fix'] = True

# --- INITIALISATION ROBUSTE ---
keys_defaults = {
    'pop_RR': 1500,
    'pop_rr': 1000,
    'nb_essais': 0,
    'last_p_seen': 0.50,
    'etape2': False,
    'history_pheno_5000': [],
    'history_alleles_5000': [],
    'history_pheno_10000': [],
    'history_alleles_10000': [],
    'current_gen_5000': 0,
    'current_gen_10000': 0,
    'current_p_5000': 0.0,
    'current_p_10000': 0.0,
    'show_explication_section': False,
    'show_video': False,
    'history_N500': [],
    'history_N20000': [],
    'gen_N500': 0,
    'gen_N20000': 0,
    'current_p_N500': 0.0,
    'current_p_N20000': 0.0,
    'show_confirmation_fix': False
}

for key, val in keys_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# 2. INTRODUCTION
st.title("🦅 Mission : comprendre la loi de Hardy-Weinberg")
st.markdown("""
Considérons une population d'oiseaux à 3 **phénotypes** (couleurs) gouvernés par 1 gène à 2 allèles **R** et **r**. 
Les oiseaux **bleus** ont le **génotype (R//R)** (homozygotes dominants), les **verts** sont **(r//r)** (homozygotes récessifs) 
et les **magentas** sont **(R//r)** (hétérozygotes). 

*Effectif total de la population : **5000 oiseaux**.*
""")

url_base = "https://raw.githubusercontent.com/olivierhoarau97410/SVT_hardy/main/"

col_img1, col_img2, col_img3 = st.columns(3)
with col_img1:
    st.image(url_base + "bleu.png", width=100)
    st.info("**[Bleu]** : Génotype (R//R)")
with col_img2:
    st.image(url_base + "magenta.png", width=100)
    st.warning("**[Magenta]** : Génotype (R//r)")
with col_img3:
    st.image(url_base + "vert.png", width=100)
    st.success("**[Vert]** : Génotype (r//r)")

st.divider()

# 3. ÉTAPE 1 : POPULATION INITIALE
st.header("1. Définir votre population initiale")
c_pop = st.columns(3)
with c_pop[0]:
    nb_RR_obs = st.number_input("Nb Bleus (R//R)", 0, 5000, key='pop_RR')
with c_pop[1]:
    nb_rr_obs = st.number_input("Nb Verts (r//r)", 0, 5000, key='pop_rr')
with c_pop[2]:
    nb_Rr_obs = 5000 - (nb_RR_obs + nb_rr_obs)
    if nb_Rr_obs < 0:
        st.error("⚠️ Total > 5000 !")
        nb_Rr_obs = 0
    st.metric("Nb Magentas (R//r)", nb_Rr_obs)

# 4. ÉTAPE 2 : MATCHING THEORIQUE
st.header("2. Mission : Retrouvez le modèle théorique")
st.info("""
💡 **Si votre population suit la loi de Hardy-Weinberg**, on doit pouvoir trouver :
- La fréquence **p** (%) de l'allèle **R**
- La fréquence **q** (%) de l'allèle **r** (avec p + q = 1)

Telles que les effectifs théoriques correspondent aux effectifs observés :
- **(R//R) = p²** (fréquence des bleus)
- **(R//r) = 2pq** (fréquence des magentas)
- **(r//r) = q²** (fréquence des verts)

🎯 **Votre mission** : Ajustez le curseur de p pour faire correspondre la théorie et la réalité !
""")

col_jeu, col_visu = st.columns([1, 1.5])
with col_jeu:
    p_slider = st.slider("Ajustez la fréquence de l'allèle R (p)", 0.0, 1.0, 0.50, step=0.01)
    q_slider = round(1.0 - p_slider, 2)
    st.write(f"Fréquence de l'allèle r (q) = **{q_slider}**")

theo_RR = int((p_slider**2) * 5000)
theo_Rr = int((2 * p_slider * q_slider) * 5000)
theo_rr = int((q_slider**2) * 5000)

if p_slider != st.session_state['last_p_seen']:
    st.session_state['nb_essais'] += 1
    st.session_state['last_p_seen'] = p_slider

with col_visu:
    df_comp = pd.DataFrame({
        "Phénotype": ["[Bleu] (R//R)", "[Magenta] (R//r)", "[Vert] (r//r)"],
        "Réel (Terrain)": [nb_RR_obs, nb_Rr_obs, nb_rr_obs],
        "Théorie (p² / 2pq / q²)": [theo_RR, theo_Rr, theo_rr]
    })
    st.table(df_comp)

precision = 80 
matching_reussi = abs(nb_RR_obs - theo_RR) <= precision and abs(nb_rr_obs - theo_rr) <= precision

# AFFICHAGE DE LA CONFIRMATION SI ON A FIXÉ LES VALEURS
if st.session_state.get('show_confirmation_fix', False):
    st.markdown(f"""
<div class="big-success-box">
    ✅ POPULATION AJUSTÉE POUR SUIVRE HARDY-WEINBERG !
    <br><br>
    <span style="font-size: 0.9em;">
    Vos valeurs initiales ont été remplacées par les valeurs théoriques :<br>
    • Bleus (R//R) : <strong>{nb_RR_obs}</strong> oiseaux<br>
    • Magentas (R//r) : <strong>{nb_Rr_obs}</strong> oiseaux<br>  
    • Verts (r//r) : <strong>{nb_rr_obs}</strong> oiseaux<br><br>
    Avec p = {p_slider:.2f} et q = {q_slider:.2f}<br><br>
    👉 Vous pouvez maintenant poursuivre la simulation ! ⬇️
    </span>
</div>
""", unsafe_allow_html=True)
    st.session_state['show_confirmation_fix'] = False

if matching_reussi:
    st.success("🎯 MATCHING RÉUSSI ! Le modèle mathématique correspond à votre population.")
    
    st.info("""
📊 **Prédiction de Hardy-Weinberg** : Les fréquences alléliques **p** et **q** 
(et donc les phénotypes [Bleu], [Magenta], [Vert]) devraient rester **constantes** 
au fil des générations.

🧬 **Ce que nous allons faire** : Simuler des accouplements aléatoires sur plusieurs générations 
pour créer des descendants et observer si les fréquences de p, q et des phénotypes 
restent vraiment stables dans le temps.

**Testons cette prédiction !** ⬇️
""")
    
    if st.button("🔬 Lancer la simulation temporelle (accouplements et descendants)", type="primary"):
        st.session_state['p_initial'] = p_slider
        st.session_state['current_p'] = (2 * nb_RR_obs + nb_Rr_obs) / 10000
        st.session_state['etape2'] = True
        st.rerun()
else:
    if st.session_state['nb_essais'] > 10:  # CHANGÉ DE 15 À 10
        # Message clignotant en gros
        st.markdown("""
<div class="big-warning-box">
    ⚠️ Votre population observée ne semble pas suivre l'équilibre de Hardy-Weinberg !
</div>
""", unsafe_allow_html=True)
        
        st.info(f"""
💡 **Deux possibilités :**

**Option 1** : Ajustez p et q pour mieux correspondre à vos observations

**Option 2** : Modifiez les effectifs pour qu'ils respectent p² / 2pq / q²

**Avec p = {p_slider:.2f}, les effectifs théoriques de Hardy-Weinberg seraient :**
- Bleus (R//R) : **{theo_RR}** oiseaux
- Magentas (R//r) : **{theo_Rr}** oiseaux  
- Verts (r//r) : **{theo_rr}** oiseaux
""")
        
        # Avertissement en rouge AVANT le bouton
        st.markdown(f"""
<div class="attention-box">
    ⚠️ ATTENTION : Si vous cliquez sur le bouton ci-dessous, VOS valeurs actuelles 
    ({nb_RR_obs} bleus, {nb_Rr_obs} magentas, {nb_rr_obs} verts) seront REMPLACÉES 
    par ces valeurs théoriques !
</div>
""", unsafe_allow_html=True)
        
        st.button("🛠️ Fixer ma population sur ces valeurs théoriques", 
                  on_click=appliquer_fix, 
                  args=(theo_RR, theo_rr),
                  type="secondary")

# 5. ÉTAPE 3 : LA SIMULATION - COMPARAISON N=5000 vs N=10000
if st.session_state['etape2']:
    st.divider()
    st.header("3. Évolution des fréquences au cours du temps")
    st.markdown("""
🧬 **Simulation en cours** : À chaque génération, nous simulons des accouplements aléatoires 
pour produire la génération suivante. 

Nous allons comparer **deux populations de tailles différentes** pour observer l'influence 
de la taille sur la stabilité des fréquences.
""")
    
    # Initialisation des deux populations si pas déjà fait
    if not st.session_state.get('history_pheno_5000'):
        st.session_state['history_pheno_5000'] = []
        st.session_state['history_alleles_5000'] = []
        st.session_state['current_gen_5000'] = 0
        st.session_state['current_p_5000'] = (2 * nb_RR_obs + nb_Rr_obs) / 10000
        
        # Génération 0 pour N=5000
        p_init = st.session_state['current_p_5000']
        st.session_state['history_pheno_5000'].extend([
            {"G": 0, "Phéno": "[Bleu]", "N": nb_RR_obs},
            {"G": 0, "Phéno": "[Magenta]", "N": nb_Rr_obs},
            {"G": 0, "Phéno": "[Vert]", "N": nb_rr_obs}
        ])
        st.session_state['history_alleles_5000'].extend([
            {"G": 0, "Allèle": "R (p)", "Freq": p_init},
            {"G": 0, "Allèle": "r (q)", "Freq": 1 - p_init}
        ])
    
    if not st.session_state.get('history_pheno_10000'):
        st.session_state['history_pheno_10000'] = []
        st.session_state['history_alleles_10000'] = []
        st.session_state['current_gen_10000'] = 0
        st.session_state['current_p_10000'] = (2 * nb_RR_obs + nb_Rr_obs) / 10000
        
        # Génération 0 pour N=10000 (proportions identiques)
        p_init = st.session_state['current_p_10000']
        nb_RR_10k = nb_RR_obs * 2
        nb_Rr_10k = nb_Rr_obs * 2
        nb_rr_10k = nb_rr_obs * 2
        
        st.session_state['history_pheno_10000'].extend([
            {"G": 0, "Phéno": "[Bleu]", "N": nb_RR_10k},
            {"G": 0, "Phéno": "[Magenta]", "N": nb_Rr_10k},
            {"G": 0, "Phéno": "[Vert]", "N": nb_rr_10k}
        ])
        st.session_state['history_alleles_10000'].extend([
            {"G": 0, "Allèle": "R (p)", "Freq": p_init},
            {"G": 0, "Allèle": "r (q)", "Freq": 1 - p_init}
        ])

    col_btn1, col_btn2 = st.columns(2)
    steps = 0
    if col_btn1.button("Génération suivante (+1)", type="primary"): steps = 1
    if col_btn2.button("Accélérer (+10 générations)", type="primary"): steps = 10

    if steps > 0:
        for _ in range(steps):
            # Simulation N=5000
            last_p_5k = st.session_state['current_p_5000']
            st.session_state['current_gen_5000'] += 1
            gen_5k = st.session_state['current_gen_5000']
            tirage_5k = np.random.multinomial(5000, [last_p_5k**2, 2*last_p_5k*(1-last_p_5k), (1-last_p_5k)**2])
            new_p_5k = (2 * tirage_5k[0] + tirage_5k[1]) / 10000
            st.session_state['current_p_5000'] = new_p_5k
            st.session_state['history_pheno_5000'].extend([
                {"G": gen_5k, "Phéno": "[Bleu]", "N": tirage_5k[0]}, 
                {"G": gen_5k, "Phéno": "[Magenta]", "N": tirage_5k[1]}, 
                {"G": gen_5k, "Phéno": "[Vert]", "N": tirage_5k[2]}
            ])
            st.session_state['history_alleles_5000'].extend([
                {"G": gen_5k, "Allèle": "R (p)", "Freq": new_p_5k}, 
                {"G": gen_5k, "Allèle": "r (q)", "Freq": 1 - new_p_5k}
            ])
            
            # Simulation N=10000
            last_p_10k = st.session_state['current_p_10000']
            st.session_state['current_gen_10000'] += 1
            gen_10k = st.session_state['current_gen_10000']
            tirage_10k = np.random.multinomial(10000, [last_p_10k**2, 2*last_p_10k*(1-last_p_10k), (1-last_p_10k)**2])
            new_p_10k = (2 * tirage_10k[0] + tirage_10k[1]) / 20000
            st.session_state['current_p_10000'] = new_p_10k
            st.session_state['history_pheno_10000'].extend([
                {"G": gen_10k, "Phéno": "[Bleu]", "N": tirage_10k[0]}, 
                {"G": gen_10k, "Phéno": "[Magenta]", "N": tirage_10k[1]}, 
                {"G": gen_10k, "Phéno": "[Vert]", "N": tirage_10k[2]}
            ])
            st.session_state['history_alleles_10000'].extend([
                {"G": gen_10k, "Allèle": "R (p)", "Freq": new_p_10k}, 
                {"G": gen_10k, "Allèle": "r (q)", "Freq": 1 - new_p_10k}
            ])
        st.rerun()

    # Affichage des graphiques
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("#### Population de N=5000")
        df_a_5k = pd.DataFrame(st.session_state['history_alleles_5000'])
        fig_5k = px.line(df_a_5k, x="G", y="Freq", color="Allèle", 
                         title="Évolution des fréquences alléliques", 
                         range_y=[0, 1])
        st.plotly_chart(fig_5k, use_container_width=True)
    
    with c2:
        st.markdown("#### Population de N=10000")
        df_a_10k = pd.DataFrame(st.session_state['history_alleles_10000'])
        fig_10k = px.line(df_a_10k, x="G", y="Freq", color="Allèle", 
                          title="Évolution des fréquences alléliques", 
                          range_y=[0, 1])
        st.plotly_chart(fig_10k, use_container_width=True)

    # QUESTION SOUS LES GRAPHIQUES
    if st.session_state['current_gen_5000'] >= 10 and not st.session_state['show_explication_section']:
        st.divider()
        st.subheader("🧐 Analyse des résultats")
        st.markdown("**Observez bien les deux graphiques ci-dessus.**")
        reponse = st.radio("**Les fréquences sont-elles parfaitement stables dans les deux populations ?**", 
                          ["OUI, parfaitement stables", 
                           "NON, elles oscillent légèrement dans les DEUX populations",
                           "NON, elles oscillent PLUS dans la petite population (N=5000)"], 
                          index=None)
        if reponse == "NON, elles oscillent PLUS dans la petite population (N=5000)":
            st.success("✅ Excellent ! Vous avez bien observé l'effet de la taille de population !")
            if st.button("💡 Aller plus loin : Comparer avec des populations encore plus différentes"):
                st.session_state['show_explication_section'] = True
                st.rerun()
        elif reponse and reponse != "NON, elles oscillent PLUS dans la petite population (N=5000)":
            st.warning("🤔 Regardez bien : les oscillations sont-elles identiques dans les deux graphiques ?")

# 6. ÉTAPE 4 : IMPACT DE LA TAILLE
if st.session_state.get('show_explication_section', False):
    st.divider()
    st.header("🔬 4. L'impact de la taille de la population")
    st.info("""
🧬 **Dérive génétique** : Dans une **petite population**, le hasard de l'échantillonnage 
(qui se reproduit avec qui ?) crée des **fluctuations aléatoires** des fréquences alléliques.

Plus la population est **grande**, plus ces fluctuations sont **faibles**.

**Attention** : Ici on ne simule que les fréquences des allèles **p** (R) et **q** (r).
""")
    
    p_init = st.session_state.get('p_initial', 0.5)
    
    if st.session_state['gen_N500'] == 0: 
        st.session_state['current_p_N500'] = p_init
    if st.session_state['gen_N20000'] == 0: 
        st.session_state['current_p_N20000'] = p_init

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Simuler 20 générations (N=500)"):
            for _ in range(20):
                st.session_state['gen_N500'] += 1
                cp = st.session_state['current_p_N500']
                cp = max(0, min(1, cp))
                tir = np.random.multinomial(500, [cp**2, 2*cp*(1-cp), (1-cp)**2])
                new_p = (2*tir[0]+tir[1])/1000
                st.session_state['current_p_N500'] = new_p
                st.session_state['history_N500'].append({
                    "G": st.session_state['gen_N500'], 
                    "Allèle": "p (R)", 
                    "Freq": new_p
                })
                st.session_state['history_N500'].append({
                    "G": st.session_state['gen_N500'], 
                    "Allèle": "q (r)", 
                    "Freq": 1-new_p
                })
            st.rerun()
        if st.session_state['history_N500']:
            df500 = pd.DataFrame(st.session_state['history_N500'])
            fig500 = px.line(df500, x="G", y="Freq", color="Allèle", range_y=[0,1], 
                             title="🌊 Dérive forte (N=500) - Fluctuations importantes",
                             color_discrete_map={"p (R)": "red", "q (r)": "blue"})
            st.plotly_chart(fig500, use_container_width=True)

    with c2:
        if st.button("Simuler 20 générations (N=20000)"):
            for _ in range(20):
                st.session_state['gen_N20000'] += 1
                cp = st.session_state['current_p_N20000']
                cp = max(0, min(1, cp))
                tir = np.random.multinomial(20000, [cp**2, 2*cp*(1-cp), (1-cp)**2])
                new_p = (2*tir[0]+tir[1])/40000
                st.session_state['current_p_N20000'] = new_p
                st.session_state['history_N20000'].append({
                    "G": st.session_state['gen_N20000'], 
                    "Allèle": "p (R)", 
                    "Freq": new_p
                })
                st.session_state['history_N20000'].append({
                    "G": st.session_state['gen_N20000'], 
                    "Allèle": "q (r)", 
                    "Freq": 1-new_p
                })
            st.rerun()
        if st.session_state['history_N20000']:
            df20k = pd.DataFrame(st.session_state['history_N20000'])
            fig20k = px.line(df20k, x="G", y="Freq", color="Allèle", range_y=[0,1], 
                              title="📊 Stabilité forte (N=20000) - Hardy-Weinberg respecté",
                              color_discrete_map={"p (R)": "green", "q (r)": "blue"})
            st.plotly_chart(fig20k, use_container_width=True)

    if st.session_state['gen_N500'] > 0 and st.session_state['gen_N20000'] > 0:
        choix_d = st.radio("**Où la loi de Hardy-Weinberg est-elle la mieux respectée ?**", 
                          ["Dans la petite population (N=500)", 
                           "Dans la grande population (N=20000)"], 
                          index=None)
        if choix_d == "Dans la grande population (N=20000)":
            st.success("✅ Bravo ! Plus la population est grande, moins la dérive génétique se fait sentir.")
            if st.button("📺 Comprendre pourquoi la taille garantit la stabilité"):
                st.session_state['show_video'] = True
                st.rerun()

# 7. CONCLUSION & QUIZ
if st.session_state.get('show_video', False):
    st.divider()
    st.video(url_base + "conclusion.mp4")
    
    st.subheader("📝 Petit Quiz de fin")
    quiz_q = """**Selon la loi de Hardy-Weinberg, les fréquences alléliques 
et phénotypiques restent constantes si :**"""
    options = [
        "La population est GRANDE, ce qui garantit des fécondations ALÉATOIRES (panmixie)",
        "La population est PETITE, ce qui concentre les allèles favorables"
    ]
    
    choix_quiz = st.radio(quiz_q, options, index=None)
    
    if choix_quiz == options[0]:
        st.success("✅ Excellente réponse !")
        st.balloons()
        st.markdown("---")
        st.header("📌 BILAN FINAL")
        st.success("""
**Loi de Hardy-Weinberg** :

Dans une **grande population** où les accouplements se font **au hasard** (panmixie), 
et en l'absence de sélection naturelle, mutations, et migrations, 
les **fréquences alléliques** (p et q) et donc les **fréquences phénotypiques** 
(p², 2pq, q²) restent **constantes** d'une génération à l'autre.

🔬 **Les 5 conditions nécessaires pour que Hardy-Weinberg soit respecté** :
1. **Grande taille de population** (évite la dérive génétique)
2. **Accouplements aléatoires** (panmixie)
3. **Pas de sélection naturelle**
4. **Pas de mutations**
5. **Pas de migrations**

⚠️ **Dans une petite population**, la dérive génétique fait fluctuer les fréquences de manière aléatoire, 
même en l'absence de sélection, mutations ou migrations !
""")
    elif choix_quiz == options[1]:
        st.error("❌ Ce n'est pas tout à fait ça...")
        st.info("""
💡 **Réfléchissez** : Dans une petite population, le hasard du tirage 
(qui se reproduit avec qui) fait varier les fréquences très rapidement. 

C'est ce qu'on appelle la **dérive génétique** !

Dans une **grande population**, ces effets du hasard se compensent et 
les fréquences restent stables.
""")

# Sidebar Reset
st.sidebar.divider()
if st.sidebar.button("🔄 Réinitialiser l'exercice"):
    st.session_state.clear()
    st.rerun()
