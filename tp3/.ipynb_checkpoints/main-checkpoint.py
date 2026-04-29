import streamlit as st
import pandas as pd
import json
import datetime
import os
import pathlib

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  CONFIGURATION — MODIFIEZ ICI AVANT LE CHALLENGE                            ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

SESSION_PASSWORD = "challenge2026"   # ← Changez ce mot de passe

TARGET_CSV_PATH = "/mount/src/cours_itic/tp3/data_test.csv"
TARGET_COLUMN    = "target"          # Colonne cible (1 = fraude, 0 = normal)
ID_COLUMN        = "ID"              # Colonne ID dans data_test.csv

TEAMS    = ["Équipe 1", "Équipe 2", "Équipe 3", "Équipe 4", "Équipe 5"]
MAX_TESTS = 5
TOP_N     = 500
DATA_FILE = "challenge_scores.json"

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  PAGE CONFIG                                                                 ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
st.set_page_config(
    page_title="Fraud Detection Challenge",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  CSS — THÈME CLAIR                                                           ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --bg:            #f0f4ff;
    --surface:       #ffffff;
    --surface2:      #eef2fb;
    --accent:        #2563eb;
    --accent-light:  #dbeafe;
    --green:         #16a34a;
    --green-light:   #dcfce7;
    --danger:        #dc2626;
    --danger-light:  #fee2e2;
    --warn:          #d97706;
    --warn-light:    #fef3c7;
    --purple:        #7c3aed;
    --purple-light:  #ede9fe;
    --text:          #1e293b;
    --muted:         #64748b;
    --border:        #e2e8f0;
    --shadow:        0 1px 3px rgba(0,0,0,0.07), 0 4px 16px rgba(0,0,0,0.04);
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
[data-testid="stToolbar"] { display: none; }
.stApp { background: var(--bg) !important; }

/* Hero */
.hero { text-align:center; padding:2.5rem 1rem 1.5rem; }
.hero-badge {
    display:inline-block; background:var(--accent-light); color:var(--accent);
    font-size:0.68rem; font-weight:700; letter-spacing:3px; text-transform:uppercase;
    padding:6px 18px; border-radius:99px; margin-bottom:1rem;
    font-family:'Space Mono',monospace;
}
.hero-title {
    font-size:2.8rem; font-weight:800; letter-spacing:-1.5px;
    color:var(--text); line-height:1.1; margin-bottom:0.4rem;
}
.hero-title span { color:var(--accent); }
.hero-sub { font-family:'Space Mono',monospace; color:var(--muted); font-size:0.75rem; letter-spacing:2px; }

/* Card */
.card {
    background:var(--surface); border:1px solid var(--border);
    border-radius:16px; padding:1.5rem; margin-bottom:1rem;
    box-shadow:var(--shadow);
}
.card-title {
    font-weight:700; font-size:0.65rem; letter-spacing:3px;
    text-transform:uppercase; color:var(--muted); margin-bottom:1rem;
    display:flex; align-items:center; gap:7px;
}
.card-title::before {
    content:''; display:inline-block; width:14px; height:3px;
    background:var(--accent); border-radius:2px;
}

/* Leaderboard */
.team-row {
    display:flex; align-items:center; gap:1rem; padding:0.85rem 1.1rem;
    border-radius:12px; margin-bottom:0.5rem; border:1.5px solid var(--border);
    background:var(--surface); transition:all 0.18s; box-shadow:var(--shadow);
}
.team-row:hover { border-color:var(--accent); transform:translateX(3px); }
.team-row-leader { border-color:#fbbf24 !important; background:linear-gradient(135deg,#fffbeb,#fef9ee) !important; }
.rank-num { font-family:'Space Mono',monospace; font-size:1.1rem; font-weight:700; width:36px; flex-shrink:0; text-align:center; }
.r1 { color:#d97706; } .r2 { color:#6b7280; } .r3 { color:#92400e; } .rn { color:#cbd5e1; }
.team-name-lb { font-weight:700; font-size:1rem; color:var(--text); flex:1; }
.team-score-lb { font-family:'Space Mono',monospace; font-size:1.55rem; font-weight:700; color:var(--accent); }
.team-score-none { font-family:'Space Mono',monospace; font-size:1.3rem; color:#cbd5e1; }
.team-denom { font-family:'Space Mono',monospace; font-size:0.72rem; color:var(--muted); margin-left:2px; }

/* Badges */
.badge { font-size:0.58rem; font-family:'Space Mono',monospace; padding:3px 9px; border-radius:99px; letter-spacing:1px; text-transform:uppercase; font-weight:700; }
.b-win    { background:#fef9c3; color:#854d0e; border:1px solid #fbbf24; }
.b-tries  { background:var(--purple-light); color:var(--purple); border:1px solid #c4b5fd; }
.b-done   { background:var(--danger-light); color:var(--danger); border:1px solid #fca5a5; }

/* Stat chips */
.stat-row { display:flex; gap:1rem; margin-bottom:1.5rem; flex-wrap:wrap; }
.stat-chip {
    flex:1; min-width:120px; background:var(--surface); border:1px solid var(--border);
    border-radius:14px; padding:1rem 1.25rem; box-shadow:var(--shadow); text-align:center;
}
.stat-num { font-family:'Space Mono',monospace; font-size:2rem; font-weight:700; color:var(--accent); line-height:1; display:block; }
.stat-label { font-size:0.62rem; color:var(--muted); text-transform:uppercase; letter-spacing:2px; margin-top:6px; display:block; }

/* Progress bar */
.pbar-wrap { background:var(--surface2); border-radius:99px; height:6px; overflow:hidden; margin-top:6px; width:80px; }
.pbar-fill { height:100%; border-radius:99px; background:linear-gradient(90deg,var(--accent),#60a5fa); }

/* History rows */
.hist-row {
    display:flex; align-items:center; gap:0.75rem; padding:0.55rem 0.75rem;
    border-radius:8px; font-family:'Space Mono',monospace; font-size:0.75rem;
    border-bottom:1px solid var(--border); color:var(--text);
}
.hist-row:last-child { border-bottom:none; }
.hist-best { background:var(--green-light); border-left:3px solid var(--green); }
.hist-ts { color:var(--muted); flex:1; }
.hist-score { color:var(--green); font-weight:700; }

/* Messages */
.msg {
    border-radius:12px; padding:0.85rem 1.1rem; font-size:0.85rem;
    font-family:'Plus Jakarta Sans',sans-serif; font-weight:500; margin-bottom:1rem;
}
.msg-success { background:var(--green-light);  color:var(--green);  border:1px solid #86efac; }
.msg-error   { background:var(--danger-light); color:var(--danger); border:1px solid #fca5a5; }
.msg-warn    { background:var(--warn-light);   color:var(--warn);   border:1px solid #fcd34d; }
.msg-info    { background:var(--accent-light); color:var(--accent); border:1px solid #93c5fd; }

/* Widgets */
div[data-testid="stSelectbox"] > div > div {
    background:var(--surface) !important; border:1.5px solid var(--border) !important;
    border-radius:10px !important; color:var(--text) !important;
}
div[data-testid="stTextInput"] > div > div > input {
    background:var(--surface) !important; border:1.5px solid var(--border) !important;
    border-radius:10px !important; color:var(--text) !important;
    font-family:'Space Mono',monospace !important; font-size:0.9rem !important;
}
div[data-testid="stTextInput"] > div > div > input:focus {
    border-color:var(--accent) !important;
    box-shadow:0 0 0 3px rgba(37,99,235,0.12) !important;
}
.stButton > button {
    width:100%; background:var(--accent) !important; color:white !important;
    border:none !important; border-radius:10px !important;
    font-family:'Plus Jakarta Sans',sans-serif !important; font-weight:700 !important;
    padding:0.65rem 1.5rem !important; font-size:0.9rem !important;
    transition:all 0.18s !important; box-shadow:0 2px 8px rgba(37,99,235,0.2) !important;
}
.stButton > button:hover {
    background:#1d4ed8 !important; transform:translateY(-1px) !important;
    box-shadow:0 6px 20px rgba(37,99,235,0.3) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background:var(--surface) !important; border-bottom:2px solid var(--border) !important; gap:0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family:'Plus Jakarta Sans',sans-serif !important; font-weight:700 !important;
    color:var(--muted) !important; background:transparent !important;
    padding:0.8rem 1.5rem !important; font-size:0.85rem;
    border-bottom:3px solid transparent !important;
}
.stTabs [aria-selected="true"] { color:var(--accent) !important; border-bottom:3px solid var(--accent) !important; }

/* Expander */
div[data-testid="stExpander"] {
    background:var(--surface) !important; border:1px solid var(--border) !important;
    border-radius:12px !important; box-shadow:var(--shadow) !important; margin-bottom:0.5rem !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background:var(--surface2) !important; border:2px dashed var(--border) !important; border-radius:14px !important;
}
[data-testid="stFileUploader"]:hover { border-color:var(--accent) !important; }
</style>
""", unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  DONNÉES                                                                     ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
def load_scores():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {t: {"tests": [], "best_score": None} for t in TEAMS}

def save_scores(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)

@st.cache_data(show_spinner=False)
def load_target():
    if not os.path.exists(TARGET_CSV_PATH):
        return None, f"Fichier '{TARGET_CSV_PATH}' introuvable. Placez-le dans le même dossier que l'application."
    try:
        df = pd.read_csv(TARGET_CSV_PATH)
    except Exception as e:
        return None, f"Erreur de lecture : {e}"
    if ID_COLUMN not in df.columns:
        return None, f"Colonne '{ID_COLUMN}' absente de '{TARGET_CSV_PATH}'. Colonnes : {list(df.columns)}"
    if TARGET_COLUMN not in df.columns:
        return None, f"Colonne '{TARGET_COLUMN}' absente de '{TARGET_CSV_PATH}'. Colonnes : {list(df.columns)}"
    fraud_ids = set(df.loc[df[TARGET_COLUMN] == 1, ID_COLUMN].astype(int).tolist())
    return fraud_ids, None

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  SESSION STATE                                                               ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
if "scores" not in st.session_state:
    st.session_state.scores = load_scores()
if "flash" not in st.session_state:
    st.session_state.flash = None
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

scores = st.session_state.scores
fraud_ids, target_error = load_target()

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  HERO                                                                        ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
st.markdown("""
<div class="hero">
    <div class="hero-badge">🏆 Machine Learning Challenge</div>
    <div class="hero-title">Fraud <span>Detection</span> Challenge</div>
    <div class="hero-sub">TOP 500 · 5 ÉQUIPES · 5 TESTS MAX PAR ÉQUIPE</div>
</div>
""", unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  TABS                                                                        ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
tab1, tab2, tab3 = st.tabs(["🏆  CLASSEMENT", "🎯  SOUMETTRE UN TEST", "⚙️  ADMIN"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — CLASSEMENT
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("<br>", unsafe_allow_html=True)

    all_tests_count = sum(len(scores[t]["tests"]) for t in TEAMS)
    active_teams    = [t for t in TEAMS if scores[t]["best_score"] is not None]
    best_overall    = max((scores[t]["best_score"] for t in active_teams), default=0)

    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-chip"><span class="stat-num">{len(active_teams)}</span><span class="stat-label">Équipes actives</span></div>
        <div class="stat-chip"><span class="stat-num">{all_tests_count}</span><span class="stat-label">Tests soumis</span></div>
        <div class="stat-chip"><span class="stat-num">{best_overall}</span><span class="stat-label">Meilleur score</span></div>
        <div class="stat-chip"><span class="stat-num">{TOP_N}</span><span class="stat-label">IDs par soumission</span></div>
    </div>
    """, unsafe_allow_html=True)

    sorted_teams = sorted(
        TEAMS,
        key=lambda t: scores[t]["best_score"] if scores[t]["best_score"] is not None else -1,
        reverse=True
    )

    st.markdown('<div class="card-title">CLASSEMENT GÉNÉRAL</div>', unsafe_allow_html=True)
    for i, team in enumerate(sorted_teams):
        rank  = i + 1
        td    = scores[team]
        tries = len(td["tests"])
        best  = td["best_score"]

        emoji    = {1:"🥇",2:"🥈",3:"🥉"}.get(rank, f"#{rank}")
        rank_cls = {1:"r1",2:"r2",3:"r3"}.get(rank, "rn")
        row_cls  = "team-row team-row-leader" if rank==1 and best is not None else "team-row"

        badges = ""
        if rank==1 and best is not None:
            badges += '<span class="badge b-win">👑 Leader</span> '
        if tries >= MAX_TESTS:
            badges += '<span class="badge b-done">Tests épuisés</span>'
        else:
            badges += f'<span class="badge b-tries">{tries}/{MAX_TESTS} tests</span>'

        score_html = (
            f'<span class="team-score-lb">{best}</span><span class="team-denom">/{TOP_N}</span>'
            if best is not None else '<span class="team-score-none">—</span>'
        )
        pct = (best/TOP_N*100) if best else 0
        pbar = f'<div class="pbar-wrap"><div class="pbar-fill" style="width:{pct:.0f}%;"></div></div>' if best else ""

        st.markdown(f"""
        <div class="{row_cls}">
            <span class="rank-num {rank_cls}">{emoji}</span>
            <span class="team-name-lb">{team}</span>
            <div style="display:flex;align-items:center;gap:0.75rem;flex-wrap:wrap;">
                {badges} {pbar} {score_html}
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="card-title">HISTORIQUE DES TESTS</div>', unsafe_allow_html=True)

    if not any(len(scores[t]["tests"]) > 0 for t in TEAMS):
        st.markdown('<div class="msg msg-info">ℹ️ Aucun test soumis pour l\'instant.</div>', unsafe_allow_html=True)
    else:
        for team in sorted_teams:
            td = scores[team]
            if not td["tests"]:
                continue
            with st.expander(f"{team}  ·  {len(td['tests'])} test(s)  ·  Meilleur : {td['best_score'] if td['best_score'] is not None else '—'}"):
                for test in reversed(td["tests"]):
                    is_best  = (test["score"] == td["best_score"])
                    row_cls  = "hist-row hist-best" if is_best else "hist-row"
                    best_bdg = ' <span class="badge b-win">BEST</span>' if is_best else ""
                    st.markdown(f"""
                    <div class="{row_cls}">
                        <span class="hist-ts">{test['timestamp']}</span>
                        <span>Test #{test['test_num']}</span>
                        <span class="hist-score">{test['score']} fraudes</span>
                        {best_bdg}
                    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — SOUMETTRE UN TEST
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("<br>", unsafe_allow_html=True)

    # Flash message
    if st.session_state.flash:
        ftype, ftext = st.session_state.flash
        st.markdown(f'<div class="msg msg-{ftype}">{ftext}</div>', unsafe_allow_html=True)
        st.session_state.flash = None

    if target_error:
        st.markdown(f'<div class="msg msg-error">⚠️ {target_error}</div>', unsafe_allow_html=True)

    col_l, col_r = st.columns([1, 1], gap="large")

    with col_l:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">IDENTIFICATION</div>', unsafe_allow_html=True)
        st.markdown("Appelez le professeur pour obtenir le mot de passe avant de soumettre.")
        st.markdown("<br>", unsafe_allow_html=True)

        team_sel   = st.selectbox("Votre équipe", TEAMS, key="sub_team")
        session_pw = st.text_input("Mot de passe de session", type="password", key="sub_pw",
                                   placeholder="Demandez-le au professeur")

        td_sel    = scores[team_sel]
        remaining = MAX_TESTS - len(td_sel["tests"])
        best_sc   = td_sel["best_score"]
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="msg msg-info" style="font-size:0.8rem;">
            ℹ️ <strong>{team_sel}</strong> — Tests restants : <strong>{remaining}</strong>
            &nbsp;·&nbsp; Meilleur score : <strong>{"—" if best_sc is None else f"{best_sc} fraudes"}</strong>
        </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">FICHIER DE SOUMISSION</div>', unsafe_allow_html=True)
        st.markdown(f"Déposez un fichier CSV avec exactement **{TOP_N} lignes** et une colonne **`ID`**.")
        st.markdown("<br>", unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            f"Fichier CSV — colonne `ID` requise · {TOP_N} lignes exactement",
            type=["csv"],
            key="sub_file"
        )

        file_valid    = False
        submitted_ids = []

        if uploaded_file is not None:
            try:
                df_sub = pd.read_csv(uploaded_file)

                # 1. Vérifier colonne ID
                if "ID" not in df_sub.columns:
                    st.markdown(
                        f'<div class="msg msg-error">✗ Colonne <strong>ID</strong> introuvable.<br>'
                        f'Colonnes détectées : <code>{", ".join(df_sub.columns.tolist())}</code></div>',
                        unsafe_allow_html=True
                    )
                else:
                    n_rows = len(df_sub)

                    # 2. Vérifier nombre de lignes
                    if n_rows != TOP_N:
                        st.markdown(
                            f'<div class="msg msg-error">✗ Votre fichier contient <strong>{n_rows} ligne(s)</strong> '
                            f'— exactement <strong>{TOP_N}</strong> sont requises.</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        # 3. Vérifier que les IDs sont des entiers valides
                        try:
                            parsed_ids = df_sub["ID"].dropna().astype(int).tolist()
                            if len(parsed_ids) != TOP_N:
                                st.markdown(
                                    f'<div class="msg msg-error">✗ Valeurs manquantes ou invalides dans la colonne ID '
                                    f'({len(parsed_ids)} valides sur {TOP_N}).</div>',
                                    unsafe_allow_html=True
                                )
                            else:
                                submitted_ids = parsed_ids
                                file_valid    = True
                                st.markdown(
                                    f'<div class="msg msg-success">✓ Fichier valide — {TOP_N} IDs détectés, prêt à soumettre.</div>',
                                    unsafe_allow_html=True
                                )
                                with st.expander("Aperçu — 5 premiers IDs"):
                                    st.dataframe(df_sub[["ID"]].head(), use_container_width=True, hide_index=True)
                        except Exception:
                            st.markdown(
                                '<div class="msg msg-error">✗ La colonne ID contient des valeurs non numériques.</div>',
                                unsafe_allow_html=True
                            )
            except Exception as e:
                st.markdown(f'<div class="msg msg-error">✗ Impossible de lire le fichier : {e}</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Bouton de soumission ──
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀  LANCER LE TEST", key="submit_btn"):
        errors = []

        if not session_pw:
            errors.append("Mot de passe de session manquant.")
        elif session_pw.strip() != SESSION_PASSWORD:
            errors.append("Mot de passe de session incorrect.")

        if len(scores[team_sel]["tests"]) >= MAX_TESTS:
            errors.append(f"{team_sel} a épuisé ses {MAX_TESTS} tests.")

        if not file_valid or not submitted_ids:
            errors.append("Fichier invalide ou absent — corrigez les erreurs indiquées ci-dessus.")

        if target_error:
            errors.append(f"Impossible d'évaluer : {target_error}")

        if errors:
            st.session_state.flash = ("error", "<br>".join(f"✗ {e}" for e in errors))
            st.rerun()
        else:
            detected = sum(1 for i in submitted_ids if i in fraud_ids)
            td       = scores[team_sel]
            test_num = len(td["tests"]) + 1
            td["tests"].append({
                "test_num":  test_num,
                "score":     detected,
                "timestamp": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            })
            if td["best_score"] is None or detected > td["best_score"]:
                td["best_score"] = detected

            save_scores(scores)
            st.session_state.scores = scores

            total_fraud = len(fraud_ids)
            recall_pct  = detected / total_fraud * 100 if total_fraud else 0
            remaining_after = MAX_TESTS - test_num

            st.session_state.flash = (
                "success",
                f"✅ Test #{test_num} validé pour <strong>{team_sel}</strong> — "
                f"<strong>{detected} fraudes détectées</strong> sur {TOP_N} transactions "
                f"({recall_pct:.1f}% de rappel). "
                f"Tests restants : {remaining_after}."
            )
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ADMIN
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("<br>", unsafe_allow_html=True)

    if not st.session_state.admin_logged:
        col_center = st.columns([1, 2, 1])[1]
        with col_center:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">CONNEXION ADMINISTRATEUR</div>', unsafe_allow_html=True)
            adm_pw = st.text_input("Mot de passe admin", type="password", key="adm_pw_input")
            if st.button("SE CONNECTER", key="adm_login"):
                if adm_pw == SESSION_PASSWORD:
                    st.session_state.admin_logged = True
                    st.rerun()
                else:
                    st.markdown('<div class="msg msg-error">✗ Mot de passe incorrect.</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Statut target
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">STATUT — FICHIER TARGET</div>', unsafe_allow_html=True)
        if target_error:
            st.markdown(f'<div class="msg msg-error">⚠️ {target_error}</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="msg msg-success">✓ <code>{TARGET_CSV_PATH}</code> chargé — '
                f'<strong>{len(fraud_ids)}</strong> transactions frauduleuses indexées.</div>',
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

        # Reset équipes
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">GESTION DES ÉQUIPES</div>', unsafe_allow_html=True)

        col_r1, col_r2 = st.columns(2, gap="large")
        with col_r1:
            team_to_reset = st.selectbox("Équipe à réinitialiser", TEAMS, key="reset_team_sel")
            if st.button(f"🔄 Reset {team_to_reset}", key="reset_one"):
                scores[team_to_reset] = {"tests": [], "best_score": None}
                save_scores(scores)
                st.session_state.scores = scores
                st.markdown(f'<div class="msg msg-success">✓ {team_to_reset} réinitialisée.</div>', unsafe_allow_html=True)
                st.rerun()
        with col_r2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("⚠️ Reset TOUTES les équipes", key="reset_all"):
                st.session_state["confirm_reset"] = True

        if st.session_state.get("confirm_reset"):
            st.markdown('<div class="msg msg-warn">⚠️ Cette action effacera tous les scores. Confirmez ?</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✓ Confirmer", key="confirm_yes"):
                    for t in TEAMS:
                        scores[t] = {"tests": [], "best_score": None}
                    save_scores(scores)
                    st.session_state.scores = scores
                    st.session_state["confirm_reset"] = False
                    st.rerun()
            with c2:
                if st.button("✗ Annuler", key="confirm_no"):
                    st.session_state["confirm_reset"] = False
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Déconnexion", key="adm_logout"):
            st.session_state.admin_logged = False
            st.rerun()