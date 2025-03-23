'use strict'

function $(selector) {
  return document.querySelector(selector)
}

function find(el, selector) {
  let finded
  return (finded = el.querySelector(selector)) ? finded : null
}

function siblings(el) {
  const siblings = []
  for (let sibling of el.parentNode.children) {
    if (sibling !== el) {
      siblings.push(sibling)
    }
  }
  return siblings
}

const showAsideBtn = $('.show-side-btn')
const sidebar = $('.sidebar')
const wrapper = $('#wrapper')

showAsideBtn.addEventListener('click', function () {
  $(`#${this.dataset.show}`).classList.toggle('show-sidebar')
  wrapper.classList.toggle('fullwidth')
})

if (window.innerWidth < 767) {
  sidebar.classList.add('show-sidebar');
}

window.addEventListener('resize', function () {
  if (window.innerWidth > 767) {
    sidebar.classList.remove('show-sidebar')
  }
})

// Initialisation du graphique circulaire (Répartition des catégories)
function initPieChart(categories, category_counts) {
  var ctxPie = document.getElementById('pieChart').getContext('2d');
  var pieChart = new Chart(ctxPie, {
      type: 'doughnut',
      data: {
          labels: categories,
          datasets: [{
              data: category_counts,
              backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#E7E9ED', '#8E5EA2'],
              borderWidth: 1
          }]
      },
      options: {
          responsive: true,
          plugins: {
              legend: {
                  position: 'bottom',
                  labels: {
                      usePointStyle: true,
                      padding: 10
                  }
              },
              tooltip: {
                  callbacks: {
                      label: function(tooltipItem) {
                          return tooltipItem.label + ': ' + tooltipItem.raw;
                      }
                  }
              },
              title: {
                  display: true,
                  text: 'Répartition des catégories',
                  font: {
                      size: 16
                  }
              }
          },
          cutout: '60%',
          maintainAspectRatio: false
      }
  });
}

// Initialisation du graphique linéaire (Ventes au fil du temps)
function initLineChart(sale_dates_labels, sale_dates_values) {
  var ctxLine = document.getElementById('lineChart').getContext('2d');
  var lineChart = new Chart(ctxLine, {
      type: 'line',
      data: {
          labels: sale_dates_labels,
          datasets: [{
              label: 'Ventes au fil du temps',
              data: sale_dates_values,
              fill: false,
              borderColor: '#4BC0C0',
              tension: 0.1
          }]
      },
      options: {
          responsive: true,
          plugins: {
              legend: {
                  position: 'top',
              },
              tooltip: {
                  callbacks: {
                      label: function(tooltipItem) {
                          return 'Ventes: ' + tooltipItem.raw;
                      }
                  }
              },
              title: {
                  display: true,
                  text: 'Ventes au fil du temps',
                  font: {
                      size: 16
                  }
              }
          },
          maintainAspectRatio: false
      }
  });
}

// Fonction principale pour initialiser les graphiques
function initCharts() {
  // Récupérer les données passées dans le template
  const chartData = document.getElementById('chart-data');
  const categories = JSON.parse(chartData.getAttribute('data-categories'));
  const category_counts = JSON.parse(chartData.getAttribute('data-category-counts'));
  const sale_dates_labels = JSON.parse(chartData.getAttribute('data-sale-dates-labels'));
  const sale_dates_values = JSON.parse(chartData.getAttribute('data-sale-dates-values'));

  // Initialiser les graphiques
  initPieChart(categories, category_counts);
  initLineChart(sale_dates_labels, sale_dates_values);
}

// Appeler la fonction d'initialisation une fois la page chargée
document.addEventListener('DOMContentLoaded', initCharts);