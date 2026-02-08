import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Loi de Hardy-Weinberg - Mission Oiseaux", layout="wide", page_icon="🦅")

# --- FONCTIONS DE CALLBACK ---
def appliquer_fix(n_rr, n_vert):
    st.session_state['pop_RR'] = n_rr
    st.session_state['pop_rr'] = n_vert
    st.session_state['nb_essais'] = 0

# --- INITIALISATION ROBUSTE ---
keys_defaults = {
    'pop_RR': 1500,
    'pop_rr': 1000,
    'nb_essais': 0,
    'last_p_seen': 0.50,
    'etape2': False,
    'history_pheno': [],
    'history_alleles': [],
    'current_gen': 0,
    'current_p': 0.0,
    'show_explication_section': False,
    'show_video': False,
    'history_N500': [],
    'history_N20000': [],
    'gen_N500': 0,
    'gen_N20000': 0,
    'current_p_N500': 0.0,
    'current_p_N20000': 0.0
}

for key, val in keys_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# 2. INTRODUCTION
st.title("🦅 Mission : comprendre la loi de Hardy-Weinberg")
st.markdown("""
Considérons une population d'oiseaux à 3 couleurs gouvernées par 1 gène à 2 allèles **R** et **r**. 
Les oiseaux **bleus** sont **(R//R)**, les **verts** sont **(r//r)** et les **magentas** sont **(R//r)**. 

*Effectif total de la population : **5000 oiseaux**.*
""")

url_base = "https://raw.githubusercontent.com/olivierhoarau97410/SVT_hardy/main/"

col_img1, col_img2, col_img3 = st.columns(3)
with col_img1:
    st.image(url_base + "bleu.png", width=100)
    st.info("**[Bleu]** : (R//R)")
with col_img2:
    st.image(url_base + "magenta.png", width=100)
    st.warning("**[Magenta]** : (R//r)")
with col_img3:
    st.image(url_base + "vert.png", width=100)
    st.success("**[Vert]** : (r//r)")

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
st.info("💡 Modèle de Hardy-Weinberg : $(R//R) = p^2$, $(r//r) = q^2$ et $(R//r) = 2pq$")

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
        "Phénotype": ["[Bleu]", "[Magenta]", "[Vert]"],
        "Réel (Terrain)": [nb_RR_obs, nb_Rr_obs, nb_rr_obs],
        "Théorie ($p^2 / 2pq / q^2$)": [theo_RR, theo_Rr, theo_rr]
    })
    st.table(df_comp)

precision = 80 
matching_reussi = abs(nb_RR_obs - theo_RR) <= precision and abs(nb_rr_obs - theo_rr) <= precision

if matching_reussi:
    st.success("🎯 MATCHING RÉUSSI ! Le modèle mathématique correspond à votre population.")
    if st.button("Lancer la simulation temporelle ⏱️"):
        st.session_state['p_initial'] = p_slider
        st.session_state['current_p'] = (2 * nb_RR_obs + nb_Rr_obs) / 10000
        st.session_state['etape2'] = True
        st.rerun()
else:
    if st.session_state['nb_essais'] > 10:
        st.warning(f"⚠️ Ta population ne semble pas suivre la loi de Hardy-Weinberg.")
        st.button("Fixer ma population sur ces valeurs théoriques 🛠️", on_click=appliquer_fix, args=(theo_RR, theo_rr))

# 5. ÉTAPE 3 : LA SIMULATION (N=5000)
if st.session_state['etape2']:
    st.divider()
    st.header("3. Évolution des fréquences au cours du temps (N=5000)")
    st.markdown("*En effet selon la loi de Hardy Weinberg ces fréquences de phénotypes (bleu, magenta et vert) dépendant des fréquences de p et de q ne doivent pas varier. Simulons des accouplements sur un temps long pour s'en assurer.*")
    
    if not st.session_state['history_pheno']:
        p_init_calc = st.session_state['current_p']
        st.session_state['history_pheno'].extend([
            {"G": 0, "Phéno": "[Bleu]", "N": nb_RR_obs},
            {"G": 0, "Phéno": "[Magenta]", "N": nb_Rr_obs},
            {"G": 0, "Phéno": "[Vert]", "N": nb_rr_obs}
        ])
        st.session_state['history_alleles'].extend([
            {"G": 0, "Allèle": "R (p)", "Freq": p_init_calc},
            {"G": 0, "Allèle": "r (q)", "Freq": 1 - p_init_calc}
        ])

    col_btn1, col_btn2 = st.columns(2)
    steps = 0
    if col_btn1.button("Génération suivante (+1)"): steps = 1
    if col_btn2.button("Accélérer (+10 générations)"): steps = 10

    if steps > 0:
        for _ in range(steps):
            last_p = st.session_state['current_p']
            st.session_state['current_gen'] += 1
            gen = st.session_state['current_gen']
            tirage = np.random.multinomial(5000, [last_p**2, 2*last_p*(1-last_p), (1-last_p)**2])
            new_p = (2 * tirage[0] + tirage[1]) / 10000
            st.session_state['current_p'] = new_p
            st.session_state['history_pheno'].extend([{"G": gen, "Phéno": "[Bleu]", "N": tirage[0]}, {"G": gen, "Phéno": "[Magenta]", "N": tirage[1]}, {"G": gen, "Phéno": "[Vert]", "N": tirage[2]}])
            st.session_state['history_alleles'].extend([{"G": gen, "Allèle": "R (p)", "Freq": new_p}, {"G": gen, "Allèle": "r (q)", "Freq": 1 - new_p}])
        st.rerun()

    df_p = pd.DataFrame(st.session_state['history_pheno'])
    df_a = pd.DataFrame(st.session_state['history_alleles'])
    c1, c2 = st.columns(2)
    # AJUSTEMENT DES TITRES ICI
    c1.plotly_chart(px.line(df_p, x="G", y="N", color="Phéno", title="Stabilité des phénotypes ?", color_discrete_map={"[Bleu]": "blue", "[Magenta]": "magenta", "[Vert]": "green"}), use_container_width=True)
    c2.plotly_chart(px.line(df_a, x="G", y="Freq", color="Allèle", title="Stabilité des allèles ?", range_y=[0, 1]), use_container_width=True)

    if st.session_state['current_gen'] >= 15 and not st.session_state['show_explication_section']:
        st.subheader("🧐 Analyse des résultats")
        reponse = st.radio("**Les fréquences sont-elles parfaitement constantes ?**", ["OUI", "NON, elles oscillent légèrement"], index=None)
        if reponse == "NON, elles oscillent légèrement":
            if st.button("💡 POURQUOI ? (Découvrir l'effet de taille)"):
                st.session_state['show_explication_section'] = True
                st.rerun()

# 6. ÉTAPE 4 : IMPACT DE LA TAILLE
if st.session_state.get('show_explication_section', False):
    st.divider()
    st.header("🔬 4. L'impact de la taille de la population")
    st.info("Attention ici on ne simule que la fréquence des allèles p et q qui sont, respectivement, les fréquence de l'allèle R et r.")
    
    

    p_init = st.session_state.get('p_initial', 0.5)
    
    if st.session_state['gen_N500'] == 0: st.session_state['current_p_N500'] = p_init
    if st.session_state['gen_N20000'] == 0: st.session_state['current_p_N20000'] = p_init

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Simuler 20 gén. (N=500)"):
            for _ in range(20):
                st.session_state['gen_N500'] += 1
                cp = st.session_state['current_p_N500']
                cp = max(0, min(1, cp))
                tir = np.random.multinomial(500, [cp**2, 2*cp*(1-cp), (1-cp)**2])
                new_p = (2*tir[0]+tir[1])/1000
                st.session_state['current_p_N500'] = new_p
                st.session_state['history_N500'].append({"G": st.session_state['gen_N500'], "Allèle": "p (R)", "Freq": new_p})
                st.session_state['history_N500'].append({"G": st.session_state['gen_N500'], "Allèle": "q (r)", "Freq": 1-new_p})
            st.rerun()
        if st.session_state['history_N500']:
            df500 = pd.DataFrame(st.session_state['history_N500'])
            fig500 = px.line(df500, x="G", y="Freq", color="Allèle", range_y=[0,1], title="Dérive forte (N=500)",
                             color_discrete_map={"p (R)": "red", "q (r)": "blue"})
            st.plotly_chart(fig500, use_container_width=True)

    with c2:
        if st.button("Simuler 20 gén. (N=20000)"):
            for _ in range(20):
                st.session_state['gen_N20000'] += 1
                cp = st.session_state['current_p_N20000']
                cp = max(0, min(1, cp))
                tir = np.random.multinomial(20000, [cp**2, 2*cp*(1-cp), (1-cp)**2])
                new_p = (2*tir[0]+tir[1])/40000
                st.session_state['current_p_N20000'] = new_p
                st.session_state['history_N20000'].append({"G": st.session_state['gen_N20000'], "Allèle": "p (R)", "Freq": new_p})
                st.session_state['history_N20000'].append({"G": st.session_state['gen_N20000'], "Allèle": "q (r)", "Freq": 1-new_p})
            st.rerun()
        if st.session_state['history_N20000']:
            df20k = pd.DataFrame(st.session_state['history_N20000'])
            fig20k = px.line(df20k, x="G", y="Freq", color="Allèle", range_y=[0,1], title="Stabilité forte (N=20000)",
                              color_discrete_map={"p (R)": "green", "q (r)": "blue"})
            st.plotly_chart(fig20k, use_container_width=True)

    if st.session_state['gen_N500'] > 0 and st.session_state['gen_N20000'] > 0:
        choix_d = st.radio("**Où la loi de Hardy-Weinberg est-elle la mieux respectée ?**", ["Dans la petite population", "Dans la grande population"], index=None)
        if choix_d == "Dans la grande population":
            st.success("Bravo ! Plus la population est grande, moins la dérive génétique se fait sentir.")
            if st.button("Comprendre la constance des fréquences si effectif grand"):
                st.session_state['show_video'] = True
                st.rerun()

# 7. CONCLUSION & QUIZ
if st.session_state.get('show_video', False):
    st.divider()
    st.video(url_base + "conclusion.mp4")
    
    st.subheader("📝 Petit Quiz de fin")
    quiz_q = "Selon la loi de Hardy Weinberg les fréquences alléliques ne varient pas (donc les phénotypes bleu, magenta et vert, non plus) car la population est :"
    options = [
        "de grande taille ce qui garantit le HASARD des fécondations",
        "de petite taille ce qui garantit le HASARD des fécondations"
    ]
    
    choix_quiz = st.radio(quiz_q, options, index=None)
    
    if choix_quiz == options[0]:
        st.success("✅ Bonne réponse !")
        st.balloons()
        st.markdown("---")
        st.header("📌 BILAN")
        st.info("**Dans une population à l'équilibre où les fréquences de phénotypes dépendent des fréquences $p^2$, $2pq$ et $q^2$, il n'y a pas de variation si la population est grande, ce qui permet de garantir que les gamètes se rencontrent AU HASARD.**")
    elif choix_quiz == options[1]:
        st.error("❌ Ce n'est pas tout à fait ça... Dans une petite population, le hasard du tirage (la dérive génétique) fait varier les fréquences très vite !")

# Sidebar Reset
st.sidebar.divider()
if st.sidebar.button("Réinitialiser l'exercice 🔄"):
    st.session_state.clear()
    st.rerun()