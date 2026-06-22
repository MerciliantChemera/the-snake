from random import randint

import pygame as pg

# Размеры поля и сетки
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
GRID_CENTER = (GRID_WIDTH // 2, GRID_HEIGHT // 2)

# Сложность игры (скорость змейки)
SPEED = 6
# Увеличивать ли по ходу роста змейки
INCREASE_SPEED_DURING_GAME = True
# Увеличение за каждое яблоко
SPEED_INCREMENT = 0.25

# Направления движения
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
UPDATE_ROTATION = {
    pg.K_UP: {
        'direction': UP,
        'conflict': DOWN
        },
    pg.K_DOWN: {
        'direction': DOWN,
        'conflict': UP
        },
    pg.K_LEFT: {
        'direction': LEFT,
        'conflict': RIGHT
        },
    pg.K_RIGHT: {
        'direction': RIGHT,
        'conflict': LEFT
        }
}

# Цвета
BOARD_BACKGROUND_COLOR = (20, 6, 68)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (240, 60, 0)
SNAKE_COLOR = (70, 180, 70)
SNAKE_HEAD_COLOR = (25, 220, 25)

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock = pg.time.Clock()


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

    def _draw_cell(
        self,
        position: tuple[int, int],
        color: tuple[int, int, int] | None = None,
        need_border: bool = False
    ) -> None:
        """Функция для отрисовки на экран одной ячейки заданного цвета."""
        color = color or self.body_color
        rect = pg.Rect(
            tuple(i * GRID_SIZE for i in position),
            (GRID_SIZE, GRID_SIZE)
        )
        pg.draw.rect(screen, color, rect)
        if need_border:
            pg.draw.rect(screen, self.border_color, rect, 1)


class Apple(GameObject):
    """Яблоко. Цель для сбора змейкой. Может рандомизировать позицию."""

    def __init__(
        self,
        color: tuple[int, int, int] = APPLE_COLOR,
        exclude_positions: list[tuple[int, int]] | None = None
    ) -> None:
        super().__init__(color=color)
        if exclude_positions is None:
            exclude_positions = [GRID_CENTER]
        self.randomize_position(exclude_positions)

    def randomize_position(
        self,
        excluded_positions: list[tuple[int, int]] | None
    ) -> None:
        """Задаёт новую случайную позицию для яблока."""
        if excluded_positions is not None:
            while self.position in excluded_positions:
                random_x = randint(0, GRID_WIDTH - 1)
                random_y = randint(0, GRID_HEIGHT - 1)
                self.position = (random_x, random_y)
    
    def draw(self) -> None:
        """Отрисовывает яблоко в его текущей позиции."""
        self._draw_cell(self.position, need_border=True)


class Snake(GameObject):
    """Управляемое игроком существо - змейка."""

    def __init__(
        self,
        color: tuple[int, int, int] = SNAKE_COLOR
    ) -> None:
        super().__init__(color=color)
        self.position = GRID_CENTER
        self.reset()

    @staticmethod
    def check_pause(func):
        def wrapper(self, *args, **kwargs):
            if not self._pause:
                func(self, *args, **kwargs)
            return None
        return wrapper

    def reset(self) -> None:
        """Сброс змейки к начальным параметрам."""
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self._last = None
        self._pause: bool = False

    def draw(self) -> None:
        """Отрисовка змейки."""
        self._draw_cell(self.get_head_position, need_border = True)

        if self._last:
            self._draw_cell(self._last, color = BOARD_BACKGROUND_COLOR)
            self._last = None

    @check_pause
    def move(self) -> None:
        """Перемещает змейку в текущем направлении движения."""
        new_position = (
            (self.get_head_position[0] + self.direction[0]) % GRID_WIDTH,
            (self.get_head_position[1] + self.direction[1]) % GRID_HEIGHT
        )
        self.positions.insert(0, new_position)
        if self.length < len(self.positions):
            self._last = self.positions.pop()

    @property
    def get_head_position(self) -> None:
        """Возвращает текущее положение головы змейки."""
        return self.positions[0]

    @check_pause
    def update_direction(self) -> None:
        """Проверяет, была ли попытка изменения направления движения.

        Буферная переменная next_direction необходима для
        того, чтобы корректно обрабатывался ввод данных.
        При попытке изменить значение напрямую, то между
        тиками 'хода' змейки (функция move()) возможно изменить
        направление движения несколько раз, что может привести
        к развороту в противоположную сторону (и последующему
        съеданию самого себя).
        """
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def switch_pause(self) -> None:
        """Переключить паузу в игре.

        Отключается движение и повороты змейки.
        """
        self._pause = not self._pause

    def update_direction(self) -> None:
        """Проверяет, была ли попытка изменения направления движения."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None


def main():
    """Основное тело программы."""
    pg.init()
    screen.fill(BOARD_BACKGROUND_COLOR)

    snake = Snake()
    apple = Apple()

    ticks_per_second = SPEED

    while True:
        clock.tick(ticks_per_second)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position == apple.position:
            snake.length += 1
            apple.randomize_position(excluded_positions=snake.positions)
            if INCREASE_SPEED_DURING_GAME:
                ticks_per_second += SPEED_INCREMENT
        elif snake.get_head_position in snake.positions[1:]:
            # Поражение: змейка врезалась в себя.
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.reset()
            apple.randomize_position(excluded_positions=snake.positions)

        snake.draw()
        apple.draw()
        pg.display.update()


def handle_keys(game_object: GameObject) -> None:
    """Функция обработки действий пользователя.

    Управление змейкой реализовано при помощи 'клавиш-стрелок'.

    При нажатии на 'пробел' ставится (снимается) пауза.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            # Поворот змейки
            if event.key in (pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT):
                direction_info = UPDATE_ROTATION.get(event.key)
                if game_object.direction != direction_info['conflict']:
                    game_object.next_direction = direction_info['direction']
            # Пауза
            if event.key == pg.K_SPACE:
                game_object.next_direction = None
                game_object.switch_pause()


if __name__ == '__main__':
    main()
