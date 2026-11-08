// R11 — Debug/test hooks ship in the production page:
//  (a) ?autotest=1 auto-plays a game (camera changes, nudge, reroll, slide, deploys) without user input
//      and POSTs a report to /__osascript_report__;
//  (b) the hooks use location.search.includes(), so unrelated params such as ?xautotest=1 also trigger;
//  (c) the autotest looks up #cam-select, but the element id is #camera-select (dead branch);
//  (d) the autotest labels any non-win "COMPLETED", never DEFEAT.
const L = require("./_lib");
(async () => {
  const rep = L.reporter("R11_debug_hooks_in_production", "autotest/dragtest hooks reachable from URL");
  const ctx = await L.open({ seed: 1111, query: "ref=xautotest=1" });
  const { page, requests } = ctx;
  const statuses = [];
  page.on("response", (r) => { if (r.url().includes("__osascript_report__")) statuses.push(r.status()); });
  const t0 = await L.snap(page);
  await page.waitForFunction(() => document.title.startsWith("TEST_COMPLETE"), null, { timeout: 20000 }).catch(() => {});
  await page.waitForTimeout(500);
  const t1 = await L.snap(page);
  const title = await page.title();
  const report = await page.evaluate(() => window.__OSASCRIPT_TEST_REPORT__ || null);
  rep.check("(b) URL '?ref=xautotest=1' (substring match) started the autotest", title.startsWith("TEST_COMPLETE"), title);
  rep.check("(a) the game was played with zero user input (hand shrank, dice/reroll spent)", t1.hand.length < 5 && t1.rerollsLeft < 2, { handBefore: t0.hand.length, handAfter: t1.hand.length, rerollsAfter: t1.rerollsLeft });
  const posts = requests.filter((r) => r.url.includes("__osascript_report__") && r.method === "POST");
  rep.check("(a) report POSTed to /__osascript_report__ on the serving origin", posts.length >= 1, { posts: posts.length, statuses });
  const camSel = await page.evaluate(() => [!!document.getElementById("cam-select"), !!document.getElementById("camera-select")]);
  rep.check("(c) #cam-select does not exist (autotest camera UI sync is dead code)", camSel[0] === false && camSel[1] === true, camSel);
  if (report) {
    rep.note("autotestReport", { outcome: report.outcome, finalScore: report.finalScore, turnsPlayed: report.turnsPlayed });
    const lostOrNot = report.finalScore.player > report.finalScore.boss ? "VICTORY" : "COMPLETED";
    rep.check("(d) autotest outcome is never DEFEAT ('COMPLETED' for losses)", report.outcome === lostOrNot && report.outcome !== "DEFEAT", report.outcome);
  }
  await rep.finish(ctx);
})().catch((e) => { console.error(e); process.exit(1); });
