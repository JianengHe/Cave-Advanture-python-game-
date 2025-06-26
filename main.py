# test for git commit and push
# print('this is a test ')
import pygame, sys, random
import pygame.freetype

def pixel_collision(mask1, rect1, mask2, rect2):
    offset_x = rect2.left - rect1.left
    offset_y = rect2.top - rect1.top
    overlap = mask1.overlap(mask2, (offset_x, offset_y))
    return overlap is not None

class Sprite:
    def __init__(self, image, position):
        self.image = image
        self.rect = image.get_rect()
        self.rect.center = position
        self.mask = pygame.mask.from_surface(image)

    def set_position(self, position):
        self.rect.center = position

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def is_colliding(self, other):
        return pixel_collision(self.mask, self.rect, other.mask, other.rect)

class Character(Sprite):
    def __init__(self, image, position):
        super().__init__(image, position)

    def move(self, change=(0, 0)):
        self.rect.move_ip(change)

class Guard(Character):
    def __init__(self, image, position, speed):
        super().__init__(image, position)
        self.speed = speed

    def move(self):
        super().move(self.speed)

    def bounce(self):
        dx, dy = self.speed
        if dx == 0:
            self.speed = (0, -dy)
        elif dy == 0:
            self.speed = (-dx, 0)

class Item(Character):
    def __init__(self, image, position):
        super().__init__(image, position)

class PowerUp(Sprite):
    def __init__(self, image, position, boost=50):
        super().__init__(image, position)
        self.boost = boost

class FreezerEnemy(Character):  # new guard that can stop player's move
    def __init__(self, image, position):
        super().__init__(image, position)
    def move(self):
        pass
    def freeze_player(self, player):  # freeze player
        player.freeze_timer = 60
        print("You got froze")

def main():
    pygame.init()
    pygame.freetype.init()

    screen_size = (800, 600)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Guardians of the Cave")
    clock = pygame.time.Clock()

    # add timer

    timer = 800
    TIMER_FONT = pygame.freetype.SysFont("TimesNewRoman", 24)

    old_map = pygame.image.load("map.png").convert()
    old_map = pygame.transform.scale(old_map, (800, 600))
    map_display = old_map.copy()

    map_collision = old_map.copy()
    map_collision.set_colorkey((255, 255, 255))
    map_obj = Character(map_collision, (400, 300))

    player_image = pygame.image.load("player.png").convert_alpha()
    player_image = pygame.transform.scale(player_image, (40, 40))
    player = Character(player_image, (50, 350))
    player.freeze_timer = 0

    guard_image = pygame.image.load("guard.png").convert_alpha()
    guard_image = pygame.transform.scale(guard_image, (40, 40))
    guard1 = Guard(guard_image, (350, 100), (2, 0))
    guard2 = Guard(guard_image, (300, 220), (0, 2))
    guard3 = Guard(guard_image, (200, 300), (2, 0))
    guards = [guard1, guard2, guard3]

    item_image = pygame.image.load("item.png").convert_alpha()
    item_image = pygame.transform.scale(item_image, (30, 30))
    item1 = Item(item_image, (350, 350))
    item2 = Item(item_image, (380, 70))
    item3 = Item(item_image, (500, 550))
    items = [item1, item2, item3]

    final_goal_image = pygame.image.load("final_goal.png").convert_alpha()
    final_goal_image = pygame.transform.scale(final_goal_image, (40, 40))
    final_goal = Character(final_goal_image, (750, 250))

    collected_items = 0

    #PowerUp
    powerup_image = pygame.image.load("powerup.png").convert_alpha()
    powerup_image = pygame.transform.scale(powerup_image, (30, 30))
    powerups = []
    while len(powerups) < 5:
        x = random.randint(30, 770)
        y = random.randint(30, 570)
        new_powerup = PowerUp(powerup_image, (x, y))
        if not new_powerup.is_colliding(map_obj):
            powerups.append(new_powerup)

    # Freezer
    freezer_image = pygame.image.load("freezer.png").convert_alpha()
    freezer_image = pygame.transform.scale(freezer_image, (40, 40))
    freezer_enemy1 = FreezerEnemy(freezer_image, (600, 400))
    freezer_enemy2 = FreezerEnemy(freezer_image, (700, 300))
    freezer_enemies = [freezer_enemy1, freezer_enemy2]

    game_over = False
    win = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

        if player.freeze_timer > 0:
            player.freeze_timer -= 1
        else:
            keys = pygame.key.get_pressed()
            original_position = player.rect.topleft
            move_x, move_y = 0, 0
            player_speed = 5
            if keys[pygame.K_LEFT]:
                move_x -= player_speed
            if keys[pygame.K_RIGHT]:
                move_x += player_speed
            if keys[pygame.K_UP]:
                move_y -= player_speed
            if keys[pygame.K_DOWN]:
                move_y += player_speed
            player.move((move_x, move_y))

        if pixel_collision(player.mask, player.rect, map_obj.mask, map_obj.rect):
            player.rect.topleft = original_position

        for guard in guards:
            guard.move()
            if pixel_collision(guard.mask, guard.rect, map_obj.mask, map_obj.rect):
                guard.bounce()

        for freezer in freezer_enemies:
            if pixel_collision(player.mask, player.rect, freezer.mask, freezer.rect):
                freezer.freeze_player(player)
            else:
                pass
        freezer_enemies = [f for f in freezer_enemies if not pixel_collision(player.mask, player.rect, f.mask, f.rect)]

        for guard in guards:
            if pixel_collision(player.mask, player.rect, guard.mask, guard.rect):
                print("Game Over!")
                game_over = True
                win = False
                break

        remaining_items = []
        for item in items:
            if pixel_collision(player.mask, player.rect, item.mask, item.rect):
                print("Collected an item!")
                collected_items += 1
            else:
                remaining_items.append(item)
        items = remaining_items

        remaining_powerups = []
        for p in powerups:
            if pixel_collision(player.mask, player.rect, p.mask, p.rect):
                timer += p.boost
                print("PowerUp collected! Timer increased by", p.boost)
            else:
                remaining_powerups.append(p)
        powerups = remaining_powerups

        if random.random() < 0.01 and len(powerups) < 5:
            for _ in range(10):
                x = random.randint(30, 770)
                y = random.randint(30, 570)
                new_powerup = PowerUp(powerup_image, (x, y))
                if not new_powerup.is_colliding(map_obj):
                    powerups.append(new_powerup)
                    break

        if collected_items == 3:
            if pixel_collision(player.mask, player.rect, final_goal.mask, final_goal.rect):
                print("Congratulations! You finished!")
                game_over = True
                win = True

        timer -= 1
        if timer <= 0:
            print("Time's up! Game over!")
            game_over = True

        screen.blit(map_display, (0, 0))
        for item in items:
            item.draw(screen)
        for p in powerups:
            p.draw(screen)
        if collected_items == 3:
            final_goal.draw(screen)
        for guard in guards:
            guard.draw(screen)
        for freezer in freezer_enemies:
            freezer.draw(screen)
        player.draw(screen)

        timer_color = (255, 0, 0) if timer < 100 else (255, 255, 255)
        TIMER_FONT.render_to(screen, (650, 20), "Time: " + str(timer), timer_color)

        pygame.display.update()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
