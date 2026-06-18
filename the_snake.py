from random import choice, randint
import pygame

# Размеры поля и сетки
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

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

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()
running = True


class GameObject:
    """Игровой объект, отрисовывающийся на поле."""
    def __init__(self):
        self.position = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.body_color = BOARD_BACKGROUND_COLOR
    
    def draw(self):
        """Функция для отрисовки на экран."""
        pass


class Apple(GameObject):
    """Яблоко.
    Цель для сбора змейкой. Может рандомизировать местоположение.
    """
    def __init__(self):
        super().__init__()
        self.body_color = APPLE_COLOR
        self.randomize_position()

    def draw(self):
        """Отрисовка яблока."""
        rect = pygame.Rect(
            (self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def randomize_position(self):
        """Задаёт новую случайную позицию для яблока."""
        random_x = randint(0, GRID_WIDTH - 1)
        random_y = randint(0, GRID_HEIGHT - 1)
        self.position = (random_x, random_y)


class Snake(GameObject):
    """Змейка. Основной игровой персонаж."""
    def __init__(self):
        """TEST!"""
        super().__init__()
        self.body_color = SNAKE_COLOR
        self.head_color = SNAKE_HEAD_COLOR
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def reset(self):
        """Сброс змейки к начальным параметрам."""
        print(f'Сбрасываем игру... Ваш счёт составил: {self.length} очков!')
        self.__init__()

    def draw(self):
        """Отрисовка змейки."""
        for position in self.positions[:-1]:
            rect = (pygame.Rect(
                (position[0] * GRID_SIZE, position[1] * GRID_SIZE),
                (GRID_SIZE, GRID_SIZE)
            ))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)
    
        head_rect = pygame.Rect(
            (self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(screen, self.head_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        if self.last:
            last_rect = pygame.Rect(
                (self.last[0] * GRID_SIZE, self.last[1] * GRID_SIZE),
                (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)
    
    def move(self, is_growing: bool = False):
        """Перемещает змейку в соответствии с текущим направлением движения.
        На вход принимает True, если необходимо увеличить змейку (на 1),
        путём неудаления последнего элемента - хвоста
        """
        self.position = self.get_next_head_position()
        self.positions.insert(0, self.position)
        if not is_growing:
            self.last = self.positions.pop()

    def get_next_head_position(self):
        """Определение следующей клетки поля, куда поползёт змейка."""
        self._update_direction()

        new_head_position = (
            (self.position[0] + self.direction[0]) % GRID_WIDTH,
            (self.position[1] + self.direction[1]) % GRID_HEIGHT
        )

        return new_head_position
    
    def _update_direction(self):
        """Проверяет, была ли попытка изменения направления движения."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None


def main():
    """Основное тело программы."""
    pygame.init()
    screen.fill(BOARD_BACKGROUND_COLOR)

    player = Snake()
    apple = Apple()

    ticks_per_second = SPEED

    while running:
        clock.tick(ticks_per_second)

        handle_keys(player)

        if player.get_next_head_position() == apple.position:
            apple.randomize_position()
            player.length += 1
            if INCREASE_SPEED_DURING_GAME:
                ticks_per_second = player.length // 5 + SPEED
            player.move(True)
        elif player.get_next_head_position() in player.positions:
            player.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position()
        else:
            player.move()

        player.draw()
        apple.draw()

        pygame.display.update()


def handle_keys(game_object):
    """Функция обработки действий пользователя."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


if __name__ == '__main__':
    main()
