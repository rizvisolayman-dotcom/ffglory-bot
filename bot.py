import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters

BASE = "https://ffglory.pro"
API_KEY = "ak_0f5db189209bbfb274f5b605508f019303ba2f92fcd70abe867d9e17f41122f6"
MKEY = "22e15fc938aef0cf08bff1a4dd7a4aaa"
HDR = {"x-api-key": MKEY}

BOT_TOKEN = os.getenv("BOT_TOKEN")

SELECTING_ACTION, SELECTING_GROUP, ENTERING_CLAN_ID, ENTERING_REGION, ENTERING_COUPON_COUNT, ENTERING_COUPON_BASIC, ENTERING_COUPON_PREMIUM = range(7)

user_data_store = {}

def api(method, path, json=None):
    r = requests.request(method, f"{BASE}{path}", params={"api_key": API_KEY}, headers=HDR, json=json, timeout=30)
    r.raise_for_status()
    return r.json()

def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Launch Group", callback_data="launch_group")],
        [InlineKeyboardButton("📋 My Groups", callback_data="my_groups")],
        [InlineKeyboardButton("💰 Check Balance", callback_data="balance")],
        [InlineKeyboardButton("🎫 Create Coupons", callback_data="create_coupons")],
    ])

def get_group_actions_keyboard(group_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏹ Stop", callback_data=f"action_stop_{group_id}"),
         InlineKeyboardButton("🔄 Restart", callback_data=f"action_restart_{group_id}")],
        [InlineKeyboardButton("🗑 Delete", callback_data=f"action_delete_{group_id}"),
         InlineKeyboardButton("⭐ Get Glory", callback_data=f"action_get-glory_{group_id}")],
        [InlineKeyboardButton("👥 Clan Info", callback_data=f"action_get-clan-info_{group_id}")],
        [InlineKeyboardButton("🔙 Back", callback_data="my_groups")],
    ])

def get_regions_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌍 ME (Middle East)", callback_data="region_me"),
         InlineKeyboardButton("🌍 US (United States)", callback_data="region_us")],
        [InlineKeyboardButton("🌍 EU (Europe)", callback_data="region_eu"),
         InlineKeyboardButton("🌍 ASIA", callback_data="region_asia")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")],
    ])

def get_confirm_keyboard(action, group_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Yes", callback_data=f"confirm_{action}_{group_id}"),
         InlineKeyboardButton("❌ No", callback_data=f"cancel_{action}_{group_id}")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 **FFGlory Bot**\n\nControl your clan groups via buttons below:",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )
    return SELECTING_ACTION

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🤖 **FFGlory Bot**\n\nControl your clan groups via buttons below:",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )
    return SELECTING_ACTION

async def launch_group_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🚀 **Launch New Group**\n\nSelect region:",
        reply_markup=get_regions_keyboard(),
        parse_mode="Markdown"
    )
    return ENTERING_REGION

async def region_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    region = query.data.split("_")[1]
    context.user_data["region"] = region
    await query.edit_message_text(
        f"🌍 Region: **{region.upper()}**\n\nEnter Clan ID:",
        parse_mode="Markdown"
    )
    return ENTERING_CLAN_ID

async def clan_id_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clan_id = update.message.text.strip()
    region = context.user_data.get("region")
    
    try:
        resp = api("POST", "/api/client/auto-clan-group", json={"region": region, "clan_id": clan_id})
        gid = resp.get("group_id", "Unknown")
        await update.message.reply_text(
            f"✅ **Group Launched!**\n\nGroup ID: `{gid}`\nRegion: {region.upper()}\nClan ID: {clan_id}",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
    except requests.HTTPError as e:
        await update.message.reply_text(
            f"❌ **Error:** {e.response.json().get('error', str(e))}",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
    return SELECTING_ACTION

async def my_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    try:
        groups = api("GET", "/api/client/my-groups")
        if not groups:
            await query.edit_message_text(
                "📋 **My Groups**\n\nNo groups found.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]])
            )
            return SELECTING_ACTION
        
        text = "📋 **My Groups**\n\n"
        for g in groups:
            text += f"`{g['group_id']}` | {g.get('region', 'N/A').upper()} | {g.get('status', 'N/A')} | Clan: {g.get('clan_id', 'N/A')}\n"
        
        keyboard = []
        for g in groups:
            keyboard.append([InlineKeyboardButton(f"🎮 {g['group_id'][:8]}... ({g.get('status', 'N/A')})", callback_data=f"group_{g['group_id']}")])
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
        
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    except requests.HTTPError as e:
        await query.edit_message_text(
            f"❌ **Error:** {e.response.json().get('error', str(e))}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]])
        )
    return SELECTING_GROUP

async def group_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    group_id = query.data.split("_")[1]
    context.user_data["selected_group"] = group_id
    
    await query.edit_message_text(
        f"🎮 **Group Actions**\n\nGroup ID: `{group_id}`\n\nSelect action:",
        parse_mode="Markdown",
        reply_markup=get_group_actions_keyboard(group_id)
    )
    return SELECTING_GROUP

async def group_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split("_")
    action = parts[1]
    group_id = parts[2]
    
    if action in ["stop", "restart", "delete"]:
        await query.edit_message_text(
            f"⚠️ **Confirm {action.upper()}**\n\nGroup: `{group_id}`\n\nAre you sure?",
            parse_mode="Markdown",
            reply_markup=get_confirm_keyboard(action, group_id)
        )
        return SELECTING_GROUP
    
    await execute_action(query, action, group_id)

async def confirm_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split("_")
    action = parts[1]
    group_id = parts[2]
    
    await execute_action(query, action, group_id)

async def cancel_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    group_id = query.data.split("_")[2]
    await query.edit_message_text(
        f"❌ **Cancelled**\n\nGroup: `{group_id}`",
        parse_mode="Markdown",
        reply_markup=get_group_actions_keyboard(group_id)
    )
    return SELECTING_GROUP

async def execute_action(query, action, group_id):
    try:
        resp = api("POST", "/api/client/group-action", json={"action": action, "group_id": group_id})
        
        if action == "get-glory":
            text = f"⭐ **Glory Points**\n\nGroup: `{group_id}`\nGlory: `{resp}`"
        elif action == "get-clan-info":
            text = f"👥 **Clan Info**\n\nGroup: `{group_id}`\n"
            for k, v in resp.items():
                text += f"{k}: `{v}`\n"
        else:
            text = f"✅ **{action.upper()} Success**\n\nGroup: `{group_id}`\nResponse: `{resp}`"
        
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_group_actions_keyboard(group_id))
    except requests.HTTPError as e:
        error = e.response.json().get('error', str(e))
        await query.edit_message_text(
            f"❌ **Error:** {error}",
            parse_mode="Markdown",
            reply_markup=get_group_actions_keyboard(group_id)
        )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    try:
        bal = api("GET", "/api/client/balance")
        text = f"💰 **Balance**\n\nBasic Credits: `{bal.get('basic_credits', 0)}`\nPremium Credits: `{bal.get('premium_credits', 0)}`"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]))
    except requests.HTTPError as e:
        await query.edit_message_text(
            f"❌ **Error:** {e.response.json().get('error', str(e))}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]])
        )
    return SELECTING_ACTION

async def create_coupons_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🎫 **Create Coupons**\n\nEnter number of coupons to create:",
        parse_mode="Markdown"
    )
    return ENTERING_COUPON_COUNT

async def coupon_count_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        count = int(update.message.text.strip())
        if count <= 0 or count > 100:
            raise ValueError
        context.user_data["coupon_count"] = count
        await update.message.reply_text(
            f"📦 Creating **{count}** coupons\n\nEnter basic credits per coupon:",
            parse_mode="Markdown"
        )
        return ENTERING_COUPON_BASIC
    except ValueError:
        await update.message.reply_text("❌ Invalid number. Enter 1-100.")
        return ENTERING_COUPON_COUNT

async def coupon_basic_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        basic = int(update.message.text.strip())
        if basic < 0:
            raise ValueError
        context.user_data["coupon_basic"] = basic
        await update.message.reply_text(
            f"Basic credits: **{basic}**\n\nEnter premium credits per coupon:",
            parse_mode="Markdown"
        )
        return ENTERING_COUPON_PREMIUM
    except ValueError:
        await update.message.reply_text("❌ Invalid number. Enter 0 or more.")
        return ENTERING_COUPON_BASIC

async def coupon_premium_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        premium = int(update.message.text.strip())
        if premium < 0:
            raise ValueError
        
        count = context.user_data["coupon_count"]
        basic = context.user_data["coupon_basic"]
        
        await update.message.reply_text(f"🔄 Creating {count} coupons...")
        
        codes = []
        for i in range(count):
            resp = api("POST", "/api/client/create-coupon", json={
                "basic_credits": basic,
                "premium_credits": premium
            })
            codes.append(resp["coupon"]["code"])
        
        text = f"✅ **Created {len(codes)} Coupons**\n\n"
        for c in codes:
            text += f"`{c}`\n"
        
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())
    except requests.HTTPError as e:
        await update.message.reply_text(
            f"❌ **Error:** {e.response.json().get('error', str(e))}",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
    except ValueError:
        await update.message.reply_text("❌ Invalid number.", reply_markup=get_main_keyboard())
    
    return SELECTING_ACTION

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.", reply_markup=get_main_keyboard())
    return SELECTING_ACTION

def main():
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN environment variable not set")
        return
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_ACTION: [
                CallbackQueryHandler(main_menu, pattern="^main_menu$"),
                CallbackQueryHandler(launch_group_start, pattern="^launch_group$"),
                CallbackQueryHandler(my_groups, pattern="^my_groups$"),
                CallbackQueryHandler(balance, pattern="^balance$"),
                CallbackQueryHandler(create_coupons_start, pattern="^create_coupons$"),
            ],
            ENTERING_REGION: [
                CallbackQueryHandler(region_selected, pattern="^region_"),
                CallbackQueryHandler(main_menu, pattern="^main_menu$"),
            ],
            ENTERING_CLAN_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, clan_id_entered),
            ],
            SELECTING_GROUP: [
                CallbackQueryHandler(group_selected, pattern="^group_"),
                CallbackQueryHandler(group_action, pattern="^action_"),
                CallbackQueryHandler(confirm_action, pattern="^confirm_"),
                CallbackQueryHandler(cancel_action, pattern="^cancel_"),
                CallbackQueryHandler(my_groups, pattern="^my_groups$"),
            ],
            ENTERING_COUPON_COUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, coupon_count_entered),
            ],
            ENTERING_COUPON_BASIC: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, coupon_basic_entered),
            ],
            ENTERING_COUPON_PREMIUM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, coupon_premium_entered),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    app.add_handler(conv_handler)
    print("Bot started...")
    import nest_asyncio
    nest_asyncio.apply()
    app.run_polling(allowed_updates=Update.ALL_TYPES)