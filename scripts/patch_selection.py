import os

filepath = 'frontend/js/ui/squads.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazamos la lógica de selección de fallback
old_fallback = """      startingPlayers = [];
      startingPlayers.push(...byPos['GK'].slice(0, 1));   // 1 arquero
      startingPlayers.push(...byPos['DEF'].slice(0, needDef));
      startingPlayers.push(...byPos['MID'].slice(0, needMid));
      startingPlayers.push(...byPos['FWD'].slice(0, needFwd));"""

new_fallback = """      // Funciones de ayuda para encajar jugadores en sus roles
      const pickBestForRoles = (pool, roles, count) => {
          let selected = [];
          let remainingPool = [...pool];
          roles.forEach(role => {
              let matchIdx = remainingPool.findIndex(p => p.exact_position === role);
              if (matchIdx >= 0) {
                  selected.push(remainingPool.splice(matchIdx, 1)[0]);
              } else {
                  // Partial match (e.g. LCB matches CB or LB)
                  let fallbackIdx = remainingPool.findIndex(p => (p.exact_position||'').includes(role.replace('B','').replace('M','').replace('W','')) || (p.exact_position||'').endsWith(role.slice(-1)));
                  if (fallbackIdx >= 0) {
                      selected.push(remainingPool.splice(fallbackIdx, 1)[0]);
                  } else {
                     if(remainingPool.length > 0) selected.push(remainingPool.shift());
                  }
              }
          });
          while(selected.length < count && remainingPool.length > 0) selected.push(remainingPool.shift());
          return selected;
      };

      const DEF_ROLES = { 3: ['LCB', 'CB', 'RCB'], 4: ['LB', 'LCB', 'RCB', 'RB'], 5: ['LWB', 'LCB', 'CB', 'RCB', 'RWB'] };
      const MID_ROLES = { 3: ['LCM', 'CDM', 'RCM'], 4: ['LM', 'LCM', 'RCM', 'RM'], 5: ['LM', 'LCM', 'CDM', 'RCM', 'RM'] };
      const FWD_ROLES = { 1: ['ST'], 2: ['LS', 'RS'], 3: ['LW', 'ST', 'RW'] };

      startingPlayers = [];
      startingPlayers.push(...byPos['GK'].slice(0, 1));   // 1 arquero
      startingPlayers.push(...pickBestForRoles(byPos['DEF'], DEF_ROLES[needDef] || [], needDef));
      startingPlayers.push(...pickBestForRoles(byPos['MID'], MID_ROLES[needMid] || [], needMid));
      startingPlayers.push(...pickBestForRoles(byPos['FWD'], FWD_ROLES[needFwd] || [], needFwd));"""

content = content.replace(old_fallback, new_fallback)

# Reemplazamos la extracción de líneas para agregar orden horizontal
old_lines = """  // Extraemos los jugadores por cada línea de la formación
  let renderedLines = [];
  for(let i=0; i<formParts.length; i++) {
     let numInLine = formParts[i];
     let linePlayers = startingPlayers.slice(playerIdx, playerIdx + numInLine);
     playerIdx += numInLine;
     renderedLines.push(linePlayers);
  }"""

new_lines = """  // Extraemos los jugadores por cada línea de la formación
  const getHorizontalOrder = (p) => {
      let pos = (p.exact_position || '').toUpperCase();
      if (pos.startsWith('L')) return -1;
      if (pos.startsWith('R')) return 1;
      return 0; // Center
  };

  let renderedLines = [];
  for(let i=0; i<formParts.length; i++) {
     let numInLine = formParts[i];
     let linePlayers = startingPlayers.slice(playerIdx, playerIdx + numInLine);
     // Ordenar de izquierda a derecha (LB -> CB -> RB)
     linePlayers.sort((a,b) => getHorizontalOrder(a) - getHorizontalOrder(b));
     playerIdx += numInLine;
     renderedLines.push(linePlayers);
  }"""

content = content.replace(old_lines, new_lines)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Selection and sorting patched successfully")
