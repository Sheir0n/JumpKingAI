import weakref

class AIManager:
    def __init__(self, game_manager):
        self.game_manager = weakref.ref(game_manager)
        self.fitness_record = 0
        self.best_genomes = []

    def observation_func(self, player):
        curr_id = player.curr_platform_id

        seen_platforms = self.game_manager().platforms[curr_id:curr_id + 3]
        if len(seen_platforms) < 3 and seen_platforms:
            last = seen_platforms[-1]
            seen_platforms.extend([last] * (3 - len(seen_platforms)))

        # ustawienie graczowi kierunku do kolejnej platformy
        player.set_suggested_direction(-1.0 if player.hitbox.centerx > seen_platforms[1].hitbox.centerx else 1.0)

        return [
            # 1. Pozycja X względem środka ekranu (od -1 do 1)
            (player.hitbox.centerx - self.game_manager().screen_width / 2) / (self.game_manager().screen_width / 2),

            # 2. Relatywna pozycja X aktualnej platformy (od -1 do 1)
            (seen_platforms[0].hitbox.centerx - player.hitbox.centerx) / (self.game_manager().screen_width / 2),

            # 3. Szerokość aktualnej platformy (0–1)
            seen_platforms[0].hitbox.width / self.game_manager().screen_width,

            # 4. Relatywna pozycja X kolejnej platformy (od -1 do 1)
            (seen_platforms[1].hitbox.centerx - player.hitbox.centerx) / (self.game_manager().screen_width / 2),

            # 5. Relatywna pozycja Y kolejnej platformy (od -1 do 1)
            (seen_platforms[1].hitbox.top - player.hitbox.bottom) / self.game_manager().screen_height,

            # 6. Szerokość kolejnej platformy (0–1)
            seen_platforms[1].hitbox.width / self.game_manager().screen_width,
        ]

    def end_generation_calculations(self):
        for player in self.game_manager().players:
            player.ai.height_record_reward()

        self.collect_and_display_gen_stats()

    def collect_and_display_gen_stats(self):
        fitness_stats = []
        for player in self.game_manager().players:
            fitness_stats.append(player.ai.genome().fitness)
        sorted_stats = sorted(fitness_stats, reverse=True)

        if sorted_stats[0] > self.fitness_record:
            self.fitness_record = sorted_stats[0]
            print("new record = ", self.fitness_record)

        for i, fitness in enumerate(sorted_stats[:10], start=1):
            print(f"{i}. {fitness:.2f}")


