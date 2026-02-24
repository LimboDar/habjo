import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import json
import random
from dataclasses import dataclass
from typing import Dict, List, Optional


# Game data structures
@dataclass
class Player:
    user_id: int
    username: str
    level: int = 1
    health: int = 100
    max_health: int = 100
    mana: int = 50
    max_mana: int = 50
    experience: int = 0
    gold: int = 10
    position_x: int = 0
    position_y: int = 0
    inventory: List[str] = None
    skills: Dict[str, int] = None
    guild: Optional[str] = None
    
    def __post_init__(self):
        if self.inventory is None:
            self.inventory = []
        if self.skills is None:
            self.skills = {}


@dataclass
class Location:
    name: str
    description: str
    type: str  # 'village', 'kingdom', 'tavern', 'shop', 'guild', 'wilderness'
    x: int
    y: int
    npcs: List[str] = None
    enemies: List[str] = None
    
    def __post_init__(self):
        if self.npcs is None:
            self.npcs = []
        if self.enemies is None:
            self.enemies = []


class GameWorld:
    def __init__(self):
        self.locations = {}
        self.generate_world()
    
    def generate_world(self):
        """Generate initial world with various locations"""
        # Create some starting locations
        self.add_location(Location("Начальная Деревня", "Маленькая деревушка на краю большого леса", "village", 0, 0, 
                                  npcs=["Трактирщик", "Кузнец", "Лесник"]))
        self.add_location(Location("Древний Замок", "Заброшенный замок возвышается над холмами", "kingdom", 2, 1,
                                  npcs=["Стражник", "Старейшина"]))
        self.add_location(Location("Таверна 'У Пьяного Гоблина'", "Шумная таверна для уставших путешественников", "tavern", 0, 1,
                                  npcs=["Хозяин таверны", "Пьяница", "Бармен"]))
        self.add_location(Location("Рынок", "Шумный рынок с торговцами", "shop", 1, 0,
                                  npcs=["Торговец", "Кузнец", "Алхимик"]))
        self.add_location(Location("Гильдия Искателей Приключений", "Место, где можно найти задания", "guild", 1, 1,
                                  npcs=["Мастер Гильдии", "Искатель приключений"]))
        
        # Add more wilderness areas
        for i in range(5):
            x, y = random.randint(-5, 5), random.randint(-5, 5)
            if (x, y) not in [(loc.x, loc.y) for loc in self.locations.values()]:
                self.add_location(Location(f"Дикие Земли {i+1}", f"Дикие земли, полные опасностей и возможностей", 
                                         "wilderness", x, y))
    
    def add_location(self, location: Location):
        self.locations[(location.x, location.y)] = location
    
    def get_location_at(self, x: int, y: int):
        return self.locations.get((x, y))


class FantasyGameBot:
    def __init__(self, token: str):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.players: Dict[int, Player] = {}
        self.world = GameWorld()
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.dp.message(Command("start"))
        async def cmd_start(message: types.Message):
            await self.start_game(message)
        
        @self.dp.message(Command("map"))
        async def cmd_map(message: types.Message):
            await self.show_map(message)
        
        @self.dp.message(Command("status"))
        async def cmd_status(message: types.Message):
            await self.show_status(message)
        
        @self.dp.message(Command("move"))
        async def cmd_move(message: types.Message):
            await self.move_player(message)
        
        @self.dp.message(Command("explore"))
        async def cmd_explore(message: types.Message):
            await self.explore_current_location(message)
        
        @self.dp.message(Command("help"))
        async def cmd_help(message: types.Message):
            await self.show_help(message)
    
    async def start_game(self, message: types.Message):
        user_id = message.from_user.id
        username = message.from_user.username or message.from_user.first_name
        
        if user_id not in self.players:
            self.players[user_id] = Player(user_id=user_id, username=username)
            welcome_text = (
                f"Добро пожаловать в мир фэнтези, {username}!\n\n"
                f"Вы начинаете как простой путешественник в начальной деревне.\n"
                f"Ваша задача - исследовать мир, развивать персонажа и выполнять задания.\n\n"
                f"Доступные команды:\n"
                f"/map - Посмотреть карту\n"
                f"/status - Статус персонажа\n"
                f"/move - Перемещение по карте\n"
                f"/explore - Исследовать текущую локацию\n"
                f"/help - Справка по командам"
            )
        else:
            welcome_text = f"С возвращением, {username}! Продолжайте своё приключение."
        
        await message.answer(welcome_text)
    
    async def show_map(self, message: types.Message):
        player = self.players.get(message.from_user.id)
        if not player:
            await message.answer("Сначала начните игру с помощью /start")
            return
        
        # Simple representation of the map around player's position
        map_text = "Карта мира:\n\n"
        map_text += "Легенда: 🏘️ - Деревня, 🏰 - Королевство, 🍺 - Таверна, 🛒 - Магазин, ⚔️ - Гильдия, 🌲 - Дикие земли\n\n"
        
        # Show locations around player (3x3 grid)
        for y in range(player.position_y - 1, player.position_y + 2):
            row = ""
            for x in range(player.position_x - 1, player.position_x + 2):
                if x == player.position_x and y == player.position_y:
                    row += "🚶‍♂️ "  # Player icon
                elif (x, y) in self.world.locations:
                    location = self.world.locations[(x, y)]
                    if location.type == "village":
                        row += "🏘️ "
                    elif location.type == "kingdom":
                        row += "🏰 "
                    elif location.type == "tavern":
                        row += "🍺 "
                    elif location.type == "shop":
                        row += "🛒 "
                    elif location.type == "guild":
                        row += "⚔️ "
                    else:
                        row += "🌲 "
                else:
                    row += "🌊 "  # Water for unexplored areas
            map_text += row + "\n"
        
        map_text += f"\nВаша позиция: ({player.position_x}, {player.position_y})"
        await message.answer(map_text)
    
    async def show_status(self, message: types.Message):
        player = self.players.get(message.from_user.id)
        if not player:
            await message.answer("Сначала начните игру с помощью /start")
            return
        
        status_text = (
            f"👤 {player.username}\n"
            f"📊 Уровень: {player.level}\n"
            f"❤️ Здоровье: {player.health}/{player.max_health}\n"
            f"✨ Мана: {player.mana}/{player.max_mana}\n"
            f"⭐ Опыт: {player.experience}\n"
            f"🪙 Золото: {player.gold}\n"
            f"📍 Позиция: ({player.position_x}, {player.position_y})\n"
            f"🎒 Инвентарь: {', '.join(player.inventory) or 'Пусто'}\n"
        )
        
        if player.guild:
            status_text += f"🏛️ Гильдия: {player.guild}\n"
        
        await message.answer(status_text)
    
    async def move_player(self, message: types.Message):
        player = self.players.get(message.from_user.id)
        if not player:
            await message.answer("Сначала начните игру с помощью /start")
            return
        
        # Parse direction from command arguments
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
        
        if not args:
            await message.answer(
                "Используйте: /move [направление]\n"
                "Примеры: /move north, /move south, /move east, /move west\n"
                "Или: /move up, /move down, /move right, /move left\n"
                "Также можно указать координаты: /move x y"
            )
            return
        
        direction = args[0].lower()
        
        # Handle coordinate movement
        if len(args) >= 2 and args[0].isdigit() and args[1].isdigit():
            target_x, target_y = int(args[0]), int(args[1])
            player.position_x = target_x
            player.position_y = target_y
            await message.answer(f"Вы переместились в точку ({target_x}, {target_y})")
        else:
            # Handle directional movement
            old_pos = (player.position_x, player.position_y)
            
            if direction in ['north', 'up']:
                player.position_y += 1
            elif direction in ['south', 'down']:
                player.position_y -= 1
            elif direction in ['east', 'right']:
                player.position_x += 1
            elif direction in ['west', 'left']:
                player.position_x -= 1
            else:
                await message.answer("Неверное направление. Используйте: north/south/east/west или up/down/right/left")
                return
            
            await message.answer(f"Вы переместились из {old_pos} в ({player.position_x}, {player.position_y})")
        
        # Check if new location exists
        location = self.world.get_location_at(player.position_x, player.position_y)
        if location:
            await message.answer(f"Вы прибыли в {location.name}: {location.description}")
    
    async def explore_current_location(self, message: types.Message):
        player = self.players.get(message.from_user.id)
        if not player:
            await message.answer("Сначала начните игру с помощью /start")
            return
        
        location = self.world.get_location_at(player.position_x, player.position_y)
        
        if not location:
            await message.answer("Вы находитесь в диких землях. Здесь пока ничего нет.")
            return
        
        explore_text = f"🔍 Вы исследуете {location.name}:\n\n{location.description}\n\n"
        
        if location.npcs:
            explore_text += f"👥 Люди: {', '.join(location.npcs)}\n"
        
        if location.enemies:
            explore_text += f"👹 Враги: {', '.join(location.enemies)}\n"
        
        explore_text += f"\nДействия:\n"
        if location.type == "tavern":
            explore_text += "🍻 Посетить таверну\n"
        elif location.type == "shop":
            explore_text += "🛒 Посетить магазин\n"
        elif location.type == "guild":
            explore_text += "⚔️ Посетить гильдию\n"
        elif location.type == "village" or location.type == "kingdom":
            explore_text += "🏘️ Осмотреть деревню/королевство\n"
        
        await message.answer(explore_text)
    
    async def show_help(self, message: types.Message):
        help_text = (
            "📖 Справка по командам:\n\n"
            "/start - Начать игру\n"
            "/map - Посмотреть карту мира\n"
            "/status - Показать статус персонажа\n"
            "/move [направление] - Перемещение (north/south/east/west или координаты)\n"
            "/explore - Исследовать текущую локацию\n"
            "/help - Эта справка\n\n"
            "🎮 Описание игры:\n"
            "Вы начинаете как простой путешественник. Исследуйте мир, посещайте разные локации, "
            "общайтесь с NPC, выполняйте задания и развивайте своего персонажа."
        )
        await message.answer(help_text)
    
    async def run(self):
        print("Запуск бота...")
        await self.dp.start_polling(self.bot)


# To run the bot, you would use:
# bot = FantasyGameBot("YOUR_TELEGRAM_BOT_TOKEN")
# asyncio.run(bot.run())