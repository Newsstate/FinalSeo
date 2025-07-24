// public/static/script.js

document.getElementById('scanForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const url = document.getElementById('urlInput').value;
  document.getElementById('loader').classList.remove('hidden');
  document.getElementById('results').classList.add('hidden');

  const res = await fetch('/api/scan', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ url })
  });

  const data = await res.json();
  document.getElementById('loader').classList.add('hidden');

  if (data.error) {
    alert(data.error);
    return;
  }

  document.getElementById('results').classList.remove('hidden');
  document.getElementById('url').innerText = data.url;
  document.getElementById('overallScore').innerText = data.overall_score;
  document.getElementById('metaTitle').innerText = data.meta_title;
  document.getElementById('metaDescription').innerText = data.meta_description;
  document.getElementById('robotsTag').innerText = data.robots_tag;
  document.getElementById('canonical').innerText = data.canonical;
  document.getElementById('langTag').innerText = data.lang_tag;
  document.getElementById('datePublished').innerText = data.date_published;
  document.getElementById('brokenLinks').innerText = data.broken_links;
  document.getElementById('nofollowLinks').innerText = data.external_links_nofollow;

  // Chart
  const ctx = document.getElementById('scoreChart').getContext('2d');
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: Object.keys(data.score_breakdown),
      datasets: [{
        label: 'SEO Score',
        data: Object.values(data.score_breakdown),
        backgroundColor: '#2f80ed'
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: { beginAtZero: true, max: 100 }
      }
    }
  });

  window.currentScan = data;
});

function exportToCSV() {
  const d = window.currentScan;
  const csv = Object.entries(d).map(([k, v]) => `${k},"${String(v).replace(/"/g, '""')}"`).join("\n");
  const blob = new Blob([csv], { type: 'text/csv' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = "seo-report.csv";
  a.click();
}

function exportToPDF() {
  const element = document.querySelector("#results");
  import('html2pdf.js').then(html2pdf => {
    html2pdf.default().from(element).save('seo-report.pdf');
  });
}
