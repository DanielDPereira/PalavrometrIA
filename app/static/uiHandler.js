document.addEventListener('DOMContentLoaded', (event) => {
  const analysisForm = document.getElementById('analysis-form');
  if (analysisForm) {
    analysisForm.addEventListener('submit', function() {
      document.getElementById('loader-overlay').style.display = 'flex';
    });
  }

  const fileInput = document.getElementById('arquivo-input');
  if (fileInput) {
    fileInput.addEventListener('change', function(e) {
      const fileName = e.target.files[0] ? e.target.files[0].name : '';
      document.getElementById('file-name-display').textContent = fileName;
    });
  }
});