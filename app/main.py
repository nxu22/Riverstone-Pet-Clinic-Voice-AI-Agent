from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.routes import router
from app.retell_webhook import router as retell_router

app = FastAPI(title="Riverstone Pet Clinic Voice Agent")
app.include_router(router)
app.include_router(retell_router)


@app.get("/health")
def health():
    return {"status": "ok", "clinic": "Riverstone Pet Clinic"}


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Riverstone Pet Clinic — Live Appointments</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: system-ui, sans-serif; background: #f5f7fa; color: #1a1a2e; }
    header {
      background: #1a1a2e; color: #fff; padding: 18px 32px;
      display: flex; align-items: center; gap: 12px;
    }
    header h1 { font-size: 1.2rem; font-weight: 600; }
    header span { font-size: 0.85rem; opacity: 0.6; margin-left: auto; }
    #status { font-size: 0.75rem; padding: 2px 10px; border-radius: 99px; background: #22c55e; color: #fff; }
    main { padding: 32px; }
    h2 { font-size: 1rem; font-weight: 600; margin-bottom: 16px; color: #444; }
    table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
    th { background: #1a1a2e; color: #fff; text-align: left; padding: 12px 16px; font-size: 0.8rem; font-weight: 500; letter-spacing: .04em; text-transform: uppercase; }
    td { padding: 12px 16px; font-size: 0.9rem; border-bottom: 1px solid #f0f0f0; }
    tr:last-child td { border-bottom: none; }
    tr:hover td { background: #f9fafb; }
    .code { font-family: monospace; font-weight: 700; color: #4f46e5; }
    .vet  { font-size: 0.8rem; color: #666; }
    .new  { animation: flash .8s ease; }
    @keyframes flash { from { background: #eef2ff; } to { background: transparent; } }
    #empty { text-align: center; padding: 48px; color: #aaa; font-size: 0.9rem; }
  </style>
</head>
<body>
  <header>
    <h1>🐾 Riverstone Pet Clinic — Live Appointments</h1>
    <span id="updated">—</span>
    <span id="status">LIVE</span>
  </header>
  <main>
    <h2>All Bookings (newest first)</h2>
    <table>
      <thead>
        <tr>
          <th>Code</th><th>Owner</th><th>Pet</th><th>Species</th>
          <th>Veterinarian</th><th>Appointment</th><th>Booked at</th>
        </tr>
      </thead>
      <tbody id="tbody"></tbody>
    </table>
    <p id="empty" style="display:none">No appointments yet. Start a call with River!</p>
  </main>
  <script>
    let prevCodes = new Set();

    function fmt(iso) {
      if (!iso) return "—";
      const d = new Date(iso.replace(" ", "T"));
      if (isNaN(d.getTime())) return "—";
      return d.toLocaleString("en-CA", { dateStyle: "medium", timeStyle: "short" });
    }

    async function refresh() {
      try {
        const res = await fetch("/appointments");
        const data = await res.json();
        const tbody = document.getElementById("tbody");
        const empty = document.getElementById("empty");

        if (data.length === 0) {
          tbody.innerHTML = "";
          empty.style.display = "block";
        } else {
          empty.style.display = "none";
          tbody.innerHTML = data.map(r => {
            const isNew = !prevCodes.has(r.confirmation_code);
            return `<tr class="${isNew ? "new" : ""}">
              <td><span class="code">${r.confirmation_code}</span></td>
              <td>${r.owner_name}</td>
              <td>${r.pet_name}</td>
              <td>${r.species}</td>
              <td class="vet">${r.vet_name}</td>
              <td>${fmt(r.date_time)}</td>
              <td>${fmt(r.created_at)}</td>
            </tr>`;
          }).join("");
          prevCodes = new Set(data.map(r => r.confirmation_code));
        }

        document.getElementById("updated").textContent =
          "Updated " + new Date().toLocaleTimeString("en-CA");
        document.getElementById("status").style.background = "#22c55e";
      } catch {
        document.getElementById("status").style.background = "#ef4444";
      }
    }

    refresh();
    setInterval(refresh, 3000);
  </script>
</body>
</html>"""
