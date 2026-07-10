"use strict";
// Dawrix PWA front-end — vanilla JS, talks to the stdlib JSON API.

const $ = (sel) => document.querySelector(sel);
const api = async (path, opts) => {
  const res = await fetch(path, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "حدث خطأ غير متوقع");
  return data;
};
const showMsg = (el, text, kind) => {
  el.textContent = text;
  el.className = "msg show " + (kind || "");
};
const clearMsg = (el) => { el.className = "msg"; el.textContent = ""; };
const fmtDate = (iso) => {
  const d = new Date(iso + "T00:00:00");
  return d.toLocaleDateString("ar-EG", { weekday: "long", day: "numeric", month: "long" });
};
const egp = (n) => n === 0 ? "مجانًا" : `${n} جنيه`;

// --- tab navigation ---
document.querySelectorAll("nav button").forEach((b) => {
  b.addEventListener("click", () => {
    document.querySelectorAll("nav button").forEach((x) => x.classList.remove("active"));
    document.querySelectorAll(".view").forEach((v) => v.classList.remove("active"));
    b.classList.add("active");
    $("#" + b.dataset.view).classList.add("active");
    if (b.dataset.view === "ops") loadOps();
  });
});

// --- populate selects ---
async function loadRefData() {
  try {
    const [areas, plans] = await Promise.all([api("/api/areas"), api("/api/plans")]);
    $("#s-area").innerHTML = areas.map((a) =>
      `<option value="${a.id}">${a.name_ar} — أيام الجمع: ${a.weekdays_ar.join("، ")}</option>`).join("");
    $("#s-plan").innerHTML = plans.map((p) =>
      `<option value="${p.id}">${p.name_ar} — ${p.price_egp} جنيه/شهر</option>`).join("");
  } catch (e) {
    showMsg($("#s-msg"), e.message, "err");
  }
}

// --- subscribe ---
$("#s-submit").addEventListener("click", async () => {
  clearMsg($("#s-msg"));
  $("#s-result").innerHTML = "";
  const btn = $("#s-submit");
  btn.disabled = true;
  try {
    const res = await api("/api/subscribe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: $("#s-name").value, phone: $("#s-phone").value,
        area_id: Number($("#s-area").value), plan_id: Number($("#s-plan").value),
      }),
    });
    showMsg($("#s-msg"), "تم الاشتراك بنجاح! الشهر الأول مجانًا.", "ok");
    const pickups = res.next_pickups.slice(0, 4).map((d) => `<li><span>${fmtDate(d)}</span><span class="pill scheduled">مجدول</span></li>`).join("");
    const bills = res.billing.map((b, i) => `<li><span>الشهر ${i + 1}</span><b>${egp(b.amount_egp)}</b></li>`).join("");
    $("#s-result").innerHTML = `
      <div class="card" style="margin-top:14px">
        <h2>${res.plan.name_ar}</h2>
        <p class="muted">مواعيد الجمع القادمة:</p>
        <ul class="clean">${pickups}</ul>
        <p class="muted" style="margin-top:14px">الفوترة:</p>
        <ul class="clean">${bills}</ul>
      </div>`;
    $("#s-name").value = ""; $("#s-phone").value = "";
  } catch (e) {
    showMsg($("#s-msg"), e.message, "err");
  } finally {
    btn.disabled = false;
  }
});

// --- my account ---
$("#a-load").addEventListener("click", async () => {
  clearMsg($("#a-msg"));
  $("#a-result").innerHTML = "";
  try {
    const res = await api("/api/me?phone=" + encodeURIComponent($("#a-phone").value.trim()));
    const s = res.subscription;
    const pickups = res.next_pickups.length
      ? res.next_pickups.map((d) => `<li><span>${fmtDate(d)}</span><span class="pill scheduled">مجدول</span></li>`).join("")
      : `<li class="muted">لا توجد مواعيد قادمة</li>`;
    $("#a-result").innerHTML = `
      <div class="card" style="margin-top:14px">
        <h2>أهلاً ${res.customer.name}</h2>
        ${s ? `<p>الباقة: <b>${s.plan_name}</b> — ${s.price_egp} جنيه/شهر · الحالة:
          <span class="pill ${s.status === "active" ? "done" : "scheduled"}">${s.status === "active" ? "نشط" : s.status}</span></p>` : "<p class='muted'>لا يوجد اشتراك</p>"}
        <p class="muted">مواعيد الجمع القادمة:</p>
        <ul class="clean">${pickups}</ul>
      </div>`;
  } catch (e) {
    showMsg($("#a-msg"), e.message, "err");
  }
});

// --- ops dashboard ---
async function loadOps() {
  clearMsg($("#o-msg"));
  if (!$("#o-date").value) $("#o-date").value = new Date().toISOString().slice(0, 10);
  try {
    const stats = await api("/api/stats");
    $("#o-stats").innerHTML = `
      <div class="stat"><b>${stats.active_subscriptions}</b><span>اشتراكات نشطة</span></div>
      <div class="stat"><b>${stats.collections_today}</b><span>عمليات جمع اليوم</span></div>
      <div class="stat"><b>${stats.done_today}</b><span>تم إتمامها اليوم</span></div>
      <div class="stat"><b>${stats.mrr_egp}</b><span>إيراد شهري متكرر (جنيه)</span></div>`;
    await loadCollections();
  } catch (e) {
    showMsg($("#o-msg"), e.message, "err");
  }
}

async function loadCollections() {
  const date = $("#o-date").value;
  const rows = await api("/api/collections?date=" + date);
  if (!rows.length) {
    $("#o-list").innerHTML = `<p class="muted">لا توجد عمليات جمع في هذا اليوم.</p>`;
    return;
  }
  $("#o-list").innerHTML = `
    <table>
      <thead><tr><th>العميل</th><th>المنطقة</th><th>الهاتف</th><th>الحالة</th><th></th></tr></thead>
      <tbody>${rows.map((r) => `
        <tr>
          <td>${r.customer}</td><td>${r.area}</td><td>${r.phone}</td>
          <td><span class="pill ${r.status}">${r.status === "done" ? "تم" : r.status === "missed" ? "فائت" : "مجدول"}</span></td>
          <td>${r.status === "scheduled" ? `<button class="btn sm" data-done="${r.id}">تم الجمع</button>` : ""}</td>
        </tr>`).join("")}</tbody>
    </table>`;
  document.querySelectorAll("[data-done]").forEach((b) => {
    b.addEventListener("click", async () => {
      b.disabled = true;
      try { await api(`/api/collections/${b.dataset.done}/done`, { method: "POST" }); await loadOps(); }
      catch (e) { showMsg($("#o-msg"), e.message, "err"); b.disabled = false; }
    });
  });
}
$("#o-load").addEventListener("click", loadOps);

// --- boot ---
loadRefData();
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js").catch(() => {});
}
