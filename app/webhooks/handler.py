from sqlalchemy import select, delete
from app.models.user import User
from app.models.reservation import Reservation
from app.core.database import AsyncSessionLocal
from app.services.whatsapp import whatsapp_service
from app.core.config import settings
import asyncio
import random
from datetime import datetime, timezone, timedelta

BR_TIMEZONE = timezone(timedelta(hours=-3))

async def handle_evolution_webhook(payload: dict):
    event = payload.get("event")
    if event != "messages.upsert":
        return

    data = payload.get("data", {})
    message = data.get("message", {})
    key = data.get("key", {})
    remote_jid = key.get("remoteJid", "")
    message_id = key.get("id", "")
    phone = remote_jid.split("@")[0] if remote_jid else ""
    push_name = data.get("pushName", "")

    is_admin = phone == settings.admin_phone

    conversation = message.get("conversation") or message.get("extendedTextMessage", {}).get("text")
    if not conversation:
        return

    text = conversation.strip().lower()

    quoted_obj = {
        "key": {"remoteJid": remote_jid, "fromMe": False, "id": message_id},
        "message": message
    }

    admin_commands = ["#admin", "1", "2", "3", "4", "5", "6", "7"]
    is_admin_cmd = text in admin_commands or text.startswith("#add") or text.startswith("#rem") or text == "#clear"

    if key.get("fromMe") and not (is_admin and is_admin_cmd):
        return

    if is_admin and is_admin_cmd:
        async with AsyncSessionLocal() as db:
            if text == "#admin":
                await whatsapp_service.send_admin_menu(remote_jid, force_admin=True)
            elif text == "1":
                await whatsapp_service.send_text(remote_jid, "🥖 Iniciando disparo de Pão Francês...", force_admin=True)
                asyncio.create_task(send_bulk_alerts("Pão Francês 🥖"))
            elif text == "2":
                await whatsapp_service.send_text(remote_jid, "🧀 Iniciando disparo de Pão de Queijo...", force_admin=True)
                asyncio.create_task(send_bulk_alerts("Pão de Queijo 🧀"))
            elif text == "3":
                await send_reservation_report(remote_jid)
            elif text == "4":
                result = await db.execute(select(User).where(User.is_active == True))
                count = len(result.scalars().all())
                await whatsapp_service.send_text(remote_jid, f"👥 Clientes ativos: {count}", force_admin=True)
            elif text == "5":
                await whatsapp_service.send_text(remote_jid, "📝 Envie: *#add* + número.\nEx: `#add 5521999998888`", force_admin=True)
            elif text == "6":
                await whatsapp_service.send_text(remote_jid, "🗑️ Envie: *#rem* + número.\nEx: `#rem 5521999998888`", force_admin=True)
            elif text == "7":
                await whatsapp_service.send_text(remote_jid, "⚠️ Envie *#clear* para apagar as reservas.", force_admin=True)
            elif text == "#clear":
                await db.execute(delete(Reservation))
                await db.commit()
                await whatsapp_service.send_text(remote_jid, "✅ Reservas apagadas!", force_admin=True)
            elif text.startswith("#add"):
                clean_p = "".join(filter(str.isdigit, text.replace("#add", "").strip()))
                if len(clean_p) >= 10:
                    result = await db.execute(select(User).where(User.phone == clean_p))
                    user = result.scalar_one_or_none()
                    if user:
                        user.is_active = True
                    else:
                        user = User(phone=clean_p, is_active=True)
                        db.add(user)
                    await db.commit()
                    await whatsapp_service.send_text(remote_jid, f"✅ Cliente {clean_p} ativado!", force_admin=True)
            elif text.startswith("#rem"):
                clean_p = "".join(filter(str.isdigit, text.replace("#rem", "").strip()))
                result = await db.execute(select(User).where(User.phone == clean_p))
                user = result.scalar_one_or_none()
                if user:
                    user.is_active = False
                    await db.commit()
                    await whatsapp_service.send_text(remote_jid, f"✅ Cliente {clean_p} desativado.", force_admin=True)
        return

    if text.isdigit():
        quantity = int(text)
        if 0 < quantity <= 100:
            now_br = datetime.now(BR_TIMEZONE)
            async with AsyncSessionLocal() as db:
                reservation = Reservation(
                    user_phone=remote_jid,
                    user_name=push_name,
                    quantity=quantity,
                    status="confirmed",
                    created_at=now_br
                )
                db.add(reservation)
                await db.commit()
            msg = f"✅ *RESERVA CONFIRMADA!*\n\n{push_name}, reservamos {quantity} pães para você.\nHorário: {now_br.strftime('%H:%M')} 🥖"
            await whatsapp_service.send_text(remote_jid, msg, quoted=quoted_obj)
            return

    elif "sair" in text:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.phone == phone))
            user = result.scalar_one_or_none()
            if not user:
                result = await db.execute(select(User).where(User.phone == remote_jid))
                user = result.scalar_one_or_none()
            if user:
                user.is_active = False
                await db.commit()
        await whatsapp_service.send_text(remote_jid, "Você não receberá mais avisos. 😔", quoted=quoted_obj)

async def send_reservation_report(remote_jid: str):
    now_br = datetime.now(BR_TIMEZONE)
    since = now_br.replace(hour=0, minute=0, second=0, microsecond=0)

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Reservation)
            .where(Reservation.created_at >= since)
            .order_by(Reservation.created_at)
        )
        reservations = result.scalars().all()

    if not reservations:
        await whatsapp_service.send_text(remote_jid, "📊 Sem reservas hoje.", force_admin=True)
        return

    total = sum(r.quantity for r in reservations)
    report = f"📊 *RESERVAS - {now_br.strftime('%d/%m')}*\n\n"
    for r in reservations:
        name = r.user_name or "Cliente"
        short_id = r.user_phone.split("@")[0][-4:]
        hora = r.created_at.astimezone(BR_TIMEZONE).strftime("%H:%M")
        report += f"• [{hora}] *{name}* (...{short_id}): {r.quantity} pães\n"
    report += f"\n*TOTAL: {total}* 🥖"
    await whatsapp_service.send_text(remote_jid, report, force_admin=True)

async def send_bulk_alerts(product_name: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.is_active == True))
        users = result.scalars().all()

    for user in users:
        text = (
            f"🚨 *PÃO QUENTINHO!* 🚨\n\nO *{product_name}* saiu! 🔥\n\n"
            f"Responda com a *QUANTIDADE* que deseja reservar.\nEx: `6`\n\n"
            f"Digite *Sair* para parar de receber avisos."
        )
        try:
            await whatsapp_service.send_text(user.phone, text)
        except Exception as e:
            print(f"Erro para {user.phone}: {e}")
        await asyncio.sleep(random.uniform(2, 4))
