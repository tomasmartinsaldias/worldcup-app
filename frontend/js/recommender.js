// recommender.js
import { state } from './state.js';

export function calculateSmartScore(match, teams) {
  if (match.home_team.is_placeholder || match.away_team.is_placeholder) {
    return 5.0; // default for playoff TBD matches
  }
  
  const home = teams[match.home_team.fifa_code];
  const away = teams[match.away_team.fifa_code];
  
  if (!home || !away || !home.metrics || !away.metrics) {
    return 6.0;
  }
  
  // 1. Squad Value (0 to 2.5 points)
  const combVal = (home.metrics.market_value_eur || 0) + (away.metrics.market_value_eur || 0);
  const valScore = Math.min((combVal / 850.0) * 2.5, 2.5);
  
  // 2. Global Popularity (0 to 2.0 points)
  const avgPop = ((home.metrics.global_popularity_score || 50) + (away.metrics.global_popularity_score || 50)) / 2;
  const popScore = (avgPop / 100.0) * 2.0;
  
  // 3. Offensive Style (xG) (0 to 1.5 points)
  const avgXg = ((home.metrics.recent_xg_avg || 1.1) + (away.metrics.recent_xg_avg || 1.1)) / 2;
  const xgScore = Math.min((avgXg / 2.0) * 1.5, 1.5);
  
  // 4. Recent Performance / Current Form (0 to 1.5 points)
  const avgEff = ((home.metrics.efficiency_score_avg || 0.19) + (away.metrics.efficiency_score_avg || 0.19)) / 2;
  const effScore = Math.min((avgEff / 0.50) * 1.5, 1.5);
  
  // 5. Historical Card/Friction Intensity (0 to 1.0 points)
  const combCards = ((home.metrics.cards_per_match_avg || 1.3) + (away.metrics.cards_per_match_avg || 1.3)) / 2;
  const cardsScore = Math.min((combCards / 2.4) * 1.0, 1.0);
  
  // 6. Star Player count (0 to 1.0 points)
  const homeStars = home.squad ? home.squad.filter(p => p.is_star_player).length : 0;
  const awayStars = away.squad ? away.squad.filter(p => p.is_star_player).length : 0;
  const starScore = Math.min(((homeStars + awayStars) / 8.0) * 1.0, 1.0);
  
  // Stage Bonus (0.5 for knockout)
  const stageBonus = (match.stage && match.stage !== 'Group Stage') ? 0.5 : 0;
  
  let finalScore = valScore + popScore + xgScore + effScore + cardsScore + starScore + stageBonus;

  // --- USER PREFERENCES ADJUSTMENTS ---
  const prefs = state.userPreferences;
  if (prefs) {
    // Favorite Team Bonus
    if (prefs.favoriteTeam === home.fifa_code || prefs.favoriteTeam === away.fifa_code) {
      finalScore += 2.5;
    }

    // Match Style Adjustments
    if (prefs.matchStyle === 'closed') {
      // Reward low xG and high cards
      if (avgXg < 1.0) finalScore += 1.0;
      if (combCards > 1.5) finalScore += 0.5;
    } else if (prefs.matchStyle === 'chaotic') {
      // Reward high xG and low cards
      if (avgXg > 1.2) finalScore += 1.0;
      if (combCards < 1.0) finalScore += 0.5;
    }

    // Favorite Players Bonus
    if (prefs.favoritePlayers && prefs.favoritePlayers.length > 0) {
      const allPlayers = [...(home.squad || []), ...(away.squad || [])];
      prefs.favoritePlayers.forEach(favName => {
        if (!favName.trim()) return;
        const found = allPlayers.some(p => p.name.toLowerCase().includes(favName.trim().toLowerCase()));
        if (found) finalScore += 0.5;
      });
    }

    // Preferred Time Bonus
    if (prefs.preferredTime && prefs.preferredTime.length > 0 && match.kickoff_at) {
      const date = new Date(match.kickoff_at);
      const hour = date.getHours();
      let timeCat = '';
      if (hour < 12) timeCat = 'morning';
      else if (hour < 18) timeCat = 'afternoon';
      else timeCat = 'evening';

      if (prefs.preferredTime.includes(timeCat)) {
        finalScore += 1.5;
      }
    }
  }

  finalScore = Math.min(Math.max(finalScore, 1.0), 10.0);
  return parseFloat(finalScore.toFixed(1));
}
