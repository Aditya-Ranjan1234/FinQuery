// frontend JS for HackRx LLM webapp

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
      const json = await resp.json();
      resultPre.textContent = JSON.stringify(json, null, 2);
      resultContainer.classList.remove("d-none");
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
