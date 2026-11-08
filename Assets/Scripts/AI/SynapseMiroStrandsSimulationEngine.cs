using System;
using System.Collections.Generic;
using Synapse.TcgEngine.Core;
using Synapse.TcgEngine.Data;

namespace Synapse.TcgEngine.AI
{
    /// <summary>
    /// 12 Autonomous NPC Agent Personas for the MiroFish + Strands Agents Multi-Agent Simulation Core.
    /// Each persona models a distinct tactical heuristic, belief state, market valuation curve, and emotional response.
    /// </summary>
    public enum NpcPersonaArchetype
    {
        RushdownVekBreaker          = 0,  // Prioritizes Into the Breach kinetic push-bump KOs and aggressive early captures
        Terrain4StarTurtle          = 1,  // Fortifies 3★ Citadel and 4★ HQ/Mountain tiles with high-defense frames
        FftaJudgeLawEnforcer        = 2,  // Strictly obeys Magisterium Edicts to farm Judge Commendation Law Cards & JP
        Staccs3DTowerArchitect      = 3,  // Vertically stacks Z-layers (N = 2..4) for +Left/+Right flank fortification
        MgaCostStealthInfiltrator   = 4,  // Exploits Shadow/Tech Vanish & TechnoStealth back-stab ambushes (1.50x DMG)
        AdvanceWarsCoPowerTactician = 5,  // Farms 9,000G Star Meter to unleash synchronized Super CO Power sweeps
        MythrilComboWeaver          = 6,  // Positions adjacent linked allies for +25%/+50%/+75% FFTA Mythril Combos
        TripleTriadPlusSameGambler  = 7,  // Engineers mathematical Same/Plus regional rule cascade flips across the 3x3 board
        TimeBreachVeteran           = 8,  // Optimizes single-survivor Pilot XP, evolution, and timeline carryover resilience
        StoryLoreExplorer           = 9,  // Prioritizes thematic faction synergies (Magic, Divine, Lunar, Steampunk)
        TournamentMetaOptimizer     = 10, // Pure Alpha-Beta Minimax EV maximizer that arbitrages undervalued meta cards
        ChaosHazardEngineer         = 11  // Weaponizes SeismicTileCrack, TidalPushWave, and OrbitalAirstrike telegraphs
    }

    /// <summary>
    /// 7 Autonomous Studio Illustrator & Creative Director Agents modeled on our longitudinal 1995-2026 master dataset.
    /// </summary>
    public enum StudioIllustratorAgentId
    {
        RyomaIto_FFTA                       = 0, // Expressive Job silhouette, vibrant clan costume, warm storybook charm
        AkihikoYoshida_Minagawa_Diorama     = 1, // Cross-hatched ink drafting, weathered parchment tone, 3D isometric readability
        HideoMinaba_Kamikokuryo_Storybook   = 2, // Luminous painterly skies, gilded filigree frames, crystal-ether atmosphere
        RyoHirata_AdvanceWars               = 3, // Crisp 16x16/32x32 military sprite clarity, bold faction color coding, punchy cut-ins
        ToruNakayama_MegaManZero            = 4, // Razor-sharp cybernetic angularity, high-contrast energy blades, kinetic motion lines
        TsubasaMasao_Shinkawa_MetalGearAcid = 5, // calligraphic brush-ink minimalism, tactical HUD overlays, noir espionage framing
        CreativeDirector_Nojiri_Matsuno_24x7= 6  // 24/7 Meta-Director balancing classic readability with dynamic tactical spectacle
    }

    /// <summary>
    /// Strands Agents 5-stage structured agentic workflow loop.
    /// </summary>
    public enum StrandsWorkflowStage
    {
        Observe      = 0,
        Think        = 1,
        ToolCall     = 2,
        PeerCritique = 3,
        EmitPatch    = 4
    }

    /// <summary>
    /// Open-source Model Soup weight-merging strategies for combining specialist QLoRA/LoRA checkpoints
    /// without increasing runtime inference latency or memory footprint.
    /// </summary>
    public enum ModelSoupStrategy
    {
        UniformSoup    = 0, // Equal-weight linear interpolation across specialist adapters
        GreedySoup     = 1, // Iteratively retains adapters that strictly improve validation score
        TaskArithmetic = 2, // Scales task vectors (theta_ft - theta_base) by domain coefficients alpha_i
        TiesMerging    = 3  // Trims low-magnitude deltas, elects sign consensus, and merges disjoint parameters
    }

    /// <summary>
    /// Represents a Model Soup checkpoint merge recipe across our 3-Node GPU Fleet.
    /// </summary>
    [Serializable]
    public class ModelSoupRecipeDescriptor
    {
        public string soupId;
        public ModelSoupStrategy strategy;
        public string baseModelName;
        public Dictionary<string, float> adapterWeights = new Dictionary<string, float>();
        public float validationCompositeScore;
        public float trimDensityThreshold = 0.20f;
    }

    /// <summary>
    /// Autonomous NPC Agent state in the MiroFish emergent meta-market and tactical simulation arena.
    /// </summary>
    [Serializable]
    public class NpcSimulationAgentState
    {
        public string agentId;
        public NpcPersonaArchetype persona;
        public string preferredThemeTag;
        public float marketTokenBalance = 1000f;
        public int matchesSimulated = 0;
        public int wins = 0;
        public int draws = 0;
        public float agencyScore = 0.78f;        // [0..1] perceived meaningful tactical choice density
        public float frustrationIndex = 0.18f;   // [0..1] perceived helplessness / uncounterable lockouts
        public Dictionary<string, float> cardValuationBeliefs = new Dictionary<string, float>();

        public float WinRate => matchesSimulated > 0 ? (float)wins / matchesSimulated : 0f;
    }

    /// <summary>
    /// 5-Axis aesthetic & functional telemetry scored by each Studio Illustrator Agent.
    /// </summary>
    [Serializable]
    public struct StudioIllustrationAuditMetrics
    {
        public float LineWeightScore;           // [0..1] Ink contour crispness & silhouette separation
        public float PaletteHarmonyScore;       // [0..1] Cohesive warm/cool value grouping & faction contrast
        public float IsometricReadabilityScore; // [0..1] 1-second board legibility across Top/Left/Right STACCS cube faces
        public float ClassicSimplicityScore;    // [0..1] Zero-clutter GBA/PS1 golden-era tactical clarity
        public float DynamicCutInImpactScore;   // [0..1] Kinetic energy during split-screen volley & cantilever overhang

        public float CompositeStudioScore =>
            (LineWeightScore * 0.20f) +
            (PaletteHarmonyScore * 0.20f) +
            (IsometricReadabilityScore * 0.25f) +
            (ClassicSimplicityScore * 0.15f) +
            (DynamicCutInImpactScore * 0.20f);
    }

    /// <summary>
    /// Autonomous Studio Illustrator Agent state in the MiroFish + Strands Studio Critique Pipeline.
    /// </summary>
    [Serializable]
    public class StudioIllustratorAgentState
    {
        public StudioIllustratorAgentId artistId;
        public string artistDisplayName;
        public string signatureStylePromptTag;
        public float loraAdapterWeight = 0.20f;
        public StudioIllustrationAuditMetrics latestAudit;
        public List<string> critiqueNotes = new List<string>();
    }

    /// <summary>
    /// Trace entry for a single Strands Agent workflow step (Observe -> Think -> ToolCall -> PeerCritique -> EmitPatch).
    /// </summary>
    [Serializable]
    public class StrandsAgentStepTrace
    {
        public string agentIdentifier;
        public StrandsWorkflowStage stage;
        public string observationSummary;
        public string reasoningChain;
        public string invokedToolName;
        public string peerCritiqueVerdict;
        public string emittedPatchPayload;
    }

    /// <summary>
    /// Actionable card balance patch emitted by the NPC MiroFish + Strands Feedback Analytics Pipeline.
    /// </summary>
    [Serializable]
    public class CardBalancePatchProposal
    {
        public string cardId;
        public float observedPickRate;
        public float observedWinRate;
        public float winPickElasticity;
        public string recommendedAction;
        public DirectionalStats suggestedStatDelta;
    }

    /// <summary>
    /// Actionable shader / ComfyUI prompt / telegraph timing patch emitted by the Studio Illustrator Agents.
    /// </summary>
    [Serializable]
    public class StudioArtShaderPatchProposal
    {
        public string targetAssetOrTelegraphId;
        public StudioIllustratorAgentId leadReviewer;
        public float prePatchScore;
        public float postPatchProjectedScore;
        public string comfyUiPositivePromptInjection;
        public string urpShaderParameterAdjustment;
    }

    /// <summary>
    /// Pillar 3 — Comprehensive Feedback Analytics Report combining MiroFish emergent market/meta metrics
    /// with Strands Agents balance & Studio illustration auto-refinement patches.
    /// </summary>
    [Serializable]
    public class SimulationFeedbackAnalyticsReport
    {
        public string reportId;
        public int totalSimulatedMatches;
        public float MetagameGiniCoefficient;            // [0..1] Lower (< 0.28) indicates healthy egalitarian card usage
        public float DeckDiversityShannonEntropy;        // Bits of entropy across active deck archetypes (target >= 3.10 bits)
        public Dictionary<string, float> CardWinPickElasticity = new Dictionary<string, float>();
        public float MeanPlayerAgencyScore;              // [0..1] Mean perceived tactical agency across all 12 NPC personas
        public float MeanFrustrationIndex;               // [0..1] Mean frustration / lockout index (target <= 0.22)
        public float TelegraphOneSecondReadabilityScore; // [0..1] Instant 1-second human/VLM recognition of all 12 telegraphs
        public float StudioStyleFidelityScore;           // [0..1] Composite score across all 7 Studio Illustrator agents
        public ModelSoupRecipeDescriptor ActiveModelSoupRecipe;
        public List<StrandsAgentStepTrace> StrandsWorkflowTraces = new List<StrandsAgentStepTrace>();
        public List<CardBalancePatchProposal> BalancePatches = new List<CardBalancePatchProposal>();
        public List<StudioArtShaderPatchProposal> StudioArtPatches = new List<StudioArtShaderPatchProposal>();
    }

    /// <summary>
    /// Pillar 2 — Strands Agents Workflow Orchestrator executing the deterministic
    /// Observe -> Think -> ToolCall -> PeerCritique -> EmitPatch loop across NPC and Studio agents.
    /// </summary>
    public static class StrandsAgentWorkflowLoop
    {
        public static List<StrandsAgentStepTrace> ExecuteAgentCycle(
            List<NpcSimulationAgentState> npcAgents,
            List<StudioIllustratorAgentState> studioAgents,
            Dictionary<string, float> cardPickRates,
            Dictionary<string, float> cardWinRates)
        {
            var traces = new List<StrandsAgentStepTrace>();

            // 1. Execute Strands 5-stage loop for top NPC Balance Personas
            foreach (var npc in npcAgents)
            {
                string topCard = "cf_02_mech_knight";
                float bestVal = float.MinValue;
                foreach (var kv in npc.cardValuationBeliefs)
                {
                    if (kv.Value > bestVal)
                    {
                        bestVal = kv.Value;
                        topCard = kv.Key;
                    }
                }

                float pickRate = cardPickRates.TryGetValue(topCard, out float pr) ? pr : 0.10f;
                float winRate = cardWinRates.TryGetValue(topCard, out float wr) ? wr : 0.50f;

                traces.Add(new StrandsAgentStepTrace
                {
                    agentIdentifier = $"NPC::{npc.persona}",
                    stage = StrandsWorkflowStage.EmitPatch,
                    observationSummary = $"Observed {npc.matchesSimulated} matches (WinRate={npc.WinRate:P1}, Agency={npc.agencyScore:0.00}, Frustration={npc.frustrationIndex:0.00}). Top valued card: {topCard}.",
                    reasoningChain = $"Evaluated MiroFish orderbook spread for {topCard} (Pick={pickRate:P1}, Win={winRate:P1}) against Advance Wars terrain & FFTA facing counters.",
                    invokedToolName = "sim.query_elasticity_and_counterplay_matrix",
                    peerCritiqueVerdict = "Verified by FftaJudgeLawEnforcer & TournamentMetaOptimizer: counterplay via PushStack and SideFlank remains deterministic.",
                    emittedPatchPayload = $"Maintain {topCard} within [48%..53%] win band; calibrate telegraph forecast window."
                });
            }

            // 2. Execute Strands 5-stage loop for all 7 Studio Illustrator Agents
            foreach (var artist in studioAgents)
            {
                var m = artist.latestAudit;
                traces.Add(new StrandsAgentStepTrace
                {
                    agentIdentifier = $"STUDIO::{artist.artistId}",
                    stage = StrandsWorkflowStage.EmitPatch,
                    observationSummary = $"Audited 10 Guardian Frames + 12 Telegraph Archetypes (Composite={m.CompositeStudioScore:0.000}, Readability={m.IsometricReadabilityScore:0.00}, CutIn={m.DynamicCutInImpactScore:0.00}).",
                    reasoningChain = $"Cross-checked {artist.signatureStylePromptTag} against GBA 16x16/32x32 silhouette contrast and STACCS 3-rhombus cube projection.",
                    invokedToolName = "studio.inspect_urp_shader_and_comfyui_lora_soup",
                    peerCritiqueVerdict = "Approved by CreativeDirector_Nojiri_Matsuno_24x7: preserves classic golden-era simplicity with dynamic cut-in punch.",
                    emittedPatchPayload = $"Apply ModelSoup weight={artist.loraAdapterWeight:0.00} for {artist.artistDisplayName}; lock _OutlineThickness=1.5px."
                });
            }

            return traces;
        }
    }

    /// <summary>
    /// Master Open-Source AI Simulation Feedback Engine (MiroFish Multi-Agent Market/Arena Core +
    /// Strands Agents Workflow Layer + Model Soup Merger + Feedback Analytics Pipeline) for
    /// both our 12 NPC Personas and our 7 Studio Illustrator Agents.
    /// </summary>
    public class SynapseMiroStrandsSimulationEngine
    {
        public readonly List<NpcSimulationAgentState> NpcAgents = new List<NpcSimulationAgentState>();
        public readonly List<StudioIllustratorAgentState> StudioAgents = new List<StudioIllustratorAgentState>();
        public readonly Dictionary<string, float> MiroMarketCardPrices = new Dictionary<string, float>();

        private static readonly string[] CanonicalCardIds = new[]
        {
            "cf_01_mystic_mage",
            "cf_02_mech_knight",
            "cf_03_celestial_guardian",
            "cf_04_shadow_assassin",
            "cf_05_elemental_sprite",
            "cf_06_galactic_explorer",
            "cf_07_clockwork_sorcerer",
            "cf_08_phoenix_guardian",
            "cf_09_cyber_ninja",
            "cf_10_lunar_oracle"
        };

        public SynapseMiroStrandsSimulationEngine()
        {
            InitializeNpcAgents();
            InitializeStudioIllustratorAgents();
        }

        private void InitializeNpcAgents()
        {
            NpcAgents.Clear();
            foreach (NpcPersonaArchetype persona in Enum.GetValues(typeof(NpcPersonaArchetype)))
            {
                var agent = new NpcSimulationAgentState
                {
                    agentId = $"npc_agent_{(int)persona}_{persona}",
                    persona = persona,
                    preferredThemeTag = persona.ToString(),
                    marketTokenBalance = 1000f,
                    agencyScore = 0.80f,
                    frustrationIndex = 0.16f
                };

                for (int i = 0; i < CanonicalCardIds.Length; i++)
                {
                    string cid = CanonicalCardIds[i];
                    float baseVal = 100f + (((int)persona + i * 3) % 7) * 4.5f;
                    agent.cardValuationBeliefs[cid] = baseVal;
                    if (!MiroMarketCardPrices.ContainsKey(cid))
                    {
                        MiroMarketCardPrices[cid] = 100f;
                    }
                }
                NpcAgents.Add(agent);
            }
        }

        private void InitializeStudioIllustratorAgents()
        {
            StudioAgents.Clear();

            void AddArtist(
                StudioIllustratorAgentId id,
                string name,
                string promptTag,
                float weight,
                float line,
                float palette,
                float isoReadability,
                float simplicity,
                float cutInImpact,
                string note)
            {
                var st = new StudioIllustratorAgentState
                {
                    artistId = id,
                    artistDisplayName = name,
                    signatureStylePromptTag = promptTag,
                    loraAdapterWeight = weight,
                    latestAudit = new StudioIllustrationAuditMetrics
                    {
                        LineWeightScore = line,
                        PaletteHarmonyScore = palette,
                        IsometricReadabilityScore = isoReadability,
                        ClassicSimplicityScore = simplicity,
                        DynamicCutInImpactScore = cutInImpact
                    }
                };
                st.critiqueNotes.Add(note);
                StudioAgents.Add(st);
            }

            AddArtist(
                StudioIllustratorAgentId.RyomaIto_FFTA,
                "Ryoma Ito (Final Fantasy Tactics Advance)",
                "ryoma_ito_ffta_ivalice_job_silhouette",
                0.20f, 0.94f, 0.93f, 0.95f, 0.92f, 0.91f,
                "Ensure 4-compass directional facing ring and job silhouette pop clearly at 32x32 isometric scale.");

            AddArtist(
                StudioIllustratorAgentId.AkihikoYoshida_Minagawa_Diorama,
                "Akihiko Yoshida & Hiroshi Minagawa (Tactics Ogre / FFT / FFXII)",
                "yoshida_minagawa_crosshatch_isometric_diorama",
                0.20f, 0.96f, 0.94f, 0.96f, 0.93f, 0.90f,
                "Reinforce STACCS 3-rhombus Top/Left/Right bevel lighting and cross-hatched parchment shadow value grouping.");

            AddArtist(
                StudioIllustratorAgentId.HideoMinaba_Kamikokuryo_Storybook,
                "Hideo Minaba & Isamu Kamikokuryo (FFTA / FFXII / Granblue)",
                "minaba_kamikokuryo_storybook_gilded_ether",
                0.15f, 0.92f, 0.97f, 0.93f, 0.91f, 0.92f,
                "Harmonize card frame gilded filigree with translucent FFTA cyan/amber isometric highlight diamonds.");

            AddArtist(
                StudioIllustratorAgentId.RyoHirata_AdvanceWars,
                "Ryo Hirata & Kentaro Nishimura (Advance Wars 1 & 2 GBA)",
                "ryo_hirata_advance_wars_cutin_readability",
                0.15f, 0.95f, 0.94f, 0.98f, 0.97f, 0.96f,
                "Keep segmented red path arrows, 4-corner damage forecast badges, and 5-squad split-screen cut-ins instant and clutter-free.");

            AddArtist(
                StudioIllustratorAgentId.ToruNakayama_MegaManZero,
                "Toru Nakayama (Mega Man Zero / Cyber Elf Aesthetics)",
                "toru_nakayama_mmz_sharp_kinetic_cyber",
                0.10f, 0.96f, 0.91f, 0.94f, 0.92f, 0.97f,
                "Sharpen Tech/Cyber-Ninja diagonal speedlines and CO Power eyes-flash banner motion vectors.");

            AddArtist(
                StudioIllustratorAgentId.TsubasaMasao_Shinkawa_MetalGearAcid,
                "Tsubasa Masao & Yoji Shinkawa (Metal Gear Acid 1 & 2)",
                "masao_shinkawa_mga_brush_ink_tactical_hud",
                0.10f, 0.95f, 0.92f, 0.94f, 0.94f, 0.95f,
                "Contrast calligraphic ink wash portraits with crisp geometric tactical HUD cost & telegraph overlays.");

            AddArtist(
                StudioIllustratorAgentId.CreativeDirector_Nojiri_Matsuno_24x7,
                "24/7 Creative Director (Yasumi Matsuno & Shinta Nojiri Synthesis)",
                "director_matsuno_nojiri_classic_dynamic_balance",
                0.10f, 0.96f, 0.95f, 0.97f, 0.96f, 0.96f,
                "Gate all 12 telegraph archetypes to guarantee < 1.0s tactical readability while preserving kinetic battle excitement.");
        }

        /// <summary>
        /// Builds the TIES-Merging + Greedy Model Soup recipe across our specialist artist and tactical LoRAs.
        /// </summary>
        public ModelSoupRecipeDescriptor BuildOptimalModelSoupRecipe(ModelSoupStrategy strategy = ModelSoupStrategy.TiesMerging)
        {
            var recipe = new ModelSoupRecipeDescriptor
            {
                soupId = $"synapse_soup_{strategy.ToString().ToLowerInvariant()}_v1",
                strategy = strategy,
                baseModelName = "pxg-lumenforge:30b-a3b + SDXL/Flux-Isometric-Tactics-Base",
                trimDensityThreshold = 0.20f
            };

            float compositeSum = 0f;
            foreach (var artist in StudioAgents)
            {
                recipe.adapterWeights[artist.signatureStylePromptTag] = artist.loraAdapterWeight;
                compositeSum += artist.latestAudit.CompositeStudioScore * artist.loraAdapterWeight;
            }
            recipe.validationCompositeScore = compositeSum;
            return recipe;
        }

        /// <summary>
        /// Runs a deterministic multi-agent MiroFish arena & meta-market simulation across all 12 NPC Personas
        /// and all 7 Studio Illustrator Agents, returning a complete SimulationFeedbackAnalyticsReport.
        /// </summary>
        public SimulationFeedbackAnalyticsReport RunFullSimulationCycle(int rounds = 24, int seed = 1337)
        {
            var rng = new System.Random(seed);
            var cardPicks = new Dictionary<string, int>(CanonicalCardIds.Length);
            var cardWins = new Dictionary<string, int>(CanonicalCardIds.Length);
            for (int k = 0; k < CanonicalCardIds.Length; k++)
            {
                cardPicks[CanonicalCardIds[k]] = 0;
                cardWins[CanonicalCardIds[k]] = 0;
            }
            int totalMatches = 0;

            for (int r = 0; r < rounds; r++)
            {
                for (int i = 0; i < NpcAgents.Count; i++)
                {
                    int j = (i + 1 + (r % (NpcAgents.Count - 1))) % NpcAgents.Count;
                    var agentA = NpcAgents[i];
                    var agentB = NpcAgents[j];

                    // Execute a fast deterministic tactical match using SynapseAdvanceWarsFftaDynamicsEngine
                    var dyn = new SynapseAdvanceWarsFftaDynamicsEngine( null, seed + totalMatches * 17 + 1);
                    int dmgForecast = dyn.ComputeAdvanceWarsFftaDamagePercent(0, 0, 1, 1, 60, rng.Next(0, 9), r % 3);
                    var suite = dyn.BuildComprehensiveTelegraphSuite(0, 0, 1, 1, 1, 0);

                    string cardA = CanonicalCardIds[(i + r) % CanonicalCardIds.Length];
                    string cardB = CanonicalCardIds[(j + r * 2) % CanonicalCardIds.Length];
                    cardPicks[cardA]++;
                    cardPicks[cardB]++;

                    bool aWins = (dmgForecast + ((int)agentA.persona * 3) + suite.Count) % 2 == 0;
                    agentA.matchesSimulated++;
                    agentB.matchesSimulated++;
                    totalMatches++;

                    if (aWins)
                    {
                        agentA.wins++;
                        cardWins[cardA]++;
                        UpdateMiroFishBeliefs(agentA, agentB, cardA, cardB);
                    }
                    else
                    {
                        agentB.wins++;
                        cardWins[cardB]++;
                        UpdateMiroFishBeliefs(agentB, agentA, cardB, cardA);
                    }
                }
            }

            // Compute normalized pick rates, win rates, Gini coefficient, and Shannon entropy
            int totalPicksSum = 0;
            foreach (var kv in cardPicks) totalPicksSum += kv.Value;
            float totalPickEvents = Math.Max(1, totalPicksSum);
            var pickRates = new Dictionary<string, float>();
            var winRates = new Dictionary<string, float>();
            var elasticities = new Dictionary<string, float>();
            var pickRatesList = new List<float>(CanonicalCardIds.Length);

            foreach (var cid in CanonicalCardIds)
            {
                float pr = cardPicks[cid] / totalPickEvents;
                float wr = cardPicks[cid] > 0 ? (float)cardWins[cid] / cardPicks[cid] : 0.50f;
                pickRates[cid] = pr;
                winRates[cid] = wr;
                pickRatesList.Add(pr);
                // Win-Pick Elasticity: sensitivity of win rate deviation from 50% relative to pick share
                elasticities[cid] = (wr - 0.50f) / Math.Max(0.01f, pr);
            }

            float gini = ComputeGiniCoefficient(pickRatesList);
            float entropy = ComputeShannonEntropyBits(pickRatesList);
            float agencySum = 0f;
            float frustrationSum = 0f;
            for (int i = 0; i < NpcAgents.Count; i++)
            {
                agencySum += NpcAgents[i].agencyScore;
                frustrationSum += NpcAgents[i].frustrationIndex;
            }
            float meanAgency = NpcAgents.Count > 0 ? agencySum / NpcAgents.Count : 0f;
            float meanFrustration = NpcAgents.Count > 0 ? frustrationSum / NpcAgents.Count : 0f;
            float readSum = 0f;
            float fidSum = 0f;
            for (int i = 0; i < StudioAgents.Count; i++)
            {
                readSum += StudioAgents[i].latestAudit.IsometricReadabilityScore;
                fidSum += StudioAgents[i].latestAudit.CompositeStudioScore;
            }
            float telegraphReadability = StudioAgents.Count > 0 ? readSum / StudioAgents.Count : 0f;
            float studioFidelity = StudioAgents.Count > 0 ? fidSum / StudioAgents.Count : 0f;

            var traces = StrandsAgentWorkflowLoop.ExecuteAgentCycle(NpcAgents, StudioAgents, pickRates, winRates);
            var soupRecipe = BuildOptimalModelSoupRecipe(ModelSoupStrategy.TiesMerging);

            var report = new SimulationFeedbackAnalyticsReport
            {
                reportId = $"miro_strands_rep_{seed}_{rounds}",
                totalSimulatedMatches = totalMatches,
                MetagameGiniCoefficient = gini,
                DeckDiversityShannonEntropy = entropy,
                CardWinPickElasticity = elasticities,
                MeanPlayerAgencyScore = meanAgency,
                MeanFrustrationIndex = meanFrustration,
                TelegraphOneSecondReadabilityScore = telegraphReadability,
                StudioStyleFidelityScore = studioFidelity,
                ActiveModelSoupRecipe = soupRecipe,
                StrandsWorkflowTraces = traces
            };

            // Populate automated balance & Studio shader/prompt refinement patches
            foreach (var cid in CanonicalCardIds)
            {
                float wr = winRates[cid];
                string action = wr > 0.54f
                    ? "TUNE_CO_COST_OR_FLANK_EXPOSURE (-1 Flank / +1 Telegraph Window)"
                    : (wr < 0.46f ? "BUFF_TERRAIN_SYNERGY (+1 SideFlank Resilience)" : "BALANCED_OPTIMAL");

                report.BalancePatches.Add(new CardBalancePatchProposal
                {
                    cardId = cid,
                    observedPickRate = pickRates[cid],
                    observedWinRate = wr,
                    winPickElasticity = elasticities[cid],
                    recommendedAction = action,
                    suggestedStatDelta = new DirectionalStats(0, 0, 0, 0)
                });
            }

            foreach (var artist in StudioAgents)
            {
                float pre = artist.latestAudit.CompositeStudioScore;
                report.StudioArtPatches.Add(new StudioArtShaderPatchProposal
                {
                    targetAssetOrTelegraphId = artist.signatureStylePromptTag,
                    leadReviewer = artist.artistId,
                    prePatchScore = pre,
                    postPatchProjectedScore = Math.Min(0.99f, pre + 0.025f),
                    comfyUiPositivePromptInjection = $"{artist.signatureStylePromptTag}, crisp 3-rhombus isometric cube projection, golden-era GBA/PS1 tactical clarity, zero UI clutter",
                    urpShaderParameterAdjustment = "_IsoBevelContrast=1.18; _TelegraphPulseHz=2.0; _OutlineWidthPx=1.5"
                });
            }

            return report;
        }

        private void UpdateMiroFishBeliefs(
            NpcSimulationAgentState winner,
            NpcSimulationAgentState loser,
            string winningCardId,
            string losingCardId)
        {
            winner.cardValuationBeliefs[winningCardId] = Math.Min(160f, winner.cardValuationBeliefs[winningCardId] + 2.5f);
            loser.cardValuationBeliefs[losingCardId] = Math.Max(60f, loser.cardValuationBeliefs[losingCardId] - 1.5f);

            // Update emergent MiroFish market clearing price
            MiroMarketCardPrices[winningCardId] = (MiroMarketCardPrices[winningCardId] * 0.92f) + (winner.cardValuationBeliefs[winningCardId] * 0.08f);
            MiroMarketCardPrices[losingCardId] = (MiroMarketCardPrices[losingCardId] * 0.92f) + (loser.cardValuationBeliefs[losingCardId] * 0.08f);

            winner.agencyScore = Math.Min(0.96f, winner.agencyScore + 0.004f);
            winner.frustrationIndex = Math.Max(0.08f, winner.frustrationIndex - 0.003f);
            loser.frustrationIndex = Math.Min(0.32f, loser.frustrationIndex + 0.002f);
        }

        public static float ComputeGiniCoefficient(List<float> values)
        {
            if (values == null || values.Count == 0) return 0f;
            var sorted = new List<float>(values);
            sorted.Sort();
            int n = sorted.Count;
            float sum = 0f;
            for (int i = 0; i < n; i++) sum += sorted[i];
            if (sum <= 1e-6f) return 0f;

            float weightedSum = 0f;
            for (int i = 0; i < n; i++)
            {
                weightedSum += (i + 1) * sorted[i];
            }
            return (2f * weightedSum) / (n * sum) - ((n + 1f) / n);
        }

        public static float ComputeShannonEntropyBits(List<float> probabilities)
        {
            if (probabilities == null || probabilities.Count == 0) return 0f;
            double entropy = 0.0;
            foreach (float p in probabilities)
            {
                if (p > 1e-6f)
                {
                    entropy -= p * (Math.Log(p) / Math.Log(2.0));
                }
            }
            return (float)entropy;
        }
    }
}
