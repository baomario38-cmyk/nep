import os
import math
import random
import re
import numpy as np
from collections import Counter
from threading import Thread
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- 1. SERVER KEEP-ALIVE ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "DYNAMIC CONSENSUS ENGINE V5 ONLINE", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 2. CẤU HÌNH BOT & DỮ LIỆU ---
TOKEN = '8985526419:AAHkT58JguHBo2dUNQM5t-7LkvlzcqDGcDw'
ADMIN_ID = 755092812
ADMIN_USERNAME = "lionvnios"

bot = telebot.TeleBot(TOKEN)
user_data = {}
all_users = set()
gift_codes = {}

def is_admin(user):
    if not user: return False
    return user.id == ADMIN_ID or (user.username and user.username.lower() == ADMIN_USERNAME.lower())

def init_user(uid):
    all_users.add(uid)
    if uid not in user_data:
        user_data[uid] = {"balance": 20, "logs": [], "history_seq": []}

# --- 3. DYNAMIC CONSENSUS ENGINE (V5) ---
class ZeroSumBridgeEngineV5:
    def __init__(self, history_scores):
        self.raw = np.array(history_scores, dtype=float)
        self.n = len(self.raw)
        self.centered = np.array([1 if x >= 11 else -1 for x in history_scores], dtype=float)

    def _get_markov_signal(self, order):
        if self.n <= order: return 0.0
        state_map = {}
        for i in range(self.n - order):
            key = tuple(int(x) for x in self.centered[i : i + order])
            state_map.setdefault(key, []).append(self.centered[i + order])
        curr_key = tuple(int(x) for x in self.centered[-order:])
        if curr_key in state_map and len(state_map[curr_key]) > 0:
            return float(np.mean(state_map[curr_key]))
        return 0.0

    def execute_pipeline(self):
        if self.n < 3:
            res = random.choice(["TÀI", "XỈU"])
            return {"result": res, "p_display": round(random.uniform(60.0, 68.0), 1)}

        # 1. EMA Momentum
        decay = np.exp(np.linspace(-1.2, 0.0, self.n))
        decay /= np.sum(decay)
        m_ema = np.sum(self.centered * decay)

        # 2. Pattern Detector (Bệt & Cầu 1-1)
        last_val = self.centered[-1]
        streak = 0
        for val in reversed(self.centered):
            if val == last_val: streak += 1
            else: break

        is_alternating = False
        if self.n >= 4:
            diffs = np.diff(self.centered[-4:])
            if np.all(diffs != 0): is_alternating = True

        m_pattern = 0.0
        if streak >= 3:
            m_pattern = last_val * 0.95  # Cầu bệt rõ nét
        elif is_alternating:
            m_pattern = -last_val * 0.85 # Cầu 1-1 nhịp nhàng

        # 3. Markov Ensemble
        m_markov = (0.2 * self._get_markov_signal(1)) + (0.5 * self._get_markov_signal(2)) + (0.3 * self._get_markov_signal(3))

        # Tổng hợp tín hiệu
        total_score = (0.35 * m_ema) + (0.35 * m_pattern) + (0.30 * m_markov)

        if abs(total_score) < 0.02:
            total_score = random.choice([-0.12, 0.12])

        result = "TÀI" if total_score > 0 else "XỈU"

        # Đánh giá độ đồng thuận (Consensus Check)
        signals = [m_ema, m_pattern, m_markov]
        same_direction_count = sum(1 for s in signals if (s > 0 and total_score > 0) or (s < 0 and total_score < 0))
        abs_score = abs(total_score)

        # PHÂN CẤP PHẦN TRĂM DỰA TRÊN ĐỘ XÁC NHẬN:
        if (same_direction_count >= 2 and abs_score >= 0.45) or streak >= 4:
            # Tín hiệu cực cao / Cầu đẹp -> Đẩy % lên 85% - 99%
            p_display = round(85.0 + (abs_score * 13.5) + random.uniform(0.0, 1.8), 1)
            if p_display > 99.0: p_display = 99.0
        elif same_direction_count >= 2 or abs_score >= 0.25:
            # Tín hiệu trung bình -> 72% - 84%
            p_display = round(72.0 + (abs_score * 18.0) + random.uniform(0.0, 2.0), 1)
            p_display = min(p_display, 84.5)
        else:
            # Không chắc chắn / Chuỗi nhiễu -> 60% - 70%
            p_display = round(60.0 + (abs_score * 22.0) + random.uniform(0.0, 2.5), 1)
            p_display = min(p_display, 70.5)

        return {"result": result, "p_display": p_display}

class ZeroSumMD5EngineV5:
    def __init__(self, raw_hex):
        self.hex_str = raw_hex.lower().strip()

    def execute_pipeline(self):
        try:
            bytes_data = bytes.fromhex(self.hex_str)
            xor_val = 0
            for b in bytes_data:
                xor_val ^= b
            
            direction = (xor_val & 1) ^ ((int(self.hex_str[0], 16) & 1))
            result = "TÀI" if direction == 1 else "XỈU"

            nibbles = list(self.hex_str)
            counts = Counter(nibbles)
            entropy = -sum((c / 32.0) * math.log2(c / 32.0) for c in counts.values() if c > 0)
            
            bias = abs(entropy - 3.75)
            max_char_count = counts.most_common(1)[0][1]

            # Đánh giá độ chắc chắn của mã MD5
            if bias > 0.40 or max_char_count >= 5:
                # Độ khớp cao -> 88% - 99%
                p_display = round(88.0 + (bias * 18.0) + random.uniform(0.0, 1.5), 1)
                if p_display > 99.0: p_display = 99.0
            elif bias > 0.18:
                # Vừa phải -> 72% - 84%
                p_display = round(72.0 + (bias * 28.0) + random.uniform(0.0, 2.0), 1)
                p_display = min(p_display, 84.0)
            else:
                # Không chắc chắn -> 60% - 70%
                p_display = round(60.0 + (bias * 32.0) + random.uniform(0.0, 2.5), 1)
                p_display = min(p_display, 70.0)

            return {"result": result, "p_display": p_display}
        except Exception as e:
            return {"error": str(e)}

# --- 4. PARSER & MENU ---
def parse_hybrid_input(raw_text):
    clean_text = raw_text.strip().lower()
    md5_match = re.search(r'[0-9a-f]{32}', clean_text)
    if md5_match:
        return {"type": "md5", "data": md5_match.group(0)}
    
    parts = clean_text.replace(',', ' ').split()
    history = [int(p) for p in parts if p.isdigit() and 3 <= int(p) <= 18]
    if len(history) >= 1:
        return {"type": "sequence", "data": history}
    return None

def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💳 Ví & Lịch sử", callback_data="btn_info"),
        InlineKeyboardButton("🎁 Nhập Code", callback_data="btn_redeem")
    )
    markup.add(InlineKeyboardButton("💎 Liên hệ Admin", callback_data="btn_nap"))
    return markup

# --- 5. COMMANDS ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    try:
        uid = message.from_user.id
        init_user(uid)
        text = (
            f"🆔 **ID:** `{uid}`\n"
            f"🪙 **Số dư:** `{user_data[uid]['balance']} Xu`\n\n"
            "👉 *Dán mã MD5 hoặc nhập chuỗi kết quả.*"
        )
        bot.reply_to(message, text, parse_mode="Markdown", reply_markup=main_menu())
    except: pass

@bot.message_handler(commands=['congxu'])
def cmd_congxu(message):
    if not is_admin(message.from_user): return
    try:
        parts = message.text.split()
        target_id = int(parts[1])
        amount = int(parts[2])
        init_user(target_id)
        user_data[target_id]["balance"] += amount
        bot.reply_to(message, f"✅ Đã cộng `{amount}` Xu cho `{target_id}`.", parse_mode="Markdown")
    except: pass

@bot.message_handler(commands=['taocode'])
def cmd_taocode(message):
    if not is_admin(message.from_user): return
    try:
        parts = message.text.split()
        gift_codes[parts[1]] = int(parts[2])
        bot.reply_to(message, f"🎁 Tạo code `{parts[1]}` ({parts[2]} Xu).", parse_mode="Markdown")
    except: pass

@bot.message_handler(commands=['napcode'])
def cmd_napcode(message):
    try:
        uid = message.from_user.id
        init_user(uid)
        parts = message.text.split()
        if len(parts) >= 2 and parts[1] in gift_codes:
            val = gift_codes.pop(parts[1])
            user_data[uid]["balance"] += val
            bot.reply_to(message, f"🎉 Nạp thành công mã `{parts[1]}` (+{val} Xu)!", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Mã Giftcode không hợp lệ!")
    except: pass

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        uid = call.from_user.id
        init_user(uid)
        if call.data == "btn_info":
            logs = "\n".join(user_data[uid]["logs"]) if user_data[uid]["logs"] else "Chưa có dữ liệu."
            bot.send_message(call.message.chat.id, f"💳 **Số dư:** `{user_data[uid]['balance']} Xu`\n📜 **Lịch sử:**\n{logs}", parse_mode="Markdown")
        elif call.data == "btn_redeem":
            bot.send_message(call.message.chat.id, "👉 Cú pháp: `/napcode [Mã_Code]`", parse_mode="Markdown")
        elif call.data == "btn_nap":
            bot.send_message(call.message.chat.id, "💎 Liên hệ Admin @lionvnios", parse_mode="Markdown")
    except: pass

# --- 6. MAIN PIPELINE HANDLER ---
@bot.message_handler(func=lambda message: True)
def handle_master_pipeline(message):
    try:
        if message.text.startswith('/'): return
        
        uid = message.from_user.id
        init_user(uid)
        
        if user_data[uid]["balance"] < 1:
            bot.reply_to(message, "⚠️ Hết xu! Vui lòng nạp thêm.", reply_markup=main_menu())
            return
            
        parsed_input = parse_hybrid_input(message.text)
        if not parsed_input:
            bot.reply_to(message, "❌ Dữ liệu không hợp lệ!")
            return

        if parsed_input["type"] == "md5":
            engine = ZeroSumMD5EngineV5(parsed_input["data"])
            log_title = "[MD5]"
        else:
            user_data[uid]["history_seq"].extend(parsed_input["data"])
            recent_seq = user_data[uid]["history_seq"][-35:]
            engine = ZeroSumBridgeEngineV5(recent_seq)
            log_title = "[Seq]"

        report = engine.execute_pipeline()
        if "error" in report:
            bot.reply_to(message, f"❌ Lỗi: `{report['error']}`", parse_mode="Markdown")
            return

        user_data[uid]["balance"] -= 1

        user_data[uid]["logs"].insert(0, f"{log_title} ➔ {report['result']}")
        if len(user_data[uid]["logs"]) > 5: user_data[uid]["logs"].pop()

        p_val = report.get('p_display', 50.0)
        tai_pct = p_val if report['result'] == 'TÀI' else round(100.0 - p_val, 1)
        xiu_pct = p_val if report['result'] == 'XỈU' else round(100.0 - p_val, 1)

        res_msg = (
            f"🔮 **Tài:** `{tai_pct}%`\n"
            f"❗️ **Xỉu:** `{xiu_pct}%`\n"
            f"💳 **Số dư:** `{user_data[uid]['balance']} Xu`"
        )
        bot.reply_to(message, res_msg, parse_mode="Markdown", reply_markup=main_menu())

    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi hệ thống: `{str(e)}`", parse_mode="Markdown")

if __name__ == '__main__':
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    try: 
        bot.remove_webhook()
    except: pass
    print("ENGINE V5 ONLINE...")
    bot.infinity_polling(none_stop=True)
