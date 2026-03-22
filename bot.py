import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════
# KART VERİTABANI
# ═══════════════════════════════════════════════

CARDS = {
    "anatomiya": {
        "name": "Anatomiya",
        "power": 5,
        "text": "Onu kəsmədən tanıya bilməzsən.",
        "ability": "Rəqibin kartının gücünü oynamadan əvvəl gör.",
        "category": "tibb"
    },
    "histologiya": {
        "name": "Histologiya",
        "power": 4,
        "text": "Gözlə görünməyən, amma hər şeyin başlandığı yer.",
        "ability": "Rəqibin kartını gör. Əgər gücü səninkindən azdırsa avtomatik qazanırsan.",
        "category": "tibb"
    },
    "rus_dili": {
        "name": "Rus Dili",
        "power": 1,
        "text": "Я — bu sadəcə hərf deyil.",
        "ability": "Rəqibin özəl gücünü bu raundda özün istifadə et.",
        "category": "dil"
    },
    "az_tarixi": {
        "name": "Az. Tarixi",
        "power": 1,
        "text": "Daşlar unudur. Torpaq unutmur.",
        "ability": "Əvvəlki raundda məğlub olmusansa +3 güc qazanırsan.",
        "category": "humanitar"
    },
    "biologiya": {
        "name": "Biologiya",
        "power": 2,
        "text": "Hər canlı bir sual, hər ölüm isə cavabdır.",
        "ability": "Oyundakı ən zəif karta qarşı +2 güc qazanırsan.",
        "category": "tibb"
    },
    "felsefe": {
        "name": "Fəlsəfə",
        "power": 1,
        "text": "Cavab vermək asandır. Düzgün sual vermək — bütün ömür lazımdır.",
        "ability": "Rəqib kartını dəyişərsə onu göstərməlidir, dəyişməzsə -1 güc itirir.",
        "category": "humanitar"
    },
    "kliniki_1": {
        "name": "Kliniki-1",
        "power": 3,
        "text": "İlk dəfə stetoskop taxdı. Ürək döyüntüsü — özünündü.",
        "ability": "+1 güc. Kliniki-2 ilə +2, hər üçü ilə rəqibin gücü yarıya enir.",
        "category": "kliniki",
        "combo": ["kliniki_2", "kliniki_3"]
    },
    "mulki_mudafie": {
        "name": "Mülki Müdafiə",
        "power": 1,
        "text": "Fəlakət vaxtını seçmir. Sən seç.",
        "ability": "Bu raundda rəqibin verdiyi bütün ziyanı sıfırla.",
        "category": "humanitar"
    },
    "informatika": {
        "name": "İnformatika",
        "power": 1,
        "text": "Sistem heç vaxt yatmır.",
        "ability": "Rəqib özəl gücünü aktivləşdiribsə onu gör və blokla.",
        "category": "humanitar"
    },
    "az_dili": {
        "name": "Az. Dili",
        "power": 1,
        "text": "Ana dili — öyrənilmir. Xatırlanır.",
        "ability": "Tək oynansa istənilən dil kartını məğlub edir. 3 dil kombosunu da məğlub edir.",
        "category": "dil",
        "special": "az_dili_wins"
    },
    "normal_fiz": {
        "name": "Normal Fiziologiya",
        "power": 5,
        "text": "Hər vuruş, hər nəfəs — milyonlarla ilin mükəmməl nəticəsi.",
        "ability": "Öz gücünə +1 əlavə et. Patoloji fiziologiyaya qarşı -1 güclə başlayır.",
        "category": "tibb",
        "special": "normal_vs_patfiz"
    },
    "biokimya": {
        "name": "Biokimya",
        "power": 4,
        "text": "Sevgi də, ölüm də — sonda eyni molekullardır.",
        "ability": "Növbəti raundda öz kartının gücü +1 olur.",
        "category": "tibb",
        "combo": ["kliniki_biokimya"]
    },
    "biofizika": {
        "name": "Biofizika",
        "power": 2,
        "text": "Bədən fizika qanunlarını pozmur.",
        "ability": "Rəqibin özəl gücü bu raundda işləmir.",
        "category": "tibb"
    },
    "epidemiologiya": {
        "name": "Epidemiologiya",
        "power": 3,
        "text": "Bir nəfər xəstələnir. Epidemioloq min nəfəri görür.",
        "ability": "Rəqib bu raundda kartını dəyişə bilməz.",
        "category": "tibb",
        "combo": ["biostatistika"]
    },
    "biostatistika": {
        "name": "Biostatistika",
        "power": 2,
        "text": "Rəqəmlər yalan söyləmir. Ama bəzən tam doğrunu da söyləmir.",
        "ability": "Rəqibin gücü səninkindən yüksəkdirsə fərqi yarıya endir.",
        "category": "tibb",
        "combo": ["epidemiologiya"]
    },
    "kliniki_2": {
        "name": "Kliniki-2",
        "power": 3,
        "text": "Artıq titrəmir. Çox az.",
        "ability": "Bu raundda məğlub olsan belə rəqib güc qazanmır — bərabər sayılır.",
        "category": "kliniki",
        "combo": ["kliniki_1", "kliniki_3"]
    },
    "tekamul": {
        "name": "Təkamül Genetikası",
        "power": 2,
        "text": "Sən milyonlarla ilin eksperimental nəticəsisən.",
        "ability": "Rəqibin gücü səninkindən 2 artıqdırsa fərqi 1-ə endir.",
        "category": "tibb"
    },
    "mikrobiologiya": {
        "name": "Mikrobiologiya",
        "power": 5,
        "text": "Onları görmürsən. Ama onlar səni çoxdan görmüşlər.",
        "ability": "Rəqibin növbəti 2 raundunda gücü -1 olur.",
        "category": "tibb"
    },
    "pat_fiz": {
        "name": "Patoloji Fiziologiya",
        "power": 5,
        "text": "Normal nə vaxt bitir, xəstəlik nə vaxt başlayır?",
        "ability": "Normal Fiziologiyaya qarşı +2 güc qazanır. Həmin kartın özəl gücü işləmir.",
        "category": "tibb",
        "special": "beats_normal_fiz"
    },
    "farmakologiya": {
        "name": "Farmakologiya",
        "power": 5,
        "text": "Hər dərman — zəhər. Fərq yalnız dozadadır.",
        "ability": "Rəqibin özəl gücünü blokla və öz gücünə +1 əlavə et.",
        "category": "tibb"
    },
    "ictimai_sag": {
        "name": "İctimai Sağlamlıq",
        "power": 3,
        "text": "Bir xəstəni müalicə edən həkim. Milyon xəstənin qarşısını alan — ictimai sağlamlıq.",
        "ability": "Əlindəki bütün kartların gücü bu raundda +1 olur.",
        "category": "tibb"
    },
    "qidalanma": {
        "name": "Qidalanmanın Əsasları",
        "power": 2,
        "text": "Sən nə yeyirsənsə — o sən deyilsən. Ama yaxınına gəlir.",
        "ability": "Növbəti raundda öz kartının gücü +2 olur.",
        "category": "tibb"
    },
    "umumi_cer": {
        "name": "Ümumi Cərrahiyyə",
        "power": 4,
        "text": "Bıçaq problemi həll edir. Əl isə həyatı.",
        "ability": "Rəqibin kartının özəl gücünü tamamilə sil.",
        "category": "tibb"
    },
    "pat_anat": {
        "name": "Patoloji Anatomiya",
        "power": 5,
        "text": "Ölüm cavab verir. Sən yalnız sualı düzgün vermək lazımdır.",
        "ability": "Tibb kartlarına qarşı +1 güc qazanır.",
        "category": "tibb",
        "special": "beats_anatomiya"
    },
    "nevrologiya": {
        "name": "Nevrologiya",
        "power": 4,
        "text": "Beyin özünü anlamağa çalışan yeganə organdır.",
        "ability": "Rəqib növbəti raundda öz kartını görə bilmir.",
        "category": "tibb"
    },
    "kliniki_3": {
        "name": "Kliniki-3",
        "power": 3,
        "text": "3-cü ildə artıq sual vermirsən — diaqnoz qoyursan.",
        "ability": "Əvvəlki 2 raundda istifadə edilməyibsə bu raundda gücü +2 olur.",
        "category": "kliniki",
        "combo": ["kliniki_1", "kliniki_2"]
    },
    "genetik_xes": {
        "name": "Uşaqlarda Genetik Xəstəliklər",
        "power": 3,
        "text": "Bəzən cavab doğulmadan əvvəl yazılmışdır.",
        "ability": "Rəqibin kartının özəl gücü işləmir. Ama sənin gücündən də -1 gedir.",
        "category": "tibb"
    },
    "endokrin": {
        "name": "Endokrinologiya",
        "power": 4,
        "text": "Hormonlar səssiz əmr verir. Bədən isə itaət edir.",
        "ability": "1ci raundda normal, 2ci raundda +1, 3cü raundda +2 güc qazanır.",
        "category": "tibb",
        "combo": ["hemotologiya"]
    },
    "hemotologiya": {
        "name": "Hemotologiya",
        "power": 4,
        "text": "Qan həyatın özüdür — hərəkətdə olan, dayanmayan.",
        "ability": "Bu raundda məğlub olsan belə növbəti raundda +1 güclə başlayırsan.",
        "category": "tibb",
        "combo": ["endokrin"]
    },
    "deri_zoh": {
        "name": "Dəri Zöhrəvi",
        "power": 3,
        "text": "Ən böyük orqan — eyni zamanda ən çox görmənin altında qalan.",
        "ability": "Rəqibin kartı bu raundda özəl gücünü istifadə edə bilmir.",
        "category": "tibb"
    },
    "radiologiya": {
        "name": "Radiologiya",
        "power": 3,
        "text": "O görür ki, gözlər görə bilmir.",
        "ability": "Rəqibin gizli kartını gör.",
        "category": "tibb"
    },
    "ilkin_tibbi": {
        "name": "İlkin Tibbi Yardım",
        "power": 3,
        "text": "İlk dəqiqə — bəzən son şansdır.",
        "ability": "Xəstəlik kartlarına qarşı rəqibin gücündən -2 sil.",
        "category": "tibb",
        "special": "heals_diseases"
    },
    "parazitologiya": {
        "name": "Parazitologiya",
        "power": 3,
        "text": "Sən onu görmürsən. O səni görür.",
        "ability": "Hər raund rəqibin gücündən -1 sil — kart əldə qaldıqca davam edir.",
        "category": "tibb"
    },
    "yoluxucu": {
        "name": "Yoluxucu Xəstəliklər",
        "power": 4,
        "text": "Düşmən gözlə görünmür. Ama izi qalır.",
        "ability": "Rəqibin əlindəki bütün kartların gücü -1 olur.",
        "category": "xestaliq"
    },
    "bioetika": {
        "name": "Bioetika",
        "power": 2,
        "text": "Edə bilmək — etmək deməkdir?",
        "ability": "İstənilən özəl gücü blokla — amma öz gücündən də -1 get.",
        "category": "humanitar"
    },
    "multikultur": {
        "name": "Multikulturalizm",
        "power": 1,
        "text": "Fərqlər bizi ayırmır — zənginləşdirir.",
        "ability": "Əlində 3 fərqli kateqoriyadan kart varsa +2 güc qazanırsan.",
        "category": "humanitar"
    },
    "ingilis_dili": {
        "name": "İngilis Dili",
        "power": 1,
        "text": "To be or not to be — bu sual hələ aktualdır.",
        "ability": "3 dil kombosu ilə rəqibin özəl gücü işləmir. Az dilinə qarşı həmişə məğlub olur.",
        "category": "dil",
        "combo": ["rus_dili", "alman_dili"]
    },
    "alman_dili": {
        "name": "Alman Dili",
        "power": 1,
        "text": "Ordnung muss sein — nizam olmalıdır.",
        "ability": "3 dil kombosu ilə rəqibin özəl gücü işləmir. Az dilinə qarşı həmişə məğlub olur.",
        "category": "dil",
        "combo": ["rus_dili", "ingilis_dili"]
    },
    "dinamik_anat": {
        "name": "Dinamik Anatomiya",
        "power": 4,
        "text": "Hərəkətdə olan bədən — dayanmış bədəndən tamamilə başqadır.",
        "ability": "Tək oynansa Normal və Patoloji Anatomiyaya məğlub olur. İkisi birlikdə gələndə hər ikisini məğlub edir.",
        "category": "tibb",
        "special": "dinamik_triangle"
    },
    "kliniki_biokimya": {
        "name": "Kliniki Biokimya",
        "power": 4,
        "text": "Qan danışır. Sən yalnız dinləməyi öyrənməlisən.",
        "ability": "Rəqibin növbəti kartı açıq oynanmalıdır.",
        "category": "tibb",
        "combo": ["biokimya"]
    },
}

DISEASE_CARDS = ["yoluxucu", "pat_fiz", "pat_anat", "genetik_xes", "parazitologiya", "deri_zoh"]

# ═══════════════════════════════════════════════
# OYUN VƏZİYYƏTİ
# ═══════════════════════════════════════════════

games = {}

def create_game(chat_id):
    all_card_keys = list(CARDS.keys())
    random.shuffle(all_card_keys)
    mid = len(all_card_keys) // 2
    
    games[chat_id] = {
        "players": [],
        "hands": {},
        "played": {},
        "active": {},
        "scores": {},
        "round": 1,
        "max_rounds": 3,
        "state": "waiting",
        "round_results": [],
        "buffs": {},
        "debuffs": {},
        "blocked": {},
        "endokrin_rounds": {},
        "kliniki3_unused": {},
        "deck1": all_card_keys[:mid],
        "deck2": all_card_keys[mid:],
        "revealed": {},
    }

def get_hand_keyboard(hand, active_cards, chat_id, player_id):
    keyboard = []
    for card_key in hand:
        card = CARDS[card_key]
        active = "🟢" if card_key in active_cards else "🔴"
        keyboard.append([
            InlineKeyboardButton(
                f"{active} {card['name']} (⭐{card['power']})",
                callback_data=f"play_{card_key}"
            )
        ])
    keyboard.append([InlineKeyboardButton("📋 Kartlarımı gör", callback_data="view_cards")])
    return InlineKeyboardMarkup(keyboard)

def get_card_detail_keyboard(hand, active_cards):
    keyboard = []
    for card_key in hand:
        card = CARDS[card_key]
        active = "🟢 AKTİV" if card_key in active_cards else "🔴 PASİV"
        keyboard.append([
            InlineKeyboardButton(
                f"{'✅' if card_key in active_cards else '❌'} {card['name']} — aktivliyi dəyiş",
                callback_data=f"toggle_{card_key}"
            )
        ])
    keyboard.append([InlineKeyboardButton("🎮 Kart oyna", callback_data="play_menu")])
    return InlineKeyboardMarkup(keyboard)

# ═══════════════════════════════════════════════
# GÜCLƏR VƏ MEXANİKA
# ═══════════════════════════════════════════════

def calculate_power(card_key, is_active, game, player_id, opponent_id, opponent_card_key):
    card = CARDS[card_key]
    base_power = card["power"]
    
    buffs = game["buffs"].get(player_id, {})
    debuffs = game["debuffs"].get(player_id, {})
    
    final_power = base_power
    
    # Bufları tətbiq et
    if "power_boost" in buffs:
        final_power += buffs["power_boost"]
    
    # Debufları tətbiq et
    if "power_reduction" in debuffs:
        final_power -= debuffs["power_reduction"]
    
    if not is_active:
        return max(1, final_power)
    
    opp_card = CARDS.get(opponent_card_key, {})
    
    # Aktiv güclər
    if card_key == "normal_fiz":
        final_power += 1
        if opponent_card_key == "pat_fiz":
            final_power -= 1
    
    elif card_key == "az_tarixi":
        if game["round_results"] and game["round_results"][-1].get("loser") == player_id:
            final_power += 3
    
    elif card_key == "farmakologiya":
        final_power += 1
    
    elif card_key == "pat_fiz":
        if opponent_card_key == "normal_fiz":
            final_power += 2
    
    elif card_key == "pat_anat":
        if opp_card.get("category") == "tibb":
            final_power += 1
    
    elif card_key == "ilkin_tibbi":
        if opponent_card_key in DISEASE_CARDS:
            final_power -= 2
    
    elif card_key == "bioetika":
        final_power -= 1
    
    elif card_key == "genetik_xes":
        final_power -= 1
    
    elif card_key == "endokrin":
        rounds_used = game["endokrin_rounds"].get(player_id, 0)
        final_power += rounds_used
        game["endokrin_rounds"][player_id] = rounds_used + 1
    
    elif card_key == "kliniki_3":
        unused = game["kliniki3_unused"].get(player_id, 0)
        if unused >= 2:
            final_power += 2
    
    elif card_key == "biologiya":
        min_power = min(CARDS[k]["power"] for k in game["hands"].get(opponent_id, []))
        if opponent_card_key and CARDS[opponent_card_key]["power"] == min_power:
            final_power += 2
    
    elif card_key == "multikultur":
        categories = set(CARDS[k]["category"] for k in game["hands"].get(player_id, []))
        if len(categories) >= 3:
            final_power += 2
    
    return max(1, final_power)


def apply_post_round_effects(card_key, is_active, game, player_id, opponent_id):
    if not is_active:
        return
    
    card = CARDS[card_key]
    
    if card_key == "mikrobiologiya":
        if "power_reduction" not in game["debuffs"].get(opponent_id, {}):
            game["debuffs"].setdefault(opponent_id, {})["power_reduction"] = 1
            game["debuffs"][opponent_id]["mikro_rounds"] = 2
    
    elif card_key == "nevrologiya":
        game["blocked"].setdefault(opponent_id, {})["view_card"] = True
    
    elif card_key == "biokimya":
        game["buffs"].setdefault(player_id, {})["power_boost"] = 1
        game["buffs"][player_id]["biokimya_next"] = True
    
    elif card_key == "qidalanma":
        game["buffs"].setdefault(player_id, {})["power_boost"] = 2
        game["buffs"][player_id]["qidalanma_next"] = True
    
    elif card_key == "hemotologiya":
        game["buffs"].setdefault(player_id, {})["hemo_next"] = True
    
    elif card_key == "yoluxucu":
        game["debuffs"].setdefault(opponent_id, {})["power_reduction"] = game["debuffs"].get(opponent_id, {}).get("power_reduction", 0) + 1

    elif card_key == "parazitologiya":
        game["debuffs"].setdefault(opponent_id, {})["power_reduction"] = game["debuffs"].get(opponent_id, {}).get("power_reduction", 0) + 1

    elif card_key == "kliniki_3":
        game["kliniki3_unused"][player_id] = 0


def check_special_win(p1_card, p2_card, p1_active, p2_active, game, p1_id, p2_id):
    """Xüsusi qalib şərtlərini yoxla. None = normal müqayisə, p1_id/p2_id = qalib"""
    
    # Azərbaycan dili qaydası
    if p1_active and p1_card == "az_dili" and CARDS[p2_card]["category"] == "dil":
        return p1_id
    if p2_active and p2_card == "az_dili" and CARDS[p1_card]["category"] == "dil":
        return p2_id
    
    # Dinamik anatomiya üçbucağı
    if p1_card == "dinamik_anat" and p1_active:
        if p2_card in ["anatomiya", "pat_anat"]:
            return p2_id
    if p2_card == "dinamik_anat" and p2_active:
        if p1_card in ["anatomiya", "pat_anat"]:
            return p1_id
    
    # Patoloji vs Normal
    if p1_card == "pat_fiz" and p2_card == "normal_fiz":
        return p1_id
    if p2_card == "pat_fiz" and p1_card == "normal_fiz":
        return p2_id
    if p1_card == "pat_anat" and p2_card == "anatomiya":
        return p1_id
    if p2_card == "pat_anat" and p1_card == "anatomiya":
        return p2_id
    
    return None


def check_combo(player_id, played_card, game):
    """Kombo yoxla"""
    card = CARDS[played_card]
    combos = card.get("combo", [])
    if not combos:
        return False
    
    hand = game["hands"].get(player_id, [])
    active = game["active"].get(player_id, [])
    
    # Kliniki kombo
    if played_card in ["kliniki_1", "kliniki_2", "kliniki_3"]:
        kliniki_in_hand = [k for k in hand if k in ["kliniki_1", "kliniki_2", "kliniki_3"]]
        if len(kliniki_in_hand) >= 3:
            return "kliniki_full"
        elif len(kliniki_in_hand) >= 2:
            return "kliniki_partial"
    
    # Epidemiologiya + Biostatistika
    if played_card == "epidemiologiya" and "biostatistika" in hand:
        return "epi_bio"
    if played_card == "biostatistika" and "epidemiologiya" in hand:
        return "epi_bio"
    
    # Endokrin + Hemo
    if played_card == "endokrin" and "hemotologiya" in hand:
        return "endo_hemo"
    if played_card == "hemotologiya" and "endokrin" in hand:
        return "endo_hemo"
    
    # Biokimya + Kliniki biokimya
    if played_card == "biokimya" and "kliniki_biokimya" in hand:
        return "bio_kliniki"
    if played_card == "kliniki_biokimya" and "biokimya" in hand:
        return "bio_kliniki"
    
    # Dil kombosu
    dil_cards = [k for k in hand if CARDS[k]["category"] == "dil"]
    if played_card in ["rus_dili", "ingilis_dili", "alman_dili"] and len(dil_cards) >= 3:
        return "dil_kombo"
    
    return False

# ═══════════════════════════════════════════════
# KOMANDA İŞLƏYİCİLƏRİ
# ═══════════════════════════════════════════════

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎴 *CodeBlue Kart Oyununa Xoş Gəldiniz!*\n\n"
        "İki oyunçu üçün tibbi kart oyunu.\n\n"
        "📌 *Komandalar:*\n"
        "/newgame — Yeni oyun başlat\n"
        "/join — Oyuna qoşul\n"
        "/hand — Kartlarını gör\n"
        "/rules — Qaydalar\n"
        "/help — Kömək",
        parse_mode="Markdown"
    )

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *CodeBlue Qaydaları:*\n\n"
        "🎮 *Necə oynanır:*\n"
        "• 2 oyunçu, 3 raund\n"
        "• Hər raundda 1 kart seçirsən\n"
        "• Daha yüksək güc olan qazanır\n\n"
        "🟢 *Aktiv/Passiv sistem:*\n"
        "• 🟢 Aktiv: Ulduz gücü + özəl güc\n"
        "• 🔴 Passiv: Yalnız ulduz gücü\n\n"
        "⭐ *Güc:* 1-5 arasında\n\n"
        "🔀 *Kombolar:* Bəzi kartlar birlikdə xüsusi güc qazanır\n\n"
        "🏆 *3 raunddan 2-ni qazanan oyunu qazanır!*",
        parse_mode="Markdown"
    )

async def new_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    create_game(chat_id)
    game = games[chat_id]
    game["players"].append(user.id)
    game["hands"][user.id] = game["deck1"][:5]
    game["active"][user.id] = []
    game["scores"][user.id] = 0
    game["buffs"][user.id] = {}
    game["debuffs"][user.id] = {}
    game["blocked"][user.id] = {}
    game["endokrin_rounds"][user.id] = 0
    game["kliniki3_unused"][user.id] = 0
    
    await update.message.reply_text(
        f"🎴 *Yeni oyun yaradıldı!*\n\n"
        f"👤 {user.first_name} oyuna qoşuldu.\n\n"
        f"İkinci oyunçu /join yazaraq qoşula bilər.",
        parse_mode="Markdown"
    )

async def join_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    if chat_id not in games:
        await update.message.reply_text("❌ Aktiv oyun yoxdur. /newgame ilə yeni oyun başladın.")
        return
    
    game = games[chat_id]
    
    if user.id in game["players"]:
        await update.message.reply_text("⚠️ Artıq oyundasınız!")
        return
    
    if len(game["players"]) >= 2:
        await update.message.reply_text("❌ Oyun artıq doludur!")
        return
    
    game["players"].append(user.id)
    game["hands"][user.id] = game["deck2"][:5]
    game["active"][user.id] = []
    game["scores"][user.id] = 0
    game["buffs"][user.id] = {}
    game["debuffs"][user.id] = {}
    game["blocked"][user.id] = {}
    game["endokrin_rounds"][user.id] = 0
    game["kliniki3_unused"][user.id] = 0
    game["state"] = "playing"
    
    p1 = game["players"][0]
    
    await update.message.reply_text(
        f"✅ *{user.first_name} oyuna qoşuldu!*\n\n"
        f"🎮 Oyun başlayır! Raund 1\n\n"
        f"Hər oyunçu /hand yazaraq kartlarını görə bilər.",
        parse_mode="Markdown"
    )

async def show_hand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    if chat_id not in games:
        await update.message.reply_text("❌ Aktiv oyun yoxdur.")
        return
    
    game = games[chat_id]
    
    if user.id not in game["players"]:
        await update.message.reply_text("❌ Siz bu oyunda deyilsiniz.")
        return
    
    hand = game["hands"].get(user.id, [])
    active_cards = game["active"].get(user.id, [])
    
    text = f"🃏 *Kartlarınız — Raund {game['round']}:*\n\n"
    for card_key in hand:
        card = CARDS[card_key]
        active_status = "🟢 AKTİV" if card_key in active_cards else "🔴 PASİV"
        text += f"{active_status} *{card['name']}* ⭐{card['power']}\n"
        text += f"_{card['ability']}_\n\n"
    
    keyboard = get_card_detail_keyboard(hand, active_cards)
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    chat_id = query.message.chat_id
    user = query.from_user
    data = query.data
    
    if chat_id not in games:
        await query.edit_message_text("❌ Aktiv oyun yoxdur.")
        return
    
    game = games[chat_id]
    
    if user.id not in game["players"]:
        await query.answer("Siz bu oyunda deyilsiniz!", show_alert=True)
        return
    
    # Kartı aktiv/passiv et
    if data.startswith("toggle_"):
        card_key = data.replace("toggle_", "")
        active = game["active"].get(user.id, [])
        
        if card_key in active:
            active.remove(card_key)
            status = "🔴 PASİV"
        else:
            active.append(card_key)
            status = "🟢 AKTİV"
        
        game["active"][user.id] = active
        hand = game["hands"].get(user.id, [])
        keyboard = get_card_detail_keyboard(hand, active)
        
        card_name = CARDS[card_key]["name"]
        await query.edit_message_text(
            f"*{card_name}* — {status} edildi!\n\nDigər kartları da dəyişə bilərsiniz:",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    
    # Oynama menyusu
    elif data == "play_menu":
        hand = game["hands"].get(user.id, [])
        active = game["active"].get(user.id, [])
        keyboard = get_hand_keyboard(hand, active, chat_id, user.id)
        await query.edit_message_text(
            f"🎮 *Raund {game['round']} — Kart seçin:*\n\n"
            f"🟢 = Aktiv (özəl güc + ulduz güc)\n"
            f"🔴 = Passiv (yalnız ulduz güc)",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    
    # Kartları gör
    elif data == "view_cards":
        hand = game["hands"].get(user.id, [])
        active = game["active"].get(user.id, [])
        keyboard = get_card_detail_keyboard(hand, active)
        
        text = f"🃏 *Kartlarınız:*\n\n"
        for card_key in hand:
            card = CARDS[card_key]
            active_status = "🟢" if card_key in active else "🔴"
            text += f"{active_status} *{card['name']}* ⭐{card['power']}\n_{card['ability']}_\n\n"
        
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
    
    # Kart oyna
    elif data.startswith("play_"):
        card_key = data.replace("play_", "")
        
        if card_key not in game["hands"].get(user.id, []):
            await query.answer("Bu kart sizdə yoxdur!", show_alert=True)
            return
        
        if user.id in game["played"]:
            await query.answer("Bu raundda artıq kart oynadınız!", show_alert=True)
            return
        
        active_cards = game["active"].get(user.id, [])
        is_active = card_key in active_cards
        
        game["played"][user.id] = {
            "card": card_key,
            "active": is_active
        }
        
        card = CARDS[card_key]
        status = "🟢 AKTİV" if is_active else "🔴 PASİV"
        
        await query.edit_message_text(
            f"✅ *{card['name']}* oynadınız! ({status})\n\n"
            f"Rəqibin oynamasını gözləyin...",
            parse_mode="Markdown"
        )
        
        # Hər iki oyunçu oynadısa
        if len(game["played"]) == 2:
            await resolve_round(context, chat_id, game)

async def resolve_round(context, chat_id, game):
    players = game["players"]
    p1_id = players[0]
    p2_id = players[1]
    
    p1_played = game["played"][p1_id]
    p2_played = game["played"][p2_id]
    
    p1_card = p1_played["card"]
    p2_card = p2_played["card"]
    p1_active = p1_played["active"]
    p2_active = p2_played["active"]
    
    # Xüsusi qalib şərtlərini yoxla
    special_winner = check_special_win(p1_card, p2_card, p1_active, p2_active, game, p1_id, p2_id)
    
    if special_winner:
        winner_id = special_winner
        loser_id = p2_id if winner_id == p1_id else p1_id
        p1_power = CARDS[p1_card]["power"]
        p2_power = CARDS[p2_card]["power"]
    else:
        p1_power = calculate_power(p1_card, p1_active, game, p1_id, p2_id, p2_card)
        p2_power = calculate_power(p2_card, p2_active, game, p2_id, p1_id, p1_card)
        
        # Kombo yoxla
        p1_combo = check_combo(p1_id, p1_card, game)
        p2_combo = check_combo(p2_id, p2_card, game)
        
        if p1_combo == "kliniki_full":
            p2_power = max(1, p2_power // 2)
        if p2_combo == "kliniki_full":
            p1_power = max(1, p1_power // 2)
        
        if p1_power > p2_power:
            winner_id = p1_id
            loser_id = p2_id
        elif p2_power > p1_power:
            winner_id = p2_id
            loser_id = p1_id
        else:
            winner_id = None
            loser_id = None
    
    # Mülki müdafiə bloku
    if p1_active and p1_card == "mulki_mudafie":
        winner_id = None
        loser_id = None
    if p2_active and p2_card == "mulki_mudafie":
        winner_id = None
        loser_id = None
    
    # Nəticəni qeyd et
    if winner_id:
        game["scores"][winner_id] = game["scores"].get(winner_id, 0) + 1
        game["round_results"].append({"winner": winner_id, "loser": loser_id})
    else:
        game["round_results"].append({"winner": None, "loser": None})
    
    # Post-raund effektlər
    apply_post_round_effects(p1_card, p1_active, game, p1_id, p2_id)
    apply_post_round_effects(p2_card, p2_active, game, p2_id, p1_id)
    
    # Debuf yenilə
    for pid in players:
        debuffs = game["debuffs"].get(pid, {})
        if "mikro_rounds" in debuffs:
            debuffs["mikro_rounds"] -= 1
            if debuffs["mikro_rounds"] <= 0:
                debuffs.pop("mikro_rounds", None)
                debuffs.pop("power_reduction", None)
    
    # Hemotologiya effekti
    for pid in players:
        buffs = game["buffs"].get(pid, {})
        if buffs.get("hemo_next") and pid == loser_id:
            game["buffs"][pid]["power_boost"] = game["buffs"][pid].get("power_boost", 0) + 1
            buffs.pop("hemo_next", None)
    
    p1_card_name = CARDS[p1_card]["name"]
    p2_card_name = CARDS[p2_card]["name"]
    
    result_text = (
        f"⚔️ *Raund {game['round']} Nəticəsi:*\n\n"
        f"👤 Oyunçu 1: *{p1_card_name}* {'🟢' if p1_active else '🔴'} — {p1_power} güc\n"
        f"👤 Oyunçu 2: *{p2_card_name}* {'🟢' if p2_active else '🔴'} — {p2_power} güc\n\n"
    )
    
    if winner_id:
        winner_num = 1 if winner_id == p1_id else 2
        result_text += f"🏆 *Oyunçu {winner_num} bu raundu qazandı!*\n\n"
    else:
        result_text += f"🤝 *Bərabər!*\n\n"
    
    result_text += f"📊 *Hesab:* Oyunçu 1 — {game['scores'].get(p1_id, 0)} | Oyunçu 2 — {game['scores'].get(p2_id, 0)}\n"
    
    # Kartları əldən çıxar
    game["hands"][p1_id].remove(p1_card)
    game["hands"][p2_id].remove(p2_card)
    game["played"] = {}
    
    # Kliniki 3 sayacı
    for pid in players:
        hand = game["hands"].get(pid, [])
        if "kliniki_3" in hand and game["played"].get(pid, {}).get("card") != "kliniki_3":
            game["kliniki3_unused"][pid] = game["kliniki3_unused"].get(pid, 0) + 1
    
    game["round"] += 1
    
    # Oyun bitdi?
    if game["round"] > game["max_rounds"] or not game["hands"][p1_id] or not game["hands"][p2_id]:
        p1_score = game["scores"].get(p1_id, 0)
        p2_score = game["scores"].get(p2_id, 0)
        
        if p1_score > p2_score:
            final_text = result_text + "\n🎉 *OYUNİ 1-Cİ OYUNÇU QAZANDI!*"
        elif p2_score > p1_score:
            final_text = result_text + "\n🎉 *OYUNİ 2-Cİ OYUNÇU QAZANDI!*"
        else:
            final_text = result_text + "\n🤝 *OYUN BƏRABƏRLİKLƏ BİTDİ!*"
        
        final_text += f"\n\nYeni oyun üçün /newgame yazın."
        del games[chat_id]
        
        await context.bot.send_message(chat_id, final_text, parse_mode="Markdown")
    else:
        result_text += f"\n\nRaund {game['round']} başlayır! /hand yazaraq kartlarınızı görün."
        await context.bot.send_message(chat_id, result_text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 *Kömək:*\n\n"
        "/newgame — Yeni oyun başlat\n"
        "/join — Oyuna qoşul\n"
        "/hand — Kartlarını gör və oyna\n"
        "/rules — Oyun qaydaları\n\n"
        "💡 *İpucu:* Kartı oynamadan əvvəl aktiv/passiv vəziyyətini dəyiş!\n"
        "🟢 Aktiv = özəl güc işləyir\n"
        "🔴 Passiv = yalnız ulduz gücü",
        parse_mode="Markdown"
    )

# ═══════════════════════════════════════════════
# ANA FUNKSIYA
# ═══════════════════════════════════════════════

def main():
    import os
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("BOT_TOKEN tapılmadı!")
        return
    
    app = Application.builder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("newgame", new_game))
    app.add_handler(CommandHandler("join", join_game))
    app.add_handler(CommandHandler("hand", show_hand))
    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("CodeBlue Bot işə düşdü!")
    app.run_polling()

if __name__ == "__main__":
    main()
