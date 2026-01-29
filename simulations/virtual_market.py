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
            stock = random.randint(100, 1000)
            products[pid] = {
                "id": pid,
                "name": f"Produit {pid}",
                "stock": stock,
                "volume_multiple": volume_multiple,
                "starting_price": round(random.uniform(5, 20), 2),
                "seller_moq": random.randint(50, 200),
                "shelf_life": "15.12.2026",
                "lot_id": lot_id
            }
            lots[lot_id]["products"].append(pid)

    for b in range(1, num_buyers+1):
        buyer_name = f"Buyer_{b}"
        buyer_products = {}
        for pid, prod in products.items():
            buyer_products[pid] = {
                "qty_desired": random.randint(prod["seller_moq"], prod["stock"]),
                "current_price": prod["starting_price"],
                "max_price": prod["starting_price"]*1.5,
                "moq": prod["seller_moq"],
                "volume_multiple": prod["volume_multiple"]
            }
        buyers.append({
            "name": buyer_name,
            "auto_bid": True,
            "products": buyer_products
        })

    return lots, products, buyers
