import os
import asyncio
from telegram import Update
from telegram.ext import Application, ContextTypes

# Получаем токен из переменной окружения
TOKEN = os.getenv("TOKEN")

# Текст, который бот будет анализировать (ты будешь его менять)
INPUT_TEXT = """
1-(1X2); 2-(1); 3-(12); 4-(1); 5-(12); 6-(2); 7-(2); 8-(1X2); 9-(1); 10-(1X2); 11-(12); 12-(2); 13-(2); 14-(12); 15-(12)
1-(12); 2-(X); 3-(1); 4-(1); 5-(X); 6-(1); 7-(X); 8-(1); 9-(X); 10-(X); 11-(1); 12-(1); 13-(X); 14-(1); 15-(X)
3.60 / 2.71 / 2.45
1.99 / 2.92 / 4.75
2.35 / 3.66 / 2.80
2.29 / 3.56 / 3.04
2.64 / 3.38 / 2.69
3.02 / 3.44 / 2.36
2.88 / 3.65 / 2.35
2.60 / 2.99 / 2.56
2.48 / 2.93 / 2.74
3.62 / 2.94 / 2.11
2.61 / 3.36 / 2.33
3.15 / 3.14 / 2.20
4.50 / 3.26 / 1.72
2.22 / 3.52 / 2.66
2.50 / 3.32 / 2.45
"""

async def analyze():
    lines = INPUT_TEXT.strip().split('\n')
    
    # Извлекаем коэффициенты
    odds = []
    for line in lines:
        if '/' in line and len(line.split('/')) == 3:
            try:
                k1, kX, k2 = [float(x.strip()) for x in line.split('/')]
                odds.append((k1, kX, k2))
            except:
                continue
    
    if len(odds) != 15:
        print(f"❌ Ошибка: найдено {len(odds)} коэффициентов, нужно 15.")
        return

    # Подсчёт 1X2 и 12
    count_1X2 = [0] * 15
    count_12 = [0] * 15
    for line in lines:
        matches = line.split(';')
        for i, match in enumerate(matches):
            if i >= 15:
                break
            if '1X2' in match:
                count_1X2[i] += 1
            if '12' in match:
                count_12[i] += 1
    
    # Находим лучший матч
    best_match = -1
    best_sum = 0
    for i in range(15):
        total = count_1X2[i] + count_12[i]
        if total > best_sum:
            best_sum = total
            best_match = i
    
    if best_sum < 4:
        print(f"❌ Нет подходящих матчей: макс. сумма 1X2+12 = {best_sum}")
        return
    
    # Метод Шина
    k1, kX, k2 = odds[best_match]
    m = 1/k1 + 1/kX + 1/k2
    p1 = (1/k1) / m
    pX = (1/kX) / m
    p2 = (1/k2) / m

    ev1 = p1 * (k1 - 1) - (1 - p1)
    evX = pX * (kX - 1) - (1 - pX)
    ev2 = p2 * (k2 - 1) - (1 - p2)
    
    max_ev = max(ev1, evX, ev2)
    if max_ev < 0.04:
        print(f"❌ Нет value: лучший EV = {max_ev:.1%}")
        return
    
    if ev1 == max_ev and k1 > 2.8:
        result = f"✅ Матч {best_match+1}: П1 ({k1:.2f}), EV = {ev1:.1%}"
    elif evX == max_ev and kX > 2.8:
        result = f"✅ Матч {best_match+1}: X ({kX:.2f}), EV = {evX:.1%}"
    elif ev2 == max_ev and k2 > 2.8:
        result = f"✅ Матч {best_match+1}: П2 ({k2:.2f}), EV = {ev2:.1%}"
    else:
        result = "❌ Коэффициент < 2.80 — нет value"
    
    print(result)
    
    # Отправляем результат в Telegram
    app = Application.builder().token(TOKEN).build()
    await app.initialize()
    await app.bot.send_message(chat_id="YOUR_CHAT_ID", text=result)
    await app.shutdown()

if __name__ == "__main__":
    asyncio.run(analyze())
