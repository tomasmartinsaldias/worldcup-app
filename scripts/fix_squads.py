import os

filepath = 'frontend/js/ui/squads.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

split_marker = "startingPlayers.sort((a,b) => getPosOrder(getPosCategory(a)) - getPosOrder(getPosCategory(b)));"
parts = content.split(split_marker)
if len(parts) != 2:
    print("Error splitting")
    exit(1)

new_tail = """
  const SLOT_COORDS = {
      'GK': { x: 50, y: 5 },
      'RB': { x: 85, y: 20 }, 'RCB': { x: 65, y: 15 }, 'CB': { x: 50, y: 15 }, 'LCB': { x: 35, y: 15 }, 'LB': { x: 15, y: 20 },
      'RWB': { x: 90, y: 35 }, 'LWB': { x: 10, y: 35 },
      'CDM': { x: 50, y: 35 }, 'RDM': { x: 65, y: 35 }, 'LDM': { x: 35, y: 35 },
      'CM': { x: 50, y: 50 }, 'RCM': { x: 65, y: 50 }, 'LCM': { x: 35, y: 50 },
      'RM': { x: 85, y: 60 }, 'LM': { x: 15, y: 60 },
      'CAM': { x: 50, y: 70 }, 'RAM': { x: 68, y: 70 }, 'LAM': { x: 32, y: 70 },
      'RW': { x: 85, y: 80 }, 'LW': { x: 15, y: 80 },
      'ST': { x: 50, y: 85 }, 'CF': { x: 50, y: 85 }, 'RS': { x: 65, y: 85 }, 'LS': { x: 35, y: 85 },
      'RF': { x: 70, y: 80 }, 'LF': { x: 30, y: 80 }
  };

  const FORMATION_SLOTS = {
      '4-3-3': ['GK', 'RB', 'RCB', 'LCB', 'LB', 'CDM', 'RCM', 'LCM', 'RW', 'ST', 'LW'],
      '4-4-2': ['GK', 'RB', 'RCB', 'LCB', 'LB', 'RM', 'RCM', 'LCM', 'LM', 'RS', 'LS'],
      '4-2-3-1': ['GK', 'RB', 'RCB', 'LCB', 'LB', 'RDM', 'LDM', 'RM', 'CAM', 'LM', 'ST'],
      '3-4-2-1': ['GK', 'RCB', 'CB', 'LCB', 'RM', 'RCM', 'LCM', 'LM', 'RAM', 'LAM', 'ST'],
      '3-4-3': ['GK', 'RCB', 'CB', 'LCB', 'RM', 'RCM', 'LCM', 'LM', 'RW', 'ST', 'LW'],
      '4-1-4-1': ['GK', 'RB', 'RCB', 'LCB', 'LB', 'CDM', 'RM', 'RCM', 'LCM', 'LM', 'ST'],
      '3-5-2': ['GK', 'RCB', 'CB', 'LCB', 'RWB', 'RDM', 'LDM', 'LWB', 'CAM', 'RS', 'LS'],
      '5-4-1': ['GK', 'RWB', 'RCB', 'CB', 'LCB', 'LWB', 'RM', 'RCM', 'LCM', 'LM', 'ST'],
      '5-3-2': ['GK', 'RWB', 'RCB', 'CB', 'LCB', 'LWB', 'RCM', 'CM', 'LCM', 'RS', 'LS'],
  };

  let targetSlots = FORMATION_SLOTS[formationStr] || FORMATION_SLOTS['4-3-3'];
  let availableSlots = [...targetSlots];
  
  let assignedPlayers = [];
  
  startingPlayers.forEach(p => {
      let prefPos = (p.exact_position || '').toUpperCase();
      let assignedSlot = null;
      
      if (availableSlots.includes(prefPos)) {
          assignedSlot = prefPos;
      } else {
          let cat = getPosCategory(p);
          let candidates = [];
          if (cat === 'GK') candidates = availableSlots.filter(s => s === 'GK');
          else if (cat === 'DEF') candidates = availableSlots.filter(s => s.includes('B'));
          else if (cat === 'MID') candidates = availableSlots.filter(s => s.includes('M'));
          else if (cat === 'FWD') candidates = availableSlots.filter(s => s.includes('S') || s.includes('F') || s.includes('W') || s.includes('T'));
          
          if (candidates.length > 0) {
              assignedSlot = candidates[0];
          } else {
              assignedSlot = availableSlots[0];
          }
      }
      
      if (assignedSlot) {
          availableSlots = availableSlots.filter(s => s !== assignedSlot);
          assignedPlayers.push({ player: p, slot: assignedSlot });
      }
  });

  const createPlayerHTML = (p, label, num) => {
    if (!p) return '';
    const lastName = p.name.split(' ').pop();
    let ratingVal = p.efficiency_score !== null ? (p.efficiency_score * 4 + 5.5) : 6.5; 
    let rating = ratingVal.toFixed(1);
    
    let ratingClass = 'rating-yellow';
    if (ratingVal >= 7.0) ratingClass = 'rating-green';
    else if (ratingVal < 6.0) ratingClass = 'rating-red';

    const parts = p.name.split(' ');
    const initials = parts.length > 1 ? parts[0][0] + parts[parts.length-1][0] : parts[0].substring(0, 2);
    
    return `
      <div class="sofascore-player" title="${p.name} - ${p.club}" onclick="window.openPlayerProfile('${team.fifa_code}', ${p.id})">
        <div class="sofa-photo-circle">
          <span>${initials.toUpperCase()}</span>
          <div class="sofa-rating-badge ${ratingClass}">${rating}</div>
        </div>
        <div class="sofa-player-name">
          <span class="sofa-player-num">${num}</span> ${lastName}
        </div>
      </div>
    `;
  };

  container.innerHTML = ''; // Limpiamos primero

  // Add formation badge
  const badge = document.createElement('div');
  badge.style.cssText = 'position: absolute; top: 1rem; right: 1rem; background: rgba(255,255,255,0.2); padding: 4px 8px; border-radius: 4px; font-weight: bold; color: white; font-size: 0.8rem; border: 1px solid rgba(255,255,255,0.3); z-index: 10; font-family: var(--font-primary);';
  badge.textContent = `Formación: ${formationStr}`;
  container.appendChild(badge);

  // Assign numbers (1 to 11) for display based on Y coordinate to be somewhat realistic
  assignedPlayers.sort((a,b) => SLOT_COORDS[a.slot].y - SLOT_COORDS[b.slot].y);
  
  assignedPlayers.forEach((item, index) => {
      let coords = SLOT_COORDS[item.slot] || { x: 50, y: 50 };
      
      const playerWrapper = document.createElement('div');
      playerWrapper.style.position = 'absolute';
      playerWrapper.style.left = `${coords.x}%`;
      playerWrapper.style.bottom = `${coords.y}%`;
      playerWrapper.style.transform = 'translate(-50%, 50%)'; // Center precisely on coordinate
      playerWrapper.style.zIndex = '10';
      
      let num = index + 1;
      playerWrapper.innerHTML = createPlayerHTML(item.player, item.slot, num);
      container.appendChild(playerWrapper);
  });
}
"""

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(parts[0] + split_marker + "\n" + new_tail)
print("Fix applied successfully")
