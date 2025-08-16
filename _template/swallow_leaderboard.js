const g_models = {{ models | tojson }};
const g_tasks = {{ tasks | tojson }};
const g_updater = [];

var swallow_leaderboard_models = function(query, sortkey) {
  if ("name" in query) {
    // Return a single model specified by a name.
    return g_models[query.name];
  } else {

    let models = [];
    for (let key in g_models) {
      const model = g_models[key];

      // Filter by the include list.
      if ("includes" in query) {
        if (query.includes.includes(model['id'])) {
          models.push(model);
        }
        continue;
      }

      // Filter by the model family.
      if ("family" in query) {
        const family = model.family.toLowerCase();
        if (Array.isArray(query.family)) {
          let m = false;
          for (let f of query.family) {
            if (family.startsWith(f.toLowerCase())) {
              m = true;
              break;
            }
          }
          if (!m) {
            continue;
          }
        } else {
          if (!family.startsWith(query.family.toLowerCase())) {
            continue;
          }
        }
      }

      // Filter by the model size.
      if ("minp" in query && model['params'] < query.minp) {
        continue;
      }
      if ("maxp" in query && query.maxp <= model['params']) {
        continue;
      }

      // Filter by the exclude list.
      if ("excludes" in query && query.excludes.includes(model['id'])) {
        continue;
      }
      
      models.push(model);
    }

    // Sort models.
    if (sortkey !== undefined) {
      models.sort((a, b) => a.results[sortkey[0]][sortkey[1]] - b.results[sortkey[0]][sortkey[1]]);
    }

    return models;
  }
};

var swallow_leaderboard_get_taskdef = function(query) {
  for (let t of g_tasks[query[0]].tasks) {
    if (query[1] == t.name) {
      return t;
    }
  }
  return null;
};

var swallow_leaderboard_tasks = function(queries) {
  let tasks = [];

  for (let query of queries) {
    for (task of g_tasks[query[0]].tasks) {
      if (task.name == query[1] || (query[1] == "__ALL__" && !task.collective)) {
        tasks.push(task);
      }
    }
  }

  return tasks;
};

var swallow_leaderboard_chart_bar = function(element, config) {
  var onclick = function(chartContext, options) {
    config.sort = (config.sort + 1) % config.tasks.length;
    option = get_option(element, config);
    ApexCharts.exec(element, 'updateOptions', option, false, true);
  };

  var get_option = function(element, config) {
    const models = swallow_leaderboard_models(config.models, config.tasks[config.sort]);

    // Build series.
    let series = [];
    let labels = [];
    for (var query of config.tasks) {
      let data = [];
      for (var model of models) {
        data.push(model.results[query[0]][query[1]]);
      }
      const t = swallow_leaderboard_get_taskdef(query);
      series.push({name: t.title, data: data});
    }

    // Build labels.
    for (var model of models) {
      labels.push(model.name);
    }
  
    // Determine the orientation.
    const horizontal = (window.outerWidth < window.outerHeight);
    const height = horizontal ? Math.max(480, labels.length * 16 + 64) : 480;
    const padding = horizontal ? {} : { left: 48, right: 48, top: 0, bottom: 64 };
    return {
      chart: {
        type: "bar",
        id: element,
        fontFamily: 'inherit',
        height: height,
        parentHeightOffset: 0,
        animations: {
          enabled: true
        },
        events: {
          xAxisLabelClick: onclick,
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
          }
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
            return typeof val == "string" ? val : parseFloat(val).toFixed(4);
          }
        },
      },
      noData: {
        text: "モデルを選択してください (Select a model)",
      },
      theme: {
        mode: document.documentElement.getAttribute("data-bs-theme") == "dark" ? "dark" : "light",
      },
    }
  };

  // Create the bar chart.
  option = get_option(element, config);
  window.ApexCharts && (new ApexCharts(document.getElementById(element), option)).render();

  // Register an update function.
  g_updater.push(function(target, updates) {
    if (target == "" || target == element) {
      Object.assign(config, updates);
      option = get_option(element, config);
      ApexCharts.exec(element, 'updateOptions', option, false, true);
    }
  });
};

var swallow_leaderboard_chart_radar = function(element, config) {
  var get_option = function(element, config) {
    const models = swallow_leaderboard_models(config.models);

    // Build series.
    let series = [];
    var labels = [];
    for (var model of models) {
      let data = [];
      labels = [];

      for (let query of config.tasks) {
        for (let t of g_tasks[query[0]].tasks) {
          if (query[1] == t.name || (query[1] == "*" && !t.collective) || (query[1] == "+" && !t.collective && !t.exclude_from_avg)) {
            data.push(model.results[query[0]][t.name]);
            labels.push(t.title);
          }
        }
      }
      series.push({
        name: model.name,
        data: data,
      });
    }

    return {
      chart: {
        type: "radar",
        id: element,
        fontFamily: 'inherit',
        height: config.height,
        parentHeightOffset: 0,
      },
      series: series,
      xaxis: {
        categories: labels,
      },
      yaxis: {
        show: false,
        tickAmount: 5,
        min: 0.,
        max: 1.,
      },
      tooltip: {
        marker: {
          show: false,
        },
      },
      noData: {
        text: "モデルを選択してください (Select a model)",
      },
      theme: {
        mode: document.documentElement.getAttribute("data-bs-theme") == "dark" ? "dark" : "light",
      },
    };
  };
  
  // Create the radar chart.
  option = get_option(element, config);
  window.ApexCharts && (new ApexCharts(document.getElementById(element), option)).render();

  // Register an update function.
  g_updater.push(function(target, updates) {
    if (target == "" || target == element) {
      Object.assign(config, updates);
      option = get_option(element, config);
      ApexCharts.exec(element, 'updateOptions', option, false, true);
    }
  });
};

var swallow_leaderboard_chart_scatter = function(element, config) {
  var get_option = function(element, config) {
    const models = swallow_leaderboard_models(config.models);
    const xcat = config.xaxis[0];
    const xname = config.xaxis[1]
    const ycat = config.yaxis[0];
    const yname = config.yaxis[1];
    // There seems to be no way to obtain a color palette from ApexCharts,
    // so these colors are hard coded.
    const theme_colors = document.documentElement.getAttribute("data-bs-theme") == "dark" ? 
      ['#4ECDC4', '#C7F464', '#81D4FA', '#FD6A6A', '#546E7A']: 
      ['#008FFB', '#00E396', '#FEB019', '#FF4560', '#775DD0'];

    var format_params = function(val) {
      const v = Math.pow(2, parseFloat(val));
      return v < 10 ? v.toFixed(1) : v.toFixed(0);
    };

    var format_value = function(val) {
      return typeof val == "string" ? val : parseFloat(val).toFixed(4);
    };

    var build_axis = function(category, name) {
      if (category == "params" || category == "active_params") {
        {% if lang == "ja" %}
        title = category == "active_params" ? "有効パラメータ数" : "パラメータ数";
        {% else %}
        title = category == "active_params" ? "Active parameters" : "Parameters";
        {% endif %}
        return {
          min: 0, // 2^0 = 1.
          max: 8, // 2^8 = 256.
          title: {text: title + " [B]"},
          tickAmount: 10,
          labels: {
            formatter: function(val) {
              const v = Math.pow(2, parseFloat(val));
              return v < 10 ? v.toFixed(1) : v.toFixed(0);
            }
          }
        }
      } else {
        return {
          min: 0,
          max: 1,
          title: {text: g_tasks[category].taskdict[name].title },
          tickAmount: 10,
          labels: {
            formatter: function(val) {
              return parseFloat(val).toFixed(1)
            }
          }
        }
      }
    };

    // Build series.
    let series = [];
    for (let model of models) {
      const x = (xcat == "params" || xcat == "active_params") ? Math.log2(model[xcat]) : model.results[xcat][xname];
      const y = (ycat == "params" || ycat == "active_params") ? Math.log2(model[ycat]) : model.results[ycat][yname];
      const family = model.family.toLowerCase();
      let color_index = 4;
      if (family.startsWith("gpt") || family.startsWith("o3") || family.startsWith("o4")) {
        color_index = 0;
      } else if (family.startsWith("llama")) {
        color_index = 1;
      } else if (family.startsWith("gemma")) {
        color_index = 2;
      } else if (family.startsWith("qwen")) {
        color_index = 3;
      }
      series.push({name: model.name, data: [[x, y]], color: theme_colors[color_index]});
    }
    const xaxis = build_axis(xcat, xname);
    const yaxis = build_axis(ycat, yname);

    return {
      chart: {
        type: "scatter",
        fontFamily: 'inherit',
        height: 480,
        parentHeightOffset: 0,
        toolbar: {
          tools: {
            download: true,
            selection: false,
            zoom: false,
            zoomin: false,
            zoomout: false,
            pan: false,
            reset: false,
          },
        },
        zoom: {
          enabled: false,
          allowMouseWheelZoom: false,
        },
      },
      series: series,
      xaxis: xaxis,
      yaxis: yaxis,
      legend: {
        show: false,
      },
      markers: {
        size: 4,
      },
      tooltip: {
        marker: {show: false},
        x: {formatter: (xcat == "params" || xcat == "active_params") ? format_params : format_value},
        y: {formatter: (ycat == "params" || ycat == "active_params") ? format_params : format_value},
      },
      theme: {
        mode: document.documentElement.getAttribute("data-bs-theme") == "dark" ? "dark" : "light",
      },
    };
  };

  // Create the radar chart.
  option = get_option(element, config);
  let obj_scatter = new ApexCharts(document.getElementById(element), option);
  console.log(obj_scatter);
  obj_scatter.render();

  // Register an update function.
  g_updater.push(function(target, updates) {
    if (target == "" || target == element) {
      Object.assign(config, updates);
      option = get_option(element, config);
      obj_scatter.updateOptions(option, false, true);
    }
  });
};

var swallow_leaderboard_chart = function(element, config) {
  //
  if (config.type == "bar") {
    swallow_leaderboard_chart_bar(element, config);
  } else if (config.type == "radar") {
    swallow_leaderboard_chart_radar(element, config);
  } else if (config.type == "scatter") {
    swallow_leaderboard_chart_scatter(element, config);
  }
};

var swallow_leaderboard_update = function(target, updates) {
  for (let i = 0; i < g_updater.length; ++i) {
    g_updater[i](target, updates);
  }
}
