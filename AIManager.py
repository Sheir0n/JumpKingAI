import neat
import neat.population
from GameManager import GameManager
from Platform import Platform

class AIManager:
    def __init__(self, gameManager: GameManager):
        self.gameManager = gameManager
        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, 'neat-config.txt')
        self.population = neat.Population(config)
        self.population.run(self.run_player, 1) #jedna generacja
    
    def run_player(self, genomes, config):
        nets = []
        players = []

        for id, g in genomes:
            net = neat.nn.FeedForwardNetwork.create(g, config)
            nets.append(net)
            g.fitness = 0
            
            self.gameManager.player.AIInputs(net, self.gameManager.build_observation, g)
            players.append(self.gameManager.player)
            