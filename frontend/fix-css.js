const fs = require('fs');
let css = fs.readFileSync('frontend/css/styles.css', 'utf-8');

const marker = '.input-hint {';
const markerIndex = css.lastIndexOf(marker);
if (markerIndex !== -1) {
    const endBlock = css.indexOf('}', markerIndex) + 1;
    css = css.substring(0, endBlock) + '\n\n';
}

const cleanStyles = `/* TIME RANGE SELECTION */
.time-range-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-top: 2rem;
  margin-bottom: 2rem;
}
.time-range-card {
  background: rgba(20,20,20,0.8);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}
.time-range-card i {
  font-size: 2rem;
  color: #aaa;
  transition: color 0.3s;
}
.time-range-card span {
  font-family: 'Outfit', sans-serif;
  font-weight: 600;
  font-size: 1.1rem;
  color: #fff;
}
.time-range-card small {
  font-family: 'Inter', sans-serif;
  color: #888;
  font-size: 0.85rem;
}
.time-range-card:hover {
  transform: translateY(-5px);
  border-color: rgba(255,255,255,0.4);
}
.time-range-card.selected {
  border-color: var(--survey-accent, #f5d061);
  background: rgba(255,255,255,0.05);
  box-shadow: 0 0 15px var(--survey-accent-glow, rgba(245, 208, 97, 0.4));
}
.time-range-card.selected i {
  color: var(--survey-accent, #f5d061);
}

/* RECOMMENDATIONS LIST & CATEGORIES */
.recommendations-list-container {
  max-height: 70vh;
  overflow-y: auto;
  overflow-x: hidden;
  text-align: left;
  padding: 10px 20px;
  /* Scrollbar custom */
  scrollbar-width: thin;
  scrollbar-color: #f5d061 #222;
}
.recommendations-list-container::-webkit-scrollbar {
  width: 8px;
}
.recommendations-list-container::-webkit-scrollbar-track {
  background: #222;
  border-radius: 4px;
}
.recommendations-list-container::-webkit-scrollbar-thumb {
  background-color: #f5d061;
  border-radius: 4px;
}

.category-section {
  margin-bottom: 3rem;
}
.category-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.5rem;
  color: #fff;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  padding-bottom: 0.5rem;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 10px;
}
.category-title i {
  color: var(--survey-accent, #f5d061);
}
.matches-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}
.out-of-schedule .matches-grid .rec-card {
  filter: grayscale(80%) opacity(0.6);
  transition: filter 0.3s;
}
.out-of-schedule .matches-grid .rec-card:hover {
  filter: grayscale(0%) opacity(1);
}
.out-of-schedule .category-title i {
  color: #888;
}
`;

fs.writeFileSync('frontend/css/styles.css', css + cleanStyles);
console.log('Fixed CSS');
