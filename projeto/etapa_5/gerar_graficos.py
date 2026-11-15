#!/usr/bin/env python3
"""
Gerador de gráficos científicos (PNG 300 DPI + GIFs) em estilo acadêmico clássico
(fundo branco, tipografia serifada e moldura completa) para a Etapa 4 Visual e Etapa 5.

Todas as figuras são calculadas diretamente sobre os dados reais do projeto:
- data/processed/base_modelagem_diaria.csv
- src/resultados/*.csv e *.json
"""

from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplconfig")

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.colors import LightSource, Normalize
from matplotlib.patches import Polygon
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

_SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = next(
    (p for p in [_SCRIPT_DIR, *_SCRIPT_DIR.parents] if (p / "data" / "processed" / "base_modelagem_diaria.csv").exists()),
    _SCRIPT_DIR.parent,
)
DATA_PATH = ROOT / "data" / "processed" / "base_modelagem_diaria.csv"
GEO_PATH = ROOT / "data" / "processed" / "br_ufs.geojson"
RES_DIR = ROOT / "src" / "resultados"

DIR_ETAPA4 = ROOT / "entrega_oficial" / "projeto" / "etapa_4_visual" / "imagens"
DIR_ETAPA5 = ROOT / "entrega_oficial" / "projeto" / "etapa_5" / "imagens"
OUT_DIRS = [DIR_ETAPA4, DIR_ETAPA5]

UF_PARA_SUB = {
    "PR": "S", "RS": "S", "SC": "S",
    "SP": "SE", "RJ": "SE", "MG": "SE", "ES": "SE", "DF": "SE", "GO": "SE", "MS": "SE", "MT": "SE", "AC": "SE", "RO": "SE",
    "AL": "NE", "BA": "NE", "CE": "NE", "PB": "NE", "PE": "NE", "PI": "NE", "RN": "NE", "SE": "NE",
    "AM": "N", "AP": "N", "MA": "N", "PA": "N", "RR": "N", "TO": "N",
}

# Paleta Acadêmica (Fundo Branco Puro)
BG_FIG = "#FFFFFF"
BG_AX = "#FFFFFF"
BORDER = "#333333"
GRID = "#CBD5E1"
TXT_DARK = "#111827"
TXT_SUB = "#374151"
TXT_AXIS = "#111827"

COR_REAL = "#111827"
COR_RL = "#D97706"
COR_RF = "#1D4ED8"
COR_GB = "#047857"
COR_ERRO = "#B91C1C"
COR_NEUTRO = "#6B7280"
COR_ROXO = "#6D28D9"

SEED = 42
ALVO = "val_cargaenergiamwmed"
SUBSISTEMAS = ["SE", "S", "NE", "N"]
NOMES_SUB = {
    "SE": "Sudeste / Centro-Oeste",
    "S": "Sul",
    "NE": "Nordeste",
    "N": "Norte",
}

CATEGORICAS = ["id_subsistema", "dia_semana", "mes"]
CLIMA = [
    "temp_max",
    "temp_media",
    "temp_min",
    "precipitacao_total",
    "radiacao_global",
    "vento_vel_media",
    "temp_media_lag_1",
    "temp_media_3d",
]
CALENDARIO = ["feriado", "dia_ano", "tendencia"]
DEFASAGENS = ["carga_lag_1", "carga_lag_7", "carga_media_7d"]
TODAS = CATEGORICAS + CLIMA + CALENDARIO + DEFASAGENS


def configurar_estilo() -> None:
    plt.rcParams.update({
        "figure.facecolor": BG_FIG,
        "axes.facecolor": BG_AX,
        "axes.edgecolor": BORDER,
        "axes.linewidth": 0.8,
        "axes.labelcolor": TXT_AXIS,
        "axes.titlecolor": TXT_DARK,
        "xtick.color": TXT_AXIS,
        "ytick.color": TXT_AXIS,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "text.color": TXT_DARK,
        "grid.color": GRID,
        "grid.linestyle": "--",
        "grid.linewidth": 0.6,
        "font.family": "serif",
        "font.serif": ["DejaVu Serif", "Times New Roman", "Times"],
        "mathtext.fontset": "dejavuserif",
        "font.size": 9.5,
        "legend.framealpha": 0.95,
        "legend.edgecolor": "#9CA3AF",
        "savefig.facecolor": BG_FIG,
    })


def fmt_br(valor: float, casas: int = 0) -> str:
    txt = f"{valor:,.{casas}f}"
    return txt.replace(",", "X").replace(".", ",").replace("X", ".")


def estilizar_eixo(ax: plt.Axes, grid_axis: str = "y") -> None:
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(True)
        ax.spines[side].set_color(BORDER)
        ax.spines[side].set_linewidth(0.8)
    if grid_axis:
        ax.grid(True, axis=grid_axis, color=GRID, linestyle="--", linewidth=0.6, alpha=0.75, zorder=0)
    else:
        ax.grid(False)


def _destinos_por_nome(nome: str) -> list[Path]:
    # Etapas 4 e 5 não repetem figuras: 01–02 vão apenas para Etapa 4 Visual; 03–09 vão apenas para Etapa 5
    if nome.startswith(("01", "02")):
        return [DIR_ETAPA4]
    return [DIR_ETAPA5]


def salvar_png(fig: plt.Figure, nome: str, dpi: int = 300) -> None:
    for d in _destinos_por_nome(nome):
        d.mkdir(parents=True, exist_ok=True)
        fig.savefig(d / nome, dpi=dpi, facecolor=BG_FIG, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


def salvar_gif(frames_rgb: list[np.ndarray], nome: str, durations_s: list[float]) -> None:
    pil_frames = [
        Image.fromarray(arr).convert("P", palette=Image.Palette.ADAPTIVE, colors=128)
        for arr in frames_rgb
    ]
    durations_ms = [int(d * 1000) for d in durations_s]
    for d in _destinos_por_nome(nome):
        d.mkdir(parents=True, exist_ok=True)
        pil_frames[0].save(
            d / nome,
            save_all=True,
            append_images=pil_frames[1:],
            duration=durations_ms,
            loop=0,
            optimize=True,
        )


def fig_para_rgb(fig: plt.Figure) -> np.ndarray:
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())
    return buf[:, :, :3].copy()


def carregar_dados() -> dict:
    base = pd.read_csv(DATA_PATH, parse_dates=["event_date"])
    gb_prev = pd.read_csv(RES_DIR / "gb_previsoes_2024.csv", parse_dates=["event_date"])
    rf_prev = pd.read_csv(RES_DIR / "rf_previsoes_2024.csv", parse_dates=["event_date"])
    rl_prev = pd.read_csv(RES_DIR / "rl_previsoes_2024.csv", parse_dates=["event_date"])
    resumo = json.loads((RES_DIR / "resumo_comparativo.json").read_text(encoding="utf-8"))
    met_gb = json.loads((RES_DIR / "metricas_gradient_boosting.json").read_text(encoding="utf-8"))
    met_rf = json.loads((RES_DIR / "metricas_random_forest.json").read_text(encoding="utf-8"))
    met_rl = json.loads((RES_DIR / "metricas_regressao_linear.json").read_text(encoding="utf-8"))

    df24 = gb_prev.merge(
        rf_prev[["id_subsistema", "event_date", "previsto_rf", "previsto_rl_lags"]],
        on=["id_subsistema", "event_date"],
    ).merge(
        rl_prev[["id_subsistema", "event_date", "previsto"]].rename(columns={"previsto": "previsto_rl"}),
        on=["id_subsistema", "event_date"],
    )
    return {
        "base": base,
        "df24": df24,
        "resumo": resumo,
        "met_gb": met_gb,
        "met_rf": met_rf,
        "met_rl": met_rl,
    }


def _construir_gb(max_iter: int = 400, colunas: list[str] | None = None) -> Pipeline:
    cols = TODAS if colunas is None else colunas
    cats = [c for c in cols if c in CATEGORICAS]
    nums = [c for c in cols if c not in CATEGORICAS]
    prep = ColumnTransformer(
        [
            ("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), cats),
            ("num", "passthrough", nums),
        ],
        verbose_feature_names_out=False,
    )
    hgb = HistGradientBoostingRegressor(
        categorical_features=list(range(len(cats))) if cats else None,
        learning_rate=0.03,
        max_iter=max_iter,
        max_leaf_nodes=15,
        min_samples_leaf=10,
        random_state=SEED,
    )
    return Pipeline([
        ("prep", prep),
        ("reg", TransformedTargetRegressor(regressor=hgb, func=np.log, inverse_func=np.exp)),
    ])


# =============================================================================
# 1. COMPARAÇÃO 3D DOS 3 MODELOS (PNG + GIF)
# =============================================================================
def _preparar_superficies_3d(base: pd.DataFrame) -> dict:
    se = base[(base["id_subsistema"] == "SE") & (base["dia_semana"] < 5) & (base["feriado"] == 0)].copy()
    se = se.dropna(subset=["temp_max", "carga_lag_7", ALVO])
    treino = se[se["ano"].between(2016, 2023)].copy()
    teste = se[se["ano"] == 2024].copy()

    cols = ["temp_max", "carga_lag_7"]
    m_rl = LinearRegression().fit(treino[cols], treino[ALVO])
    m_rf = RandomForestRegressor(
        n_estimators=200, max_features=1.0, min_samples_leaf=4, random_state=SEED, n_jobs=-1
    ).fit(treino[cols], treino[ALVO])
    m_gb = HistGradientBoostingRegressor(
        learning_rate=0.04, max_iter=300, max_leaf_nodes=12, min_samples_leaf=8, random_state=SEED
    ).fit(treino[cols], treino[ALVO])

    gx = np.linspace(teste["temp_max"].quantile(0.02), teste["temp_max"].quantile(0.99), 34)
    gy = np.linspace(teste["carga_lag_7"].quantile(0.03), teste["carga_lag_7"].quantile(0.98), 34)
    GX, GY = np.meshgrid(gx, gy)
    grid_df = pd.DataFrame({"temp_max": GX.ravel(), "carga_lag_7": GY.ravel()})

    Z_rl = m_rl.predict(grid_df).reshape(GX.shape) / 1000.0
    Z_rf = m_rf.predict(grid_df).reshape(GX.shape) / 1000.0
    Z_gb = m_gb.predict(grid_df).reshape(GX.shape) / 1000.0

    p_rl = m_rl.predict(teste[cols]) / 1000.0
    p_rf = m_rf.predict(teste[cols]) / 1000.0
    p_gb = m_gb.predict(teste[cols]) / 1000.0

    return {
        "teste": teste,
        "GX": GX,
        "GY": GY / 1000.0,
        "Z_rl": Z_rl,
        "Z_rf": Z_rf,
        "Z_gb": Z_gb,
        "p_rl": p_rl,
        "p_rf": p_rf,
        "p_gb": p_gb,
    }


def _desenhar_eixo_3d(
    ax: plt.Axes,
    dados3d: dict,
    subt: str,
    Z_surf: np.ndarray,
    p_pred: np.ndarray,
    cor_surf: str,
    elev: float,
    azim: float,
) -> None:
    teste = dados3d["teste"]
    x_pts = teste["temp_max"].to_numpy()
    y_pts = teste["carga_lag_7"].to_numpy() / 1000.0
    z_pts = teste[ALVO].to_numpy() / 1000.0
    cores_pts = np.where(
        x_pts >= 31.0,
        "#B91C1C",
        np.where(x_pts >= 26.0, "#D97706", "#1D4ED8"),
    )
    z_min = float(min(z_pts.min(), dados3d["Z_rl"].min()) - 1.5)
    z_max = float(max(z_pts.max(), dados3d["Z_gb"].max()) + 1.5)
    ls = LightSource(azdeg=315, altdeg=45)
    idx_destaque = np.argsort(np.abs(z_pts - dados3d["p_rl"]))[-20:]

    ax.set_facecolor(BG_FIG)
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.set_facecolor((0.98, 0.98, 0.99, 1.0))
        axis.pane.set_edgecolor("#9CA3AF")
        axis._axinfo["grid"]["color"] = GRID
        axis._axinfo["grid"]["linewidth"] = 0.55

    ax.plot_surface(
        dados3d["GX"],
        dados3d["GY"],
        Z_surf,
        color=cor_surf,
        alpha=0.35,
        edgecolor=cor_surf,
        linewidth=0.22,
        antialiased=True,
        shade=True,
        lightsource=ls,
        zorder=1,
    )

    for idx in idx_destaque:
        ax.plot(
            [x_pts[idx], x_pts[idx]],
            [y_pts[idx], y_pts[idx]],
            [p_pred[idx], z_pts[idx]],
            color=COR_ERRO,
            lw=1.25,
            alpha=0.80,
            zorder=3,
        )

    ax.scatter(
        x_pts,
        y_pts,
        z_pts,
        c=cores_pts,
        s=16,
        alpha=0.85,
        edgecolors="#FFFFFF",
        linewidth=0.35,
        depthshade=False,
        zorder=4,
    )

    ax.set_title(subt, fontsize=10.5, pad=6)
    ax.set_xlabel("Temp. máxima (°C)", fontsize=8.3, labelpad=6)
    ax.set_ylabel("Carga t-7 (mil MWmed)", fontsize=8.3, labelpad=6)
    ax.set_zlabel("Carga real (mil MWmed)", fontsize=8.3, labelpad=5)
    ax.set_xlim(23.5, 36.2)
    ax.set_ylim(34.5, 53.5)
    ax.set_zlim(z_min, z_max)
    ax.set_box_aspect((1.0, 1.0, 0.78))
    ax.tick_params(labelsize=7.5)
    ax.view_init(elev=elev, azim=azim)


def _legenda_3d_elementos() -> list:
    return [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#1D4ED8", markersize=6.5, label="Temp. máx. < 26 °C"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#D97706", markersize=6.5, label="Temp. máx. 26–31 °C"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#B91C1C", markersize=6.5, label="Temp. máx. ≥ 31 °C"),
        plt.Line2D([0], [0], color=COR_ERRO, lw=1.4, label="Resíduo vertical (|Real − Previsto|)"),
    ]


def _plotar_3d_comparativo(dados3d: dict, elev: float, azim: float, dpi: int = 300) -> plt.Figure:
    fig = plt.figure(figsize=(14.6, 5.2), dpi=dpi)
    fig.patch.set_facecolor(BG_FIG)
    paineis = [
        ("(a) Regressão Linear", dados3d["Z_rl"], dados3d["p_rl"], "#D97706"),
        ("(b) Random Forest", dados3d["Z_rf"], dados3d["p_rf"], "#2563EB"),
        ("(c) Gradient Boosting", dados3d["Z_gb"], dados3d["p_gb"], "#059669"),
    ]
    for i, (subt, Z_surf, p_pred, cor_surf) in enumerate(paineis, start=1):
        ax = fig.add_subplot(1, 3, i, projection="3d")
        _desenhar_eixo_3d(ax, dados3d, subt, Z_surf, p_pred, cor_surf, elev, azim)

    fig.legend(
        handles=_legenda_3d_elementos(),
        loc="lower center",
        ncol=4,
        frameon=True,
        facecolor="#FFFFFF",
        edgecolor="#9CA3AF",
        fontsize=8.5,
        bbox_to_anchor=(0.5, 0.01),
    )
    fig.subplots_adjust(left=0.02, right=0.98, top=0.92, bottom=0.12, wspace=0.08)
    return fig


def _plotar_3d_unico(
    dados3d: dict,
    titulo_painel: str,
    Z_surf: np.ndarray,
    p_pred: np.ndarray,
    cor_surf: str,
    elev: float,
    azim: float,
    dpi: int = 110,
) -> plt.Figure:
    fig = plt.figure(figsize=(6.8, 5.4), dpi=dpi)
    fig.patch.set_facecolor(BG_FIG)
    ax = fig.add_subplot(1, 1, 1, projection="3d")
    _desenhar_eixo_3d(ax, dados3d, titulo_painel, Z_surf, p_pred, cor_surf, elev, azim)
    fig.legend(
        handles=_legenda_3d_elementos(),
        loc="lower center",
        ncol=2,
        frameon=True,
        facecolor="#FFFFFF",
        edgecolor="#9CA3AF",
        fontsize=8.0,
        bbox_to_anchor=(0.5, 0.015),
    )
    fig.subplots_adjust(left=0.04, right=0.96, top=0.92, bottom=0.16)
    return fig


def gerar_visual_01(dados: dict) -> None:
    dados3d = _preparar_superficies_3d(dados["base"])
    fig_png = _plotar_3d_comparativo(dados3d, elev=25, azim=-135, dpi=300)
    salvar_png(fig_png, "01_comparacao_3d_modelos.png", dpi=300)

    # Remove antigo GIF unificado se existir
    antigo_gif = DIR_ETAPA4 / "01_comparacao_3d_modelos.gif"
    if antigo_gif.exists():
        antigo_gif.unlink()

    # 3 GIFs individuais olhando a encosta frontal da superfície [-165°, -105°]
    # mantendo paredes XYZ e eixo Carga Real fixos no lado esquerdo sem saltos de canvas
    t_curve = np.linspace(0.0, np.pi, 32)
    azins_ida = -165.0 + 60.0 * 0.5 * (1.0 - np.cos(t_curve))
    azins = np.concatenate([azins_ida, azins_ida[-2:0:-1]])
    especs = [
        ("01a_3d_regressao_linear.gif", "(a) Regressão Linear Múltipla", dados3d["Z_rl"], dados3d["p_rl"], "#D97706"),
        ("01b_3d_random_forest.gif", "(b) Random Forest", dados3d["Z_rf"], dados3d["p_rf"], "#2563EB"),
        ("01c_3d_gradient_boosting.gif", "(c) Gradient Boosting", dados3d["Z_gb"], dados3d["p_gb"], "#059669"),
    ]
    for nome_gif, tit_m, Z_m, p_m, cor_m in especs:
        frames = []
        durations = []
        for idx, az in enumerate(azins):
            fig_f = _plotar_3d_unico(dados3d, tit_m, Z_m, p_m, cor_m, elev=25, azim=float(az), dpi=105)
            frames.append(fig_para_rgb(fig_f))
            plt.close(fig_f)
            durations.append(0.65 if idx in (0, len(azins_ida) - 1) else 0.15)
        salvar_gif(frames, nome_gif, durations)
    print("✓ Visual 01 gerado (PNG 300 DPI + 3 GIFs frontais lentos em [-165°, -105°])")


# =============================================================================
# 2. PLACAR GLOBAL DOS MODELOS (PNG 300 DPI)
# =============================================================================
def gerar_visual_02(dados: dict) -> None:
    comp = dados["resumo"]["comparacao_global_2024"]
    ordem_chaves = [
        ("Regressão Linear (clima, sem lags)", "Reg. Linear (sem lags)", COR_RL),
        ("Baseline Ingênuo (carga_lag_7)", "Baseline (lag 7)", COR_NEUTRO),
        ("Random Forest", "Random Forest", COR_RF),
        ("Regressão Linear + Lags (log)", "Reg. Linear + Lags (log)", "#C2410C"),
        ("Gradient Boosting", "Gradient Boosting", COR_GB),
    ]

    labels = [x[1] for x in ordem_chaves][::-1]
    cores = [x[2] for x in ordem_chaves][::-1]
    mapes = [comp[x[0]]["MAPE_%"] for x in ordem_chaves][::-1]
    maes = [comp[x[0]]["MAE"] for x in ordem_chaves][::-1]
    rmses = [comp[x[0]]["RMSE"] for x in ordem_chaves][::-1]
    r2s = [comp[x[0]]["R2"] for x in ordem_chaves][::-1]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.6, 4.6), sharey=True)

    y = np.arange(len(labels))
    for yi, m_val, r2_val, cor in zip(y, mapes, r2s, cores):
        ax1.hlines(yi, 0, m_val, color=cor, lw=2.2, zorder=2)
        ax1.scatter(m_val, yi, color=cor, s=70, zorder=3, edgecolors="#111827", linewidth=0.5)
        ax1.text(
            m_val + 0.22,
            yi,
            f"{fmt_br(m_val, 2)}% (R² = {fmt_br(r2_val, 4)})",
            va="center",
            ha="left",
            fontsize=8.6,
            color=TXT_DARK,
        )

    ax1.set_yticks(y)
    ax1.set_yticklabels(labels, fontsize=9.0)
    ax1.set_xlim(0, 12.2)
    ax1.set_xlabel("MAPE (%)")
    ax1.set_title("(a) MAPE (%) e R² no teste (2024)", fontsize=10.2, loc="left", pad=8)
    estilizar_eixo(ax1, grid_axis="x")

    h = 0.34
    b1 = ax2.barh(y + h / 2, maes, height=h, color="#60A5FA", edgecolor="#1E3A8A", linewidth=0.5, label="MAE (MWmed)", zorder=2)
    b2 = ax2.barh(y - h / 2, rmses, height=h, color="#1E3A8A", edgecolor="#0F172A", linewidth=0.5, label="RMSE (MWmed)", zorder=2)
    for bar, val in zip(b1, maes):
        ax2.text(val + 38, bar.get_y() + bar.get_height() / 2, fmt_br(val, 0), va="center", fontsize=8.2, color=TXT_DARK)
    for bar, val in zip(b2, rmses):
        ax2.text(val + 38, bar.get_y() + bar.get_height() / 2, fmt_br(val, 0), va="center", fontsize=8.2, color=TXT_DARK)

    ax2.set_xlim(0, 3400)
    ax2.xaxis.set_major_formatter(FuncFormatter(lambda x, _: fmt_br(x, 0)))
    ax2.set_xlabel("Erro (MWmed)")
    ax2.set_title("(b) MAE e RMSE no teste (2024)", fontsize=10.2, loc="left", pad=8)
    ax2.legend(loc="lower right", frameon=True, facecolor="#FFFFFF", fontsize=8.5)
    estilizar_eixo(ax2, grid_axis="x")

    fig.subplots_adjust(left=0.18, right=0.98, top=0.90, bottom=0.15, wspace=0.10)
    salvar_png(fig, "02_placar_modelos_2024.png", dpi=300)
    print("✓ Visual 02 gerado (Placar global 2024)")


# =============================================================================
# 3. QUEDA DO ERRO POR SUBSISTEMA (DUMBBELL / SLOPE)
# =============================================================================
def gerar_visual_03(dados: dict) -> None:
    por_sub = dados["resumo"]["mape_por_subsistema_2024"]
    ordem = ["NE", "N", "SE", "S"]

    fig, ax = plt.subplots(figsize=(10.2, 4.4))
    y_pos = np.arange(len(ordem))

    for i, sub in enumerate(ordem):
        v_rl = por_sub[sub]["Regressão Linear (sem lags)"]
        v_rf = por_sub[sub]["Random Forest"]
        v_gb = por_sub[sub]["Gradient Boosting"]

        ax.hlines(i, v_gb, v_rl, color="#9CA3AF", lw=1.8, zorder=1)
        ax.scatter(v_rl, i, color=COR_RL, marker="^", s=85, zorder=4, edgecolors="#111827", linewidth=0.5)
        ax.scatter(v_rf, i, color=COR_RF, marker="s", s=70, zorder=4, edgecolors="#111827", linewidth=0.5)
        ax.scatter(v_gb, i, color=COR_GB, marker="o", s=85, zorder=5, edgecolors="#111827", linewidth=0.5)

        ax.text(v_rl + 0.18, i, f"{fmt_br(v_rl, 2)}%", va="center", ha="left", fontsize=8.6, color=TXT_DARK)
        ax.text(v_gb - 0.18, i, f"{fmt_br(v_gb, 2)}%", va="center", ha="right", fontsize=8.6, color=TXT_DARK)
        ax.text(v_rf, i + 0.16, f"{fmt_br(v_rf, 2)}%", va="bottom", ha="center", fontsize=8.2, color=COR_RF)

    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"{NOMES_SUB[s]} ({s})" for s in ordem], fontsize=9.2)
    ax.set_xlim(0.4, 11.8)
    ax.set_ylim(-0.55, 3.65)
    ax.set_xlabel("MAPE (%) no teste (2024)")
    ax.set_title("Erro percentual (MAPE) por subsistema elétrico em 2024", fontsize=10.5, loc="left", pad=8)
    estilizar_eixo(ax, grid_axis="x")

    leg = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=COR_GB, markeredgecolor="#111827", markersize=7.5, label="Gradient Boosting"),
        plt.Line2D([0], [0], marker="s", color="w", markerfacecolor=COR_RF, markeredgecolor="#111827", markersize=7.0, label="Random Forest"),
        plt.Line2D([0], [0], marker="^", color="w", markerfacecolor=COR_RL, markeredgecolor="#111827", markersize=8.0, label="Reg. Linear (sem lags)"),
    ]
    ax.legend(handles=leg, loc="lower right", frameon=True, facecolor="#FFFFFF", fontsize=8.5)
    fig.subplots_adjust(left=0.23, right=0.97, top=0.89, bottom=0.15)
    salvar_png(fig, "03_queda_erro_subsistemas.png", dpi=300)
    print("✓ Visual 03 gerado (Queda por subsistema)")


# =============================================================================
# 4. ISOLANDO O EFEITO AR-CONDICIONADO (PNG + GIF)
# =============================================================================
def _preparar_curvas_termicas(base: pd.DataFrame, df24: pd.DataFrame) -> dict:
    treino = pd.concat([base[base["ano"] <= 2022], base[base["ano"] == 2023]], ignore_index=True)
    modelo_gb = _construir_gb(max_iter=400).fit(treino[TODAS], treino[ALVO])

    grade_t = np.linspace(14, 32, 37)
    curvas_sub = {}
    for sub in SUBSISTEMAS:
        amostra = df24[(df24["id_subsistema"] == sub) & (df24["dia_semana"] < 5)]
        gt = grade_t[grade_t >= 22] if sub in ("NE", "N") else grade_t
        resp = []
        for tv in gt:
            X_sim = amostra[TODAS].copy()
            X_sim[["temp_media", "temp_media_lag_1", "temp_media_3d"]] = tv
            X_sim["temp_max"] = tv + 5.0
            X_sim["temp_min"] = tv - 5.0
            resp.append(modelo_gb.predict(X_sim).mean())
        resp_arr = np.array(resp)
        curvas_sub[sub] = (gt, (resp_arr / resp_arr[0] - 1.0) * 100.0)

    se24 = df24[df24["id_subsistema"] == "SE"].dropna(subset=["temp_media"]).copy()
    se24["tipo_dia"] = np.where((se24["dia_semana"] >= 5) | (se24["feriado"] == 1), "Fim de semana / feriado", "Dia útil")
    uteis = se24[se24["tipo_dia"] == "Dia útil"].sort_values("temp_media").copy()

    lr_2d = LinearRegression().fit(uteis[["temp_media"]], uteis[ALVO])
    t_grid = np.linspace(uteis["temp_media"].min(), uteis["temp_media"].max(), 80)
    y_lin = lr_2d.predict(pd.DataFrame({"temp_media": t_grid}))

    coef_cub = np.polyfit(uteis["temp_media"], uteis[ALVO], deg=3)
    y_curva = np.polyval(coef_cub, t_grid)

    uteis["pred_lin"] = lr_2d.predict(uteis[["temp_media"]])
    quentes = uteis[uteis["temp_media"] >= 23.8].copy()
    quentes["erro_abs"] = np.abs(quentes[ALVO] - quentes["pred_lin"])
    hastes = quentes.nlargest(16, "erro_abs")

    return {
        "se24": se24,
        "uteis": uteis,
        "t_grid": t_grid,
        "y_lin": y_lin,
        "y_curva": y_curva,
        "hastes": hastes,
        "curvas_sub": curvas_sub,
    }


def gerar_visual_04(dados: dict) -> None:
    d4 = _preparar_curvas_termicas(dados["base"], dados["df24"])
    se24 = d4["se24"]
    uteis = d4["uteis"]
    folgas = se24[se24["tipo_dia"] != "Dia útil"]

    fig, axs = plt.subplots(2, 2, figsize=(13.0, 8.2))

    # (a) Amostra completa
    ax = axs[0, 0]
    ax.scatter(se24["temp_media"], se24[ALVO] / 1000.0, s=18, alpha=0.65, color=COR_NEUTRO, edgecolors="#FFFFFF", lw=0.3)
    ax.set_title("(a) Amostra completa — SE (2024)", fontsize=10.2, loc="left", pad=6)
    ax.set_xlabel("Temperatura média diária (°C)")
    ax.set_ylabel("Carga elétrica (mil MWmed)")
    ax.set_ylim(32, 55.5)
    estilizar_eixo(ax, grid_axis="both")

    # (b) Estratificação por tipo de dia
    ax = axs[0, 1]
    ax.scatter(uteis["temp_media"], uteis[ALVO] / 1000.0, s=20, alpha=0.72, color=COR_RF, edgecolors="#FFFFFF", lw=0.3, label="Dias úteis")
    ax.scatter(folgas["temp_media"], folgas[ALVO] / 1000.0, s=20, alpha=0.65, color="#9CA3AF", edgecolors="#FFFFFF", lw=0.3, label="Fins de semana / feriados")
    ax.set_title("(b) Estratificação por tipo de dia — SE (2024)", fontsize=10.2, loc="left", pad=6)
    ax.set_xlabel("Temperatura média diária (°C)")
    ax.set_ylabel("Carga elétrica (mil MWmed)")
    ax.set_ylim(32, 55.5)
    ax.legend(loc="upper left", frameon=True, facecolor="#FFFFFF", fontsize=8.4)
    estilizar_eixo(ax, grid_axis="both")

    # (c) Dias úteis: ajuste linear vs. não linear
    ax = axs[1, 0]
    ax.axvspan(15.0, 22.0, color="#EFF6FF", alpha=0.75, zorder=0, label="Faixa amena (15–22 °C)")
    ax.axvspan(24.0, 29.0, color="#FFF7ED", alpha=0.80, zorder=0, label="Acima de 24 °C")
    ax.scatter(uteis["temp_media"], uteis[ALVO] / 1000.0, s=18, alpha=0.58, color=COR_RF, edgecolors="#FFFFFF", lw=0.3, zorder=2)
    for _, row in d4["hastes"].iterrows():
        ax.plot(
            [row["temp_media"], row["temp_media"]],
            [row["pred_lin"] / 1000.0, row[ALVO] / 1000.0],
            color=COR_ERRO,
            lw=1.1,
            alpha=0.72,
            zorder=3,
        )
    ax.plot(d4["t_grid"], d4["y_lin"] / 1000.0, "--", color=COR_RL, lw=2.0, zorder=4, label="Ajuste linear")
    ax.plot(d4["t_grid"], d4["y_curva"] / 1000.0, "-", color=COR_GB, lw=2.4, zorder=5, label="Ajuste não linear (cúbico)")
    ax.set_title("(c) Dias úteis: ajuste linear vs. não linear — SE", fontsize=10.2, loc="left", pad=6)
    ax.set_xlabel("Temperatura média diária (°C)")
    ax.set_ylabel("Carga em dias úteis (mil MWmed)")
    ax.set_xlim(15.2, 28.6)
    ax.set_ylim(36, 55.5)
    ax.legend(loc="upper left", fontsize=8.0, frameon=True, facecolor="#FFFFFF")
    estilizar_eixo(ax, grid_axis="both")

    # (d) Curva de resposta parcial aprendida pelo Gradient Boosting
    ax = axs[1, 1]
    cores_sub = {"SE": COR_RF, "S": COR_ROXO, "NE": COR_RL, "N": COR_GB}
    ax.axhline(0, color=COR_NEUTRO, lw=0.9, ls=":")
    ax.axvspan(24.0, 32.0, color="#FFF7ED", alpha=0.65, zorder=0)
    for sub in SUBSISTEMAS:
        gt, var_pct = d4["curvas_sub"][sub]
        ax.plot(gt, var_pct, lw=2.2, color=cores_sub[sub], label=f"{sub} (+{fmt_br(var_pct[-1], 1)}%)")
    ax.set_title("(d) Resposta parcial à temperatura (Gradient Boosting)", fontsize=10.2, loc="left", pad=6)
    ax.set_xlabel("Temperatura média simulada (°C)")
    ax.set_ylabel("Variação na carga prevista (%)")
    ax.set_xlim(14, 32.5)
    ax.set_ylim(-1.2, 16.2)
    ax.legend(loc="upper left", fontsize=8.4, frameon=True, facecolor="#FFFFFF")
    estilizar_eixo(ax, grid_axis="both")

    fig.subplots_adjust(left=0.07, right=0.97, top=0.94, bottom=0.08, hspace=0.30, wspace=0.20)
    salvar_png(fig, "04_isolando_efeito_ar_condicionado.png", dpi=300)

    # GIF científico em 4 passos no mesmo eixo
    frames = []
    durations = []
    atos = [
        ("(a) Amostra completa — SE (2024)", 1),
        ("(b) Estratificação por tipo de dia — SE (2024)", 2),
        ("(c) Dias úteis: ajuste linear e resíduos (> 24 °C)", 3),
        ("(d) Dias úteis: ajuste linear vs. não linear — SE", 4),
    ]
    for titulo_ato, passo in atos:
        for sub_step in range(3):
            fig_g, ax_g = plt.subplots(figsize=(8.6, 5.0), dpi=110)
            if passo == 1:
                ax_g.scatter(se24["temp_media"], se24[ALVO] / 1000.0, s=24, alpha=0.65, color=COR_NEUTRO, edgecolors="#FFFFFF", lw=0.35)
            elif passo == 2:
                alpha_folga = max(0.25, 0.75 - sub_step * 0.22)
                ax_g.scatter(folgas["temp_media"], folgas[ALVO] / 1000.0, s=22, alpha=alpha_folga, color="#9CA3AF", edgecolors="#FFFFFF", lw=0.35, label="Fins de semana / feriados")
                ax_g.scatter(uteis["temp_media"], uteis[ALVO] / 1000.0, s=26, alpha=0.82, color=COR_RF, edgecolors="#FFFFFF", lw=0.35, label="Dias úteis")
            else:
                ax_g.axvspan(15.0, 22.0, color="#EFF6FF", alpha=0.75, zorder=0, label="Faixa amena (15–22 °C)")
                ax_g.axvspan(24.0, 29.0, color="#FFF7ED", alpha=0.80, zorder=0, label="Acima de 24 °C")
                ax_g.scatter(uteis["temp_media"], uteis[ALVO] / 1000.0, s=22, alpha=0.60, color=COR_RF, edgecolors="#FFFFFF", lw=0.35, zorder=2)
                if passo == 3:
                    for _, row in d4["hastes"].iterrows():
                        ax_g.plot([row["temp_media"], row["temp_media"]], [row["pred_lin"] / 1000.0, row[ALVO] / 1000.0], color=COR_ERRO, lw=1.35, alpha=0.80, zorder=3)
                    ax_g.plot(d4["t_grid"], d4["y_lin"] / 1000.0, "--", color=COR_RL, lw=2.3, zorder=4, label="Ajuste linear")
                else:
                    ax_g.plot(d4["t_grid"], d4["y_lin"] / 1000.0, "--", color=COR_RL, lw=1.7, alpha=0.55, zorder=3, label="Ajuste linear")
                    ax_g.plot(d4["t_grid"], d4["y_curva"] / 1000.0, "-", color=COR_GB, lw=2.7, zorder=5, label="Ajuste não linear")
            ax_g.set_xlim(15.2, 28.6)
            ax_g.set_ylim(32.0, 55.5)
            ax_g.set_title(titulo_ato, fontsize=10.5, loc="left", pad=8)
            ax_g.set_xlabel("Temperatura média diária (°C)")
            ax_g.set_ylabel("Carga elétrica (mil MWmed)")
            if passo >= 2:
                ax_g.legend(loc="upper left", fontsize=8.3, frameon=True, facecolor="#FFFFFF")
            estilizar_eixo(ax_g, grid_axis="both")
            fig_g.subplots_adjust(left=0.10, right=0.96, top=0.90, bottom=0.12)
            frames.append(fig_para_rgb(fig_g))
            plt.close(fig_g)
            durations.append(0.55 if sub_step == 2 else 0.35)
    salvar_gif(frames, "04_isolando_efeito_ar_condicionado.gif", durations)
    print("✓ Visual 04 gerado (PNG 300 DPI + GIF 4 atos)")


# =============================================================================
# 5. COMO O GRADIENT BOOSTING APRENDE COM OS RESÍDUOS (PNG + GIF)
# =============================================================================
def gerar_visual_05(dados: dict) -> None:
    base = dados["base"]
    treino = pd.concat([base[base["ano"] <= 2022], base[base["ano"] == 2023]], ignore_index=True)
    teste = base[base["ano"] == 2024].copy()

    janela_mask = (teste["id_subsistema"] == "SE") & teste["event_date"].between("2024-02-12", "2024-03-18")
    t_zoom = teste[janela_mask].sort_values("event_date").copy()

    etapas_arvores = [1, 15, 30, 50, 80, 120, 200, 400]
    preds_zoom = {}
    mapes_globais = {}
    for n_arvs in etapas_arvores:
        m = _construir_gb(max_iter=n_arvs).fit(treino[TODAS], treino[ALVO])
        p_all = m.predict(teste[TODAS])
        mapes_globais[n_arvs] = float(mean_absolute_percentage_error(teste[ALVO], p_all) * 100.0)
        preds_zoom[n_arvs] = m.predict(t_zoom[TODAS]) / 1000.0

    fig, axs = plt.subplots(2, 2, figsize=(13.0, 8.0))
    real_z = t_zoom[ALVO].to_numpy() / 1000.0
    datas_z = t_zoom["event_date"]

    quadros_n = [
        (axs[0, 0], 15, "(a) Ensemble com 15 árvores"),
        (axs[0, 1], 50, "(b) Ensemble com 50 árvores"),
        (axs[1, 0], 400, "(c) Ensemble com 400 árvores"),
    ]
    for ax, n_arvs, tit in quadros_n:
        prev_z = preds_zoom[n_arvs]
        for d_x, r_y, p_y in zip(datas_z, real_z, prev_z):
            ax.plot([d_x, d_x], [p_y, r_y], color=COR_ERRO, lw=1.0, alpha=0.68, zorder=2)
        ax.plot(datas_z, real_z, color=COR_REAL, lw=1.8, label="Carga real (ONS)", zorder=3)
        ax.plot(datas_z, prev_z, color=COR_GB, lw=2.0, label=f"Previsto GB ({n_arvs} árv.)", zorder=4)
        ax.set_title(f"{tit} (MAPE = {fmt_br(mapes_globais[n_arvs], 2)}%)", fontsize=10.0, loc="left", pad=6)
        ax.set_ylabel("Carga SE (mil MWmed)")
        ax.set_ylim(16.0, 56.0)
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
        ax.legend(loc="lower right", fontsize=8.2, frameon=True, facecolor="#FFFFFF")
        estilizar_eixo(ax, grid_axis="both")

    ax4 = axs[1, 1]
    gb_tr = dados["met_gb"]["treino"]["MAPE_%"]
    gb_te = dados["met_gb"]["teste"]["MAPE_%"]
    rf_tr = dados["met_rf"]["treino"]["MAPE_%"]
    rf_te = dados["met_rf"]["teste"]["MAPE_%"]

    x = np.array([0, 1])
    w = 0.30
    b_tr = ax4.bar(x - w / 2, [rf_tr, gb_tr], width=w, color="#9CA3AF", edgecolor="#374151", linewidth=0.6, label="Treino (2016–2023)")
    b_te = ax4.bar(x + w / 2, [rf_te, gb_te], width=w, color=[COR_RF, COR_GB], edgecolor="#111827", linewidth=0.6, label="Teste (2024)")
    for b, val in zip(b_tr, [rf_tr, gb_tr]):
        ax4.text(b.get_x() + b.get_width() / 2, val + 0.08, f"{fmt_br(val, 2)}%", ha="center", va="bottom", fontsize=8.8, color=TXT_DARK)
    for b, val in zip(b_te, [rf_te, gb_te]):
        ax4.text(b.get_x() + b.get_width() / 2, val + 0.08, f"{fmt_br(val, 2)}%", ha="center", va="bottom", fontsize=8.8, color=TXT_DARK)

    ax4.set_xticks(x)
    ax4.set_xticklabels(["Random Forest", "Gradient Boosting"], fontsize=9.5)
    ax4.set_ylim(0, 4.1)
    ax4.set_ylabel("MAPE (%)")
    ax4.set_title("(d) Erro MAPE (%): Treino (2016–2023) vs. Teste (2024)", fontsize=10.0, loc="left", pad=6)
    ax4.legend(loc="upper right", fontsize=8.2, frameon=True, facecolor="#FFFFFF")
    estilizar_eixo(ax4, grid_axis="y")

    fig.subplots_adjust(left=0.07, right=0.97, top=0.94, bottom=0.08, hspace=0.30, wspace=0.18)
    salvar_png(fig, "05_como_gb_aprende_residuos.png", dpi=300)

    # GIF científico step-by-step
    frames = []
    durations = []
    for idx_e, n_arvs in enumerate(etapas_arvores):
        fig_g, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(10.6, 4.4), dpi=110, gridspec_kw={"width_ratios": [1.5, 1.0]})
        prev_z = preds_zoom[n_arvs]
        for d_x, r_y, p_y in zip(datas_z, real_z, prev_z):
            ax_l.plot([d_x, d_x], [p_y, r_y], color=COR_ERRO, lw=1.2, alpha=0.72, zorder=2)
        ax_l.plot(datas_z, real_z, color=COR_REAL, lw=1.9, label="Carga real (ONS)", zorder=3)
        ax_l.plot(datas_z, prev_z, color=COR_GB, lw=2.2, label=f"Previsto GB ({n_arvs} árv.)", zorder=4)
        ax_l.set_ylim(10.0, 56.0)
        ax_l.set_ylabel("Carga SE (mil MWmed)")
        ax_l.xaxis.set_major_locator(mdates.DayLocator(interval=7))
        ax_l.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
        ax_l.legend(loc="lower right", fontsize=8.2, frameon=True, facecolor="#FFFFFF")
        ax_l.set_title(f"(a) Série SE (Fev–Mar/2024) — {n_arvs} {'árvore' if n_arvs == 1 else 'árvores'}", fontsize=9.8, loc="left")
        estilizar_eixo(ax_l, grid_axis="both")

        xs_cur = etapas_arvores[: idx_e + 1]
        ys_cur = [mapes_globais[k] for k in xs_cur]
        ax_r.plot(range(len(etapas_arvores)), [mapes_globais[k] for k in etapas_arvores], color=GRID, lw=1.6, ls="--")
        ax_r.plot(range(len(xs_cur)), ys_cur, color=COR_GB, lw=2.2, marker="o", markersize=6)
        ax_r.scatter(len(xs_cur) - 1, ys_cur[-1], color=COR_ERRO, s=70, zorder=5)
        ax_r.text(
            max(0.55, len(xs_cur) - 1.15) if len(xs_cur) == 1 else min(len(etapas_arvores) - 1.15, len(xs_cur) - 1),
            ys_cur[-1] + 1.8,
            f"{fmt_br(ys_cur[-1], 2)}%",
            ha="center",
            fontsize=8.8,
            color=TXT_DARK,
        )
        ax_r.set_xticks(range(len(etapas_arvores)))
        ax_r.set_xticklabels([str(k) for k in etapas_arvores], fontsize=8.3)
        ax_r.set_ylim(0.0, max(mapes_globais.values()) + 6.5)
        ax_r.set_xlabel("Número acumulado de árvores")
        ax_r.set_ylabel("MAPE global em 2024 (%)")
        ax_r.set_title("(b) Convergência do MAPE (2024)", fontsize=9.8, loc="left")
        estilizar_eixo(ax_r, grid_axis="y")

        fig_g.subplots_adjust(left=0.07, right=0.97, top=0.89, bottom=0.14, wspace=0.22)
        frames.append(fig_para_rgb(fig_g))
        plt.close(fig_g)
        durations.append(1.5 if n_arvs in (1, 400) else 0.65)
    salvar_gif(frames, "05_como_gb_aprende_residuos.gif", durations)
    print("✓ Visual 05 gerado (PNG 300 DPI + GIF residual step-by-step)")


# =============================================================================
# 6. A RECEITA DA PREVISÃO, ABLAÇÃO E CASCATA REAL (PNG 300 DPI)
# =============================================================================
def gerar_visual_06(dados: dict) -> None:
    base = dados["base"]
    df24 = dados["df24"]
    met_gb = dados["met_gb"]
    met_rf = dados["met_rf"]

    treino = pd.concat([base[base["ano"] <= 2022], base[base["ano"] == 2023]], ignore_index=True)
    m_full = _construir_gb(max_iter=400).fit(treino[TODAS], treino[ALVO])

    dia = df24[(df24["id_subsistema"] == "SE") & (df24["event_date"] == pd.Timestamp("2024-03-12"))].copy()
    x0 = dia[TODAS].copy()
    x0["dia_semana"] = 6
    x0[["temp_media", "temp_media_lag_1", "temp_media_3d"]] = 20.0
    x0["temp_max"] = 25.0
    x0["temp_min"] = 16.0

    x1 = x0.copy()
    x1["dia_semana"] = dia["dia_semana"].values[0]

    p0 = float(m_full.predict(x0)[0])
    p1 = float(m_full.predict(x1)[0])
    p2 = float(m_full.predict(dia[TODAS])[0])
    real_obs = float(dia[ALVO].values[0])
    tmax = float(dia["temp_max"].values[0])
    data_str = dia["event_date"].dt.strftime("%d/%m/%Y").values[0]

    print(
        f"  [Waterfall {data_str}] base_amena_folga={p0:.1f}, dia_util={p1:.1f} (+{p1-p0:.1f}), "
        f"full={p2:.1f} (+{p2-p1:.1f}), real={real_obs:.1f}, temp_max={tmax:.1f}"
    )

    fig = plt.figure(figsize=(13.2, 8.2))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.0], hspace=0.38, wspace=0.42, left=0.16, right=0.97, top=0.94, bottom=0.08)

    # (a) Estudo de ablação
    ax1 = fig.add_subplot(gs[0, 0])
    abl = met_gb["ablacao"]
    cen_keys = [
        ("Completo", "Modelo completo", COR_GB),
        ("Sem variáveis climáticas (H1)", "Sem clima (H1)", COR_RL),
        ("Sem calendário (H3)", "Sem calendário (H3)", COR_ERRO),
        ("Sem defasagens da carga (H3)", "Sem lags (H3/H4)", COR_ROXO),
    ][::-1]
    y1 = np.arange(len(cen_keys))
    vals_mae = [abl[k]["MAE"] for k, _, _ in cen_keys]
    vals_mape = [abl[k]["MAPE_%"] for k, _, _ in cen_keys]
    cores1 = [c for _, _, c in cen_keys]
    b1 = ax1.barh(y1, vals_mae, color=cores1, height=0.52, edgecolor="#111827", linewidth=0.5, alpha=0.90)
    for bar, mae_v, mape_v in zip(b1, vals_mae, vals_mape):
        ax1.text(
            mae_v + 18,
            bar.get_y() + bar.get_height() / 2,
            f"{fmt_br(mae_v, 0)} ({fmt_br(mape_v, 2)}%)",
            va="center",
            fontsize=8.3,
            color=TXT_DARK,
        )
    ax1.set_yticks(y1)
    ax1.set_yticklabels([lbl for _, lbl, _ in cen_keys], fontsize=8.8)
    ax1.set_xlim(0, 1120)
    ax1.set_xlabel("MAE em 2024 (MWmed)")
    ax1.set_title("(a) Estudo de ablação — MAE em 2024 (MWmed)", fontsize=10.0, loc="left", pad=6)
    estilizar_eixo(ax1, grid_axis="x")

    # (b) Importância por permutação
    ax2 = fig.add_subplot(gs[0, 1])
    imp_gb = met_gb["importancia_permutacao_pp"]
    imp_rf = met_rf["importancia_permutacao_pp"]
    itens_imp = [
        ("carga_lag_1", "carga_lag_1"),
        ("carga_lag_7", "carga_lag_7"),
        ("dia_semana", "dia_semana"),
        ("carga_media_7d", "carga_media_7d"),
        ("temp_max", "temp_max"),
        ("feriado", "feriado"),
        ("temp_media", "temp_media"),
    ][::-1]
    y2 = np.arange(len(itens_imp))
    v_gb_i = [imp_gb[k] for k, _ in itens_imp]
    v_rf_i = [max(imp_rf[k], 0.0) for k, _ in itens_imp]
    h2 = 0.36
    ax2.barh(y2 + h2 / 2, v_gb_i, height=h2, color=COR_GB, edgecolor="#111827", linewidth=0.5, label="Gradient Boosting")
    ax2.barh(y2 - h2 / 2, v_rf_i, height=h2, color=COR_RF, edgecolor="#111827", linewidth=0.5, alpha=0.85, label="Random Forest")
    for idx_i, (vg, vr) in enumerate(zip(v_gb_i, v_rf_i)):
        ax2.text(vg + 0.35, idx_i + h2 / 2, f"+{fmt_br(vg, 2)}", va="center", fontsize=7.6, color=COR_GB)
        if vr >= 0.05:
            ax2.text(vr + 0.35, idx_i - h2 / 2, f"+{fmt_br(vr, 2)}", va="center", fontsize=7.6, color=COR_RF)
        elif vg > 0.2:
            ax2.text(0.35, idx_i - h2 / 2, "0,00", va="center", fontsize=7.4, color=COR_RF)
    ax2.set_yticks(y2)
    ax2.set_yticklabels([lbl for _, lbl in itens_imp], fontsize=8.8)
    ax2.set_xlim(0, 26.8)
    ax2.set_xlabel("ΔMAPE ao permutar (p.p.)")
    ax2.set_title("(b) Importância por permutação — ΔMAPE (p.p.)", fontsize=10.0, loc="left", pad=6)
    ax2.legend(loc="lower right", fontsize=8.2, frameon=True, facecolor="#FFFFFF")
    estilizar_eixo(ax2, grid_axis="x")

    # (c) Waterfall aditivo real em 12/03/2024 no Sudeste
    ax3 = fig.add_subplot(gs[1, :])
    b0 = p0 / 1000.0
    d1 = (p1 - p0) / 1000.0
    d2 = (p2 - p1) / 1000.0
    pf = p2 / 1000.0
    rl_obs = real_obs / 1000.0

    etapas_wf = [
        "Base (dom., 20 °C)",
        "+ Dia útil",
        f"+ Calor ({fmt_br(tmax, 1)} °C)",
        "Previsão GB",
        "Carga real (ONS)",
    ]
    bottoms = [0.0, b0, b0 + d1, 0.0, 0.0]
    heights = [b0, d1, d2, pf, rl_obs]
    cols_wf = [COR_NEUTRO, COR_RF, COR_ERRO, COR_GB, COR_REAL]
    x3 = np.arange(len(etapas_wf))
    ax3.bar(x3, heights, bottom=bottoms, width=0.44, color=cols_wf, edgecolor="#111827", linewidth=0.6, zorder=3)

    ax3.plot([0.22, 0.78], [b0, b0], ":", color="#6B7280", lw=1.2)
    ax3.plot([1.22, 1.78], [b0 + d1, b0 + d1], ":", color="#6B7280", lw=1.2)
    ax3.plot([2.22, 2.78], [pf, pf], ":", color="#6B7280", lw=1.2)

    rotulos_wf = [
        f"{fmt_br(p0 / 1000.0, 2)}",
        f"+{fmt_br((p1 - p0) / 1000.0, 2)}",
        f"+{fmt_br((p2 - p1) / 1000.0, 2)}",
        f"{fmt_br(pf, 2)}",
        f"{fmt_br(rl_obs, 2)}",
    ]
    for xi, bot, h_val, r_txt in zip(x3, bottoms, heights, rotulos_wf):
        ax3.text(xi, bot + h_val + 0.45, r_txt, ha="center", va="bottom", fontsize=8.8, color=TXT_DARK)

    ax3.set_xticks(x3)
    ax3.set_xticklabels(etapas_wf, fontsize=9.0)
    ax3.set_ylim(35.0, 52.8)
    ax3.set_ylabel("Carga SE (mil MWmed)")
    ax3.set_title(f"(c) Decomposição aditiva da previsão — SE ({data_str})", fontsize=10.0, loc="left", pad=6)
    estilizar_eixo(ax3, grid_axis="y")

    salvar_png(fig, "06_receita_previsao_e_ablacao.png", dpi=300)
    print("✓ Visual 06 gerado (Receita, ablação e cascata real)")


# =============================================================================
# 7. ZOOM CARNAVAL + ONDAS DE CALOR + 4 MINI-PAINÉIS LEGÍVEIS (PNG 300 DPI)
# =============================================================================
def gerar_visual_07(dados: dict) -> None:
    df24 = dados["df24"]
    por_sub = dados["resumo"]["mape_por_subsistema_2024"]

    fig = plt.figure(figsize=(13.4, 7.6))
    gs = fig.add_gridspec(2, 4, height_ratios=[1.35, 1.0], hspace=0.34, wspace=0.22, left=0.06, right=0.98, top=0.94, bottom=0.08)
    ax_top = fig.add_subplot(gs[0, :])

    se_z = df24[(df24["id_subsistema"] == "SE") & df24["event_date"].between("2024-02-01", "2024-03-20")].sort_values("event_date")
    ax_top.axvspan(pd.Timestamp("2024-02-10"), pd.Timestamp("2024-02-14"), color="#EDE9FE", alpha=0.75, zorder=0, label="Carnaval (10–14/02)")
    ax_top.axvspan(pd.Timestamp("2024-03-11"), pd.Timestamp("2024-03-18"), color="#FFF7ED", alpha=0.80, zorder=0, label="Onda de calor (11–18/03)")

    ax_top.fill_between(
        se_z["event_date"],
        se_z["previsto_rl"] / 1000.0,
        se_z[ALVO] / 1000.0,
        where=se_z[ALVO] > se_z["previsto_rl"],
        color=COR_ERRO,
        alpha=0.10,
        label="Desvio Reg. Linear (sem lags)",
    )
    ax_top.plot(se_z["event_date"], se_z["previsto_rl"] / 1000.0, "--", color=COR_RL, lw=1.6, label="Reg. Linear (sem lags)")
    ax_top.plot(se_z["event_date"], se_z["previsto_rf"] / 1000.0, "-.", color=COR_RF, lw=1.5, label="Random Forest")
    ax_top.plot(se_z["event_date"], se_z[ALVO] / 1000.0, "-", color=COR_REAL, lw=2.0, label="Carga real (ONS)")
    ax_top.plot(se_z["event_date"], se_z["previsto_gb"] / 1000.0, "-", color=COR_GB, lw=1.9, label="Gradient Boosting")

    ax_top.set_title("(a) Série diária no Subsistema SE — Fev–Mar/2024", fontsize=10.2, loc="left", pad=6)
    ax_top.set_ylabel("Carga (mil MWmed)")
    ax_top.set_ylim(33.5, 55.5)
    ax_top.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax_top.legend(loc="lower right", ncol=4, fontsize=7.8, frameon=True, facecolor="#FFFFFF")
    estilizar_eixo(ax_top, grid_axis="both")

    letras = ["b", "c", "d", "e"]
    for col_i, (sub, letra) in enumerate(zip(SUBSISTEMAS, letras)):
        ax_s = fig.add_subplot(gs[1, col_i])
        sub_z = df24[(df24["id_subsistema"] == sub) & df24["event_date"].between("2024-02-01", "2024-03-31")].sort_values("event_date")
        ax_s.plot(sub_z["event_date"], sub_z["previsto_rl"] / 1000.0, "--", color=COR_RL, lw=1.2, alpha=0.85, label="Linear")
        ax_s.plot(sub_z["event_date"], sub_z[ALVO] / 1000.0, "-", color=COR_REAL, lw=1.5, label="Real")
        ax_s.plot(sub_z["event_date"], sub_z["previsto_gb"] / 1000.0, "-", color=COR_GB, lw=1.4, label="GB")
        mape_sub = por_sub[sub]["Gradient Boosting"]
        ax_s.set_title(f"({letra}) {sub} (MAPE = {fmt_br(mape_sub, 2)}%)", fontsize=9.4, loc="left", pad=5)
        if col_i == 0:
            ax_s.set_ylabel("Carga (mil MWmed)")
            ax_s.legend(loc="lower left", fontsize=7.4, frameon=True, facecolor="#FFFFFF")
        ax_s.xaxis.set_major_locator(mdates.DayLocator(bymonthday=[1, 15]))
        ax_s.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
        ax_s.tick_params(axis="x", labelsize=7.5)
        estilizar_eixo(ax_s, grid_axis="both")

    salvar_png(fig, "07_zoom_carnaval_e_verao_2024.png", dpi=300)
    print("✓ Visual 07 gerado (Zoom Carnaval/Ondas de Calor + 4 subsistemas)")


# =============================================================================
# 8. IMPACTO OPERACIONAL NO ONS E DISTRIBUIÇÃO DE ERROS EM 2024 (PNG 300 DPI)
# =============================================================================
def gerar_visual_08(dados: dict) -> None:
    comp = dados["resumo"]["comparacao_global_2024"]
    df24 = dados["df24"].copy()

    if "carga_lag_7" not in df24.columns:
        lag7_df = dados["base"][["id_subsistema", "event_date", "carga_lag_7"]]
        df24 = df24.merge(lag7_df, on=["id_subsistema", "event_date"], how="left")

    modelos = [
        "Reg. Linear (sem lags)",
        "Baseline (lag 7)",
        "Random Forest",
        "Gradient Boosting",
    ][::-1]
    maes_v = [
        comp["Regressão Linear (clima, sem lags)"]["MAE"],
        comp["Baseline Ingênuo (carga_lag_7)"]["MAE"],
        comp["Random Forest"]["MAE"],
        comp["Gradient Boosting"]["MAE"],
    ][::-1]
    cores_v = [COR_RL, COR_NEUTRO, COR_RF, COR_GB][::-1]

    erros_diarios = [
        np.abs(df24[ALVO] - df24["previsto_rl"]).dropna().to_numpy(),
        np.abs(df24[ALVO] - df24["carga_lag_7"]).dropna().to_numpy(),
        np.abs(df24[ALVO] - df24["previsto_rf"]).dropna().to_numpy(),
        np.abs(df24[ALVO] - df24["previsto_gb"]).dropna().to_numpy(),
    ][::-1]

    print("  [Distribuição |Real - Previsto| em 2024 (MWmed)]")
    for nome_m, arr in zip(modelos, erros_diarios):
        print(
            f"    {nome_m:24s} -> mediana={np.median(arr):7.1f}, "
            f"Q3={np.percentile(arr, 75):7.1f}, P95={np.percentile(arr, 95):7.1f}, max={np.max(arr):7.1f}"
        )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.6, 4.6), sharey=True)

    y = np.arange(len(modelos))
    bars = ax1.barh(y, maes_v, color=cores_v, height=0.50, edgecolor="#111827", linewidth=0.6, zorder=3)
    for mw_ref, txt_ref in [(500, "500 MW"), (1000, "1.000 MW"), (1500, "1.500 MW")]:
        ax1.axvline(mw_ref, color="#6B7280", ls=":", lw=1.1, zorder=1)
        ax1.text(mw_ref, 3.45, txt_ref, ha="center", va="bottom", fontsize=7.8, color=TXT_SUB)

    for b, val in zip(bars, maes_v):
        ax1.text(val + 35, b.get_y() + b.get_height() / 2, f"{fmt_br(val, 0)}", va="center", fontsize=8.8, color=TXT_DARK)

    ax1.set_yticks(y)
    ax1.set_yticklabels(modelos, fontsize=9.0)
    ax1.set_xlim(0, 2150)
    ax1.set_ylim(-0.5, 3.85)
    ax1.xaxis.set_major_formatter(FuncFormatter(lambda x, _: fmt_br(x, 0)))
    ax1.set_xlabel("MAE (MWmed)")
    ax1.set_title("(a) Erro médio absoluto (MAE) e referências de porte", fontsize=10.0, loc="left", pad=8)
    estilizar_eixo(ax1, grid_axis="x")

    bp = ax2.boxplot(
        erros_diarios,
        positions=y,
        vert=False,
        widths=0.45,
        patch_artist=True,
        showfliers=True,
        flierprops=dict(marker="o", markerfacecolor="#6B7280", markeredgecolor="none", markersize=2.5, alpha=0.35),
        medianprops=dict(color="#111827", linewidth=1.6),
        whiskerprops=dict(color="#333333", linewidth=1.0),
        capprops=dict(color="#333333", linewidth=1.0),
        boxprops=dict(linewidth=0.9, edgecolor="#111827"),
    )
    for patch, cor in zip(bp["boxes"], cores_v):
        patch.set_facecolor(cor)
        patch.set_alpha(0.65)

    for yi, arr in zip(y, erros_diarios):
        med = float(np.median(arr))
        p95 = float(np.percentile(arr, 95))
        ax2.text(p95 + 120, yi + 0.25, f"Med: {fmt_br(med, 0)} | P95: {fmt_br(p95, 0)}", va="bottom", ha="left", fontsize=7.8, color=TXT_DARK)

    ax2.set_yticks(y)
    ax2.set_yticklabels(modelos, fontsize=9.0)
    ax2.set_xlim(0, 12500)
    ax2.xaxis.set_major_formatter(FuncFormatter(lambda x, _: fmt_br(x, 0)))
    ax2.set_xlabel("Erro absoluto diário |Real − Previsto| (MWmed)")
    ax2.set_title("(b) Distribuição do erro absoluto diário em 2024 (n = 1.464)", fontsize=10.0, loc="left", pad=8)
    estilizar_eixo(ax2, grid_axis="x")

    ax1.set_yticks(y)
    ax1.set_yticklabels(modelos, fontsize=9.0)

    fig.subplots_adjust(left=0.16, right=0.98, top=0.89, bottom=0.15, wspace=0.10)
    salvar_png(fig, "08_impacto_ons_e_arquitetura_aws.png", dpi=300)
    print("✓ Visual 08 gerado (MAE e distribuição dos erros em 2024)")


# =============================================================================
# 9. MAPA DO BRASIL POR SUBSISTEMA ELÉTRICO (CLIMA/CARGA E MAPE)
# =============================================================================
def gerar_visual_09(dados: dict) -> None:
    if not GEO_PATH.exists():
        raise FileNotFoundError(f"GeoJSON do Brasil não encontrado em {GEO_PATH}")

    geo = json.loads(GEO_PATH.read_text(encoding="utf-8"))
    d4 = _preparar_curvas_termicas(dados["base"], dados["df24"])
    df24 = dados["df24"]
    por_sub = dados["resumo"]["mape_por_subsistema_2024"]

    stats_sub = {}
    for sub in SUBSISTEMAS:
        sub_df = df24[df24["id_subsistema"] == sub]
        sens_t = float(d4["curvas_sub"][sub][1][-1])
        stats_sub[sub] = {
            "temp_media": float(sub_df["temp_media"].mean()),
            "carga_media_mil": float(sub_df[ALVO].mean() / 1000.0),
            "sens_t": sens_t,
            "mape_gb": float(por_sub[sub]["Gradient Boosting"]),
            "mape_rl": float(por_sub[sub]["Regressão Linear (sem lags)"]),
        }

    # Prepara polígonos por UF (coloca DF no fim para desenhar por cima de GO)
    features = sorted(
        geo["features"],
        key=lambda f: 1 if f["properties"].get("sigla") == "DF" else 0,
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.2, 6.4))

    cmap_a = plt.get_cmap("YlOrRd")
    norm_a = Normalize(vmin=0.0, vmax=16.0)
    cmap_b = plt.get_cmap("YlGnBu")
    norm_b = Normalize(vmin=1.5, vmax=3.2)

    patches_a, cols_a = [], []
    patches_b, cols_b = [], []

    for feat in features:
        uf = feat["properties"].get("sigla", "")
        sub = UF_PARA_SUB.get(uf)
        if not sub:
            continue
        geom = feat["geometry"]
        aneis = (
            [geom["coordinates"][0]]
            if geom["type"] == "Polygon"
            else [p[0] for p in geom["coordinates"]]
        )
        cor_a = cmap_a(norm_a(stats_sub[sub]["sens_t"]))
        cor_b = cmap_b(norm_b(stats_sub[sub]["mape_gb"]))
        for ring in aneis:
            pts = np.asarray(ring, dtype=float)
            patches_a.append(Polygon(pts, closed=True))
            cols_a.append(cor_a)
            patches_b.append(Polygon(pts, closed=True))
            cols_b.append(cor_b)

    pc_a = PatchCollection(patches_a, facecolors=cols_a, edgecolors="#374151", linewidths=0.45, zorder=2)
    pc_b = PatchCollection(patches_b, facecolors=cols_b, edgecolors="#374151", linewidths=0.45, zorder=2)
    ax1.add_collection(pc_a)
    ax2.add_collection(pc_b)

    # Anotações sóbrias fora do contorno dos estados (à esquerda do MT para N; oceano branco para NE, SE/CO e S)
    pos_textos = {
        "N": {"xy": (-62.8, -5.8), "xytext": (-67.5, -18.5), "seta": True, "cor_txt": "#111827"},
        "NE": {"xy": (-40.2, -6.2), "xytext": (-34.8, 1.6), "seta": True, "cor_txt": "#111827"},
        "SE": {"xy": (-45.5, -19.5), "xytext": (-31.6, -21.0), "seta": True, "cor_txt": "#111827"},
        "S": {"xy": (-51.8, -27.2), "xytext": (-40.5, -30.5), "seta": True, "cor_txt": "#111827"},
    }

    for sub, cfg in pos_textos.items():
        st = stats_sub[sub]
        nome_curto = "SE/CO" if sub == "SE" else sub
        txt_a = (
            f"{nome_curto}\n"
            f"T̄ = {fmt_br(st['temp_media'], 1)} °C | {fmt_br(st['carga_media_mil'], 1)}k MW\n"
            f"ΔT = +{fmt_br(st['sens_t'], 1)}%"
        )
        txt_b = (
            f"{nome_curto}\n"
            f"GB: {fmt_br(st['mape_gb'], 2)}%\n"
            f"Reg. Lin.: {fmt_br(st['mape_rl'], 2)}%"
        )

        cor_txt_a = cfg["cor_txt"]
        cor_txt_b = "#111827"

        for ax, txt_lbl, c_txt in [(ax1, txt_a, cor_txt_a), (ax2, txt_b, cor_txt_b)]:
            if cfg["seta"]:
                ax.annotate(
                    txt_lbl,
                    xy=cfg["xy"],
                    xytext=cfg["xytext"],
                    ha="center",
                    va="center",
                    fontsize=7.8,
                    color=c_txt,
                    arrowprops=dict(arrowstyle="-", color="#374151", lw=0.75),
                    zorder=5,
                )
            else:
                ax.text(
                    cfg["xytext"][0],
                    cfg["xytext"][1],
                    txt_lbl,
                    ha="center",
                    va="center",
                    fontsize=7.8,
                    color=c_txt,
                    zorder=5,
                )

    for ax, tit in [
        (ax1, "(a) Sensibilidade térmica e carga média por subsistema"),
        (ax2, "(b) Erro percentual (MAPE) por subsistema em 2024"),
    ]:
        ax.set_xlim(-75.2, -24.2)
        ax.set_ylim(-35.2, 6.5)
        ax.set_aspect(1.03)
        ax.set_xlabel("Longitude (°)")
        ax.set_title(tit, fontsize=10.0, loc="left", pad=8)
        estilizar_eixo(ax, grid_axis="both")
    ax1.set_ylabel("Latitude (°)")
    ax2.set_ylabel("")

    sm_a = plt.cm.ScalarMappable(norm=norm_a, cmap=cmap_a)
    sm_b = plt.cm.ScalarMappable(norm=norm_b, cmap=cmap_b)
    cbar_a = fig.colorbar(sm_a, ax=ax1, orientation="horizontal", fraction=0.042, pad=0.11, aspect=32)
    cbar_a.set_label("Variação da carga prevista entre 14 °C e 32 °C (%)", fontsize=8.5)
    cbar_a.ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: fmt_br(x, 0)))

    cbar_b = fig.colorbar(sm_b, ax=ax2, orientation="horizontal", fraction=0.042, pad=0.11, aspect=32)
    cbar_b.set_label("MAPE do Gradient Boosting em 2024 (%)", fontsize=8.5)
    cbar_b.ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: fmt_br(x, 1)))

    fig.subplots_adjust(left=0.06, right=0.98, top=0.93, bottom=0.12, wspace=0.12)
    salvar_png(fig, "09_mapa_brasil_subsistemas.png", dpi=300)
    print("✓ Visual 09 gerado (Mapa do Brasil por subsistema)")


def _limpar_imagens_trocadas() -> None:
    if DIR_ETAPA4.exists():
        for p in DIR_ETAPA4.iterdir():
            if p.is_file() and (not p.name.startswith(("01", "02")) or p.name == "01_comparacao_3d_modelos.gif"):
                p.unlink()
    if DIR_ETAPA5.exists():
        for p in DIR_ETAPA5.iterdir():
            if p.is_file() and p.name.startswith(("01", "02")):
                p.unlink()


def main() -> None:
    configurar_estilo()
    print("Carregando bases locais e métricas validadas...")
    dados = carregar_dados()

    _limpar_imagens_trocadas()
    gerar_visual_01(dados)
    gerar_visual_02(dados)
    gerar_visual_03(dados)
    gerar_visual_04(dados)
    gerar_visual_05(dados)
    gerar_visual_06(dados)
    gerar_visual_07(dados)
    gerar_visual_08(dados)
    gerar_visual_09(dados)

    print("\nArquivos gerados com sucesso em:")
    for d in OUT_DIRS:
        arqs = sorted(p.name for p in d.iterdir() if p.is_file())
        print(f" - {d}: {len(arqs)} arquivos -> {arqs}")


if __name__ == "__main__":
    main()
