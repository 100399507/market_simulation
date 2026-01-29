# main_app.py
import streamlit as st
import copy
import random
import string
import altair as alt
import pandas as pd
from core.allocation_algo import run_auto_bid_aggressive, solve_model
from core.recommendation import simulate_optimal_bid

# -----------------------------
# Génération marché virtuel
# -----------------------------
def random_string(n=5):
    return "".join(random.choices(string.ascii_uppercase, k=n))

def generate_virtual_market(num_lots=2, num_products=3, num_buyers=5):
    VOLUME_MULTIPLE = 10  # On force tout en multiples de 10
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

            # Stock multiple de 10
            stock = (random.randint(10, 1000) // VOLUME_MULTIPLE) * VOLUME_MULTIPLE
            if stock == 0:
                stock = VOLUME_MULTIPLE

            # MOQ multiple de 10
            seller_moq = (random.randint(10, 200) // VOLUME_MULTIPLE) * VOLUME_MULTIPLE
            if seller_moq == 0:
                seller_moq = VOLUME_MULTIPLE

            products[pid] = {
                "id": pid,
                "name": f"Produit {pid}",
                "stock": stock,
                "volume_multiple": VOLUME_MULTIPLE,
                "starting_price": round(random.uniform(5, 20), 2),
                "seller_moq": seller_moq,
                "shelf_life": "31.12.2026",
                "lot_id": lot_id
            }
            lots[lot_id]["products"].append(pid)

    # Générer acheteurs
    for b in range(1, num_buyers+1):
        buyer_name = f"Buyer_{b}"
        buyer_products = {}
        for pid, prod in products.items():
            # Quantité désirée multiple de 10 et ≤ stock
            min_qty = prod["seller_moq"]
            max_qty = prod["stock"]
            if min_qty > max_qty:
                min_qty = max_qty
            possible_qtys = list(range(min_qty, max_qty + 1, VOLUME_MULTIPLE))
            if not possible_qtys:
                qty_desired = min_qty
            else:
                qty_desired = random.choice(possible_qtys)

            buyer_products[pid] = {
                "qty_desired": qty_desired,
                "starting_price": prod["starting_price"],  # prix initial
                "current_price": prod["starting_price"],   # prix courant pour l'auto-bid
                "max_price": round(prod["starting_price"] * random.uniform(1.1, 2.0), 2),
                "moq": prod["seller_moq"],
                "volume_multiple": VOLUME_MULTIPLE
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

        all_results = []
        all_history = []
        total_ca_global = 0
        progress_bar = st.progress(0)
        num_lots_total = len(lots)
        lot_counter = 0

        # --- Simulation lot par lot ---
        for lot_id, lot in lots.items():
            lot_products = [products[pid] for pid in lot["products"]]

            # Sélection des acheteurs pour ce lot
            buyers_for_lot = []
            for b in buyers:
                prod_for_lot = {pid: p for pid, p in b["products"].items() if pid in lot["products"]}
                if prod_for_lot:
                    buyers_for_lot.append({
                        "name": b["name"],
                        "auto_bid": b.get("auto_bid", False),
                        "products": prod_for_lot
                    })

            # --- Lancer l'auto-bid avec suivi des incréments et arrêt si quantité allouée atteinte ---
            buyers_simulated_lot = copy.deepcopy(buyers_for_lot)
            allocations = {b["name"]: {pid: 0 for pid in lot["products"]} for b in buyers_simulated_lot}
            
            for round_num in range(30):
                changes_made = False
            
                # Calcul allocations à ce round
                allocations_round, _ = solve_model(buyers_simulated_lot, lot_products)
            
                for b in buyers_simulated_lot:
                    if not b.get("auto_bid", False):
                        continue
                    for pid, p in b["products"].items():
                        qty_allocated = allocations_round[b["name"]].get(pid, 0)
                        if qty_allocated >= p["qty_desired"]:
                            # Stopper l'enchère si l'acheteur a déjà obtenu sa quantité
                            continue
            
                        old_price = p["current_price"]
                        step = max(0.1, p["current_price"] * 0.05)
                        next_price = min(p["current_price"] + step, p["max_price"])
                        if next_price > old_price:
                            p["current_price"] = round(next_price, 2)
                            changes_made = True
                            # Historique
                            all_history.append({
                                "Lot": lot["lot_name"],
                                "Round": round_num + 1,
                                "Acheteur": b["name"],
                                "Produit": products[pid]["name"],
                                "Prix précédent (€)": old_price,
                                "Prix actuel (€)": p["current_price"]
                            })
            
                # Si plus aucun changement, on sort
                if not changes_made:
                    break

            # Après la boucle, calcul final des allocations
            allocations, total_ca_lot = solve_model(buyers_simulated_lot, lot_products)
            total_ca_global += total_ca_lot


            # --- Stocker résultats finaux ---
            for b in buyers_simulated_lot:
                buyer_name = b["name"]
                for pid, p in b["products"].items():
                    all_results.append({
                        "Lot": lot["lot_name"],
                        "Acheteur": buyer_name,
                        "Produit": products[pid]["name"],
                        "Qté demandée": p["qty_desired"],
                        "Qté allouée": allocations[buyer_name].get(pid, 0),
                        "Prix initial (€)": p["starting_price"],
                        "Prix max (€)": p["max_price"],
                        "Prix final (€)": p["current_price"]
                    })

            lot_counter += 1
            progress_bar.progress(lot_counter / num_lots_total)

        # --- Affichage résultats ---
        st.subheader("📊 Résultats allocation virtuelle par lot")
        df_results = pd.DataFrame(all_results)
        st.dataframe(df_results)

        st.markdown(f"### 💰 Chiffre d'affaires total simulé : {total_ca_global:.2f} €")

        st.subheader("📋 Récapitulatif complet par lot, produit et acheteur")
        lot_rows = []

        for lot_id, lot in lots.items():
            for pid in lot["products"]:
                product_info = products[pid]
                for row in all_results:
                    if row["Produit"] == product_info["name"] and row["Lot"] == lot["lot_name"]:
                        qty_allocated = row["Qté allouée"]
                        stock_total = product_info["stock"]
                        percent_allocated = round((qty_allocated / stock_total) * 100, 2) if stock_total > 0 else 0

                        lot_rows.append({
                            "Lot": lot["lot_name"],
                            "Produit": product_info["name"],
                            "Stock total": stock_total,
                            "MOQ": product_info["seller_moq"],
                            "Volume multiple": product_info["volume_multiple"],
                            "Acheteur": row["Acheteur"],
                            "Qté demandée": row["Qté demandée"],
                            "Qté allouée": qty_allocated,
                            "Prix initial (€)": row["Prix initial (€)"],
                            "Prix max (€)": row["Prix max (€)"],
                            "Prix final (€)": row["Prix final (€)"],
                            "% de quantité écoulée": percent_allocated
                        })

        df_lot_summary = pd.DataFrame(lot_rows)
        st.dataframe(df_lot_summary.sort_values(["Lot", "Produit", "Acheteur"]))

        if all_history:
            st.subheader("📈 Historique des incréments de prix par lot")
            df_history = pd.DataFrame(all_history)
            st.dataframe(df_history.sort_values(["Lot", "Round", "Produit", "Acheteur"]))
            # --- Graphique évolution des prix ---

            st.subheader("📈 Courbes d'évolution des prix par produit et acheteur")
        
            # Préparer les données pour Altair
            df_chart = df_history.copy()
            df_chart["Round"] = df_chart["Round"].astype(int)
            df_chart["Prix actuel (€)"] = df_chart["Prix actuel (€)"].astype(float)
        
            # Créer le graphique
            chart = alt.Chart(df_chart).mark_line(point=True).encode(
                x="Round:O",
                y="Prix actuel (€):Q",
                color="Acheteur:N",
                strokeDash="Produit:N",
                tooltip=["Lot", "Produit", "Acheteur", "Round", "Prix actuel (€)"]
            ).properties(
                width=800,
                height=400
            ).interactive()
        
            st.altair_chart(chart)

