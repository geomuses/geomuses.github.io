import os
import logging
from datetime import datetime
from functools import wraps

# 基礎庫
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import futu as ft  # 建議使用標準的 futu 導入名稱

# ── 直接配置區 (在此修改你的設定) ──────────────────────────────
TELEGRAM_TOKEN   = "8312172130:AAHVyEpIItPeuiAykeuN9CMCJya_Gz6U7uk"  # 填入 BotFather 給你的 Token
ALLOWED_CHAT_IDS = {-1003370646305,6749555057}       # 填入你的 Telegram User ID (數字)
MOOMOO_HOST      = "127.0.0.1"               # OpenD 運行地址
MOOMOO_PORT      = 11111                     # OpenD 端口
MOOMOO_ACC_ID    = 0

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ── 鉴权装饰器 ─────────────────────────────────────────────
def restricted(func):
    """只允许白名单用户访问"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if ALLOWED_CHAT_IDS and user_id not in ALLOWED_CHAT_IDS:
            await update.message.reply_text("⛔ 未授权访问")
            logger.warning(f"Unauthorized access attempt by user {user_id}")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper


# ── Moomoo 辅助函数 ────────────────────────────────────────
def get_trade_context():
    """获取 Moomoo 交易上下文（港美股）"""
    trd_ctx = ft.OpenSecTradeContext(
        filter_trdmarket=ft.TrdMarket.US,
        host=MOOMOO_HOST,
        port=MOOMOO_PORT,
        security_firm=ft.SecurityFirm.FUTUSECURITIES,
    )
    return trd_ctx


def get_account_id(trd_ctx) -> int:
    """获取账户 ID"""
    if MOOMOO_ACC_ID:
        return MOOMOO_ACC_ID
    ret, data = trd_ctx.get_acc_list()
    if ret == ft.RET_OK and not data.empty:
        return int(data.iloc[0]["acc_id"])
    raise RuntimeError("无法获取账户列表")


def fmt_number(n, decimals=2) -> str:
    """格式化数字"""
    try:
        return f"{float(n):,.{decimals}f}"
    except Exception:
        return str(n)


def fmt_pct(n) -> str:
    """格式化百分比"""
    try:
        v = float(n)
        arrow = "📈" if v >= 0 else "📉"
        sign  = "+" if v >= 0 else ""
        return f"{arrow} {sign}{v:.2f}%"
    except Exception:
        return str(n)


# ── /start & /help ─────────────────────────────────────────
@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("💰 账户余额", callback_data="balance"),
            InlineKeyboardButton("📊 持仓列表", callback_data="positions"),
        ],
        [
            InlineKeyboardButton("📋 今日订单", callback_data="orders"),
            InlineKeyboardButton("📈 盈亏汇总", callback_data="pnl"),
        ],
        [
            InlineKeyboardButton("🔄 刷新", callback_data="refresh"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🤖 *Moomoo Bot 已就绪*\n\n"
        "选择下方按钮或输入指令查询账户信息：\n\n"
        "`/balance`  — 账户余额\n"
        "`/positions` — 当前持仓\n"
        "`/orders`   — 今日订单\n"
        "`/pnl`      — 盈亏汇总\n"
        "`/status`   — 连接状态",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


@restricted
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)


# ── /status ────────────────────────────────────────────────
@restricted
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.callback_query.message
    try:
        trd_ctx = get_trade_context()
        acc_id  = get_account_id(trd_ctx)
        trd_ctx.close()
        text = (
            "✅ *连接状态*\n\n"
            f"🔌 OpenD: `{MOOMOO_HOST}:{MOOMOO_PORT}`\n"
            f"🆔 账户 ID: `{acc_id}`\n"
            f"🕐 时间: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`"
        )
    except Exception as e:
        text = f"❌ *连接失败*\n\n`{e}`"
    await msg.reply_text(text, parse_mode="Markdown")


# ── /balance ───────────────────────────────────────────────
@restricted
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    await msg.reply_text("⏳ 正在連線 OpenD 並查詢餘額...")
    
    trd_ctx = None
    try:
        # 1. 建立連線
        trd_ctx = get_trade_context()
        
        # 2. 獲取帳戶 ID
        acc_id = get_account_id(trd_ctx)
        
        # 3. 查詢資金 (改用更穩定的接口名稱)
        # 注意：馬來西亞帳戶建議明確指定 TrdEnv.REAL
        ret, data = trd_ctx.get_acc_funds(trd_env=ft.TrdEnv.REAL, acc_id=acc_id)

        if ret == ft.RET_OK:
            row = data.iloc[0]
            # 這裡根據馬來西亞 Moomoo 的返回欄位調整
            text = (
                f"💰 *Moomoo 賬戶餘額 (MY)*\n"
                f"─────────────────\n"
                f"💵 總資產：`{fmt_number(row.get('total_assets', 0))}`\n"
                f"🏦 現金：`{fmt_number(row.get('cash', 0))}`\n"
                f"📊 市值：`{fmt_number(row.get('market_val', 0))}`\n"
                f"⚡ 購買力：`{fmt_number(row.get('power', 0))}`\n"
                f"─────────────────\n"
                f"🕐 更新時間：`{datetime.now().strftime('%H:%M:%S')}`"
            )
        else:
            text = f"❌ 查詢失敗：{data}"

    except Exception as e:
        text = f"⚠️ 發生錯誤：\n`{str(e)}`"
    
    finally:
        # 確保查詢完成後才關閉連線
        if trd_ctx:
            trd_ctx.close()
            
    keyboard = [[InlineKeyboardButton("🔄 刷新", callback_data="balance")]]
    await msg.reply_text(text, parse_mode="Markdown")



# ── /positions ─────────────────────────────────────────────
@restricted
async def positions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.callback_query.message
    await msg.reply_text("⏳ 查询持仓中…")
    try:
        trd_ctx = get_trade_context()
        acc_id  = get_account_id(trd_ctx)
        ret, data = trd_ctx.position_list_query(trd_env=ft.TrdEnv.REAL, acc_id=acc_id, refresh_cache=True)
        trd_ctx.close()

        if ret != ft.RET_OK:
            await msg.reply_text(f"❌ 查询失败：{data}")
            return

        if data.empty:
            await msg.reply_text("📭 当前无持仓")
            return

        lines = ["📊 *当前持仓*\n─────────────────"]
        for _, row in data.iterrows():
            pnl_pct = fmt_pct(row.get("pl_ratio_real", 0))
            lines.append(
                f"\n🔹 *{row['stock_name']}* (`{row['code']}`)\n"
                f"   数量: `{fmt_number(row['qty'], 0)}` 股\n"
                f"   成本: `{fmt_number(row['cost_price'])}`  现价: `{fmt_number(row['price'])}`\n"
                f"   市值: `{fmt_number(row['market_val'])} {row.get('currency','USD')}`\n"
                f"   盈亏: `{fmt_number(row['pl_val'])}` {pnl_pct}"
            )
        lines.append(f"\n─────────────────\n🕐 `{datetime.now().strftime('%H:%M:%S')}`")
        text = "\n".join(lines)

    except Exception as e:
        text = f"❌ 错误：`{e}`"

    keyboard = [[InlineKeyboardButton("🔄 刷新", callback_data="positions")]]
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))


# ── /orders ────────────────────────────────────────────────
@restricted
async def orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.callback_query.message
    await msg.reply_text("⏳ 查询今日订单中…")
    try:
        trd_ctx = get_trade_context()
        acc_id  = get_account_id(trd_ctx)
        ret, data = trd_ctx.order_list_query(trd_env=ft.TrdEnv.REAL, acc_id=acc_id, refresh_cache=True)
        trd_ctx.close()

        if ret != ft.RET_OK:
            await msg.reply_text(f"❌ 查询失败：{data}")
            return

        if data.empty:
            await msg.reply_text("📭 今日无订单")
            return

        STATUS_EMOJI = {
            "SUBMITTED": "🟡", "FILLED_ALL": "✅", "CANCELLED_ALL": "❌",
            "FILLED_PART": "🟠", "FAILED": "🔴", "DISABLED": "⚫",
        }

        lines = ["📋 *今日订单*\n─────────────────"]
        for _, row in data.iterrows():
            side  = "买入 🟢" if str(row.get("trd_side", "")).upper() == "BUY" else "卖出 🔴"
            emoji = STATUS_EMOJI.get(str(row.get("order_status", "")).upper(), "⚪")
            lines.append(
                f"\n{emoji} *{row.get('stock_name','')}* (`{row['code']}`)\n"
                f"   方向: {side}  数量: `{fmt_number(row['qty'],0)}`\n"
                f"   委托价: `{fmt_number(row['price'])}`  成交价: `{fmt_number(row.get('dealt_avg_price',0))}`\n"
                f"   状态: `{row.get('order_status','')}`\n"
                f"   时间: `{row.get('create_time','')}`"
            )
        lines.append(f"\n─────────────────\n🕐 `{datetime.now().strftime('%H:%M:%S')}`")
        text = "\n".join(lines)

    except Exception as e:
        text = f"❌ 错误：`{e}`"

    keyboard = [[InlineKeyboardButton("🔄 刷新", callback_data="orders")]]
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))


# ── /pnl ───────────────────────────────────────────────────
@restricted
async def pnl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.callback_query.message
    await msg.reply_text("⏳ 查询盈亏中…")
    try:
        trd_ctx = get_trade_context()
        acc_id  = get_account_id(trd_ctx)

        ret_acc, acc_data = trd_ctx.accinfo_query(trd_env=ft.TrdEnv.REAL, acc_id=acc_id, refresh_cache=True)
        ret_pos, pos_data = trd_ctx.position_list_query(trd_env=ft.TrdEnv.REAL, acc_id=acc_id, refresh_cache=True)
        trd_ctx.close()

        if ret_acc != ft.RET_OK:
            await msg.reply_text(f"❌ 查询失败：{acc_data}")
            return

        row      = acc_data.iloc[0]
        currency = row.get("currency", "USD")
        unrealized = float(row.get("unrealized_pl", 0))
        realized   = float(row.get("realized_pl", 0))
        total_pl   = unrealized + realized

        lines = [
            "📈 *盈亏汇总*\n─────────────────",
            f"💹 未实现盈亏：`{fmt_number(unrealized)} {currency}` {fmt_pct(unrealized / max(float(row.get('market_val',1)),1) * 100)}",
            f"✅ 已实现盈亏：`{fmt_number(realized)} {currency}`",
            f"📊 总盈亏：`{fmt_number(total_pl)} {currency}`",
            "─────────────────",
        ]

        if ret_pos == ft.RET_OK and not pos_data.empty:
            lines.append("*各股盈亏：*")
            for _, r in pos_data.iterrows():
                lines.append(
                    f"  • *{r['code']}*: `{fmt_number(r['pl_val'])}` {fmt_pct(r.get('pl_ratio_real',0))}"
                )

        lines.append(f"─────────────────\n🕐 `{datetime.now().strftime('%H:%M:%S')}`")
        text = "\n".join(lines)

    except Exception as e:
        text = f"❌ 错误：`{e}`"

    keyboard = [[InlineKeyboardButton("🔄 刷新", callback_data="pnl")]]
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))


# ── Inline 按钮回调 ────────────────────────────────────────
CALLBACK_MAP = {
    "balance":   balance,
    "positions": positions,
    "orders":    orders,
    "pnl":       pnl,
    "refresh":   start,
}

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    handler = CALLBACK_MAP.get(query.data)
    if handler:
        await handler(update, context)


# ── 未知指令 ───────────────────────────────────────────────
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ 未知指令，输入 /start 查看帮助"
    )


# ── 主程序 ─────────────────────────────────────────────────
def main():
    if not TELEGRAM_TOKEN:
        raise ValueError("请在 .env 设置 TELEGRAM_TOKEN")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start",     start))
    app.add_handler(CommandHandler("help",      help_cmd))
    app.add_handler(CommandHandler("status",    status))
    app.add_handler(CommandHandler("balance",   balance))
    app.add_handler(CommandHandler("positions", positions))
    app.add_handler(CommandHandler("orders",    orders))
    app.add_handler(CommandHandler("pnl",       pnl))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    logger.info("🤖 Moomoo Telegram Bot 启动中…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()