#!/usr/bin/env python3
"""
Мониторинг игроков LabWar для GitHub Actions
Проверяет 36 игроков за 5 секунд
"""

import asyncio
import aiohttp
import os
from datetime import datetime

# Настройки
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
BASE_URL = "http://labwar.ru"
LOGIN_URL = f"{BASE_URL}/index.php?mod=autorize&login=bot1&pass=00000000&scin="

# Все игроки для проверки
PLAYERS = [
    "Barmaleikin", "Subbota96", "angel_of_dead1", "syslenok_88", "Lord555",
    "Znatok", "Sprei", "OBRON555", "den77", "CaIIIeHbkA", "_4ka_", "MeinKrieg",
    "_ASUS_", "AvtoRitet", "Zipp0_", "_DONZ_", "B_A_T", "xxxMAXxxx", "Klassik",
    "CHIPS", "Diabolo", "Ded1", "RED_HEAD_", "ShymaXER", "Krot13", "KAMAZ",
    "1Kazak1", "4uKaTuJIo", "PeaceDeath", "xXx_stalker_xXx", "jafar",
    "aleksandr_25", "Eclerhik", "Sharliz", "Wolf9", "PaHDoM"
]

# Скучные мобы (не отправляем уведомления)
BLACKLIST = {
    "Морф", "Сектант", "Вампир-пластун", "Серебристый Морф", "Топтун",
    "Трупоед", "Раненый Вампир-пластун", "Гигантский Морф", "Боец", "Охранник",
    "Старый робот", "Собака-мутант", "Шнырь", "Белесое существо", "Доктор",
    "Разведчик", "Здоровяк", "Каннибал", "Рослый охранник", "Булочник",
    "Мастиф", "Крупный ревун", "Старший разведчиков", "Кумус", "Снайпер",
    "Большой урлок", "Малый урлок", "Рэкетир", "Торговец", "Старший смены",
    "Серый ревун", "Сектант с кинжалом", "Раненый Каннибал", "Крапивник",
    "Бандит", "Ниточный червь", "Спецназовец", "Мурр", "Малый ревун",
    "Заключенный", "Часовой в берете", "Часовой в каске", "Рослый бандит",
    "Главарь банды", "Спецмен", "Пулеметчик", "Водитель", "Секс", "ВВС33",
    "Штурмовик", "Штурмовик-ветеран", "Связной", "Сталкер Петрович",
    "Танцовщица Гаечка", "Бродяга Скрудж", "Бродяга Микки", "Заключенный с прутом",
    "Дедушка Мороз", "Дохлый охранник", "Санта Клаус", "Заключенный с шокером",
    "Крепкий охранник", "Заключенный с заточкой", "Бультерьер", "Прохожий",
    "Сутенер", "Флорист", "Кузнец", "Вышибала", "Погонщик", "Гравер",
    "Трактирщик", "Тайный поклонник", "Громила", "Боря", "Бродяга", "Моня",
    "Алконафт Алеша", "Часовой", "Амбал", "Стрелок экипажа"
}

class LabWarMonitor:
    def __init__(self):
        self.session = None
        self.cookies = None
        
    async def send_to_telegram(self, message: str):
        """Отправляем сообщение в Telegram"""
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {
                'chat_id': CHAT_ID,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            async with self.session.post(url, data=data, timeout=5):
                pass  # Просто отправляем
        except:
            pass  # Игнорируем ошибки
        
    async def login_to_game(self):
        """Входим в игру под аккаунтом bot1"""
        print("🔐 Входим в игру...")
        try:
            # Создаем сессию для быстрых запросов
            connector = aiohttp.TCPConnector(limit_per_host=20)
            self.session = aiohttp.ClientSession(connector=connector)
            
            # Используем ссылку для автовхода
            async with self.session.get(LOGIN_URL, timeout=10) as response:
                self.cookies = response.cookies
                print("✅ Вошли успешно!")
                return True
        except Exception as e:
            print(f"❌ Ошибка входа: {e}")
            return False
    
    async def check_player(self, player: str):
        """Проверяем одного игрока"""
        try:
            url = f"{BASE_URL}/index.php?mod=players&name={player}"
            
            async with self.session.get(
                url, 
                cookies=self.cookies,
                timeout=5
            ) as response:
                
                if response.status != 200:
                    return
                    
                html = await response.text()
                await self.check_battle(html, player)
                
        except Exception:
            pass
    
    async def check_battle(self, html: str, player: str):
        """Проверяем, есть ли бой"""
        # 1. Ищем "В бою"
        if "В бою" not in html:
            return
        
        # 2. Извлекаем информацию о бое
        battle_text = self.get_battle_text(html)
        if not battle_text:
            return
        
        # 3. Проверяем черный список
        for mob in BLACKLIST:
            if mob in battle_text:
                print(f"  🚫 {player}: {mob} (скучный моб)")
                return
        
        # 4. Отправляем уведомление
        time_now = datetime.now().strftime("%H:%M:%S")
        message = f"⚔️ БОЙ: {player} 🕒 {time_now}\n📝 {battle_text[:100]}..."
        
        await self.send_to_telegram(message)
        print(f"  ⚡ {player}: БОЙ! Сообщение отправлено")
    
    def get_battle_text(self, html: str) -> str:
        """Достаем текст про бой"""
        try:
            # Ищем где в HTML написано "В бою"
            pos = html.find("В бою")
            if pos == -1:
                return ""
            
            # Берем 300 символов вокруг
            start = max(0, pos - 50)
            end = min(len(html), pos + 250)
            return html[start:end]
        except:
            return ""
    
    async def check_all_players(self):
        """Проверяем ВСЕХ игроков сразу"""
        print(f"🚀 Начинаем проверку {len(PLAYERS)} игроков...")
        
        if not await self.login_to_game():
            return
        
        # Создаем задачи для всех игроков
        tasks = []
        for player in PLAYERS:
            task = asyncio.create_task(self.check_player(player))
            tasks.append(task)
        
        # Запускаем все задачи одновременно
        await asyncio.gather(*tasks, return_exceptions=True)
        
        print(f"✅ Проверили {len(PLAYERS)} игроков")
    
    async def cleanup(self):
        """Закрываем соединения"""
        if self.session:
            await self.session.close()

async def main():
    """Главная функция"""
    monitor = LabWarMonitor()
    try:
        await monitor.check_all_players()
    finally:
        await monitor.cleanup()

# Запускаем программу
if __name__ == "__main__":
    asyncio.run(main())
