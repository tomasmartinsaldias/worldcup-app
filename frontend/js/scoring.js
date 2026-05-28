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
  const valScore = Math.min((combVal / 850.0) * 2.5, 2.5); // Max points at 850M+ combined
  
  // 2. Global Popularity (0 to 2.0 points)
  const avgPop = ((home.metrics.global_popularity_score || 50) + (away.metrics.global_popularity_score || 50)) / 2;
  const popScore = (avgPop / 100.0) * 2.0;
  
  // 3. Offensive Style (xG) (0 to 1.5 points)
  const avgXg = ((home.metrics.recent_xg_avg || 1.1) + (away.metrics.recent_xg_avg || 1.1)) / 2;
  const xgScore = Math.min((avgXg / 2.0) * 1.5, 1.5); // Max points at 2.0 xG
  
  // 4. Recent Performance / Current Form (0 to 1.5 points)
  const avgEff = ((home.metrics.efficiency_score_avg || 0.19) + (away.metrics.efficiency_score_avg || 0.19)) / 2;
  const effScore = Math.min((avgEff / 0.50) * 1.5, 1.5); // Max points at 0.50 average efficiency
  
  // 5. Historical Card/Friction Intensity (0 to 1.0 points)
  const combCards = ((home.metrics.cards_per_match_avg || 1.3) + (away.metrics.cards_per_match_avg || 1.3)) / 2;
  const cardsScore = Math.min((combCards / 2.4) * 1.0, 1.0); // Max points at 2.4 cards per match
  
  // 6. Star Player count (0 to 1.0 points)
  const homeStars = home.squad ? home.squad.filter(p => p.is_star_player).length : 0;
  const awayStars = away.squad ? away.squad.filter(p => p.is_star_player).length : 0;
  const starScore = Math.min(((homeStars + awayStars) / 8.0) * 1.0, 1.0); // Max points at 8 stars
  
  // Stage Bonus (0.5 for knockout)
  const stageBonus = (match.stage && match.stage !== 'Group Stage') ? 0.5 : 0;
  
  let finalScore = valScore + popScore + xgScore + effScore + cardsScore + starScore + stageBonus;
  finalScore = Math.min(Math.max(finalScore, 1.0), 10.0);
  return parseFloat(finalScore.toFixed(1));
}

export function calculateFormRating(player) {
  let ratingVal = 6.5; // default fallback
  
  if (player.minutes_recent && player.minutes_recent > 0) {
    const p90 = 90.0 / player.minutes_recent;
    const xG90 = (player.xG_intl || 0) * p90;
    const sca90 = (player.sca_intl || 0) * p90;
    const gca90 = (player.gca_intl || 0) * p90;
    const progP90 = (player.progressive_passes_intl || 0) * p90;
    const progC90 = (player.progressive_carries_intl || 0) * p90;
    
    let baseScore = 6.0;
    let performance = 0;
    
    const pos = (player.position || '').toLowerCase();
    if (pos.includes('delantero') || pos.includes('forward') || pos.includes('atacante')) {
      performance = (xG90 * 2.0) + (gca90 * 1.5) + (sca90 * 0.2);
    } else if (pos.includes('centrocampista') || pos.includes('midfielder')) {
      performance = (sca90 * 0.4) + (progP90 * 0.15) + (gca90 * 1.0) + (progC90 * 0.1);
    } else if (pos.includes('defensa') || pos.includes('defender')) {
      performance = (progC90 * 0.2) + (progP90 * 0.2) + (sca90 * 0.3);
    } else if (pos.includes('portero') || pos.includes('goalkeeper')) {
      let gkBase = 1.0;
      if (player.market_value_eur) gkBase += Math.min(player.market_value_eur / 20.0, 1.5);
      if (player.caps) gkBase += Math.min(player.caps / 50.0, 1.0);
      performance = player.efficiency_score ? (player.efficiency_score * 3) : gkBase;
    } else {
      performance = (xG90 * 0.5) + (sca90 * 0.2) + (progP90 * 0.1);
    }
    
    const effBonus = player.efficiency_score !== null ? (player.efficiency_score * 1.5) : 0;
    ratingVal = baseScore + performance + effBonus;
  } else if (player.efficiency_score !== null) {
    ratingVal = player.efficiency_score * 4 + 5.5;
  }

  return Math.min(Math.max(ratingVal, 5.0), 9.9);
}
