# main_app.py
import streamlit as st
import copy
import random
import string
import pandas as pd
from core.allocation_algo import run_auto_bid_aggressive, solve_model
from core.recommendation import simulate_optimal_bid

# -----------------------------
# Génération marché virtuel
# -----------------------------
def random_string(n=5):
    return "".join(random.choices(string.ascii_uppercase, k=n))

def generate_virtual_market(num_lots=2, num_products=3, num_buyers=5):
    lots = {}
    products = {}
    buyers = []

    # Générer lots et produits
    for l in range(1, num_lots+1):
        lot_id = f"lot_{l}"
        seller_id = f"Seller_{random_string(3)}"
        lots[lot_id] = {
            "seller_id": seller_id,
            "lot_name": f"Lot {lot_id}",
            "global_moq": random.randint(50, 200),
            "products": []
        }

        for p in range(1, num_products+1):
            pid = f"{lot_id}_P{p}"
            volume_multiple = random.choice([10, 20, 50])
            stock = random.randint(100, 1000)
            products[pid] = {
                "id": pid,
                "name": f"Produit {pid}",
                "stock": stock,
                "volume_multiple": volume_multiple,
                "starting_price": round(random.uniform(5, 20), 2),
                "seller_moq": random.randint(50, 200),
                "shelf_life": "31.12.2026",
                "lot_id": lot_id
            }
            lots[lot_id]["products"].append(pid)

    # Générer acheteurs
    for b in range(1, num_buyers+1):
        buyer_name = f"Buyer_{b}"
        buyer_products = {}
        for pid, prod in products.items():
            buyer_products[pid] = {
                "qty_desired": random.randint(prod["seller_moq"], prod["stock"]),
                "current_price": prod["starting_price"],
                "max_price": round(prod["starting_price"] * random.uniform(1.1, 2.0), 2),
                "moq": prod["seller_moq"],
                "volume_multiple": prod["volume_multiple"]
            }
        buyers.append({
            "name": buyer_name,
            "auto_bid": True,
            "products": buyer_products
        })

    return lots, products, buyers

# -----------------------------
# Interface principale
# -----------------------------
st.title("🏛️ Plateforme Enchères - Test et Réel")

mode = st.radio("Choisir le mode :", ["Marché réel", "Marché virtuel (simulation)"])

if mode == "Marché réel":
    st.info("Utilisez cette section pour saisir vos enchères réelles et voir vos allocations.")

    # Ici tu peux mettre ton ancien code buyer_app.py intégré ou importer
    from apps.buyer_app import buyer_app
    buyer_app()

else:
    st.info("Génération automatique de lots, produits et acheteurs pour tests massifs.")

    num_lots = st.number_input("Nombre de lots", min_value=1, max_value=20, value=3)
    num_products_per_lot = st.number_input("Produits par lot", min_value=1, max_value=10, value=3)
    num_buyers = st.number_input("Nombre d'acheteurs", min_value=1, max_value=50, value=5)

    if st.button("🧪 Générer marché virtuel et lancer simulation"):
        lots, products, buyers = generate_virtual_market(
            num_lots=num_lots,
            num_products=num_products_per_lot,
            num_buyers=num_buyers
        )

        st.success("✅ Marché virtuel généré !")

        # Lancer l'auto-bid avec barre de progression
            st.subheader("🚀 Simulation auto-bid en cours...")
            progress_bar = st.progress(0)
            status_text = st.empty()

            max_rounds = 30
            buyers_simulated = copy.deepcopy(buyers)

            for round_num in range(1, max_rounds + 1):
                status_text.text(f"Round {round_num}/{max_rounds}")

                # Lancer un seul round de l'auto-bid
                buyers_simulated = run_auto_bid_aggressive(buyers_simulated, list(products.values()), max_rounds=1)

                # Mettre à jour la barre
                progress_bar.progress(round_num / max_rounds)

            progress_bar.empty()
            status_text.text("✅ Simulation terminée !")

            # Résolution finale
            allocations, total_ca = solve_model(buyers_simulated, list(products.values()))

            st.subheader("📊 Résultats allocation virtuelle")
            rows = []
            for b in buyers_simulated:
                buyer_name = b["name"]
                for pid, p in b["products"].items():
                    rows.append({
                        "Acheteur": buyer_name,
                        "Produit": products[pid]["name"],
                        "Qté demandée": p["qty_desired"],
                        "Qté allouée": allocations[buyer_name].get(pid, 0),
                        "Prix final (€)": p["current_price"]
                    })
            df_results = pd.DataFrame(rows)
            st.dataframe(df_results)

            st.markdown(f"### 💰 Chiffre d'affaires total simulé : {total_ca:.2f} €")
