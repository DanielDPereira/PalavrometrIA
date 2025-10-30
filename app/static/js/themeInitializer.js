(function() {
  try {
    const theme = localStorage.getItem('theme');
    if (theme === 'dark') {
      document.documentElement.classList.add('dark-mode');
    } else if (theme === 'light') {
       document.documentElement.classList.remove('dark-mode');
    }
  } catch (e) {
    console.warn('LocalStorage indisponível para salvar tema.');
  }
})();