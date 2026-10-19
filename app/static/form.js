// Client-side validation + submission with error handling.
const form = document.getElementById("complaint-form");
const resultBox = document.getElementById("result");
const submitBtn = document.getElementById("submit-btn");

function setError(field, message) {
  document.getElementById("err-" + field).textContent = message;
  document.getElementById(field).classList.toggle("invalid", Boolean(message));
}

function validate(values) {
  const errors = {};
  if (values.name.length < 2) errors.name = "Name must be at least 2 characters.";
  if (!values.category) errors.category = "Please select a category.";
  if (!values.priority) errors.priority = "Please select a priority.";
  if (values.description.length < 10) errors.description = "Description must be at least 10 characters.";
  return errors;
}

function showResult(ok, html) {
  resultBox.hidden = false;
  resultBox.className = "result " + (ok ? "ok" : "fail");
  resultBox.innerHTML = html;
}

function escapeHtml(s) {
  const d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  resultBox.hidden = true;

  const values = {
    name: form.elements["name"].value.trim(),
    category: form.elements["category"].value,
    priority: form.elements["priority"].value,
    description: form.elements["description"].value.trim(),
  };

  const errors = validate(values);
  ["name", "category", "priority", "description"].forEach((f) => setError(f, errors[f] || ""));
  if (Object.keys(errors).length) return;

  submitBtn.disabled = true;
  submitBtn.textContent = "Submitting...";
  try {
    const res = await fetch("/api/complaints", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values),
    });
    const data = await res.json();

    if (res.ok) {
      showResult(true,
        `<strong>Complaint submitted!</strong><br>ID: <b>${escapeHtml(data.complaint_id)}</b><br>` +
        `Priority: ${escapeHtml(data.priority)}<br>Assigned to: ${escapeHtml(data.assigned_to)}<br>` +
        `Status: ${escapeHtml(data.status)}`);
      form.reset();
    } else if (res.status === 422 && data.fields) {
      Object.entries(data.fields).forEach(([f, m]) => setError(f, m));
    } else {
      showResult(false, escapeHtml(data.error || "Something went wrong."));
    }
  } catch (err) {
    showResult(false, "Network error. Please check your connection and try again.");
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Submit";
  }
});

// Track complaint
document.getElementById("track-btn").addEventListener("click", async () => {
  const box = document.getElementById("track-result");
  const id = document.getElementById("track-id").value.trim();
  box.hidden = false;
  if (!id) { box.className = "result fail"; box.textContent = "Enter a complaint ID."; return; }
  try {
    const res = await fetch("/api/complaints/" + encodeURIComponent(id));
    const data = await res.json();
    if (!res.ok) { box.className = "result fail"; box.textContent = data.error; return; }
    box.className = "result ok";
    box.innerHTML = `<b>${escapeHtml(data.complaint_id)}</b> &mdash; ${escapeHtml(data.status)}<br>` +
      `Category: ${escapeHtml(data.category)} | Priority: ${escapeHtml(data.priority)}<br>` +
      `Assigned to: ${escapeHtml(data.assigned_to)}<br>Last updated: ${escapeHtml(data.updated_at)}`;
  } catch (err) {
    box.className = "result fail";
    box.textContent = "Network error. Please try again.";
  }
});
