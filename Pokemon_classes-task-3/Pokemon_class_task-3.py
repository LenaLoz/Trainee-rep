from enum import Enum
from pydantic import BaseModel, PrivateAttr
import logging
from typing import Optional, List, ClassVar

# try:
# logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
#           format="%(asctime)s %(levelname)s %(message)s")
# logging.info("Test log entry")
# except Exception as e:
# print(f"Logging error: {e}")
# Настройка логирования

logging.basicConfig(
    level=logging.INFO,
    filename="py_log.log",
    filemode="w",
    format="%(asctime)s %(levelname)s %(message)s",
    encoding='utf-8'
)


class Typo(Enum):
    WATER = 1.3
    FIRE = 1.2
    WIND = 1.4
    EARTH = 1.1


type_effectiveness = {
    (Typo.WIND, Typo.FIRE): 1.2,
    (Typo.WIND, Typo.WATER): 1.5,
    (Typo.WIND, Typo.EARTH): 2,
    (Typo.FIRE, Typo.EARTH): 1.5,
    (Typo.WATER, Typo.FIRE): 0.75,
    (Typo.WATER, Typo.EARTH): 1.2,
}


def effective_attack(attacker, defender):
    # есть ли прямая пара в словаре
    if (attacker, defender) in type_effectiveness:
        return type_effectiveness[(attacker, defender)]
    # есть ли обратная пара в словаре
    elif (defender, attacker) in type_effectiveness:
        # Если есть, возвращаем обратное значение эффективности
        return 1 / type_effectiveness[(defender, attacker)]
    # Если пары нет - возвращаем 1
    else:
        return 1


class PokemonModel(BaseModel):
    name: str
    type: Typo
    level: int = 1
    experience: int = 0


class Pokemon(PokemonModel):
    BASE_HEALTH: ClassVar[int] = 100
    BASE_ATTACK: ClassVar[int] = 10
    BASE_PROTECTION: ClassVar[int] = 5
    BASE_SPEED: ClassVar[int] = 1
    EXPR_PER_LEVEL: ClassVar[int] = 50

    # Использование PrivateAttr для приватных атрибутов
    _health: int = PrivateAttr()
    _attack: int = PrivateAttr()
    _protection: int = PrivateAttr()
    _speed: float = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._update_stats()

    def _update_stats(self):
        self._health = self.BASE_HEALTH * self.level
        self._attack = self.BASE_ATTACK * self.level
        self._protection = self.BASE_PROTECTION * self.level
        self._speed = self.BASE_SPEED * self.type.value

    def add_experience(self, exp_plus: int):
        self.experience += exp_plus
        logging.info(f"{self.name} получил {exp_plus} единиц опыта.")
        while self.experience >= Pokemon.EXPR_PER_LEVEL:
            self.experience -= Pokemon.EXPR_PER_LEVEL
            self._level_up()

    def _level_up(self):
        self.level += 1
        self._update_stats()

    def take_damage(self, damage: int):
        self.health -= damage  # Теперь используем сеттер свойства health
        logging.info(f"{self.name} получил {damage} урона. Здоровье теперь: {self.health}.")
        return self.health == 0

    @property
    def speed(self):
        return self._speed

    @property
    def protection(self):
        return self._protection

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, value):
        self._health = max(value, 0)

    def attack_pokemon(self, opponent):
        damage = max(self._attack - opponent.protection, 1)
        effectiveness = effective_attack(self.type, opponent.type)
        effective_damage = int(damage * effectiveness)
        return opponent.take_damage(effective_damage)


class TrainerModel(BaseModel):
    name: str
    victory: int = 0
    failure: int = 0
    team: List[Pokemon] = []

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True


class Trainer(TrainerModel):
    MAX_TEAM_SIZE: ClassVar[int] = 3

    def __init__(self, **data):
        super().__init__(**data)

    def add_pokemon(self, pokemon: Pokemon) -> None:
        if len(self.team) < Trainer.MAX_TEAM_SIZE:
            self.team.append(pokemon)
            logging.info(f"{pokemon.name} добавлен в команду тренера {self.name}.")
        else:
            raise ValueError(f"Команда уже полная. Максимальный размер команды: {Trainer.MAX_TEAM_SIZE}.")

    def del_pokemon(self, pokemon: Pokemon) -> bool:
        try:
            if pokemon in self.team:
                self.team.remove(pokemon)
                logging.info(f"{pokemon.name} удален из команды тренера {self.name}.")
                return True
            else:
                raise ValueError(f"Такого покемона - {pokemon} ніт.")
        except ValueError as e:
            logging.exception("Ошибка при удалении покемона из команды")

    def victory_register(self) -> None:
        self.victory += 1
        logging.info(f"{self.name} зарегистрировал победу.")

    def failure_register(self) -> None:
        self.failure += 1
        logging.info(f"{self.name} зарегистрировал поражение.")


class FightStatus(Enum):
    WAITING = "Чекаємо"
    IN_PROGRESS = "У ін прогресі"
    FINISH = "Завершено"


class Fight():
    def __init__(self, pokemon1: Pokemon, pokemon2: Pokemon, trainer1: Trainer, trainer2: Trainer):
        self.pokemon1 = pokemon1
        self.pokemon2 = pokemon2
        self.trainer1 = trainer1
        self.trainer2 = trainer2
        self.status = FightStatus.WAITING

    def running_order(self):
        if self.pokemon1.speed >= self.pokemon2.speed:
            return self.pokemon1, self.pokemon2
        else:
            return self.pokemon2, self.pokemon1

    def perform_turn(self):
        first, second = self.running_order()
        logging.info(f"Начинается ход. {first.name} атакует {second.name}.")

        if first.attack_pokemon(second):  # Если побежден
            self.status = FightStatus.FINISH
            logging.info(f"{second.name} был побежден {first.name}.")
            self.register_battle_outcome(first)
            return True

        logging.info(f"{second.name} выдержал атаку {first.name}.")

        if second.attack_pokemon(first):  # Если первый побежден
            self.status = FightStatus.FINISH
            logging.info(f"{first.name} был побежден {second.name}.")
            self.register_battle_outcome(second)
            return True

        logging.info(f"{first.name} выдержал атаку {second.name}.")
        return False

    def register_battle_outcome(self, winner: Pokemon):
        experience_gain = 20
        winner.add_experience(experience_gain)
        logging.info(f"{winner.name} выиграл бой и получил {experience_gain} опыта.")

        if winner == self.pokemon1:
            winner_trainer = self.trainer1
            loser_trainer = self.trainer2
        else:
            winner_trainer = self.trainer2
            loser_trainer = self.trainer1

        # Регистрируем победу и поражение
        winner_trainer.victory_register()
        loser_trainer.failure_register()
        logging.info(
            f"{winner_trainer.name} зарегистрировал победу. {loser_trainer.name} зарегистрировал поражение.")

    def start_fight(self):
        self.status = FightStatus.IN_PROGRESS
        logging.info(f"Бой между {self.pokemon1.name} и {self.pokemon2.name} начался.")
        while self.status == FightStatus.IN_PROGRESS:
            turn_result = self.perform_turn()
            if turn_result:
                logging.info("Бой завершен.")
                break


bulbasaur = Pokemon(name="Bulbasaur", type=Typo.EARTH, level=5)
pikachu = Pokemon(name="Pikachu", type=Typo.WIND, level=3)

# Создание тренеров
ash = Trainer(name="Ash")
misty = Trainer(name="Misty")

# Добавление покемонов в команды тренеров
ash.add_pokemon(pikachu)
misty.add_pokemon(bulbasaur)

# Печать информации о командах тренеров
print(f"{ash.name}'s team: {[p.name for p in ash.team]}")
print(f"{misty.name}'s team: {[p.name for p in misty.team]}")

# Инициирование битвы между первыми покемонами тренеров
battle = Fight(pokemon1=ash.team[0], pokemon2=misty.team[0], trainer1=ash, trainer2=misty)

# Начало битвы
print("Битва началась!")
battle.start_fight()

# Печать результатов битвы
if battle.status == FightStatus.FINISH:
    print(f"Битва завершена. Победитель: {battle.pokemon1.name if battle.pokemon1.health > 0 else battle.pokemon2.name}")
    print(f"{ash.name} - Побед: {ash.victory}, Поражений: {ash.failure}")
    print(f"{misty.name} - Побед: {misty.victory}, Поражений: {misty.failure}")
