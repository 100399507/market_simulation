import random
import string

def random_string(n=5):
    return "".join(random.choices(string.ascii_uppercase, k=n))

def generate_virtual_market(num_lots=2, num_products=3, num_buyers=5):
    lots = {}
    products = {}
    buyers = []

    VOLUME_MULTIPLE = 10  # Tout sera multiple de 10

    # --- Générer lots et produits ---
    for l in range(1, num_lots + 1):
        lot_id = f"lot_{l}"
        seller_id = f"Seller_{random_string(3)}"
        lots[lot_id] = {
            "seller_id": seller_id,
            "lot_name": f"Lot {lot_id}",
            "global_moq": VOLUME_MULTIPLE * random.randint(5, 20),
            "products": []
        }

        for p in range(1, num_products + 1):
            pid = f"{lot_id}_P{p}"
            volume_multiple = VOLUME_MULTIPLE

            # Stock total multiple de volume_multiple
            stock = VOLUME_MULTIPLE * random.randint(10, 100)

            # MOQ multiple de volume_multiple
            seller_moq = VOLUME_MULTIPLE * random.randint(5, 20)

            products[pid] = {
                "id": pid,
                "name": f"Produit {pid}",
                "stock": stock,
                "volume_multiple": volume_multiple,
                "starting_price": round(random.uniform(5, 20), 2),
                "seller_moq": seller_moq,
                "shelf_life": "31.12.2026",
                "lot_id": lot_id
            }
            lots[lot_id]["products"].append(pid)

    # --- Générer acheteurs ---
    for b in range(1, num_buyers + 1):
        buyer_name = f"Buyer_{b}"
        buyer_products = {}
        for pid, prod in products.items():
            max_qty = prod["stock"]  # ≤ stock total
            min_qty = prod["seller_moq"]  # ≥ MOQ

            if min_qty > max_qty:
                min_qty = max_qty  # éviter plage vide
            if min_qty == 0:
                min_qty = VOLUME_MULTIPLE

            # Générer quantité désirée multiple de volume_multiple
            possible_qtys = list(range(min_qty, max_qty + 1, prod["volume_multiple"]))
            qty_desired = random.choice(possible_qtys) if possible_qtys else min_qty

            buyer_products[pid] = {
                "qty_desired": qty_desired,
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
