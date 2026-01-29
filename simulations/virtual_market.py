import random
import string

def random_string(n=5):
    return "".join(random.choices(string.ascii_uppercase, k=n))

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
            "global_moq": random.randint(50, 200),
            "products": []
        }

        for p in range(1, num_products+1):
            pid = f"{lot_id}_P{p}"
            volume_multiple = random.choice([10, 20, 50])

            # Stock total multiple de volume_multiple
            stock = random.randint(100, 1000)
            stock = (stock // volume_multiple) * volume_multiple
            if stock == 0:
                stock = volume_multiple

            # MOQ multiple de volume_multiple
            seller_moq = random.randint(50, 200)
            seller_moq = (seller_moq // volume_multiple) * volume_multiple
            if seller_moq == 0:
                seller_moq = volume_multiple

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

    # Générer acheteurs
    for b in range(1, num_buyers+1):
        buyer_name = f"Buyer_{b}"
        buyer_products = {}
        for pid, prod in products.items():
            # Limiter la quantité désirée à ≤ stock, multiple du volume
            max_qty = (prod["stock"] // prod["volume_multiple"]) * prod["volume_multiple"]
            min_qty = (prod["seller_moq"] // prod["volume_multiple"]) * prod["volume_multiple"]
            if min_qty > max_qty:
                min_qty = max_qty  # éviter plage vide
            if min_qty == 0:
                min_qty = prod["volume_multiple"]

            possible_qtys = list(range(min_qty, max_qty + 1, prod["volume_multiple"]))
            qty_desired = random.choice(possible_qtys)

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
