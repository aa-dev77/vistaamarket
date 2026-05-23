// Admin Panel JavaScript
let adminProducts = [];
let adminOrders = [];

// Check login
async function checkAuth() {
  try {
    const res = await fetch("/api/admin/check");
    const data = await res.json();
    if (data.is_admin) {
      showDashboard();
      loadAllData();
    }
  } catch (err) {}
}

// Admin Login
async function adminLogin(event) {
  event.preventDefault();
  const password = document.getElementById("adminPassword").value;

  try {
    const res = await fetch("/api/admin/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    });

    const data = await res.json();
    if (data.success) {
      showDashboard();
      loadAllData();
    } else {
      alert("Noto'g'ri parol!");
    }
  } catch (err) {
    alert("Serverga ulanishda xatolik!");
  }
}

// Logout
async function adminLogout() {
  await fetch("/api/admin/logout", { method: "POST" });
  window.location.reload();
}

// Show Dashboard
function showDashboard() {
  document.getElementById("loginScreen").style.display = "none";
  document.getElementById("dashboard").style.display = "flex";
}

// Tab Management
function showTab(tabName) {
  document
    .querySelectorAll(".tab-panel")
    .forEach((el) => (el.style.display = "none"));
  document
    .querySelectorAll(".sidebar-btn")
    .forEach((b) => b.classList.remove("active"));

  const tab = document.getElementById(tabName + "Tab");
  if (tab) tab.style.display = "block";

  const btn = document.querySelector(`[data-tab="${tabName}"]`);
  if (btn) btn.classList.add("active");

  document.getElementById("currentTabTitle").textContent = btn
    ? btn.querySelector("span").textContent
    : tabName;

  if (tabName === "products") loadProducts();
  if (tabName === "orders") loadOrders();
}

// Load all data
async function loadAllData() {
  await loadProducts();
  await loadOrders();
}

// Load Products
async function loadProducts() {
  try {
    const res = await fetch("/api/products");
    const data = await res.json();
    if (data.success) {
      adminProducts = data.products;
      renderProducts();
      updateStats();
    }
  } catch (err) {
    console.error(err);
  }
}

// Render Products
function renderProducts(filter = "") {
  const container = document.getElementById("adminProductsList");
  const filtered = filter
    ? adminProducts.filter((p) =>
        p.name.toLowerCase().includes(filter.toLowerCase()),
      )
    : adminProducts;

  container.innerHTML = `
        <div class="table-row table-header">
            <span>Rasm</span>
            <span>Nomi</span>
            <span>Narx</span>
            <span>Soni</span>
            <span>Harakat</span>
        </div>
        ${filtered
          .map(
            (p) => `
            <div class="table-row">
                <img src="${p.image}" alt="" onerror="this.src='https://placehold.co/60'">
                <div>
                    <strong>${p.name}</strong>
                    <small style="display:block;color:var(--gray-600);">${p.category}</small>
                </div>
                <div>
                    <strong style="color:var(--primary);">${formatPrice(p.price)} so'm</strong>
                    ${p.old_price > p.price ? `<br><small style="text-decoration:line-through;">${formatPrice(p.old_price)}</small>` : ""}
                </div>
                <span style="padding:4px 8px;border-radius:50px;font-size:12px;background:${p.in_stock > 5 ? "var(--primary-light)" : "#FEE2E2"};color:${p.in_stock > 5 ? "var(--primary)" : "var(--red)"};">${p.in_stock} dona</span>
                <button onclick="deleteProduct('${p.id}')" style="background:var(--red);color:white;border:none;padding:6px 12px;border-radius:4px;cursor:pointer;">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </div>
        `,
          )
          .join("")}
    `;
}

// Filter products
function filterAdminProducts() {
  const search = document.getElementById("productSearch").value;
  renderProducts(search);
}

// Add Product
async function addProduct(event) {
  event.preventDefault();

  const productData = {
    name: document.getElementById("newName").value,
    category: document.getElementById("newCategory").value,
    price: document.getElementById("newPrice").value,
    old_price:
      document.getElementById("newOldPrice").value ||
      document.getElementById("newPrice").value,
    in_stock: document.getElementById("newStock").value,
    discount: document.getElementById("newDiscount").value || 0,
    image:
      document.getElementById("newImage").value ||
      "https://placehold.co/400x400?text=Product",
    description: document.getElementById("newDescription").value,
  };

  try {
    const res = await fetch("/api/admin/products", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(productData),
    });

    const data = await res.json();
    if (data.success) {
      alert("Mahsulot qo'shildi!");
      event.target.reset();
      loadProducts();
      showTab("products");
    } else {
      alert("Xatolik: " + data.message);
    }
  } catch (err) {
    alert("Serverda xatolik!");
  }
}

// Delete Product
async function deleteProduct(productId) {
  if (!confirm("O'chirishni tasdiqlaysizmi?")) return;

  try {
    const res = await fetch("/api/admin/products", {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: productId }),
    });

    const data = await res.json();
    if (data.success) {
      alert("O'chirildi!");
      loadProducts();
    }
  } catch (err) {
    alert("Xatolik!");
  }
}

// Load Orders
async function loadOrders() {
  try {
    const res = await fetch("/api/orders");
    const data = await res.json();
    if (data.success) {
      adminOrders = data.orders;
      renderOrders();
      updateOrderStats();
    }
  } catch (err) {
    console.error(err);
  }
}

// Render Orders
function renderOrders() {
  const container = document.getElementById("adminOrdersList");

  container.innerHTML = adminOrders
    .map(
      (order) => `
        <div class="order-card">
            <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
                <strong style="color:var(--primary);">#${order.order_id}</strong>
                <span style="padding:4px 12px;border-radius:50px;font-size:12px;font-weight:600;
                    background:${order.status === "pending" ? "#FEF3C7" : order.status === "delivered" ? "#D1FAE5" : "#DBEAFE"};
                    color:${order.status === "pending" ? "#F59E0B" : order.status === "delivered" ? "#10B981" : "#2563EB"};">
                    ${order.status_text || order.status}
                </span>
            </div>
            <div style="margin-bottom:8px;"><strong>${order.customer_name}</strong> | ${order.phone}</div>
            <div style="color:var(--gray-600);font-size:13px;margin-bottom:8px;">
                ${order.items?.map((i) => `${i.name || "Mahsulot"} ×${i.quantity || 1}`).join(", ") || ""}
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <strong style="font-size:18px;color:var(--primary);">${formatPrice(order.total)} so'm</strong>
                <select onchange="updateOrderStatus('${order.order_id}', this.value)" 
                    style="padding:8px;border-radius:6px;border:2px solid var(--gray-200);font-size:13px;">
                    <option value="pending" ${order.status === "pending" ? "selected" : ""}>Tayyorlanmoqda</option>
                    <option value="confirmed" ${order.status === "confirmed" ? "selected" : ""}>Yo'lda</option>
                    <option value="delivered" ${order.status === "delivered" ? "selected" : ""}>Yetkazilgan</option>
                    <option value="cancelled" ${order.status === "cancelled" ? "selected" : ""}>Bekor qilingan</option>
                </select>
            </div>
        </div>
    `,
    )
    .join("");
}

// Update Order Status
async function updateOrderStatus(orderId, status) {
  try {
    await fetch(`/api/admin/orders/${orderId}/status`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
    });
    loadOrders();
    alert("Status yangilandi!");
  } catch (err) {
    alert("Xatolik!");
  }
}

// Update Stats
function updateStats() {
  document.getElementById("totalProducts").textContent = adminProducts.length;
  const categories = new Set(adminProducts.map((p) => p.category));
  document.getElementById("totalCategories").textContent = categories.size;
}

// Update Order Stats
function updateOrderStats() {
  document.getElementById("pendingOrders").textContent = adminOrders.filter(
    (o) => o.status === "pending",
  ).length;
  document.getElementById("completedOrders").textContent = adminOrders.filter(
    (o) => o.status === "delivered",
  ).length;
  document.getElementById("orderCount").textContent = adminOrders.filter(
    (o) => o.status === "pending",
  ).length;

  const total = adminOrders.reduce((sum, o) => sum + (o.total || 0), 0);
  document.getElementById("totalRevenue").textContent =
    formatPrice(total) + " so'm";
}

// Refresh current tab
function refreshCurrentTab() {
  const activeTab = document.querySelector('.tab-panel[style*="block"]')?.id;
  if (activeTab === "productsTab") loadProducts();
  else if (activeTab === "ordersTab") loadOrders();
}

// Helpers
function formatPrice(price) {
  return price?.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ") || "0";
}

// Initialize
checkAuth();
