import os

css_path = r"c:\Users\user\Downloads\app_mundial\worldcup-app\frontend\style.css"
css_append = """
/* --- Execution Features: Skeletons, Error States, Staggered Animations --- */

/* Staggered Animations */
.matches-grid > div {
  animation: fadeUpStagger 0.5s cubic-bezier(0.4, 0, 0.2, 1) both;
}

.matches-grid > div:nth-child(1) { animation-delay: 0.05s; }
.matches-grid > div:nth-child(2) { animation-delay: 0.10s; }
.matches-grid > div:nth-child(3) { animation-delay: 0.15s; }
.matches-grid > div:nth-child(4) { animation-delay: 0.20s; }
.matches-grid > div:nth-child(5) { animation-delay: 0.25s; }
.matches-grid > div:nth-child(n+6) { animation-delay: 0.30s; }

@keyframes fadeUpStagger {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Skeleton Loader */
.skeleton-loader {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  gap: 1.5rem;
  width: 100%;
}

.skeleton-card {
  height: 200px;
  background: linear-gradient(90deg, var(--bg-tertiary) 25%, var(--bg-secondary) 50%, var(--bg-tertiary) 75%);
  background-size: 400% 100%;
  animation: skeletonLoading 1.5s ease-in-out infinite;
  border-radius: 20px;
  border: 1px solid var(--border-glass);
}

@keyframes skeletonLoading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Error State */
.error-state-card {
  text-align: center;
  padding: 3rem;
  background: var(--bg-card);
  border: 1px solid var(--border-glass);
  border-radius: 20px;
  color: var(--text-primary);
  grid-column: 1 / -1;
  box-shadow: var(--shadow-card);
}

.error-state-card .error-icon {
  font-size: 3rem;
  color: var(--accent-red);
  margin-bottom: 1rem;
}

.error-state-card h3 {
  font-family: var(--font-primary);
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  color: var(--accent-navy);
}

.error-state-card p {
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
}

.retry-btn {
  background: var(--accent-navy);
  color: #fff;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-family: var(--font-primary);
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition-fast);
}

.retry-btn:hover {
  background: var(--accent-red);
  transform: translateY(-2px);
}
"""

with open(css_path, "a", encoding="utf-8") as f:
    f.write(css_append)

print("CSS additions complete.")
