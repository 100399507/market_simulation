import streamlit as st
from simulations.virtual_market import generate_virtual_market
from simulations.run_simulation import run_mass_simulation
from simulations.visualize import show_simulation_results

st.set_page_config(page_title="Simulation Enchères", layout="wide")
st.title("🧪 Simulation de marché")

# Paramètres de génération
num_lots = st.number_input("Nombre de lots", min_value=1, max_value=10, value=2)
num_products = st.number_input("Nombre de produits par lot", min_value=1, max_value=10, value=3)
num_buyers = st.number_input("Nombre d'acheteurs", min_value=1, max_value=50, value=5)
num_iterations = st.number_input("Nombre d'itérations de simulation", min_value=1, max_value=50, value=10)

if st.button("🚀 Générer marché virtuel et lancer simulation"):
    lots, products, buyers = generate_virtual_market(
        num_lots=num_lots,
        num_products=num_products,
        num_buyers=num_buyers
    )
    st.success("✅ Marché virtuel généré !")

    sim_results = run_mass_simulation(buyers, products, num_iterations=num_iterations)
    st.success("✅ Simulation terminée !")

    show_simulation_results(sim_results, products)
