import random

from . import constants

class BaseValuesRandomizer:
    @classmethod
    def randomize_stats(cls, vanilla_stats, random_factor):
        min_val = 20
        max_val = 235

        bst_list = []
        for stat in vanilla_stats:
            bst_list.append(stat)
        bst = sum(bst_list)
        new_stats_bytes = bytearray()

        # Start with an array of 5 numbers, all at the minimum value
        new_stats = [min_val] * 5
        current_sum = sum(new_stats)

        # Increment numbers until we reach BST
        while current_sum < bst:
            # Randomly select an index to increase
            idx = cls.select_index(random_factor)

            # Only increase if it won't exceed max_val
            if new_stats[idx] < max_val:
                new_stats[idx] += 1
                current_sum += 1
            else:
                # Check if all numbers are maxed out (should never happen with correct BST input)
                if all(n == max_val for n in new_stats):
                    raise RuntimeError("All stats reached max_val but BST is not yet met. Something went wrong!")

        random.shuffle(new_stats)
        for stat in new_stats:
            try:
                new_stats_bytes.extend(stat.to_bytes(1, "big"))
            except OverflowError:
                print("ERROR: BST is too high.")
                print("BST_STR: " + str(vanilla_stats))
                print("BST: " + str(bst))
                print("STATS: " + str(new_stats))
                exit(1)

        return new_stats_bytes

    @classmethod
    def select_index(cls, random_factor):
        random_factor = random_factor - 1
        weight_map = {
            1: constants.bst_weights[0] if random.random() < 0.5 else constants.bst_weights[1],
            2: constants.bst_weights[2],
            3: constants.bst_weights[3]
        }
        
        return random.choices([0, 1, 2, 3, 4], weights=weight_map.get(random_factor, constants.bst_weights[0]))[0]
