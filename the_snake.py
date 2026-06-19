from random import randint

import pygame as pg

# Размеры поля и сетки
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
GRID_CENTER = [GRID_WIDTH // 2, GRID_HEIGHT // 2]

# Сложность игры (скорость змейки)
SPEED = 6
# Увеличивать ли по ходу роста змейки
INCREASE_SPEED_DURING_GAME = True

# Направления движения
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета
BOARD_BACKGROUND_COLOR = (20, 6, 68)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (240, 60, 0)
SNAKE_COLOR = (70, 180, 70)
SNAKE_HEAD_COLOR = (25, 220, 25)

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock = pg.time.Clock()
running = True


class GameObject:
    """Игровой объект, отрисовывающийся на поле."""

    def __init__(
        self,
        color: tuple[int, int, int] = BOARD_BACKGROUND_COLOR,
        border_color: tuple[int, int, int] = BORDER_COLOR,
        position: tuple[int, int] = GRID_CENTER
    ) -> None:
        self.position = position
        self.body_color = color
        self.border_color = border_color

    def draw(self) -> None:
        """Функция для отрисовки на экран. Должна быть переопределена."""
        raise NotImplementedError('Необходимо переопределить метод draw()')

    def _draw_one(
        self,
        position: tuple[int, int],
        color: tuple[int, int, int] | None = None
    ) -> None:
        """Функция для отрисовки на экран одной ячейки заданного цвета."""
        if color is None:
            color = self.body_color
        rect = pg.Rect(
            (position[0] * GRID_SIZE, position[1] * GRID_SIZE),
            (GRID_SIZE, GRID_SIZE)
        )
        pg.draw.rect(screen, color, rect)
        pg.draw.rect(screen, self.border_color, rect, 1)


class Apple(GameObject):
    """Яблоко. Цель для сбора змейкой. Может рандомизировать позицию."""

    def __init__(
            self,
            color: tuple[int, int, int] = APPLE_COLOR,
            exclude_positions: list[tuple[int, int]] | None = None
        ):
        super().__init__(color=color)
        self.randomize_position(exclude_positions)

    def randomize_position(
            self,
            excluded: list[tuple[int, int]] | None = None
        ):
        """Задаёт новую случайную позицию для яблока."""
        if excluded is not None:
            while self.position in excluded:
                random_x = randint(0, GRID_WIDTH - 1)
                random_y = randint(0, GRID_HEIGHT - 1)
                self.position = (random_x, random_y)
    
    def draw(self):
        """Отрисовывает яблоко в его текущей позиции."""
        self._draw_one(self.position)


class Snake(GameObject):
    """Змейка. Основной игровой персонаж."""

    def __init__(
        self,
        color: tuple[int, int, int] = SNAKE_COLOR
    ):
        super().__init__(color=color)
        self.reset()

    def reset(self):
        """Сброс змейки к начальным параметрам."""
        self.length: int = 1
        self.position = GRID_CENTER
        self.positions: list[tuple[int, int]] = [self.position]
        self.direction: tuple[int, int] = RIGHT
        self.last = None

    def draw(self):
        """Отрисовка змейки."""
        for position in self.positions:
            self._draw_one(position)

        if self.last:
            self._draw_one(self.last, BOARD_BACKGROUND_COLOR)

    def move(self):
        """Перемещает змейку в текущем направлении движения."""
        self.position[0] += self.direction[0]
        self.position[1] += self.direction[1]
        self.positions.insert(0, self.position)

    def get_head_position(self):
        """Возвращает текущее положение головы змейки."""
        return self.position


def main():
    """Основное тело программы."""
    pg.init()
    screen.fill(BOARD_BACKGROUND_COLOR)

    player = Snake()  # управляемое игроком существо - змейка
    apple = Apple()  # цель для сбора игроком

    ticks_per_second = SPEED

    while running:
        clock.tick(ticks_per_second)

        handle_keys(player)

        player.move()

        # сбор яблока
        if player.position == apple.position:
            apple.randomize_position(excluded = player.positions)
        # столкновение с собой
        elif player.get_head_position() in player.positions[1:]:
            screen.fill(BOARD_BACKGROUND_COLOR)
            player.reset()
            apple.randomize_position(excluded = player.positions)

        player.draw()
        apple.draw()
        pg.display.update()


def handle_keys(game_object):
    """Функция обработки действий пользователя."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


if __name__ == '__main__':
    main()
