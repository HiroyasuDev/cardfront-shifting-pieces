// Simulation suites. Every job: { label, policy, stage, n, seedBase, opts }
"use strict";
const MAIN_POLICIES = ["random", "greedy", "greedy_dice", "greedy_slide", "greedy_all", "lookahead",
  "expert", "expert_margin", "expert_nodice", "expert_noslide", "expert_notools", "oracle"];
const N = +(process.env.NGAMES || 10000);

function grid(prefix, policies, stages, opts, n) {
  const jobs = [];
  for (const st of stages) for (const p of policies) {
    const games = (p === "expert_margin") ? Math.min(n || N, 500) : (n || N);
    jobs.push({ label: `${prefix}_${p}_s${st + 1}`, policy: p, stage: st, n: games, seedBase: 1000000 * (st + 1), opts: opts || {} });
  }
  return jobs;
}

// What-if variants (each re-simulated with the same seeds as the baseline)
const VARIANTS = {
  base:            {},
  bossTieRandom:   { bossTieRandom: true },                       // fix: genuinely random tie-break
  noRefill:        { nudgeRefill: 0 },                            // nudges do not refill
  coldDice:        { startDice: [1, 2, 3] },                      // no free boosts at stage start
  slideNoCapture:  { slideCanCapture: false },                    // slide repositions only
  noSlide:         { slideEnabled: false },
  aiBonus2:        { aiBonus: 2 },
  aiBonus3:        { aiBonus: 3 },
  tuned:           { startDice: [1, 2, 3], slideCanCapture: false }, // proposed package (bonus via stage table)
};

const SUITES = {
  main: () => grid("main", MAIN_POLICIES, [0, 1, 2, 3]),
  smoke: () => grid("smoke", MAIN_POLICIES, [0, 2], {}, 200),
  variants: () => {
    const jobs = [];
    const pols = ["random", "greedy", "greedy_slide", "greedy_all", "lookahead", "expert"];
    for (const [v, opts] of Object.entries(VARIANTS)) {
      if (v === "base") continue;
      const stages = (v === "aiBonus2" || v === "aiBonus3") ? [0] : [0, 2];
      jobs.push(...grid(`var_${v}`, pols, stages, opts, +(process.env.NVAR || 10000)));
    }
    return jobs;
  },
};
SUITES.VARIANTS = VARIANTS;
module.exports = SUITES;
