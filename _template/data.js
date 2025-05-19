const g_models = {{ models | tojson }};
const g_taskcats = {{ taskcats | tojson }};

function query_models(type = "all", minp = null, maxp = null, includes = null, excludes = null)
{
  let models = [];
  for (let key in g_models) {
    const model = g_models[key];

    if (type == "base" && model['base_model'] != "") {
      continue;
    } else if (type == "chat" && model['base_model'] == "") {
      continue;
    }

    if (includes !== null && includes.includes(model['id'])) {
      models.push(model);
      continue;
    }

    if (minp !== null && model['params'] < minp) {
      continue;
    }
    if (maxp !== null && maxp < model['params']) {
      continue;
    }
    if (excludes !== null && excludes.includes(model['id'])) {
      continue;
    }
    models.push(model);
  }

  return models;
}
