import random
import string

def random_string(n=5):
    return "".join(random.choices(string.ascii_uppercase, k=n))

def round_up_to_multiple(value, multiple):
    """Arrondir la valeur au multiple supérieur ou égal"""
    return ((value + multiple - 1) // multiple) * multiple

def round_down_to_multiple(value, multiple):
    """Arrondir la valeur au multiple inférieur ou égal"""
    return (value // multiple) * multiple

def generate_virtual_market(num_lots=2, num_products=3, num_buyers=5):
    lots = {}
    products = {}
    buyers = []

    for l in range(1, num_lots+1):
        lot_id = f"lot_{l}"
        seller_id = f"Seller_{random_string(3)}"
        lots[lot_id] = {
            "seller_id": seller_id,
            "lot_name": f"Lot {lot_id}",
            "global_moq": 0,  # sera calculé plus tard si nécessaire
            "products": []
        }

        for p in range(1, num_products+1):
            pid = f"{lot_id}_P{p}"
            volume_multiple = random.choice([10, 20, 50])

            # Générer stock et MOQ comme multiples
            stock_raw = random.randint(100, 1000)
            stock = round_down_to_multiple(stock_raw, volume_multiple)

            moq_raw = random.randint(50, min(200, stock))
            seller_moq = round_up_to_multiple(moq_raw, volume_multiple)

            products[pid] = {
                "id": pid,
                "name": f"Produit {pid}",
                "stock": stock,
                "volume_multiple": volume_multiple,
                "starting_price": round(random.uniform(5, 20), 2),
                "seller_moq": seller_moq,
                "shelf_life": "15.12.2026",
                "lot_id": lot_id
            }
            lots[lot_id]["products"].append(pid)

    # Générer acheteurs
    for b in range(1, num_buyers+1):
        buyer_name = f"Buyer_{b}"
        buyer_products = {}
        for pid, prod in products.items():
            min_qty = prod["seller_moq"]
            max_qty = prod["stock"]

            if min_qty > max_qty:
                # Si le MOQ dépasse le stock, on ajuste
                min_qty = max_qty

            # Choisir quantité désirée multiple de volume_multiple
            possible_qtys = [q for q in range(min_qty, max_qty + 1) if q % prod["volume_multiple"] == 0]
            qty_desired = random.choice(possible_qtys) if possible_qtys else max_qty


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
