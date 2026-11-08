// A01 — Static card analysis. Parses PLAYER_HEROES / ENEMY_MECHS / STAGES straight out of the
// game HTML (no hand-copied numbers) and writes analysis/cards.json + analysis/cards.md.
const fs = require("fs");
const path = require("path");
const SRC = "/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/WebPlayable/cardfront_cradle_of_echoes_playable.html";
const OUTD = path.join(__dirname);
const html = fs.readFileSync(SRC, "utf8");

function parseBlock(name) {
  const start = html.indexOf(`const ${name} = [`);
  const end = html.indexOf("];", start);
  const block = html.slice(start, end);
  const re = /id:\s*"([^"]+)",\s*name:\s*"([^"]+)",\s*nesw:\s*\[(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\]/g;
  const out = [];
  let m;
  while ((m = re.exec(block))) out.push({ id: m[1], name: m[2], nesw: [m[3], m[4], m[5], m[6]].map(Number), line: html.slice(0, start + m.index).split("\n").length + 2 });
  return out;
}
const heroes = parseBlock("PLAYER_HEROES");
const enemies = parseBlock("ENEMY_MECHS");
const stages = [...html.matchAll(/bossId:\s*"([^"]+)".*?aiBonus:\s*(\d+)/g)].map((m) => ({ bossId: m[1], aiBonus: Number(m[2]) }));
const E = ["N", "E", "S", "W"];
const OPP = [2, 3, 0, 1];
const sum = (a) => a.reduce((x, y) => x + y, 0);
const mean = (a) => sum(a) / a.length;
const sd = (a) => Math.sqrt(mean(a.map((x) => (x - mean(a)) ** 2)));
const clamp9 = (v) => Math.min(9, v);
const eff = (nesw, b) => nesw.map((v) => clamp9(v + b));

const all = [...heroes.map((c) => ({ ...c, side: "hero" })), ...enemies.map((c) => ({ ...c, side: "enemy" }))];
const perCard = all.map((c) => ({ id: c.id, name: c.name, side: c.side, nesw: c.nesw, total: sum(c.nesw), min: Math.min(...c.nesw), max: Math.max(...c.nesw), sd: +sd(c.nesw).toFixed(2), line: c.line }));

// strict dominance across all 16
const dominance = [];
for (const a of all) for (const b of all) {
  if (a === b) continue;
  if (a.nesw.every((v, i) => v >= b.nesw[i]) && a.nesw.some((v, i) => v > b.nesw[i])) dominance.push({ dominant: a.id, dominated: b.id, sameSide: a.side === b.side });
}
const identical = [];
for (let i = 0; i < all.length; i++) for (let j = i + 1; j < all.length; j++) if (all[i].nesw.join() === all[j].nesw.join()) identical.push([all[i].id, all[j].id, all[i].nesw]);

// capture matrix: hero H placed on side d of enemy X captures if H[d] > X[opp d]
function captureFacings(att, def) { return [0, 1, 2, 3].filter((d) => att[d] > def[OPP[d]]).map((d) => E[d]); }
const conditions = [
  { key: "S1-2 unboosted", heroB: 0, aiB: 0 }, { key: "S1-2 boosted", heroB: 1, aiB: 0 },
  { key: "S3-4 unboosted", heroB: 0, aiB: 1 }, { key: "S3-4 boosted", heroB: 1, aiB: 1 },
];
const condSummary = conditions.map((cd) => {
  let hc = 0, ec = 0, n = 0;
  for (const h of heroes) for (const x of enemies) {
    const H = eff(h.nesw, cd.heroB), X = eff(x.nesw, cd.aiB);
    hc += captureFacings(H, X).length; ec += captureFacings(X, H).length; n += 4;
  }
  return { condition: cd.key, heroBoost: cd.heroB, aiBonus: cd.aiB, heroCapturesEnemyPct: +(100 * hc / n).toFixed(1), enemyCapturesHeroPct: +(100 * ec / n).toFixed(1), facings: n };
});
const matrixS1 = heroes.map((h) => ({ hero: h.id, cells: enemies.map((x) => `${captureFacings(h.nesw, x.nesw).length}/${captureFacings(x.nesw, h.nesw).length}`) }));
const matrixS3 = heroes.map((h) => ({ hero: h.id, cells: enemies.map((x) => `${captureFacings(h.nesw, eff(x.nesw, 1)).length}/${captureFacings(eff(x.nesw, 1), h.nesw).length}`) }));

// per-edge distributions
const edgeDist = {};
for (const side of ["hero", "enemy"]) {
  const cs = all.filter((c) => c.side === side);
  edgeDist[side] = E.map((e, i) => ({ edge: e, values: cs.map((c) => c.nesw[i]), mean: +mean(cs.map((c) => c.nesw[i])).toFixed(2) }));
}
// average power per stage
const heroAvg = mean(heroes.flatMap((h) => h.nesw));
const enemyAvg = mean(enemies.flatMap((x) => x.nesw));
const stagePower = stages.map((s, i) => ({
  stage: i + 1, bossId: s.bossId, aiBonus: s.aiBonus,
  heroAvgEdgeUnboosted: +heroAvg.toFixed(3),
  heroAvgEdgeBoosted: +mean(heroes.flatMap((h) => eff(h.nesw, 1))).toFixed(3),
  enemyAvgEdge: +mean(enemies.flatMap((x) => eff(x.nesw, s.aiBonus))).toFixed(3),
  gapUnboosted: +(heroAvg - mean(enemies.flatMap((x) => eff(x.nesw, s.aiBonus)))).toFixed(3),
}));
// clamp losses and invulnerable edges
const clampLoss = all.flatMap((c) => c.nesw.map((v, i) => ({ id: c.id, edge: E[i], v })).filter((x) => x.v >= 9));
const invulnerable = conditions.map((cd) => {
  const list = [];
  for (const x of enemies) {
    const X = eff(x.nesw, cd.aiB);
    for (let i = 0; i < 4; i++) {
      const best = Math.max(...heroes.map((h) => eff(h.nesw, cd.heroB)[OPP[i]]));
      if (best <= X[i]) list.push(`${x.id}.${E[i]}=${X[i]} (best hero ${E[OPP[i]]}=${best})`);
    }
  }
  const heroSafe = [];
  for (const h of heroes) {
    const H = eff(h.nesw, cd.heroB);
    for (let i = 0; i < 4; i++) {
      const best = Math.max(...enemies.map((x) => eff(x.nesw, cd.aiB)[OPP[i]]));
      if (best <= H[i]) heroSafe.push(`${h.id}.${E[i]}=${H[i]}`);
    }
  }
  return { condition: cd.key, enemyEdgesNoHeroCanBeat: list, heroEdgesNoEnemyCanBeat: heroSafe.length, heroEdgesTotal: heroes.length * 4 };
});

const result = { source: SRC, heroes: heroes.length, enemies: enemies.length, stages, perCard, totals: { heroAvgEdge: +heroAvg.toFixed(3), enemyAvgEdge: +enemyAvg.toFixed(3), heroAvgTotal: +mean(heroes.map((h) => sum(h.nesw))).toFixed(2), enemyAvgTotal: +mean(enemies.map((x) => sum(x.nesw))).toFixed(2), minHeroTotal: Math.min(...heroes.map((h) => sum(h.nesw))), maxEnemyTotal: Math.max(...enemies.map((x) => sum(x.nesw))) }, edgeDist, dominance, identical, condSummary, matrixS1, matrixS3, stagePower, clampLoss, invulnerable };
fs.writeFileSync(path.join(OUTD, "cards.json"), JSON.stringify(result, null, 2));

// markdown
let md = `# Static card analysis (generated by analysis/A01_card_analysis.js from ${path.basename(SRC)})\n\n`;
md += `| Card | Side | N | E | S | W | Total | Min | Max | SD |\n|---|---|---|---|---|---|---|---|---|---|\n`;
for (const c of perCard) md += `| ${c.name} (\`${c.id}\`, L${c.line}) | ${c.side} | ${c.nesw.join(" | ")} | **${c.total}** | ${c.min} | ${c.max} | ${c.sd} |\n`;
md += `\nHero avg edge ${result.totals.heroAvgEdge}, enemy avg edge ${result.totals.enemyAvgEdge}; hero avg total ${result.totals.heroAvgTotal} vs enemy ${result.totals.enemyAvgTotal}; weakest hero total ${result.totals.minHeroTotal} > strongest enemy total ${result.totals.maxEnemyTotal}.\n\n`;
md += `## Per-edge means\n\n| Side | N | E | S | W |\n|---|---|---|---|---|\n`;
for (const side of ["hero", "enemy"]) md += `| ${side} | ${edgeDist[side].map((e) => e.mean).join(" | ")} |\n`;
md += `\n## Capture likelihood per (hero, enemy, facing) triple\n\n| Condition | hero boost | aiBonus | hero captures enemy | enemy captures hero |\n|---|---|---|---|---|\n`;
for (const c of condSummary) md += `| ${c.condition} | +${c.heroBoost} | +${c.aiBonus} | ${c.heroCapturesEnemyPct}% | ${c.enemyCapturesHeroPct}% |\n`;
const mtable = (mx, title) => {
  let s = `\n## ${title}\nCell = facings (of 4) where hero captures enemy / enemy captures hero.\n\n| hero \\ enemy | ${enemies.map((x) => x.id.replace("e_", "")).join(" | ")} |\n|---|${enemies.map(() => "---").join("|")}|\n`;
  for (const row of mx) s += `| ${row.hero.replace("h_", "")} | ${row.cells.join(" | ")} |\n`;
  return s;
};
md += mtable(matrixS1, "Dominance matrix — Stages 1–2, unboosted hero (aiBonus 0)");
md += mtable(matrixS3, "Dominance matrix — Stages 3–4, unboosted hero vs aiBonus +1");
md += `\n## Strict dominance (A ≥ B on every edge, > on at least one)\n\n${dominance.length} pairs; same-side pairs: ${dominance.filter((d) => d.sameSide).map((d) => `${d.dominant} ≻ ${d.dominated}`).join(", ") || "none"}.\nCross-side: ${dominance.filter((d) => !d.sameSide).length} pairs (all hero ≻ enemy: ${dominance.filter((d) => !d.sameSide).every((d) => d.dominant.startsWith("h_"))}).\n\nIdentical stat lines: ${identical.map((p) => `${p[0]} = ${p[1]} [${p[2]}]`).join("; ") || "none"}.\n`;
md += `\n## Average edge power per stage\n\n| Stage | bossId | aiBonus | hero avg (unboosted) | hero avg (boosted) | enemy avg | gap (unboosted) |\n|---|---|---|---|---|---|---|\n`;
for (const s of stagePower) md += `| ${s.stage} | ${s.bossId} | ${s.aiBonus} | ${s.heroAvgEdgeUnboosted} | ${s.heroAvgEdgeBoosted} | ${s.enemyAvgEdge} | ${s.gapUnboosted} |\n`;
md += `\n## Clamp-at-9 and unbeatable edges\n\nEdges already at 9 (boost wasted): ${clampLoss.map((c) => `${c.id}.${c.edge}`).join(", ") || "none"}.\n\n`;
for (const iv of invulnerable) md += `- ${iv.condition}: enemy edges no hero can beat: ${iv.enemyEdgesNoHeroCanBeat.join(", ") || "none"}; hero edges no enemy can beat: ${iv.heroEdgesNoEnemyCanBeat}/${iv.heroEdgesTotal}\n`;
fs.writeFileSync(path.join(OUTD, "cards.md"), md);
console.log(md);
