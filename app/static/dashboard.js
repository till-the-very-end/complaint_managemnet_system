const rows = document.getElementById("rows");
const filter = document.getElementById("filter");
const errBox = document.getElementById("dash-error");
const STATUSES = ["Pending", "In Progress", "Resolved"];

function esc(s) {
  const d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

async function load() {
  errBox.hidden = true;
  const q = filter.value ? "?status=" + encodeURIComponent(filter.value) : "";
  try {
    const res = await fetch("/api/complaints" + q);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to load.");

    document.getElementById("count-pending").textContent = data.counts["Pending"];
    document.getElementById("count-progress").textContent = data.counts["In Progress"];
    document.getElementById("count-resolved").textContent = data.counts["Resolved"];

    rows.innerHTML = data.complaints.length ? "" : '<tr><td colspan="7">No complaints found.</td></tr>';
    data.complaints.forEach((c) => {
      const options = STATUSES.map(
        (s) => `<option value="${s}" ${s === c.status ? "selected" : ""}>${s}</option>`
      ).join("");
      rows.insertAdjacentHTML("beforeend",
        `<tr><td>${esc(c.complaint_id)}</td><td>${esc(c.name)}</td><td>${esc(c.category)}</td>` +
        `<td><span class="badge ${esc(c.priority)}">${esc(c.priority)}</span></td>` +
        `<td>${esc(c.assigned_to || "-")}</td>` +
        `<td><select data-id="${esc(c.complaint_id)}">${options}</select></td>` +
        `<td>${esc(c.created_at)}</td></tr>`);
    });
  } catch (err) {
    errBox.hidden = false;
    errBox.textContent = err.message || "Network error.";
  }
}

rows.addEventListener("change", async (e) => {
  if (e.target.tagName !== "SELECT") return;
  try {
    const res = await fetch(`/api/complaints/${e.target.dataset.id}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: e.target.value }),
    });
    if (!res.ok) throw new Error((await res.json()).error);
  } catch (err) {
    errBox.hidden = false;
    errBox.textContent = "Could not update status: " + err.message;
    return;
  }
  load();
});

filter.addEventListener("change", load);
load();
