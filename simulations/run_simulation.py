import copy
from core.allocation_algo import run_auto_bid_aggressive, solve_model
from core.recommendation import simulate_optimal_bid

def run_mass_simulation(buyers, products, num_iterations=10):
    """
    Simule plusieurs scénarios de comportement d'acheteurs.
    Chaque itération peut modifier certains prix max pour tester l'algorithme.
    """
    simulation_results = []

    for i in range(num_iterations):
        buyers_copy = copy.deepcopy(buyers)

        # Exemple de scénario : augmenter aléatoirement certains prix max
        for buyer in buyers_copy:
            for pid, prod in buyer["products"].items():
                if prod["max_price"] < 100:  # limite arbitraire
                    prod["max_price"] *= 1 + 0.05 * i  # incrément progressif itératif

        # Lancer l'auto-bid
        buyers_after_bid = run_auto_bid_aggressive(buyers_copy, list(products.values()), max_rounds=30)

        # Résolution finale
        allocations, total_ca = solve_model(buyers_after_bid, list(products.values()))

        # Stocker résultats
        simulation_results.append({
            "iteration": i+1,
            "buyers": buyers_after_bid,
            "allocations": allocations,
            "total_ca": total_ca
        })

    return simulation_results
