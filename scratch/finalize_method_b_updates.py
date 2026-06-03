import os
import shutil

def main():
    print("=== FINALIZANDO IMPLEMENTACIÓN DEL MÉTODO B ===")
    
    # 1. Eliminar documentos obsoletos
    files_to_delete = [
        "documentacion/score_jugadores_clusters.md",
    ]
    for filepath in files_to_delete:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"  [Deleted] File: {filepath}")
            
    # Eliminar carpeta experimental alternative
    dir_to_delete = "documentacion/clustering_alternative"
    if os.path.exists(dir_to_delete):
        shutil.rmtree(dir_to_delete)
        print(f"  [Deleted] Directory: {dir_to_delete}")
        
    # 2. Actualizar guia_maestra_scores.md
    guia_path = "documentacion/guia_maestra_scores.md"
    if os.path.exists(guia_path):
        with open(guia_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Reemplazar descripción de Metodología de clustering
        old_desc = """  * **Clustering por Arquetipos de Élite (>75):** Entrena el modelo KMeans únicamente con jugadores de valoración global superior a 75 para fijar centros limpios de estilo competitivo, asignando luego a todos los jugadores a esos arquetipos estructurados.
* **Grupos y Arquetipos Deducidos:**
  * **Goalkeepers:** *Sweeper Keeper* (Alisson), *Tradicional/Atajador* (Courtois), *Arquero Anómalo* (Mvogo).
  * **Centerbacks:** *Central Dominador/Aéreo* (van Dijk), *Central de Cobertura/Rápido* (Saliba), *Central Tanque/Físico* (Gabriel).
  * **Fullbacks:** *Lateral Físico/3er Central* (Gvardiol), *Lateral Equilibrado* (Koundé), *Lateral Ofensivo/Carrilero* (Hakimi).
  * **Midfielders:** *Todocampista Box-to-Box* (Bellingham), *Enganche/Mediapunta* (Wirtz), *Organizador/Pivote Técnico* (Rodri).
  * **Strikers:** *Delantero de Presión* (Dembélé), *Velocista de Ruptura* (Mbappé), *Hombre Objetivo/Nueve* (Håland).
  * **Wingers:** *Extremo Asociativo* (Salah), *Regateador Puro* (Yamal), *Volante Táctico/Extremo Defensivo* (Saka)."""

        new_desc = """  * **Estandarización y Reducción por PCA (Método B):** Incorpora el peso (`weight_kg`) y la altura (`height_cm`), estandariza usando `StandardScaler` (z-score) y aplica un análisis PCA para retener el $\ge 80\%$ de varianza explicada.
  * **Supresión de PC1 (Ignorar Calidad):** Para evitar que el algoritmo clasifique a los jugadores por "buenos" o "malos", se descarta la primera componente principal (PC1), la cual correlaciona en un $>88\%$ con la calidad general (`overall`). KMeans opera únicamente sobre las componentes restantes (PC2 a PCN), agrupándolos exclusivamente por estilo y rol táctico.
  * **Optimización de $K$ (Silhouette Score):** Se optimiza dinámicamente el número de clusters para cada posición, asegurando clusters de tamaño consistente ($>10$ jugadores) y forzando $K=4$ para los mediocampistas.
* **Grupos y Arquetipos Deducidos:**
  * **Goalkeepers (K=3):** Representados por Alisson (89), Kobel (86) y Courtois (89).
  * **Centerbacks (K=3):** Representados por Gabriel Magalhães (88), Virgil van Dijk (90) y Jonathan Tah (87).
  * **Fullbacks (K=3):** Representados por Achraf Hakimi (89), Jules Koundé (87) y Nuno Mendes (86).
  * **Midfielders (K=4):** Representados por Joshua Kimmich (89 - *Organizadores*), Rodri (90 - *Pivotes Físicos*), Florian Wirtz (89 - *Mediapuntas*) y Jude Bellingham (90 - *Box-to-box*).
  * **Strikers (K=3):** Representados por Harry Kane (89), Ousmane Dembélé (90) y Kylian Mbappé (91).
  * **Wingers (K=3):** Representados por Raphinha (89), Bukayo Saka (88) y Mohamed Salah (91)."""

        content = content.replace(old_desc, new_desc)
        content = content.replace("理论 documentation: score_jugadores_clusters.md", "Detalle de metodología: score_jugadores_perfil_clusters.md")
        content = content.replace("[score_jugadores_clusters.md](file:///c:/Users/tomas/Desktop/proyectos/worldcup-app/documentacion/score_jugadores_clusters.md)", "[score_jugadores_perfil_clusters.md](file:///c:/Users/tomas/Desktop/proyectos/worldcup-app/documentacion/score_jugadores_perfil_clusters.md)")
        
        with open(guia_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("  [Updated] File: guia_maestra_scores.md")

if __name__ == "__main__":
    main()
