import streamlit as st
import pandas as pd

def show_simulation_results(sim_results, products):
    """
    Affiche les résultats de simulation dans Streamlit.
    """
    st.title("📊 Résultats de Simulation")

    # Total CA par itération
    ca_df = pd.DataFrame([{
        "Itération": res["iteration"],
        "Chiffre d'affaires total": res["total_ca"]
    } for res in sim_results])
    st.subheader("💰 Chiffre d'affaires par simulation")
    st.dataframe(ca_df)
    st.line_chart(ca_df.set_index("Itération")["Chiffre d'affaires total"])

    # Allocations par produit pour la dernière simulation
    last_res = sim_results[-1]
    allocations = last_res["allocations"]
    alloc_rows = []
    for buyer_name, prod_allocs in allocations.items():
        for pid, qty in prod_allocs.items():
            alloc_rows.append({
                "Acheteur": buyer_name,
                "Produit": products[pid]["name"],
                "Qté allouée": qty
            })
    st.subheader("📦 Allocations finales (dernière simulation)")
    st.dataframe(pd.DataFrame(alloc_rows))
