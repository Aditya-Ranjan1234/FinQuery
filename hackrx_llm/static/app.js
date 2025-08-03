// frontend JS for HackRx LLM webapp

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("query-form");
  const queryInput = document.getElementById("query");
  const spinner = document.getElementById("spinner");
  const submitBtn = document.getElementById("submit-btn");
  const resultContainer = document.getElementById("result-container");
  const resultPre = document.getElementById("result");

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
});
