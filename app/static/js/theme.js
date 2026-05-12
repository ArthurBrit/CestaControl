(function () {
  const button = document.querySelector("[data-theme-toggle]");
  const root = document.documentElement;

  function setTheme(theme) {
    root.dataset.theme = theme;
    document.body.classList.toggle("theme-dark", theme === "dark");
    try {
      localStorage.setItem("theme", theme);
    } catch (error) {
      // Theme still works for this page when storage is blocked.
    }
    if (button) {
      button.textContent = theme === "dark" ? "Claro" : "Escuro";
      button.setAttribute("aria-label", theme === "dark" ? "Usar modo claro" : "Usar modo escuro");
    }
  }

  setTheme(root.dataset.theme || "light");

  if (button) {
    button.addEventListener("click", function () {
      setTheme(root.dataset.theme === "dark" ? "light" : "dark");
    });
  }
})();
