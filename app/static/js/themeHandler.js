document.addEventListener('DOMContentLoaded', (event) => {
  try {
    const themeToggleBtn = document.getElementById('theme-toggle');
    const docElement = document.documentElement;

    if (themeToggleBtn) {
      themeToggleBtn.addEventListener('click', () => {
        docElement.classList.toggle('dark-mode');
        
        const isDarkMode = docElement.classList.contains('dark-mode');
        localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
      });
    }
  } catch (e) {
    console.warn('Botão de tema não encontrado ou localStorage indisponível.');
  }
});