import numpy as np
import spaceinvaders as spcinv


class Species(object):
    def __init__(self, s_id, species_population, genome):
        self.species_id = s_id
        self.species_population = species_population
        self.generation_number = 0
        self.species_genome_representative = genome

        genome.set_species(self.species_id)
        genome.set_generation(self.generation_number)
        self.genomes = {i:genome.clone() for i in xrange(self.species_population)}
        for i in xrange(1, self.species_population):
            self.genomes[i].reinitialize()

        # Information used for culling and population control
        self.active = True
        self.no_improvement_generations_allowed = config.STAGNATED_SPECIES_THRESHOLD
        self.times_stagnated = 0
        self.avg_max_fitness_achieved = 0
        self.generation_with_max_fitness = 0
        
        
# This function holds the interface and interaction with SpaceInvaders
    def generate_fitness(self):
        species_score = 0
        
        self.pretty_print_s_id(self.species_id)
        self.pretty_print_gen_id(self.generation_number)

        neural_networks = self.genomes.values()

        # Run the game with each organism in the current generation
        app = spcinv.FlappyBirdApp(neural_networks)
        app.play()
        results = app.crash_info

        for crash_info in results:

            distance_from_pipes = 0
            if (crash_info['y'] < crash_info['upperPipes'][0]['y']):
                distance_from_pipes = abs(crash_info['y'] - crash_info['upperPipes'][0]['y'])       
            elif (crash_info['y'] > crash_info['upperPipes'][0]['y']):      
                distance_from_pipes = abs(crash_info['y'] - crash_info['lowerPipes'][0]['y'])       

            fitness_score = ((crash_info['score'] * 1000)       
                              + (crash_info['distance'])        
                              - (distance_from_pipes * 3)       
                              - (1.5 * crash_info['energy']))

            # Should experiment with this more.
            # fitness_score = ((crash_info['distance'])
            #                  - (1.5 * crash_info['energy']))

            neural_networks[crash_info['network_id']].set_fitness(fitness_score)
            species_score += fitness_score

        print "\nSpecies Score:", species_score

        return species_score

