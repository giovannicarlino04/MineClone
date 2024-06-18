import random
from ursina import Entity, Vec3, distance, invoke, destroy, curve

class Mob(Entity):
    def __init__(self, player, hostile=True):
        super().__init__(
            model='cube',
            texture="textures/zombie.png" if hostile else "textures/sheep.png",
            scale=(1, 1, 1),
            position=self.random_spawn_position()
        )
        self.player = player
        self.hostile = hostile
        self.max_follow_distance = 10
        self.min_follow_distance = 2
        self.attack_range = 1.5
        self.speed = 0.008 if hostile else 0.006
        self.jump_height = 2
        self.jump_duration = 0.5
        self.damage = 10
        self.health = 15 if hostile else 10
        self.following_player = False
        self.can_jump = True

    def update(self):
        distance_to_player = distance(self.position, self.player.position)

        if self.hostile:
            if distance_to_player < self.max_follow_distance:
                self.move_towards_player()
                self.following_player = True
            elif self.following_player and distance_to_player > self.max_follow_distance + 2:
                self.following_player = False
        else:
            self.move_randomly()

        if self.intersects(self.player):
            self.player.decrease_health(self.damage)

        if distance_to_player > self.max_follow_distance + 5 or self.health <= 0:
            self.die()

    def random_spawn_position(self):
        return Vec3(random.uniform(-10, 10), 1, random.uniform(-10, 10))

    def move_towards_player(self):
        direction = self.player.position - self.position
        direction.y = 0
        direction = direction.normalized()
        self.position += direction * self.speed

    def move_randomly(self):
        self.position += Vec3(random.uniform(-1, 1), 0, random.uniform(-1, 1)) * self.speed

    def jump(self):
        if self.can_jump:
            self.can_jump = False
            self.animate_jump()

    def animate_jump(self):
        jump_sequence = [
            Vec3(0, self.jump_height, 0),
            Vec3(0, 0, 0)
        ]
        self.animate_position(jump_sequence, self.jump_duration, curve=curve.linear, on_complete=self.finish_jump)

    def finish_jump(self):
        self.can_jump = True

    def receive_damage(self, damage_amount):
        self.health -= damage_amount
        if self.health <= 0:
            self.die()
        else:
            print(f"Mob received {damage_amount} damage! Health: {self.health}")

    def die(self):
        invoke(self.kill, delay=1.0)

    def kill(self):
        destroy(self)

    @staticmethod
    def spawn_random_mob(player):
        hostile = random.choice([True, False])
        new_mob = Mob(player, hostile=hostile)
        return new_mob

    @staticmethod
    def spawn_continuous_mobs(player):
        def spawn_mob():
            new_mob = Mob.spawn_random_mob(player)
            invoke(spawn_mob, delay=random.uniform(5, 10))
        
        spawn_mob()

