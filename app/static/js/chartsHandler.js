// --- Script dos Gráficos (Chart.js) ---
document.addEventListener('DOMContentLoaded', (event) => {
  
  const chartDataElement = document.getElementById('chart-data');
  if (!chartDataElement) {
    return; // Não há dados de gráfico para renderizar
  }

  try {
    const chartData = JSON.parse(chartDataElement.textContent);

    // Gráfico de Frequência de Palavras (Barra)
    const freqCtx = document.getElementById('freqPalavrasChart')?.getContext('2d');
    if (freqCtx && chartData.freq_labels && chartData.freq_data) {
      new Chart(freqCtx, {
        type: 'bar',
        data: {
          labels: chartData.freq_labels,
          datasets: [{
            label: 'Frequência',
            data: chartData.freq_data,
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1,
            borderRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                precision: 0
              }
            }
          },
          plugins: {
            legend: {
              display: false
            }
          }
        }
      });
    }

    // Gráfico classes gramaticais (Pizza)
    const tiposCtx = document.getElementById('tiposPalavrasChart')?.getContext('2d');
    if (tiposCtx && chartData.tipos_labels && chartData.tipos_data) {
      new Chart(tiposCtx, {
        type: 'doughnut',
        data: {
          labels: chartData.tipos_labels,
          datasets: [{
            data: chartData.tipos_data,
            backgroundColor: [
              '#36A2EB', '#FF6384', '#FFCE56', '#4BC0C0', '#9966FF',
              '#FF9F40', '#8AFF33', '#33FFA8', '#FF3380', '#335BFF'
            ],
            hoverOffset: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { 
              position: 'right',
              labels: {
                boxWidth: 12,
                font: { size: 12 }
              }
            },
          }
        }
      });
    }
  
  } catch (e) {
    console.error("Erro ao processar dados do gráfico:", e);
  }
});