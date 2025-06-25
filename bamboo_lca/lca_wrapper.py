import bw2calc as bc
import pandas as pd
import numpy as np
import os


class LCAWrapper:
    def perform_static(self, demand, datapackage, directory, k, t, myact):
        """
        Perform static simulation and save the lca score.

        Parameters:
            * demand: The dictionary of the functional unit, for example: {<index>: <amount>}.
            * datapackage: The datapackage used for simulation.
            * directory: The directory to save output file.
            * k: The case identifier.
            * t: The type of the simulation, such as "static", "uniform_0.2".
            * myact: 
        """
        lca = bc.LCA(
            demand=demand,
            data_objs=[datapackage],
        )
        lca.lci()
        lca.lcia()

        print(f"Brightway calculated lca score: {lca.score, myact}")
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, f"CASE_{k}_{t}_MC_simulations_{myact}.csv")

        with open(filename, "w") as file:
            file.write("kg CO2eq\n") # TODO: Write the header -> Not use this function, so it's ok for now.
            file.write(f"{lca.score}")
            print(f"Static LCA result saved to {filename}.")

    def perform_stochastic(self, index, datapackage, directory, k, t, myact, batch_size=50, num_batches=10):
        """
        Perform Monte Carlo simulation and save the lca score.
        """
        lca = bc.LCA(
            demand={index: 1},
            data_objs=[datapackage],
            use_distributions=True,
        )
        lca.lci()
        lca.lcia()

        print(f"Brightway calculated lca score(with uncertainty): {lca.score, myact}")
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, f"CASE_{k}_{t}_MC_simulations_{myact}.csv")

        with open(filename, "w") as file:
            file.write("kg CO2eq\n")
            for p in range(num_batches):
                batch_results = [lca.score for _ in zip(range(batch_size), lca)]
                df_batch = pd.DataFrame(batch_results, columns=["kg CO2eq"])
                df_batch.to_csv(file, header=False, index=False)
                print(f"Batch {p} saved to {filename}.")

        print(f"Results saved to {filename}.")

    def manual_lca(self, A, B, C, index): 
        """
        Perform Monte Carlo simulation without brightway.
        """
        f = np.zeros((len(A), 1))
        f[index] = 1
        lca_score = np.sum(C.dot(B.dot((np.linalg.inv(A)).dot(f))))
        
        return float(lca_score)