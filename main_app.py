# main_app.py
import streamlit as st
from apps import buyer_app, seller_app
from simulations.virtual_market import generate_virtual_market
from core.allocation_algo import run_auto_bid_aggressive, solve_model
import pandas as pd

st.set_page_config(
    page_title="Market Allocation Simulator",
    layout="wide"
)

st.title("🛒 Market Allocation Simulator")

menu = ["Accueil", "Acheteur", "Vendeur", "Simulation de marché"]
choice = st.sidebar.selectbox("Navigation", menu)

if choice == "Accueil":
    st.markdown(
        """
        Bienvenue sur le simulateur de marché multiproduit !
        
        🔹 Utilisez **Acheteur** pour simuler vos enchères et recommandations.  
        🔹 Utilisez **Vendeur** pour suivre vos lots et le chiffre d'affaires.  
        🔹 Utilisez **Simulation de marché** pour tester des scénarios massifs et observer le comportement des algorithmes.
        """
    )

elif choice == "Acheteur":
    st.subheader("💡 Espace Acheteur")
    buyer_app.buyer_app()

elif choice == "Vendeur":
    st.subheader("💡 Espace Vendeur")
    seller_app.seller_app()

elif choice == "Simulation de marché":
    st.subheader("💻 Simulation de marché virtuelle")

    # Paramètres de simulation
    num_lots = st.number_input("Nombre de lots", min_value=1, max_value=20, value=3)
    num_products_per_lot = st.number_input("Nombre de produits par lot", min_value=1, max_value=10, value=3)
    num_buyers = st.number_input("Nombre d'acheteurs", min_value=1, max_value=50, value=10)
    
    if st.button("🧪 Générer marché virtuel et lancer simulation"):

        # Génération du marché
        lots, products, buyers = generate_virtual_market(
            num_lots=num_lots,
            num_products_per_lot=num_products_per_lot,
            num_buyers=num_buyers
        )
        st.success("✅ Marché virtuel généré avec succès !")

        # Lancer auto-bid pour tous les acheteurs
        buyers_after_bid = run_auto_bid_aggressive(buyers, list(products.values()))

        # Calculer allocations et CA
        allocations, total_ca = solve_model(buyers_after_bid, list(products.values()))

        # Affichage des résultats
        st.subheader("📊 Résultats des allocations")
        rows = []
        for b in buyers_after_bid:
            buyer_name = b["name"]
            for pid, prod in b["products"].items():
                rows.append({
                    "Acheteur": buyer_name,
                    "Produit": products[pid]["name"],
                    "Qté demandée": prod["qty_desired"],
                    "Qté allouée": allocations[buyer_name].get(pid, 0),
                    "Prix final (€)": prod["current_price"]
                })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)

        st.markdown(f"### 💵 Chiffre d'affaires total simulé : {total_ca:.2f} €")
