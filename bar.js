// Implement a function to build data for the bar chart.
var bar_initialize = function(element, models, tasks, sortkey, title = undefined) {
  // Sort the models.
  let _models = models.concat();
  _models.sort((a, b) => a.results[sortkey[0]][sortkey[1]] - b.results[sortkey[0]][sortkey[1]]);

  // Build series.
  let series = [];
  for (var task of tasks) {
    let data = [];
    for (var model of _models) {
      data.push(model.results[task[0]][task[1]]);
    }
    series.push({name: g_taskcats[task[0]].tasks[task[1]].title, data: data});
  }

  // Build labels.
  let labels = [];
  for (var model of _models) {
    labels.push(model.name);
  }

  // Determine the orientation.
  const horizontal = (window.outerWidth < window.outerHeight);
  const height = horizontal ? Math.max(480, labels.length * 16 + 64) : 480;
  const padding = horizontal ? {} : { left: 48, right: 48, top: 0, bottom: 64 };
  const option = {
    chart: {
      type: "bar",
      id: element,
      fontFamily: 'inherit',
      height: height,
      parentHeightOffset: 0,
      animations: {
        enabled: true
      },
    },
    plotOptions: {
      bar: {
        horizontal: horizontal,
      },
    },
    grid: {
      padding: padding,
    },
    series: series,
    xaxis: {
      categories: labels,
      labels: {
        hideOverlappingLabels: false,
        style: {
//            fontSize: '9px',
        }
      }
    },
    yaxis: {
      tickAmount: 5,
      min: 0.,
      max: 1.,
      labels: {
        formatter: function(val) {
          return typeof val == "string" ? val : parseFloat(val).toFixed(1);
        },
        maxWidth: horizontal ? 320 : 160,
      },
    },
    dataLabels: {
      enabled: false
    },
    stroke: {
      show: true,
      width: 2,
      colors: ['transparent']
    },
    legend: {
      position: 'top',
    },
    tooltip: {
      marker: {
        show: false,
      },
      y: {
        formatter: function(val) {
          return typeof val == "string" ? val : parseFloat(val).toFixed(3);
        }
      },
    },
    title: {
      text: title,
      align: "center",
    }
  };

  // Create the bar chart.
  window.ApexCharts && (new ApexCharts(document.getElementById(element), option)).render();
}
