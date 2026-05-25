# fetch_fbref_qualifiers.R
# Script para extraer datos de clasificatorias al Mundial 2026 desde FBref

# Instalar dependencias si no están presentes
if (!requireNamespace("worldfootballR", quietly = TRUE)) {
  print("Instalando worldfootballR desde CRAN...")
  install.packages("worldfootballR", repos = "https://cloud.r-project.org")
}
library(worldfootballR)

if (!requireNamespace("dplyr", quietly = TRUE)) {
  install.packages("dplyr", repos = "https://cloud.r-project.org")
}
library(dplyr)

# Obtener ruta base dinámica (parent de scripts)
args <- commandArgs(trailingOnly = TRUE)
base_dir <- if (length(args) > 0) args[1] else ".."
output_path <- file.path(base_dir, "data", "fbref_qualifiers_cache.csv")

print(paste("Ruta base del proyecto:", base_dir))
print(paste("Guardando resultados en:", output_path))

# URLs de clasificatorias 2026 por confederación en FBref
qualifier_urls <- c(
  "https://fbref.com/en/comps/239/2026-WCQ-UEFA/2026-WCQ-UEFA-Stats",
  "https://fbref.com/en/comps/240/2026-WCQ-CONMEBOL/2026-WCQ-CONMEBOL-Stats",
  "https://fbref.com/en/comps/236/2026-WCQ-AFC/2026-WCQ-AFC-Stats",
  "https://fbref.com/en/comps/242/2026-WCQ-CAF/2026-WCQ-CAF-Stats",
  "https://fbref.com/en/comps/238/2026-WCQ-CONCACAF/2026-WCQ-CONCACAF-Stats",
  "https://fbref.com/en/comps/241/2026-WCQ-OFC/2026-WCQ-OFC-Stats"
)

# Tipos de estadísticas a extraer
stat_types <- c("standard", "shooting", "passing", "gca", "possession")

combined_stats <- NULL

for (url in qualifier_urls) {
  print(paste("Procesando URL:", url))
  
  # Extraer estadísticas estándar como base para la lista de jugadores
  std_data <- NULL
  tryCatch({
    std_data <- fb_player_season_stats(url, stat_type = "standard")
    Sys.sleep(12) # Rate limit friendly
  }, error = function(e) {
    print(paste("  Error al obtener standard stats para", url, ":", e$message))
  })
  
  if (is.null(std_data) || nrow(std_data) == 0) {
    next
  }
  
  # Seleccionar columnas base
  # Dependiendo de la versión de worldfootballR, las columnas pueden ser diferentes
  # Normalmente son: Player, Squad, Nation, Pos, Age, MP, Min, Gls, Ast
  # Intentamos normalizar las columnas clave
  std_cols <- colnames(std_data)
  player_col <- grep("Player", std_cols, value = TRUE)[1]
  squad_col <- grep("Squad|Team", std_cols, value = TRUE)[1]
  
  if (is.na(player_col) || is.na(squad_col)) {
    print("  No se encontraron columnas de Player o Squad básicas. Saltando...")
    next
  }
  
  # DataFrame base de jugadores
  url_players <- std_data %>%
    select(Player = !!player_col, Squad = !!squad_col) %>%
    distinct()
  
  # Inicializar columnas nuevas
  url_players$xG <- NA
  url_players$sca <- NA
  url_players$gca <- NA
  url_players$progressive_passes <- NA
  url_players$progressive_carries <- NA
  
  # Intentar cruzar con Shooting (para xG)
  tryCatch({
    shoot_data <- fb_player_season_stats(url, stat_type = "shooting")
    Sys.sleep(12)
    xg_col <- grep("xG", colnames(shoot_data), value = TRUE)[1]
    if (!is.na(xg_col)) {
      shoot_subset <- shoot_data %>%
        select(Player = !!player_col, Squad = !!squad_col, xG_val = !!xg_col) %>%
        group_by(Player, Squad) %>%
        summarise(xG_val = max(as.numeric(xG_val), na.rm = TRUE), .groups = 'drop')
      url_players <- left_join(url_players, shoot_subset, by = c("Player", "Squad")) %>%
        mutate(xG = coalesce(xG, xG_val)) %>%
        select(-xG_val)
    }
  }, error = function(e) { print(paste("  Error shooting:", e$message)) })
  
  # Intentar cruzar con GCA (SCA y GCA)
  tryCatch({
    gca_data <- fb_player_season_stats(url, stat_type = "gca")
    Sys.sleep(12)
    sca_col <- grep("SCA", colnames(gca_data), value = TRUE)[1]
    gca_col <- grep("GCA", colnames(gca_data), value = TRUE)[1]
    
    gca_subset <- gca_data %>% group_by(Player = !!player_col, Squad = !!squad_col)
    
    if (!is.na(sca_col) && !is.na(gca_col)) {
      gca_subset <- gca_subset %>%
        summarise(sca_val = sum(as.numeric(!!sym(sca_col)), na.rm = TRUE),
                  gca_val = sum(as.numeric(!!sym(gca_col)), na.rm = TRUE), .groups = 'drop')
      url_players <- left_join(url_players, gca_subset, by = c("Player", "Squad")) %>%
        mutate(sca = coalesce(sca, sca_val), gca = coalesce(gca, gca_val)) %>%
        select(-sca_val, -gca_val)
    }
  }, error = function(e) { print(paste("  Error GCA:", e$message)) })
  
  # Intentar pases progresivos (Passing)
  tryCatch({
    pass_data <- fb_player_season_stats(url, stat_type = "passing")
    Sys.sleep(12)
    prog_pass_col <- grep("PrgP|Prog", colnames(pass_data), value = TRUE)[1]
    if (!is.na(prog_pass_col)) {
      pass_subset <- pass_data %>%
        select(Player = !!player_col, Squad = !!squad_col, pp_val = !!prog_pass_col) %>%
        group_by(Player, Squad) %>%
        summarise(pp_val = sum(as.numeric(pp_val), na.rm = TRUE), .groups = 'drop')
      url_players <- left_join(url_players, pass_subset, by = c("Player", "Squad")) %>%
        mutate(progressive_passes = coalesce(progressive_passes, pp_val)) %>%
        select(-pp_val)
    }
  }, error = function(e) { print(paste("  Error passing:", e$message)) })
  
  # Intentar conducciones progresivas (Possession)
  tryCatch({
    poss_data <- fb_player_season_stats(url, stat_type = "possession")
    Sys.sleep(12)
    prog_carr_col <- grep("PrgC|Prog", colnames(poss_data), value = TRUE)[1]
    if (!is.na(prog_carr_col)) {
      poss_subset <- poss_data %>%
        select(Player = !!player_col, Squad = !!squad_col, pc_val = !!prog_carr_col) %>%
        group_by(Player, Squad) %>%
        summarise(pc_val = sum(as.numeric(pc_val), na.rm = TRUE), .groups = 'drop')
      url_players <- left_join(url_players, poss_subset, by = c("Player", "Squad")) %>%
        mutate(progressive_carries = coalesce(progressive_carries, pc_val)) %>%
        select(-pc_val)
    }
  }, error = function(e) { print(paste("  Error possession:", e$message)) })
  
  # Unir al acumulado
  if (is.null(combined_stats)) {
    combined_stats <- url_players
  } else {
    combined_stats <- bind_rows(combined_stats, url_players)
  }
}

# Guardar a CSV
if (!is.null(combined_stats)) {
  write.csv(combined_stats, output_path, row.names = FALSE, na = "")
  print("¡Scraping finalizado con éxito! Caché generado en data/fbref_qualifiers_cache.csv")
} else {
  print("No se pudo extraer ninguna estadística.")
}
