import neat
import neat.population
from GameManager import GameManager
from Platform import Platform
from Player import Player

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
            self.gameManager.createPlayer()
            currentPlayer = self.gameManager.players[len(self.gameManager.players)-1]
            print("nowy ai gracz")

            for p in self.gameManager.platforms:
                if p.reward_level == currentPlayer.curr_platform_reward_level+1:
                    nextPlatform : Platform = p
                    break
            observation = [currentPlayer.posX/self.gameManager.screenWidth, currentPlayer.posY/self.gameManager.screenWidth, nextPlatform.hitbox.centerx/self.gameManager.screenWidth, nextPlatform.hitbox.centery/self.gameManager.screenHeight, currentPlayer.inAir, currentPlayer.upAcceleration] 

            currentPlayer.AIInputs(
            net,
            lambda: self.gameManager.build_observation(currentPlayer),  # przekazujemy kontekst gracza
            g
            )
            players.append(currentPlayer)
            
            