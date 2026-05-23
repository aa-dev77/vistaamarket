// Vista Market - Asosiy JavaScript
var products = [];
var cart = JSON.parse(localStorage.getItem("vm_cart") || "[]");
var favs = JSON.parse(localStorage.getItem("vm_fav") || "[]");
var userProfile = JSON.parse(localStorage.getItem("vm_profile") || "{}");
var curView = "products";
var curCat = "all";
var selProd = null;
var dq = 1;
var prevView = "products";
var currentBanner = 0;
var bannerInterval = null;
var banners = [];

// Kategoriyalar
var categories = [
  { id: "all", name: "Barchasi" },
  { id: "parfum", name: "Parfyumeriya" },
  { id: "cosmetics", name: "Kosmetika" },
  { id: "dishes", name: "Idish-tovoq" },
  { id: "clothes", name: "Kiyim" },
  { id: "powders", name: "Kukunlar" },
  { id: "electronics", name: "Elektronika" },
  { id: "toys", name: "O'yinchoqlar" },
];

// Telegram WebApp
if (window.Telegram && window.Telegram.WebApp) {
  var tg = window.Telegram.WebApp;
  tg.ready();
  tg.expand();
}

document.addEventListener("DOMContentLoaded", function () {
  loadBanners();
  renderCategories();
  loadProducts();
  updateBadge();
});

// ==================== BANNER ====================
async function loadBanners() {
  try {
    var r = await fetch("/api/banners");
    var d = await r.json();
    if (d.success && d.banners && d.banners.length > 0) {
      banners = d.banners.filter(function (b) {
        return b.active === true;
      });
      if (banners.length > 0) renderBanner();
    }
  } catch (e) {
    console.log("Banner yuklanmadi");
  }
}

function renderBanner() {
  var section = document.getElementById("bannerSection");
  var track = document.getElementById("bannerTrack");
  var dots = document.getElementById("bannerDots");
  if (!section || !track || !dots || banners.length === 0) return;

  section.style.display = "block";
  track.innerHTML = "";
  dots.innerHTML = "";

  for (var i = 0; i < banners.length; i++) {
    var b = banners[i];
    var slide = document.createElement("div");
    slide.className = "banner-slide";
    slide.onclick = (function (link) {
      return function () {
        if (link && link !== "/") window.location.href = link;
      };
    })(b.link);
    slide.innerHTML =
      '<img src="' +
      b.image +
      '" onerror="this.src=\'https://placehold.co/800x300?text=Vista\'">' +
      '<div class="banner-overlay">' +
      "<h3>" +
      (b.title || "") +
      "</h3>" +
      "<p>" +
      (b.subtitle || "") +
      "</p>" +
      "</div>";
    track.appendChild(slide);

    var dot = document.createElement("div");
    dot.className = "banner-dot" + (i === 0 ? " active" : "");
    dot.onclick = (function (idx) {
      return function () {
        goToBanner(idx);
      };
    })(i);
    dots.appendChild(dot);
  }

  if (banners.length > 1) {
    bannerInterval = setInterval(function () {
      goToBanner((currentBanner + 1) % banners.length);
    }, 5000);
  }
}

function goToBanner(index) {
  var track = document.getElementById("bannerTrack");
  var dots = document.querySelectorAll(".banner-dot");
  if (!track) return;
  currentBanner = index;
  track.style.transform = "translateX(-" + currentBanner * 100 + "%)";
  for (var i = 0; i < dots.length; i++) {
    dots[i].classList.toggle("active", i === currentBanner);
  }
}

// ==================== KATEGORIYALAR ====================
function renderCategories() {
  var container = document.getElementById("categoriesList");
  if (!container) return;
  var html = "";
  for (var i = 0; i < categories.length; i++) {
    html +=
      '<button class="cat' +
      (curCat === categories[i].id ? " active" : "") +
      '" onclick="filterCat(\'' +
      categories[i].id +
      "', this)\">" +
      categories[i].name +
      "</button>";
  }
  container.innerHTML = html;
}

// ==================== MAHSULOTLAR ====================
async function loadProducts() {
  var grid = document.getElementById("productsGrid");
  if (!grid) return;
  grid.innerHTML =
    '<div style="text-align:center;padding:40px;"><i class="fa-solid fa-spinner fa-pulse fa-2x" style="color:#00A86B;"></i><p style="margin-top:10px;">Yuklanmoqda...</p></div>';

  try {
    var url =
      curCat === "all" ? "/api/products" : "/api/products?category=" + curCat;
    var r = await fetch(url);
    var d = await r.json();
    if (d.success) {
      products = d.products;
      renderProducts();
    }
  } catch (e) {
    grid.innerHTML =
      '<div style="text-align:center;padding:40px;color:red;"><i class="fa-solid fa-circle-exclamation"></i><p>Xatolik yuz berdi</p></div>';
  }
}

function renderProducts() {
  var grid = document.getElementById("productsGrid");
  if (!grid) return;
  if (products.length === 0) {
    grid.innerHTML =
      '<div style="text-align:center;padding:40px;color:#94A3B8;">Mahsulotlar topilmadi</div>';
    return;
  }

  var html = "";
  for (var i = 0; i < products.length; i++) {
    var p = products[i];
    var inCartFlag = cart.some(function (c) {
      return c.id === p.id;
    });
    var qty = getQty(p.id);
    var isFav = favs.includes(p.id);

    html += '<div class="card" onclick="openDetail(\'' + p.id + "')\">";
    if (p.discount > 0)
      html += '<span class="disc">-' + p.discount + "%</span>";
    html +=
      '<button class="fav ' +
      (isFav ? "act" : "") +
      '" onclick="event.stopPropagation();toggleFav(\'' +
      p.id +
      "')\">" +
      '<i class="fa-' +
      (isFav ? "solid" : "regular") +
      ' fa-heart"></i></button>';
    html +=
      '<img src="' +
      p.image +
      '" onerror="this.src=\'https://placehold.co/400\'">';
    html += '<div class="info">';
    html += '<div class="name">' + p.name + "</div>";
    html +=
      '<div class="price-block"><span class="price">' +
      fmt(p.price) +
      " so'm</span>";
    if (p.old_price > p.price)
      html += '<span class="old">' + fmt(p.old_price) + " so'm</span>";
    html += "</div>";

    if (inCartFlag) {
      html += '<div class="qty-ctrl" onclick="event.stopPropagation()">';
      html += "<button onclick=\"chgCart('" + p.id + "',-1)\">-</button>";
      html += "<span>" + qty + "</span>";
      html += "<button onclick=\"chgCart('" + p.id + "',1)\">+</button>";
      html += "</div>";
    } else {
      html +=
        '<button class="buy-btn" onclick="event.stopPropagation();addCart(\'' +
        p.id +
        '\')"><i class="fa-solid fa-cart-plus"></i> Savatga</button>';
    }
    html += "</div></div>";
  }
  grid.innerHTML = html;
}

function getQty(id) {
  var item = cart.find(function (x) {
    return x.id === id;
  });
  return item ? item.quantity : 0;
}

// ==================== DETAIL ====================
function openDetail(id) {
  selProd = products.find(function (p) {
    return p.id === id;
  });
  if (!selProd) return;
  dq = 1;
  document.getElementById("dImg").src = selProd.image;
  document.getElementById("dName").textContent = selProd.name;
  document.getElementById("dDesc").textContent =
    selProd.description || "Sifatli mahsulot";
  document.getElementById("dPrice").textContent = fmt(selProd.price) + " so'm";
  var oldEl = document.getElementById("dOld");
  if (selProd.old_price > selProd.price) {
    oldEl.textContent = fmt(selProd.old_price) + " so'm";
    oldEl.style.display = "block";
  } else {
    oldEl.style.display = "none";
  }
  document.getElementById("dStock").textContent = selProd.in_stock + " dona";
  document.getElementById("dQty").textContent = dq;
  var disc = document.getElementById("dDisc");
  if (selProd.discount > 0) {
    disc.textContent = "-" + selProd.discount + "%";
    disc.style.display = "inline-block";
  } else {
    disc.style.display = "none";
  }
  updateDTotal();
  prevView = curView;
  showView("detail");
}

function dQty(c) {
  dq = Math.max(1, dq + c);
  document.getElementById("dQty").textContent = dq;
  updateDTotal();
}

function updateDTotal() {
  document.getElementById("dTotal").textContent =
    fmt(selProd.price * dq) + " so'm";
}

function addFromDetail() {
  addCart(selProd.id, dq);
  toast("Savatga qo'shildi");
  goBack();
}

// ==================== SAVAT ====================
function addCart(id, q) {
  q = q || 1;
  var ex = cart.find(function (i) {
    return i.id === id;
  });
  if (ex) {
    ex.quantity += q;
  } else {
    var p = products.find(function (i) {
      return i.id === id;
    });
    if (p) cart.push({ ...p, quantity: q });
  }
  saveCart();
  updateBadge();
  renderProducts();
}

function chgCart(id, c) {
  var it = cart.find(function (i) {
    return i.id === id;
  });
  if (it) {
    it.quantity += c;
    if (it.quantity <= 0)
      cart = cart.filter(function (i) {
        return i.id !== id;
      });
  }
  saveCart();
  updateBadge();
  renderProducts();
  if (curView === "cart") renderCart();
}

function clearCart() {
  if (confirm("Savatni tozalansinmi?")) {
    cart = [];
    saveCart();
    updateBadge();
    renderProducts();
    renderCart();
    toast("Savat tozalandi");
  }
}

function saveCart() {
  localStorage.setItem("vm_cart", JSON.stringify(cart));
}

function updateBadge() {
  var total = cart.reduce(function (s, i) {
    return s + i.quantity;
  }, 0);
  var b = document.getElementById("cartBadge");
  if (b) {
    b.textContent = total;
    b.style.display = total > 0 ? "flex" : "none";
  }
}

function renderCart() {
  var list = document.getElementById("cartList");
  var empty = document.getElementById("emptyCart");
  var bottom = document.getElementById("cartBottom");
  if (!list || !empty || !bottom) return;

  if (cart.length === 0) {
    list.innerHTML = "";
    empty.style.display = "block";
    bottom.style.display = "none";
    return;
  }
  empty.style.display = "none";
  bottom.style.display = "block";

  list.innerHTML = cart
    .map(function (i) {
      return (
        '<div class="cart-item">' +
        '<img src="' +
        i.image +
        '" onerror="this.src=\'https://placehold.co/60\'">' +
        '<div class="cart-info">' +
        '<div class="cart-name">' +
        i.name +
        "</div>" +
        '<div class="cart-price">' +
        fmt(i.price) +
        " so'm</div>" +
        "</div>" +
        '<div class="cart-qty">' +
        "<button onclick=\"chgCart('" +
        i.id +
        "',-1)\">-</button>" +
        "<span>" +
        i.quantity +
        "</span>" +
        "<button onclick=\"chgCart('" +
        i.id +
        "',1)\">+</button>" +
        "</div>" +
        '<i class="fa-solid fa-trash-can rm-btn" onclick="rmCart(\'' +
        i.id +
        "')\"></i>" +
        "</div>"
      );
    })
    .join("");

  var total = cart.reduce(function (s, i) {
    return s + i.price * i.quantity;
  }, 0);
  document.getElementById("cartTotal").textContent = fmt(total) + " so'm";
}

function rmCart(id) {
  cart = cart.filter(function (i) {
    return i.id !== id;
  });
  saveCart();
  updateBadge();
  renderProducts();
  renderCart();
}

// ==================== BUYURTMA ====================
function openCheckout() {
  if (userProfile.phone) {
    document.getElementById("cPhone").value = userProfile.phone;
  }
  if (userProfile.name) {
    document.getElementById("cName").value = userProfile.name;
  }

  var itemsHtml = "";
  var total = 0;
  for (var i = 0; i < cart.length; i++) {
    var subtotal = cart[i].price * cart[i].quantity;
    total += subtotal;
    itemsHtml +=
      '<div style="display:flex;justify-content:space-between;margin-bottom:8px;font-size:13px;">' +
      "<span>" +
      cart[i].name +
      ' <span style="color:#94A3B8;">x' +
      cart[i].quantity +
      "</span></span>" +
      '<span style="font-weight:600;color:#00A86B;">' +
      fmt(subtotal) +
      " so'm</span>" +
      "</div>";
  }
  document.getElementById("checkoutItems").innerHTML = itemsHtml;
  document.getElementById("checkoutTotal").textContent = fmt(total) + " so'm";
  prevView = "cart";
  showView("checkout");
}

async function submitOrder(e) {
  e.preventDefault();
  var name = document.getElementById("cName").value.trim();
  var phone = document.getElementById("cPhone").value.trim();
  var address = document.getElementById("cAddr").textContent.trim();

  if (!name || !phone) {
    toast("Ism va telefon majburiy!", "e");
    return;
  }
  if (cart.length === 0) {
    toast("Savat bo'sh!", "e");
    return;
  }
  if (address === "Manzilni tanlang" || !address) {
    toast("Manzilni tanlang!", "e");
    return;
  }

  var total = cart.reduce(function (s, i) {
    return s + i.price * i.quantity;
  }, 0);

  try {
    var r = await fetch("/api/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: name,
        phone: phone,
        address: address,
        items: cart.map(function (i) {
          return {
            id: i.id,
            name: i.name,
            quantity: i.quantity,
            price: i.price,
          };
        }),
      }),
    });
    var d = await r.json();
    if (d.success) {
      var orders = JSON.parse(localStorage.getItem("vm_orders") || "[]");
      orders.unshift({
        order_id: d.order.order_id,
        status: "pending",
        status_text: "Tayyorlanmoqda",
        items: cart.map(function (i) {
          return { name: i.name, quantity: i.quantity };
        }),
        total: total,
        created_at: new Date().toISOString(),
      });
      localStorage.setItem("vm_orders", JSON.stringify(orders));

      cart = [];
      saveCart();
      updateBadge();
      renderProducts();
      toast("Buyurtma #" + d.order.order_id + " qabul qilindi!");
      showView("products");
    }
  } catch (er) {
    toast("Server xatosi", "e");
  }
}

// ==================== SEVIMLILAR ====================
function toggleFav(id) {
  var idx = favs.indexOf(id);
  if (idx > -1) {
    favs.splice(idx, 1);
    toast("Sevimlilardan olib tashlandi");
  } else {
    favs.push(id);
    toast("Sevimlilarga qo'shildi");
  }
  localStorage.setItem("vm_fav", JSON.stringify(favs));
  renderProducts();
  if (curView === "favorites") renderFavs();
}

function renderFavs() {
  var fp = products.filter(function (p) {
    return favs.includes(p.id);
  });
  var g = document.getElementById("favGrid");
  var e = document.getElementById("emptyFav");
  if (!g || !e) return;

  if (fp.length === 0) {
    g.innerHTML = "";
    e.style.display = "block";
    return;
  }
  e.style.display = "none";
  g.innerHTML = fp
    .map(function (p) {
      return (
        '<div class="card" onclick="openDetail(\'' +
        p.id +
        "')\">" +
        '<button class="fav act" onclick="event.stopPropagation();toggleFav(\'' +
        p.id +
        '\')"><i class="fa-solid fa-heart"></i></button>' +
        '<img src="' +
        p.image +
        '" onerror="this.src=\'https://placehold.co/400\'">' +
        '<div class="info">' +
        '<div class="name">' +
        p.name +
        "</div>" +
        '<div class="price-block"><span class="price">' +
        fmt(p.price) +
        " so'm</span></div>" +
        "</div></div>"
      );
    })
    .join("");
}

// ==================== PROFIL ====================
function loadProfile() {
  var name = userProfile.name || "Foydalanuvchi";
  var phone = userProfile.phone || "";

  document.getElementById("profileName").textContent = name;
  if (phone) {
    document.getElementById("profilePhone").innerHTML =
      '<i class="fa-solid fa-phone"></i> ' + phone;
  } else {
    document.getElementById("profilePhone").innerHTML =
      '<i class="fa-solid fa-phone"></i> Telefon qo\'shilmagan';
  }

  document.getElementById("editName").value = userProfile.name || "";
  document.getElementById("editPhone").value = userProfile.phone || "";

  loadProfileOrders();
  checkAdminAccess();
}

async function checkAdminAccess() {
  try {
    var r = await fetch("/api/admin/check");
    var d = await r.json();
    if (d.is_admin) {
      document.getElementById("adminSection").style.display = "block";
    }
  } catch (e) {}
}

function openEditProfileModal() {
  document.getElementById("editProfileModal").style.display = "flex";
}

function saveProfile() {
  var name = document.getElementById("editName").value.trim();
  var phone = document.getElementById("editPhone").value.trim();

  userProfile = {
    name: name || "Foydalanuvchi",
    phone: phone || "",
  };

  localStorage.setItem("vm_profile", JSON.stringify(userProfile));

  document.getElementById("profileName").textContent = userProfile.name;
  if (userProfile.phone) {
    document.getElementById("profilePhone").innerHTML =
      '<i class="fa-solid fa-phone"></i> ' + userProfile.phone;
  } else {
    document.getElementById("profilePhone").innerHTML =
      '<i class="fa-solid fa-phone"></i> Telefon qo\'shilmagan';
  }

  closeModal("editProfileModal");
  toast("Profil saqlandi!");
}

function loadProfileOrders() {
  var container = document.getElementById("profileOrders");
  if (!container) return;

  var orders = JSON.parse(localStorage.getItem("vm_orders") || "[]");

  if (orders.length === 0) {
    container.innerHTML =
      '<div style="text-align:center;padding:30px;color:#94A3B8;">' +
      '<i class="fa-solid fa-receipt fa-2x"></i>' +
      '<p style="margin-top:10px;">Buyurtmalar yo\'q</p>' +
      '<button onclick="showView(\'products\')" style="margin-top:10px;padding:8px 20px;background:#00A86B;color:#fff;border:none;border-radius:30px;cursor:pointer;">Xarid qilish</button>' +
      "</div>";
    return;
  }

  var html = "";
  for (var i = 0; i < orders.length; i++) {
    var o = orders[i];
    var statusClass = "";
    var statusText = "";

    if (o.status === "pending") {
      statusClass = "status-pending";
      statusText = "Tayyorlanmoqda";
    } else if (o.status === "confirmed") {
      statusClass = "status-confirmed";
      statusText = "Yo'lda";
    } else if (o.status === "delivered") {
      statusClass = "status-delivered";
      statusText = "Yetkazilgan";
    } else if (o.status === "cancelled") {
      statusClass = "status-cancelled";
      statusText = "Bekor qilingan";
    } else {
      statusClass = "status-pending";
      statusText = o.status_text || "Tayyorlanmoqda";
    }

    var date = "";
    if (o.created_at) {
      var d = new Date(o.created_at);
      date = d.getDate() + "." + (d.getMonth() + 1) + "." + d.getFullYear();
    }

    html +=
      '<div class="order-card">' +
      '<div class="order-header">' +
      '<span class="order-id"><i class="fa-solid fa-hashtag"></i> ' +
      o.order_id +
      "</span>" +
      '<span class="order-status ' +
      statusClass +
      '">' +
      statusText +
      "</span>" +
      "</div>" +
      '<div class="order-items">' +
      (o.items
        ? o.items
            .map(function (item) {
              return item.name + " x" + item.quantity;
            })
            .join(", ")
        : "") +
      "</div>" +
      '<div class="order-total">' +
      "<span>" +
      date +
      "</span>" +
      "<strong>" +
      fmt(o.total) +
      " so'm</strong>" +
      "</div>" +
      "</div>";
  }
  container.innerHTML = html;
}

function logout() {
  if (confirm("Chiqishni tasdiqlaysizmi?\nBarcha ma'lumotlar saqlanadi.")) {
    localStorage.clear();
    window.location.reload();
  }
}

// ==================== MANZIL ====================
function openAddressModal() {
  document.getElementById("addressModal").style.display = "flex";
}

function closeModal(id) {
  document.getElementById(id).style.display = "none";
}

function getGPS() {
  if (!navigator.geolocation) {
    toast("GPS qo'llab-quvvatlanmaydi", "e");
    return;
  }
  toast("Manzil aniqlanmoqda...", "s");
  navigator.geolocation.getCurrentPosition(
    async function (pos) {
      try {
        var r = await fetch(
          "https://nominatim.openstreetmap.org/reverse?lat=" +
            pos.coords.latitude +
            "&lon=" +
            pos.coords.longitude +
            "&format=json&accept-language=uz",
        );
        var d = await r.json();
        var addr =
          d.display_name ||
          pos.coords.latitude.toFixed(4) +
            ", " +
            pos.coords.longitude.toFixed(4);
        document.getElementById("cAddr").textContent = addr.substring(0, 100);
        document.getElementById("addressInput").value = addr;
      } catch (er) {
        var addr =
          pos.coords.latitude.toFixed(4) +
          ", " +
          pos.coords.longitude.toFixed(4);
        document.getElementById("cAddr").textContent = addr;
        document.getElementById("addressInput").value = addr;
      }
      closeModal("addressModal");
      toast("Manzil aniqlandi");
    },
    function () {
      toast("GPS aniqlanmadi", "e");
    },
  );
}

function saveAddress() {
  var addr = document.getElementById("addressInput").value.trim();
  if (addr) {
    document.getElementById("cAddr").textContent = addr;
    closeModal("addressModal");
    toast("Manzil saqlandi");
  } else {
    toast("Manzil kiriting", "e");
  }
}

// ==================== NAVIGATION - HEADER FAQAT PRODUCTS SAHIFASIDA ====================
function showView(v) {
    // 1. Barcha sahifalarni yashirish
    var pages = ['page-products', 'page-detail', 'page-cart', 'page-checkout', 'page-favorites', 'page-profile'];
    for (var i = 0; i < pages.length; i++) {
        var el = document.getElementById(pages[i]);
        if (el) el.classList.remove('active');
    }
    
    // 2. HEADER: faqat products sahifasida block, boshqalarida none
    var header = document.getElementById('header');
    if (header) {
        if (v === 'products') {
            header.style.display = 'block';   // Products da ko'rinadi
        } else {
            header.style.display = 'none';    // Boshqa hamma sahifalarda yo'qoladi
        }
    }
    
    // 3. Bottom nav: faqat checkout da yashirinadi
    var nav = document.querySelector('.bottom-nav');
    if (nav) {
        if (v === 'checkout') {
            nav.style.display = 'none';
        } else {
            nav.style.display = 'flex';
        }
    }
    
    // 4. Sahifani ko'rsatish
    var target = document.getElementById('page-' + v);
    if (target) target.classList.add('active');
    curView = v;
    
    // 5. Sahifaga mos funksiyalar
    if (v === 'cart') renderCart();
    if (v === 'favorites') renderFavs();
    if (v === 'profile') loadProfile();
    if (v === 'products') renderProducts();
    
    // 6. Bottom nav tugmalarini active qilish
    document.querySelectorAll('.nav-btn').forEach(function(b) {
        b.classList.remove('active');
    });
    var btn = document.querySelector('[data-nav="' + v + '"]');
    if (btn) btn.classList.add('active');
}

function goBack() {
  showView(prevView);
}

function filterCat(cat, btn) {
  curCat = cat;
  document.querySelectorAll(".cat").forEach(function (b) {
    b.classList.remove("active");
  });
  if (btn) btn.classList.add("active");
  loadProducts();
}

// ==================== TOAST ====================
function toast(msg, type) {
  type = type || "s";
  var el = document.createElement("div");
  el.className = "toast" + (type === "e" ? " toast-e" : "");
  el.innerHTML =
    '<i class="fa-solid fa-' +
    (type === "s" ? "check-circle" : "exclamation-circle") +
    '"></i> ' +
    msg;
  document.body.appendChild(el);
  setTimeout(function () {
    el.style.opacity = "0";
    setTimeout(function () {
      el.remove();
    }, 300);
  }, 2500);
}

// ==================== FORMAT ====================
function fmt(p) {
  return p ? p.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ") : "0";
}
