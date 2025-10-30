document.addEventListener('DOMContentLoaded', (event) => {
  const analysisForm = document.getElementById('analysis-form');
  if (analysisForm) {
    analysisForm.addEventListener('submit', function() {
      document.getElementById('loader-overlay').style.display = 'flex';
    });
  }
  
  const textInput = document.getElementById('texto-input');
  const urlInput = document.getElementById('url-input');
  const fileInput = document.getElementById('arquivo-input');
  const fileDisplay = document.getElementById('file-name-display');

  if (textInput && urlInput && fileInput) {
    
    // Quando digitar no TEXTAREA
    textInput.addEventListener('input', () => {
      if (textInput.value.trim() !== '') {
        urlInput.value = ''; // Limpa URL
        fileInput.value = ''; // Limpa arquivo
        fileDisplay.textContent = '';
      }
    });

    // Quando digitar na URL
    urlInput.addEventListener('input', () => {
      if (urlInput.value.trim() !== '') {
        textInput.value = ''; // Limpa texto
        fileInput.value = ''; // Limpa arquivo
        fileDisplay.textContent = '';
      }
    });

    // Quando selecionar um ARQUIVO
    fileInput.addEventListener('change', (e) => {
      const fileName = e.target.files[0] ? e.target.files[0].name : '';
      fileDisplay.textContent = fileName;
      
      if (fileName !== '') {
        textInput.value = ''; // Limpa texto
        urlInput.value = ''; // Limpa URL
      }
    });
  }
});