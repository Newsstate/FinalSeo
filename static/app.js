async function runAudit() {
  const url = document.getElementById("urlInput").value;
  const res = await fetch("/api/audit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url })
  });
  const data = await res.json();
  document.getElementById("resultBox").textContent = JSON.stringify(data, null, 2);
}