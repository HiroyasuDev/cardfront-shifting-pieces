// MiroFish-style playtest personas for Cardfront: Cradle of Echoes (grounded run).
// Naming follows Backend/synapse_miro_strands_sim_engine.py NPC_PERSONAS (CamelCase archetype handles).
// Every behavioural parameter below is consumed by play_swarm.js — nothing here is decorative.
//
// policy:        "greedy"        – maximise immediate flips (ties: own-edge safety)
//                "lane"          – greedy + bonus for boosted-column placement & column control
//                "expectimax"    – 2-ply: my plan, then E[boss greedy reply] over unseen enemy cards
//                "minimax"       – 2-ply worst-case boss reply
//                "minmax3"       – expectimax + 3rd ply (my best follow-up) for the top-K plans
//                "spectacle"     – maximise flips this turn incl. slide combos (ignores safety)
//                "random_biased" – uniformly random legal move, but takes an obvious flip w.p. flipBias
//                "coverage"      – expectimax, tie-broken toward never-yet-played heroes / unused mechanics
// epsilon:       probability a turn's chosen placement is replaced by a random legal placement (error/noise)
// thinkMs:       [min,max] modeled decision time per turn (waited for real in the browser)
// nudge:         "never" | "when_gain" (nudge only if plan value improves) | "eval" (search all nudge combos)
// reroll:        "never" | "drama" (reroll w.p. 0.5 when <2 cols boosted) | "low_boost" (reroll when 0 cols boosted)
// slide:         "never" | "when_gain" | "eval" | "spectacle"
// dragJitter:    std-dev of release point as a fraction of tile size (real mouse sloppiness)
// misdropProb:   probability a drag is first released over a non-tile area (springs back, retried)
// dragSteps:     mouse.move interpolation steps (speed of the drag gesture)
// patience:      frustration budget; when cumulative frustration > patience the persona "would quit"
//                (logged as would_quit; matches are still completed so every persona has full coverage)
// ownerMisread:  probability per enemy-adjacent edge of misjudging tile ownership (colour-vision model)
module.exports = [
  {
    id: "p01", name: "TripleTriadEdgeVeteran", archetype: "Triple Triad veteran (FF8/FF14 card player)",
    policy: "minimax", epsilon: 0.03, thinkMs: [1200, 2600], nudge: "when_gain", reroll: "never", slide: "when_gain",
    dragJitter: 0.08, misdropProb: 0.0, dragSteps: 18, patience: 3.0, ownerMisread: 0,
    voice: "Has played thousands of Triple Triad hands; judges everything against Same/Plus/Combo rules and corner-safety play.",
  },
  {
    id: "p02", name: "QueensBloodLaneBuilder", archetype: "Queen's Blood (FF7 Rebirth) fan",
    policy: "lane", epsilon: 0.06, thinkMs: [1400, 2800], nudge: "when_gain", reroll: "low_boost", slide: "when_gain",
    dragJitter: 0.10, misdropProb: 0.02, dragSteps: 16, patience: 3.0, ownerMisread: 0,
    voice: "Thinks in lanes/rows and pawn ranks; loves board-control mini-games inside bigger RPGs.",
  },
  {
    id: "p03", name: "SnapCompetitiveGrinder", archetype: "Marvel Snap competitive grinder",
    policy: "expectimax", epsilon: 0.04, thinkMs: [400, 950], nudge: "eval", reroll: "low_boost", slide: "eval",
    dragJitter: 0.14, misdropProb: 0.03, dragSteps: 8, patience: 2.0, ownerMisread: 0,
    voice: "Plays 3-minute ranked games all day; values speed, tension, and meaningful last-turn decisions.",
  },
  {
    id: "p04", name: "CasualMobileTapper", archetype: "Casual mobile player",
    policy: "random_biased", flipBias: 0.6, epsilon: 0.0, thinkMs: [600, 1500], nudge: "never", reroll: "drama", slide: "never",
    dragJitter: 0.22, misdropProb: 0.10, dragSteps: 6, patience: 1.5, ownerMisread: 0,
    voice: "Plays on the bus in short bursts; doesn't read rules text, wants it to feel good immediately.",
  },
  {
    id: "p05", name: "IntoTheBreachTactician", archetype: "Into the Breach tactician",
    policy: "minimax", epsilon: 0.0, thinkMs: [2500, 4500], nudge: "eval", reroll: "never", slide: "eval",
    dragJitter: 0.06, misdropProb: 0.0, dragSteps: 22, patience: 3.5, ownerMisread: 0,
    voice: "Wants perfect information and telegraphed enemy intent; hates hidden randomness deciding outcomes.",
  },
  {
    id: "p06", name: "TCGFirstTimeNewcomer", archetype: "Complete TCG newcomer",
    policy: "random_biased", flipBias: 0.35, epsilon: 0.0, thinkMs: [2500, 6000], nudge: "never", reroll: "never", slide: "never",
    dragJitter: 0.25, misdropProb: 0.18, dragSteps: 30, patience: 1.5, ownerMisread: 0,
    voice: "Has never played a card game beyond Solitaire; unsure what the numbers on the card edges mean.",
  },
  {
    id: "p07", name: "StreamerSpectacleCaster", archetype: "Streamer / spectator-minded",
    policy: "spectacle", epsilon: 0.08, thinkMs: [900, 2000], nudge: "when_gain", reroll: "drama", slide: "spectacle",
    dragJitter: 0.12, misdropProb: 0.03, dragSteps: 14, patience: 2.0, ownerMisread: 0,
    voice: "Narrates every move for chat; wants big readable swings, juicy effects, and thumbnail-worthy moments.",
  },
  {
    id: "p08", name: "DeuteranopiaColorReader", archetype: "Colourblind (deuteranopia) player",
    policy: "expectimax", epsilon: 0.05, thinkMs: [1600, 3200], nudge: "when_gain", reroll: "never", slide: "when_gain",
    dragJitter: 0.10, misdropProb: 0.02, dragSteps: 16, patience: 2.5, ownerMisread: 0.08,
    voice: "Has deuteranopia (red-green); relies on shape/text cues rather than red vs green/gold distinctions.",
  },
  {
    id: "p09", name: "CompletionistCollector", archetype: "Completionist",
    policy: "coverage", epsilon: 0.03, thinkMs: [1400, 2600], nudge: "when_gain", reroll: "low_boost", slide: "when_gain",
    forceTryMechanics: true, dragJitter: 0.09, misdropProb: 0.01, dragSteps: 16, patience: 3.5, ownerMisread: 0,
    voice: "Wants to see every card, every stage, every mechanic; looks for collection/progression hooks.",
  },
  {
    id: "p10", name: "MinMaxOptimizer", archetype: "Min-max optimizer",
    policy: "minmax3", epsilon: 0.0, thinkMs: [1800, 3200], nudge: "eval", reroll: "never", slide: "eval",
    dragJitter: 0.06, misdropProb: 0.0, dragSteps: 18, patience: 3.0, ownerMisread: 0,
    voice: "Solves games; computes expected values, looks for dominant strategies and degenerate lines.",
  },
];
