using System;
using System.Collections.Generic;
using UnityEngine;

namespace Synapse.TcgEngine.Core
{
    public enum CardType
    {
        None = 0,
        Hero = 5,
        Character = 10,
        Spell = 20,
        Artifact = 30,
        Secret = 40,
        Equipment = 50,
    }

    public enum GameState
    {
        Connecting = 0,
        Play = 20,
        GameEnded = 99,
    }

    public enum GamePhase
    {
        None = 0,
        StartTurn = 10,
        Main = 20,
        EndTurn = 30,
    }

    public enum SelectorType
    {
        None = 0,
        SelectTarget = 10,
        SelectorCard = 20,
        SelectorChoice = 30,
    }

    [Serializable]
    public class TeamData : ScriptableObject
    {
        public string id;
        public string title;
        public Sprite icon;
        public Color color = Color.white;
    }

    [Serializable]
    public class RarityData : ScriptableObject
    {
        public string id;
        public string title;
        public Sprite icon;
        public int rank = 1;
    }

    [Serializable]
    public class TraitData : ScriptableObject
    {
        public string id;
        public string title;
        public Sprite icon;
    }

    [Serializable]
    public struct TraitStat
    {
        public TraitData trait;
        public int value;
    }

    [Serializable]
    public class StatusData : ScriptableObject
    {
        public string id;
        public string title;
        public int hvalue = 1;
    }

    [Serializable]
    public class AbilityData : ScriptableObject
    {
        public string id;
        public string title;
        [TextArea(3, 5)]
        public string desc;
        public int trigger;
        public int target;
        public int value = 1;
        public int duration = 1;
        public int mana_cost = 0;
        public bool exhaust = false;
        public AbilityData[] chain_abilities = Array.Empty<AbilityData>();
    }

    [Serializable]
    public class PackData : ScriptableObject
    {
        public string id;
        public string title;
        public int cards = 5;
        public int cost = 100;
    }

    [Serializable]
    public class DeckData : ScriptableObject
    {
        public string id;
        public string title;
        public CardData hero;
        public CardData[] cards = Array.Empty<CardData>();
    }

    [Serializable]
    public class LevelData : ScriptableObject
    {
        public string id;
        public string title;
        public int level = 1;
        public DeckData player_deck;
        public DeckData ai_deck;
        public int ai_level = 3;
        public int reward_xp = 100;
        public int reward_coins = 100;
    }

    [CreateAssetMenu(fileName = "VariantData", menuName = "TcgEngine/VariantData", order = 5)]
    public class VariantData : ScriptableObject
    {
        public string id;
        public string title;
        public Sprite frame;
        public Sprite frame_board;
        public Color color = Color.white;
        public int cost_factor = 1;
        public bool is_default;

        public static List<VariantData> variant_list = new List<VariantData>();

        public string GetSuffix() => "_" + id;
    }

    [CreateAssetMenu(fileName = "card", menuName = "TcgEngine/CardData", order = 5)]
    public class CardData : ScriptableObject
    {
        public string id;

        [Header("Display")]
        public string title;
        public Sprite art_full;
        public Sprite art_board;

        [Header("Stats")]
        public CardType type = CardType.Character;
        public TeamData team;
        public RarityData rarity;
        public int mana = 1;
        public int attack = 5;
        public int hp = 5;

        [Header("Traits")]
        public TraitData[] traits = Array.Empty<TraitData>();
        public TraitStat[] stats = Array.Empty<TraitStat>();

        [Header("Abilities")]
        public AbilityData[] abilities = Array.Empty<AbilityData>();

        [Header("Card Text")]
        [TextArea(3, 5)]
        public string text;

        [Header("Description")]
        [TextArea(5, 10)]
        public string desc;

        [Header("Availability")]
        public bool deckbuilding = true;
        public int cost = 100;
        public PackData[] packs = Array.Empty<PackData>();

        [Header("CardFront 3x3 & Atelier")]
        public int dir_north = 5;
        public int dir_east = 5;
        public int dir_south = 5;
        public int dir_west = 5;
        public int dice_pip_affinity = 1;
        public string sovereign_style_id = "";
        public string glb_model_id = "";

        [Header("Collector Identification (Shadowverse EVOLVE / BP Standard)")]
        public string originalTitleJp = "機構翼の少女・ローザ(進化前)";
        public string cardGameTitle = "Shadowverse EVOLVE";
        public string boosterVersionEn = "[BP05] Eternal omens";
        public string originalVersionJp = "ブースターパック第5弾 永劫なる絶傑";
        public string collectorCardNumber = "BP05-110 SR";
        public string collectorRarity = "SR";
        public string evolutionStateJp = "進化前";

        public static List<CardData> card_list = new List<CardData>();
        public static Dictionary<string, CardData> card_dict = new Dictionary<string, CardData>();

        public bool IsBoardCard()
        {
            return type == CardType.Character || type == CardType.Artifact || type == CardType.Hero;
        }

        public static CardData Get(string id)
        {
            if (string.IsNullOrEmpty(id))
                return null;
            if (card_dict.TryGetValue(id, out var found))
                return found;
            return null;
        }
    }

    [Serializable]
    public struct Slot : IEquatable<Slot>
    {
        public int x;
        public int y;
        public int p;

        public static int x_min = 1;
        public static int x_max = 5;
        public static int y_min = 1;
        public static int y_max = 3;
        public static bool ignore_p = false;
        public const int cf_grid_size = 3;

        public Slot(int pid)
        {
            this.x = 0;
            this.y = 0;
            this.p = pid;
        }

        public Slot(int x, int y, int pid)
        {
            this.x = x;
            this.y = y;
            this.p = pid;
        }

        public bool IsValid()
        {
            return x >= x_min && x <= x_max && y >= y_min && y <= y_max && p >= 0;
        }

        public static int GetP(int pid)
        {
            return ignore_p ? 0 : pid;
        }

        public int GetDicevadersColumnIndex()
        {
            if (x < 1)
                return 0;
            return (x - 1) % cf_grid_size;
        }

        public List<Slot> GetAdjacentSlots3x3()
        {
            List<Slot> neighbors = new List<Slot>(4);
            int gx = ((x - 1) % cf_grid_size) + 1;
            int gy = y > 1 ? (((y - 1) % cf_grid_size) + 1) : (((x - 1) / cf_grid_size) % cf_grid_size) + 1;
            bool use_2d_coords = (y_max >= cf_grid_size || y > 1);

            if (gy + 1 <= cf_grid_size)
                neighbors.Add(use_2d_coords ? new Slot(gx, gy + 1, p) : new Slot((gy * cf_grid_size) + gx, y, p));
            if (gx + 1 <= cf_grid_size)
                neighbors.Add(use_2d_coords ? new Slot(gx + 1, gy, p) : new Slot(((gy - 1) * cf_grid_size) + (gx + 1), y, p));
            if (gy - 1 >= 1)
                neighbors.Add(use_2d_coords ? new Slot(gx, gy - 1, p) : new Slot(((gy - 2) * cf_grid_size) + gx, y, p));
            if (gx - 1 >= 1)
                neighbors.Add(use_2d_coords ? new Slot(gx - 1, gy, p) : new Slot(((gy - 1) * cf_grid_size) + (gx - 1), y, p));

            return neighbors;
        }

        public bool Equals(Slot other) => x == other.x && y == other.y && p == other.p;
        public override bool Equals(object obj) => obj is Slot s && Equals(s);
        public override int GetHashCode() => (x * 397) ^ (y * 17) ^ p;
        public static bool operator ==(Slot a, Slot b) => a.Equals(b);
        public static bool operator !=(Slot a, Slot b) => !a.Equals(b);
        public static Slot None => new Slot(0, 0, 0);
    }

    [Serializable]
    public class CardTrait
    {
        public string id;
        public int value;

        public CardTrait(string id, int value)
        {
            this.id = id;
            this.value = value;
        }
    }

    [Serializable]
    public class CardStatus
    {
        public string id;
        public int value;
        public int duration = 1;
        public bool permanent = true;

        public CardStatus(string id, int value, int duration)
        {
            this.id = id;
            this.value = value;
            this.duration = duration;
        }
    }

    [Serializable]
    public class Card
    {
        public string card_id;
        public string uid;
        public int player_id;
        public string variant_id = "default";

        public Slot slot;
        public bool exhausted;
        public int damage = 0;

        public int mana = 0;
        public int attack = 0;
        public int hp = 0;

        public int mana_ongoing = 0;
        public int attack_ongoing = 0;
        public int hp_ongoing = 0;

        public string equipped_uid = null;

        public List<CardTrait> traits = new List<CardTrait>();
        public List<CardTrait> ongoing_traits = new List<CardTrait>();
        public List<CardStatus> status = new List<CardStatus>();
        public List<CardStatus> ongoing_status = new List<CardStatus>();
        public List<string> abilities = new List<string>();
        public List<string> abilities_ongoing = new List<string>();

        [NonSerialized] private CardData data = null;
        [NonSerialized] private VariantData vdata = null;

        public Card() { }

        public Card(string card_id, string uid, int player_id)
        {
            this.card_id = card_id;
            this.uid = uid;
            this.player_id = player_id;
        }

        public CardData CardData
        {
            get
            {
                if (data == null || data.id != card_id)
                    data = CardData.Get(card_id);
                return data;
            }
            set => data = value;
        }

        public VariantData VariantData
        {
            get => vdata;
            set => vdata = value;
        }

        public CardTrait GetTrait(string id)
        {
            foreach (CardTrait trait in traits)
            {
                if (trait.id == id)
                    return trait;
            }
            return null;
        }

        public int GetTraitValue(string id)
        {
            CardTrait t = GetTrait(id);
            return t != null ? t.value : 0;
        }

        public void SetTrait(string id, int value)
        {
            CardTrait trait = GetTrait(id);
            if (trait != null)
                trait.value = value;
            else
                traits.Add(new CardTrait(id, value));
        }

        public void AddTrait(string id, int value)
        {
            CardTrait trait = GetTrait(id);
            if (trait != null)
                trait.value += value;
            else
                SetTrait(id, value);
        }
    }

    [Serializable]
    public class Player
    {
        public int player_id;
        public string username;
        public string avatar;
        public string cardback;
        public string deck;
        public bool is_ai = false;
        public int ai_level = 1;

        public bool connected = false;
        public bool ready = false;

        public int hp = 20;
        public int hp_max = 20;
        public int mana = 0;
        public int mana_max = 0;
        public int kill_count = 0;

        public Dictionary<string, Card> cards_all = new Dictionary<string, Card>();
        public Card hero = null;

        public List<Card> cards_deck = new List<Card>();
        public List<Card> cards_hand = new List<Card>();
        public List<Card> cards_board = new List<Card>();
        public List<Card> cards_equip = new List<Card>();
        public List<Card> cards_discard = new List<Card>();
        public List<Card> cards_secret = new List<Card>();
        public List<Card> cards_temp = new List<Card>();

        public List<CardTrait> traits = new List<CardTrait>();
        public List<CardStatus> status = new List<CardStatus>();

        public Player(int id)
        {
            this.player_id = id;
            this.username = "Player_" + id;
        }

        public bool IsReady() => ready && cards_all.Count > 0;
        public bool IsConnected() => connected || is_ai;
    }

    [Serializable]
    public struct GameSettings
    {
        public int nb_players;
        public static GameSettings Default => new GameSettings { nb_players = 2 };
    }

    [Serializable]
    public class Game
    {
        public string game_uid;
        public GameSettings settings = GameSettings.Default;

        public int first_player = 0;
        public int current_player = 0;
        public int turn_count = 0;
        public float turn_timer = 0f;

        public GameState state = GameState.Connecting;
        public GamePhase phase = GamePhase.None;

        public Player[] players = Array.Empty<Player>();

        public SelectorType selector = SelectorType.None;
        public int selector_player_id = 0;
        public string selector_ability_id;
        public string selector_caster_uid;

        public string last_played;
        public string last_target;
        public string last_destroyed;
        public string last_summoned;
        public string ability_triggerer;
        public int rolled_value;

        public HashSet<string> ability_played = new HashSet<string>();
        public HashSet<string> cards_attacked = new HashSet<string>();

        [Header("CardFront Dicevaders & Chapter Pacing")]
        public int[] dice_pips = new int[5] { 1, 2, 3, 4, 5 };
        public bool[] dice_locked = new bool[5];
        public int budge_tokens = 2;
        public int chrono_charges = 1;
        public float active_resonance_multiplier = 1.0f;
        public int active_chapter_number = 1;
        public bool is_echo_ghost_match = false;
        public bool high_contrast_silhouette_lock = false;

        public Game() { }

        public Game(string uid, int nb_players)
        {
            this.game_uid = uid;
            players = new Player[nb_players];
            for (int i = 0; i < nb_players; i++)
                players[i] = new Player(i);
            settings = GameSettings.Default;
        }

        public Player GetPlayer(int id)
        {
            if (players != null && id >= 0 && id < players.Length)
                return players[id];
            return null;
        }

        public bool IsOnBoard(Card card)
        {
            if (card == null || players == null)
                return false;
            foreach (Player p in players)
            {
                if (p != null && p.cards_board != null && p.cards_board.Contains(card))
                    return true;
            }
            return false;
        }

        public Card GetSlotCard(Slot slot)
        {
            if (players == null)
                return null;
            foreach (Player p in players)
            {
                if (p == null || p.cards_board == null)
                    continue;
                foreach (Card c in p.cards_board)
                {
                    if (c != null && c.slot.x == slot.x && c.slot.y == slot.y && (Slot.ignore_p || c.slot.p == slot.p))
                        return c;
                }
            }
            return null;
        }
    }
}
