import neat
import neat.population
from GameManager import GameManager
from Platform import Platform
from Player import Player

class AIManager:
    def __init__(self, gameManager: GameManager):
        self.gameManager = gameManager
        config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            'neat-config.txt'
        )
        self.population = neat.Population(config)
        self.gen = 0

        self.stop_running = False

    def run_one_generation(self):
        self.gen += 1
        print(f"Generacja {self.gen}")
        self.population.run(self.run_player, 1)

    def run_player(self, genomes, config):
        nets = []
        players = []

        for id, g in genomes:
            net = neat.nn.FeedForwardNetwork.create(g, config)
            nets.append(net)
            g.fitness = 0
            self.gameManager.createPlayer()
            currentPlayer = self.gameManager.players[len(self.gameManager.players)-1]
            print("nowy ai gracz")

            currentPlayer.AIInputs(
            net,
            lambda: self.gameManager.build_observation(currentPlayer),  # przekazujemy kontekst gracza
            g)
            players.append(currentPlayer)


            
            