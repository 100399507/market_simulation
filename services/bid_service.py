from services.state_manager import load_json, save_json
from datetime import datetime

def save_final_allocations(buyers, allocations, lot_id, seller_id, path="data/bids_history.json"):
    history = load_json(path)
    timestamp = datetime.now().isoformat()

    for buyer in buyers:
        buyer_name = buyer["name"]
        for prod_id, qty_alloc in allocations.get(buyer_name, {}).items():
            final_price = buyer["products"][prod_id]["current_price"]
            entry = {
                "buyer": buyer_name,
                "lot_id": lot_id,
                "product": prod_id,
                "qty_desired": buyer["products"][prod_id]["qty_desired"],
                "qty_allocated": qty_alloc,
                "final_price": final_price,
                "max_price": buyer["products"][prod_id]["max_price"],
                "timestamp": timestamp,
                "seller_id": seller_id
            }
            history.append(entry)
    save_json(path, history)
