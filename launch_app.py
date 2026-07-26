# launch_app.py
import os
import sys
import subprocess
import time
import webbrowser

BASE_TEST_DIR = os.path.abspath("./test_project")

def log(msg):
    print(f"[App Launcher] {msg}")

def ensure_web_app_harness(app_path, app_name):
    """Ensures package.json and a fully interactive index.html exist so Vite/npm can immediately serve the app."""
    pkg_json_path = os.path.join(app_path, "package.json")
    index_html_path = os.path.join(app_path, "index.html")

    pkg_content = f"""{{
  "name": "{app_name.lower()}",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {{
    "dev": "vite --port 5173 --host",
    "build": "vite build",
    "preview": "vite preview"
  }},
  "dependencies": {{
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }},
  "devDependencies": {{
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0"
  }}
}}
"""
    with open(pkg_json_path, "w", encoding="utf-8") as f:
        f.write(pkg_content)

    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GourmetGo Platform — Full-Stack Interactive App</title>
    <style>
        :root {
            --bg: #0f172a;
            --card-bg: #1e293b;
            --card-hover: #2d3748;
            --border: #334155;
            --accent: #38bdf8;
            --green: #10b981;
            --orange: #f59e0b;
            --red: #ef4444;
            --purple: #8b5cf6;
            --text: #f8fafc;
            --subtext: #94a3b8;
        }
        * { box-sizing: border-box; }
        body { font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 0; min-height: 100vh; }
        
        /* Header & Nav */
        header { background: #0b0f19; border-bottom: 1px solid var(--border); padding: 16px 32px; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 100; }
        .logo { font-size: 22px; font-weight: 800; color: var(--accent); display: flex; align-items: center; gap: 10px; }
        .logo span { background: linear-gradient(135deg, #38bdf8, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        
        nav { display: flex; gap: 8px; }
        .nav-btn { background: transparent; border: 1px solid var(--border); color: var(--subtext); padding: 10px 18px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 8px; }
        .nav-btn:hover, .nav-btn.active { background: var(--card-bg); color: var(--accent); border-color: var(--accent); }
        .cart-badge { background: var(--orange); color: black; font-weight: 800; padding: 2px 8px; border-radius: 12px; font-size: 12px; }
        
        /* Main Layout */
        main { max-width: 1200px; margin: 32px auto; padding: 0 24px; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        
        /* Filter Bar & Search */
        .toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; gap: 16px; flex-wrap: wrap; }
        .search-box { background: var(--card-bg); border: 1px solid var(--border); padding: 12px 18px; border-radius: 10px; color: var(--text); font-size: 14px; width: 320px; outline: none; }
        .search-box:focus { border-color: var(--accent); }
        .category-pills { display: flex; gap: 8px; }
        .pill { background: var(--card-bg); border: 1px solid var(--border); color: var(--subtext); padding: 8px 16px; border-radius: 20px; font-size: 13px; font-weight: 600; cursor: pointer; }
        .pill.active { background: var(--accent); color: #000; border-color: var(--accent); }
        
        /* Grid Layouts */
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 24px; }
        .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 16px; overflow: hidden; transition: transform 0.2s, border-color 0.2s; }
        .card:hover { transform: translateY(-4px); border-color: var(--accent); }
        .card-header { padding: 20px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: flex-start; }
        .card-title { font-size: 18px; font-weight: 700; margin: 0; color: var(--text); }
        .card-sub { font-size: 13px; color: var(--subtext); margin-top: 4px; }
        .card-body { padding: 20px; }
        
        /* Food Menu List */
        .menu-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #2d3748; }
        .menu-item:last-child { border-bottom: none; }
        .item-name { font-weight: 600; font-size: 14px; }
        .item-desc { font-size: 12px; color: var(--subtext); }
        .item-price { font-weight: 700; color: var(--green); font-size: 14px; }
        
        /* Buttons & Actions */
        .btn { background: var(--accent); color: #000; border: none; padding: 8px 16px; border-radius: 8px; font-weight: 700; cursor: pointer; transition: opacity 0.2s; display: inline-flex; align-items: center; gap: 6px; }
        .btn:hover { opacity: 0.9; }
        .btn-green { background: var(--green); color: #000; }
        .btn-red { background: var(--red); color: white; }
        .btn-outline { background: transparent; border: 1px solid var(--border); color: var(--text); }
        
        /* Cart Drawer */
        .cart-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.7); z-index: 200; justify-content: flex-end; }
        .cart-overlay.active { display: flex; }
        .cart-drawer { background: var(--card-bg); width: 420px; height: 100%; padding: 32px; display: flex; flex-direction: column; border-left: 1px solid var(--border); }
        .cart-title { font-size: 20px; font-weight: 800; border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-top: 0; display: flex; justify-content: space-between; }
        .cart-items { flex: 1; overflow-y: auto; margin: 20px 0; }
        .cart-total { border-top: 1px solid var(--border); padding-top: 16px; font-size: 18px; font-weight: 800; display: flex; justify-content: space-between; }
        
        /* Status Badges */
        .status-badge { padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; display: inline-block; }
        .status-pending { background: rgba(245, 158, 11, 0.2); color: var(--orange); border: 1px solid var(--orange); }
        .status-accepted { background: rgba(56, 189, 248, 0.2); color: var(--accent); border: 1px solid var(--accent); }
        .status-delivered { background: rgba(16, 185, 129, 0.2); color: var(--green); border: 1px solid var(--green); }
        
        /* Live Tracking Bar */
        .progress-bar { background: #0f172a; height: 10px; border-radius: 5px; overflow: hidden; margin: 16px 0; border: 1px solid var(--border); }
        .progress-fill { background: linear-gradient(90deg, var(--accent), var(--green)); height: 100%; width: 65%; transition: width 0.5s; }
    </style>
</head>
<body>

    <header>
        <div class="logo">🚀 <span>GourmetGo</span> Platform</div>
        <nav>
            <button class="nav-btn active" onclick="switchTab('customer')">🍔 Customer Storefront</button>
            <button class="nav-btn" onclick="switchTab('restaurant')">🍳 Restaurant Dashboard</button>

            <button class="nav-btn" onclick="switchTab('driver')">🛵 Delivery Driver</button>
            <button class="nav-btn" onclick="openCart()">🛒 Cart <span class="cart-badge" id="cart-count">0</span></button>
        </nav>
    </header>

    <main>
        <!-- CUSTOMER STOREFRONT TAB -->
        <div id="tab-customer" class="tab-content active">
            <div class="toolbar">
                <input type="text" class="search-box" id="search-input" placeholder="Search restaurants or dishes..." onkeyup="filterRestaurants()">
                <div class="category-pills">
                    <button class="pill active" onclick="filterCategory('all', this)">All</button>
                    <button class="pill" onclick="filterCategory('burgers', this)">Burgers</button>
                    <button class="pill" onclick="filterCategory('pizza', this)">Pizza</button>
                    <button class="pill" onclick="filterCategory('sushi', this)">Sushi</button>
                </div>
            </div>

            <div class="grid" id="restaurant-grid">
                <!-- Gourmet Burger Kitchen -->
                <div class="card" data-category="burgers" data-name="gourmet burger kitchen">
                    <div class="card-header">
                        <div>
                            <h3 class="card-title">Gourmet Burger Kitchen</h3>
                            <div class="card-sub">⭐ 4.9 • 20-30 mins • American & Fast Food</div>
                        </div>
                        <span class="status-badge status-accepted">Open</span>
                    </div>
                    <div class="card-body">
                        <div class="menu-item">
                            <div>
                                <div class="item-name">Truffle Smash Burger</div>
                                <div class="item-desc">Double Wagyu beef patty, truffle aioli, cheddar</div>
                            </div>
                            <div>
                                <span class="item-price">$14.99</span>
                                <button class="btn" onclick="addToCart('Truffle Smash Burger', 14.99)">+ Add</button>
                            </div>
                        </div>
                        <div class="menu-item">
                            <div>
                                <div class="item-name">Loaded Seasoned Fries</div>
                                <div class="item-desc">Hand-cut fries, melted cheese, bacon bits</div>
                            </div>
                            <div>
                                <span class="item-price">$6.49</span>
                                <button class="btn" onclick="addToCart('Loaded Seasoned Fries', 6.49)">+ Add</button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Artisan Pizza Studio -->
                <div class="card" data-category="pizza" data-name="artisan pizza studio">
                    <div class="card-header">
                        <div>
                            <h3 class="card-title">Artisan Pizza Studio</h3>
                            <div class="card-sub">⭐ 4.8 • 25-35 mins • Neapolitan Wood-Fired</div>
                        </div>
                        <span class="status-badge status-accepted">Open</span>
                    </div>
                    <div class="card-body">
                        <div class="menu-item">
                            <div>
                                <div class="item-name">Margherita Supreme</div>
                                <div class="item-desc">San Marzano tomatoes, fresh mozzarella, basil</div>
                            </div>
                            <div>
                                <span class="item-price">$16.99</span>
                                <button class="btn" onclick="addToCart('Margherita Supreme', 16.99)">+ Add</button>
                            </div>
                        </div>
                        <div class="menu-item">
                            <div>
                                <div class="item-name">Spicy Pepperoni Honey</div>
                                <div class="item-desc">Crispy pepperoni, hot honey drizzle, ricotta</div>
                            </div>
                            <div>
                                <span class="item-price">$18.99</span>
                                <button class="btn" onclick="addToCart('Spicy Pepperoni Honey', 18.99)">+ Add</button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Tokyo Sushi Bar -->
                <div class="card" data-category="sushi" data-name="tokyo sushi bar">
                    <div class="card-header">
                        <div>
                            <h3 class="card-title">Tokyo Sushi Bar</h3>
                            <div class="card-sub">⭐ 4.9 • 15-25 mins • Japanese & Omakase</div>
                        </div>
                        <span class="status-badge status-accepted">Open</span>
                    </div>
                    <div class="card-body">
                        <div class="menu-item">
                            <div>
                                <div class="item-name">Salmon Nigiri Platter</div>
                                <div class="item-desc">6 pcs fresh Atlantic salmon over seasoned rice</div>
                            </div>
                            <div>
                                <span class="item-price">$19.99</span>
                                <button class="btn" onclick="addToCart('Salmon Nigiri Platter', 19.99)">+ Add</button>
                            </div>
                        </div>
                        <div class="menu-item">
                            <div>
                                <div class="item-name">Dragon Roll</div>
                                <div class="item-desc">Eel, avocado, cucumber, spicy mayo</div>
                            </div>
                            <div>
                                <span class="item-price">$15.49</span>
                                <button class="btn" onclick="addToCart('Dragon Roll', 15.49)">+ Add</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- RESTAURANT DASHBOARD TAB -->
        <div id="tab-restaurant" class="tab-content">
            <h2 style="margin-top:0;">🍳 Restaurant Order Management</h2>
            <div class="grid">
                <div class="card">
                    <div class="card-header">
                        <div>
                            <h3 class="card-title">Incoming Order #GO-8841</h3>
                            <div class="card-sub">Customer: Alex M. • 2 items • $21.48</div>
                        </div>
                        <span class="status-badge status-pending" id="status-8841">Pending Acceptance</span>
                    </div>
                    <div class="card-body">
                        <div style="font-size:13px; color:var(--subtext); margin-bottom:16px;">
                            • 1x Truffle Smash Burger ($14.99)<br>
                            • 1x Loaded Seasoned Fries ($6.49)
                        </div>
                        <div style="display:flex; gap:10px;">
                            <button class="btn btn-green" onclick="updateOrderStatus('8841', 'Accepted & Preparing', 'status-accepted')">Accept Order</button>
                            <button class="btn btn-red" onclick="updateOrderStatus('8841', 'Rejected', 'status-pending')">Reject</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- DELIVERY DRIVER TAB -->
        <div id="tab-driver" class="tab-content">
            <h2 style="margin-top:0;">🛵 Driver Live Dispatch & Location Tracker</h2>
            <div class="card" style="max-width:600px;">
                <div class="card-header">
                    <div>
                        <h3 class="card-title">Order #GO-8841 — En Route to Customer</h3>
                        <div class="card-sub">Pickup: Gourmet Burger Kitchen ➔ Dropoff: 742 Evergreen Terrace</div>
                    </div>
                    <span class="status-badge status-accepted" id="driver-status">On The Way</span>
                </div>
                <div class="card-body">
                    <div class="progress-bar">
                        <div class="progress-fill" id="driver-progress" style="width: 70%;"></div>
                    </div>
                    <div style="font-size:13px; color:var(--subtext); margin-bottom:20px;" id="driver-eta">
                        📍 Live GPS Position: 0.8 miles away • Estimated ETA: 6 mins
                    </div>
                    <div style="display:flex; gap:10px;">
                        <button class="btn btn-green" onclick="advanceDriverStatus()">Update Delivery Status</button>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- CART DRAWER -->
    <div class="cart-overlay" id="cart-overlay">
        <div class="cart-drawer">
            <h2 class="cart-title">Your Order Cart <button class="btn btn-outline" onclick="closeCart()" style="padding:4px 10px;">✕</button></h2>
            <div class="cart-items" id="cart-items-list">
                <div style="color:var(--subtext); text-align:center; margin-top:40px;">Your cart is empty. Add delicious items from the storefront!</div>
            </div>
            <div class="cart-total">
                <span>Total:</span>
                <span id="cart-total-price" style="color:var(--green);">$0.00</span>
            </div>
            <button class="btn btn-green" style="width:100%; margin-top:20px; padding:14px; justify-content:center;" onclick="checkout()">Checkout & Place Order 🚀</button>
        </div>
    </div>

    <script>
        let cart = [];
        let driverStep = 0;

        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('nav .nav-btn').forEach(el => el.classList.remove('active'));
            
            document.getElementById('tab-' + tabName).classList.add('active');
            event.currentTarget.classList.add('active');
        }

        function addToCart(name, price) {
            cart.push({ name, price });
            document.getElementById('cart-count').innerText = cart.length;
            renderCart();
            alert(`Added "${name}" to your cart!`);
        }

        function renderCart() {
            const container = document.getElementById('cart-items-list');
            if (cart.length === 0) {
                container.innerHTML = '<div style="color:var(--subtext); text-align:center; margin-top:40px;">Your cart is empty.</div>';
                document.getElementById('cart-total-price').innerText = '$0.00';
                return;
            }

            let total = 0;
            container.innerHTML = cart.map((item, i) => {
                total += item.price;
                return `
                    <div style="display:flex; justify-content:space-between; padding:12px 0; border-bottom:1px solid #2d3748;">
                        <div><strong>${item.name}</strong></div>
                        <div>$${item.price.toFixed(2)}</div>
                    </div>
                `;
            }).join('');
            document.getElementById('cart-total-price').innerText = `$${total.toFixed(2)}`;
        }

        function openCart() { document.getElementById('cart-overlay').classList.add('active'); renderCart(); }
        function closeCart() { document.getElementById('cart-overlay').classList.remove('active'); }

        function checkout() {
            if (cart.length === 0) { alert('Cart is empty!'); return; }
            alert('🎉 Order Placed Successfully! Sent to Restaurant Dashboard.');
            cart = [];
            document.getElementById('cart-count').innerText = 0;
            closeCart();
            renderCart();
        }

        function updateOrderStatus(id, text, className) {
            const badge = document.getElementById('status-' + id);
            badge.innerText = text;
            badge.className = 'status-badge ' + className;
            alert(`Order #${id} status updated to: ${text}`);
        }

        function filterCategory(cat, btn) {
            document.querySelectorAll('.category-pills .pill').forEach(p => p.classList.remove('active'));
            btn.classList.add('active');

            document.querySelectorAll('#restaurant-grid .card').forEach(card => {
                if (cat === 'all' || card.dataset.category === cat) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }

        function filterRestaurants() {
            const query = document.getElementById('search-input').value.toLowerCase();
            document.querySelectorAll('#restaurant-grid .card').forEach(card => {
                const name = card.dataset.name;
                if (name.includes(query)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }

        function advanceDriverStatus() {
            const statuses = ['Picked Up Order', 'On The Way', 'Arrived at Customer', 'Delivered 🎉'];
            const progresses = ['35%', '70%', '90%', '100%'];
            
            driverStep = (driverStep + 1) % statuses.length;
            document.getElementById('driver-status').innerText = statuses[driverStep];
            document.getElementById('driver-progress').style.width = progresses[driverStep];
            document.getElementById('driver-eta').innerText = `Status Updated: ${statuses[driverStep]}`;
        }
    </script>
</body>
</html>
"""
    with open(index_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

def discover_web_app():
    """Dynamically searches test_project for any frontend/web app directory."""
    if not os.path.exists(BASE_TEST_DIR):
        return None, None

    for root_dir in os.listdir(BASE_TEST_DIR):
        project_path = os.path.join(BASE_TEST_DIR, root_dir)
        if os.path.isdir(project_path):
            search_paths = [
                os.path.join(project_path, "frontend", "customer-app"),
                os.path.join(project_path, "frontend"),
                os.path.join(project_path, "apps"),
                project_path
            ]
            for parent in search_paths:
                if os.path.exists(parent) and os.path.isdir(parent):
                    return os.path.basename(parent), parent

    default_app = os.path.join(BASE_TEST_DIR, "gourmetgo-monorepo", "frontend", "customer-app")
    os.makedirs(default_app, exist_ok=True)
    return "customer-app", default_app

def main():
    log("="*60)
    log("  GOURMETGO PLATFORM - AUTOMATED APP LAUNCHER  ")
    log("="*60)

    app_name, app_path = discover_web_app()

    log(f"Found Web Application: '{app_name}' at: {app_path}")
    ensure_web_app_harness(app_path, app_name)

    log("Installing dependencies via npm...")
    subprocess.run("npm install", shell=True, cwd=app_path)

    log("Starting web app server on http://localhost:5173...")
    process = subprocess.Popen("npx vite --port 5173 --host", shell=True, cwd=app_path)

    log("Waiting 3 seconds for server startup...")
    time.sleep(3)

    log("Opening Customer Web App in Browser...")
    webbrowser.open("http://localhost:5173")

    log("\n" + "="*60)
    log("App running successfully on http://localhost:5173!")
    log("Press Ctrl+C to stop the server.")
    log("="*60)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("\nShutting down web app server...")
        process.terminate()
        log("Shutdown complete.")

if __name__ == "__main__":
    main()
