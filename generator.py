import geopandas as gpd
import matplotlib.pyplot as plt
import os
from matplotlib.patches import Patch

# Chemins vers tes données
PATH_COMMUNES = "data/communes_togo.shp"
PATH_PREF = "data/prefectures_togo.shp"
PATH_REGIONS = "data/regions_togo.shp"
PATH_ROUTES = "data/reseau_routier.shp"
PATH_EAU = "data/reseau_hydro.shp"

def charger_donnees():
    """Charge les couches SIG du Togo avec sécurité SCR"""
    gdf_comm = gpd.read_file(PATH_COMMUNES)
    gdf_pref = gpd.read_file(PATH_PREF)
    gdf_reg = gpd.read_file(PATH_REGIONS)
    gdf_roads = gpd.read_file(PATH_ROUTES)
    gdf_water = gpd.read_file(PATH_EAU)
    
    for gdf in [gdf_comm, gdf_pref, gdf_reg, gdf_roads, gdf_water]:
        if gdf.crs is None:
            gdf.set_crs(epsg=4326, inplace=True)
            
    return gdf_comm, gdf_pref, gdf_reg, gdf_roads, gdf_water

def generer_visuel_commune(nom_commune, couleur_theme, nom_auteur, titre_perso):
    """Génère l'Atlas avec titre automatique et mise en page pro"""
    gdf_comm, gdf_pref, gdf_reg, gdf_roads, gdf_water = charger_donnees()
    
    # Détection intelligente des colonnes
    c_com_nom = 'Communes' if 'Communes' in gdf_comm.columns else 'Commune'
    c_com_reg = 'ADM1_FR' if 'ADM1_FR' in gdf_comm.columns else 'Adm1_fr'
    c_com_pref = 'ADM2_FR' if 'ADM2_FR' in gdf_comm.columns else 'Adm2_fr'

    cible = gdf_comm[gdf_comm[c_com_nom] == nom_commune]
    if cible.empty: return None

    nom_pref = cible[c_com_pref].values[0]
    nom_reg = cible[c_com_reg].values[0]
    
    # Identification des parents pour les cartons
    c_pref_id = 'ADM2_FR' if 'ADM2_FR' in gdf_pref.columns else 'Adm2_fr'
    pref_parente = gdf_pref[gdf_pref[c_pref_id] == nom_pref]
    c_reg_id = 'ADM1_FR' if 'ADM1_FR' in gdf_reg.columns else 'Adm1_fr'
    region_parente = gdf_reg[gdf_reg[c_reg_id] == nom_reg]
    
    voisins = gdf_comm[gdf_comm.geometry.touches(cible.geometry.iloc[0])]

    # MISE EN PAGE : Grille de 6 colonnes pour élargir les cartons
    fig = plt.figure(figsize=(22, 16), facecolor='#FEF9E7')
    
    # --- GESTION AUTOMATIQUE DU TITRE ---
    if titre_perso and titre_perso.strip() != "":
        texte_titre = titre_perso.upper()
    else:
        texte_titre = f"CARTE DE LOCALISATION DE LA COMMUNE DE {nom_commune.upper()}"

    fig.suptitle(texte_titre, fontsize=24, fontweight='bold', color='#2C3E50', 
                 y=0.94, va='top', bbox=dict(facecolor='white', edgecolor='#2C3E50', boxstyle='round,pad=0.5'))

    # Définition des zones de dessin
    ax_main = plt.subplot2grid((6, 6), (1, 0), colspan=4, rowspan=5)
    ax_togo = plt.subplot2grid((6, 6), (1, 4), colspan=2)
    ax_region = plt.subplot2grid((6, 6), (2, 4), colspan=2)
    ax_pref = plt.subplot2grid((6, 6), (3, 4), colspan=2)

    for ax in [ax_main, ax_togo, ax_region, ax_pref]:
        for spine in ax.spines.values():
            spine.set_visible(True); spine.set_color('#2C3E50'); spine.set_linewidth(1.5)
        if ax != ax_main: ax.set_xticks([]); ax.set_yticks([])

    # --- DESSIN CARTE PRINCIPALE ---
    voisins.plot(ax=ax_main, color='#FDFEFE', edgecolor='#BDC3C7', linewidth=0.5, linestyle='--')
    cible.plot(ax=ax_main, color=couleur_theme, edgecolor='black', linewidth=2.0, zorder=5)
    gdf_water.clip(cible).plot(ax=ax_main, color='#3498DB', linewidth=1.5, zorder=6)
    gdf_roads.clip(cible).plot(ax=ax_main, color='red', linewidth=1.2, zorder=6) # ROUTES ROUGES

    # Grille et Nord
    ax_main.tick_params(axis='both', labelsize=10, labelbottom=True, labelleft=True)
    ax_main.grid(True, linestyle='-', linewidth=0.3, color='#BDC3C7')
    ax_main.annotate('N', xy=(0.97, 0.97), xytext=(0.97, 0.92), arrowprops=dict(facecolor='black', width=1, headwidth=8), xycoords='axes fraction')

    # Légende
    leg_el = [
        Patch(facecolor=couleur_theme, edgecolor='black', label=f'Territoire : {nom_commune}'),
        Patch(facecolor='#FDFEFE', edgecolor='#BDC3C7', label='Communes limitrophes'),
        plt.Line2D([0], [0], color='#3498DB', lw=2, label='Réseau Hydrographique'),
        plt.Line2D([0], [0], color='red', lw=1.5, label='Réseau Routier')
    ]
    ax_main.legend(handles=leg_el, loc='lower left', fontsize=11, frameon=True, facecolor='white', shadow=True)

    # Échelle
    ax_main.annotate('0          5km', xy=(0.02, -0.05), xycoords='axes fraction', fontsize=11, fontweight='bold')
    ax_main.plot([0.02, 0.12], [-0.03, -0.03], color='black', lw=2, transform=ax_main.transAxes)

    # --- CARTONS DE DROITE ---
    ax_togo.set_title("SITUATION NATIONALE", fontsize=12, fontweight='bold', pad=10)
    gdf_reg.plot(ax=ax_togo, color='white', edgecolor='grey', linewidth=0.3)
    region_parente.plot(ax=ax_togo, color='#AED6F1', edgecolor='black')
    
    ax_region.set_title("ZONAGE RÉGIONAL", fontsize=12, fontweight='bold', pad=10)
    region_parente.plot(ax=ax_region, color='white', edgecolor='black', linewidth=0.8)
    pref_parente.plot(ax=ax_region, color='#F9E79F', edgecolor='black')
    
    ax_pref.set_title("ZONAGE PRÉFECTORAL", fontsize=12, fontweight='bold', pad=10)
    pref_parente.plot(ax=ax_pref, color='white', edgecolor='black', linewidth=1.0)
    cible.plot(ax=ax_pref, color=couleur_theme, alpha=0.7)

    # Signature
    fig.text(0.98, 0.02, f"Auteur certifié : {nom_auteur}\nJCDC TOGO / DGSCN", fontsize=12, ha='right', fontweight='bold', fontstyle='italic')

    # Zoom adaptatif
    b = cible.total_bounds
    ax_main.set_xlim([b[0]-0.02, b[2]+0.02]); ax_main.set_ylim([b[1]-0.02, b[3]+0.02])

    if not os.path.exists("outputs"): os.makedirs("outputs")
    output_path = f"outputs/Atlas_{nom_commune}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    return output_path