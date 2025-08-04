// frontend JS for HackRx LLM webapp

// Format clause text for better readability
function formatClauseText(text) {
  // Replace newlines with <br> for HTML display
  let formatted = text.replace(/\n/g, '<br>');
  
  // Add spacing after colons for better readability
  formatted = formatted.replace(/:([^<])/g, ': $1');
  
  return formatted;
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("query-form");
  const queryInput = document.getElementById("query");
  const spinner = document.getElementById("spinner");
  const submitBtn = document.getElementById("submit-btn");
  const resultContainer = document.getElementById("result-container");
  const resultPre = document.getElementById("result");
  // Upload elements
  const uploadForm = document.getElementById("upload-form");
  const filesInput = document.getElementById("files");
  const uploadSpinner = document.getElementById("upload-spinner");
  const uploadBtn = document.getElementById("upload-btn");
  const uploadMsg = document.getElementById("upload-msg");
  // Sample select
  const sampleSelect = document.getElementById("sample-select");

  // Prefill last query (localStorage)
  const lastQuery = localStorage.getItem("lastQuery");
  if (lastQuery) {
    queryInput.value = lastQuery;
  }

  // Handle sample selector change
  sampleSelect?.addEventListener("change", () => {
    if (sampleSelect.value) {
      queryInput.value = sampleSelect.value;
    }
  });

  // Handle query form submit
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = queryInput.value.trim();
    if (!query) return;

    // UI feedback
    spinner.classList.remove("d-none");
    submitBtn.disabled = true;
    resultContainer.classList.add("d-none");

    try {
      const resp = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      if (!resp.ok) {
        throw new Error(`Server error: ${resp.status}`);
      }
      const data = await resp.json();
      
      // Save raw JSON for toggling
      resultPre.textContent = JSON.stringify(data, null, 2);
      
      // Update decision badge
      const decisionBadge = document.getElementById('decision-badge');
      const decisionClass = data.decision.toLowerCase() === 'approved' ? 'decision-approved' : 'decision-rejected';
      decisionBadge.innerHTML = `
        <span class="decision-badge ${decisionClass}">
          ${data.decision.toUpperCase()}
          ${data.amount ? ` (₹${data.amount.toLocaleString()})` : ''}
        </span>
      `;
      
      // Update justification
      document.getElementById('justification').innerHTML = `
        <p class="mb-0">${data.justification}</p>
      `;
      
      // Update clauses
      const clausesContainer = document.getElementById('clauses-container');
      clausesContainer.innerHTML = data.clauses.map((clause, index) => `
        <div class="clause-card">
          <div class="clause-header">
            Clause ${index + 1} <span class="text-muted">• ${clause.id}</span>
          </div>
          <div class="clause-body">
            <p class="mb-2">${formatClauseText(clause.text)}</p>
            <div class="source-path" title="${clause.source}">
              <i class="bi bi-file-earmark-text"></i> ${clause.source.split('/').pop()}
            </div>
          </div>
        </div>
      `).join('');
      
      // Show the result container
      resultContainer.classList.remove("d-none");
      
      // Add event listener for JSON toggle
      document.getElementById('show-json-btn').onclick = () => {
        const resultPre = document.getElementById('result');
        const isVisible = !resultPre.classList.contains('d-none');
        resultPre.classList.toggle('d-none', !isVisible);
        this.textContent = isVisible ? 'View Raw JSON' : 'Hide Raw JSON';
      };
    } catch (err) {
      resultPre.textContent = `Error: ${err}`;
      resultContainer.classList.remove("d-none");
    } finally {
      spinner.classList.add("d-none");
      submitBtn.disabled = false;
    }
  });

  // Handle upload form submit
  uploadForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!filesInput.files.length) return;

    uploadSpinner.classList.remove("d-none");
    uploadBtn.disabled = true;
    uploadMsg.classList.add("d-none");

    const formData = new FormData();
    for (const file of filesInput.files) {
      formData.append("files", file);
    }

    try {
      const resp = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });
      const json = await resp.json();
      if (!resp.ok) throw new Error(json.error || resp.statusText);
      uploadMsg.textContent = `Uploaded ${json.uploaded.length} file(s), added ${json.clauses_added} clauses.`;
      uploadMsg.classList.remove("d-none");
      uploadMsg.classList.add("text-success");
    } catch (err) {
      uploadMsg.textContent = `Upload failed: ${err}`;
      uploadMsg.classList.remove("d-none");
      uploadMsg.classList.remove("text-success");
      uploadMsg.classList.add("text-danger");
    } finally {
      uploadSpinner.classList.add("d-none");
      uploadBtn.disabled = false;
      filesInput.value = "";
    }
  });
});
