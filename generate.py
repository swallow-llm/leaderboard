import copy
import yaml
import json
import operator
import os
from jinja2 import Template, Environment, FileSystemLoader
from markdown_it import MarkdownIt

def apply_language(obj, lang):
    if isinstance(obj, list):
        return [apply_language(item, lang) for item in obj]
    elif isinstance(obj, dict):
        if lang in obj:
            return str(obj[lang])
        else:
            return {key: apply_language(value, lang) for key, value in obj.items()}
    else:
        return obj

def apply_category(models, category_name):
    return {key: value for key, value in models.items() if category_name in value['category']}

def get_ranking_data(models, taskcat, task):
    # Create a model list with the results of the specified task.
    M = []
    for m in models.values():
        if taskcat in m['results']:
            if task in m['results'][taskcat] and 0 <= m['results'][taskcat][task]:
                M.append(dict(id=m['id'], name=m['name'], value=m['results'][taskcat][task]))

    # Sort the models in ascending order of the results.
    M.sort(key=lambda m: m['value'], reverse=True)

    # Build a ranking data.
    data = dict(
        taskcat=taskcat,
        task=task,
        ids=[m['id'] for m in M],
        names=[m['name'] for m in M],
        values=[m['value'] for m in M],
    )

    return data

def count_rank_of_model(data, model):
    r = 0
    v = None
    for i, (key, value) in enumerate(zip(data['ids'], data['values'])):
        if value != v:
            r = i
            v = value
        if key == model['id']:
            break
    
    d = {}
    d['taskcat'] = data['taskcat']
    d['task'] = data['task']
    d['series'] = data['values'][::-1]
    d['labels'] = data['names'][::-1]
    d['ids'] = data['ids'][::-1]
    d['rank'] = r+1
    d['value'] = v
    return d

def get_radar_data(model, taskcats, category):
    tasks = taskcats[category]['tasks']
    d = dict(id=category, title=taskcats[category]['title'], series=[], tasks=[])
    for task in tasks.values():
        if not task.get('collective', False):
            d['series'].append(model['results'][category][task['name']])
            d['tasks'].append(task['short'])
    return d

def load_yaml(filename, lang):
    with open(filename) as fi:
        obj = yaml.safe_load(fi)
        obj = apply_language(obj, lang)
        return obj

def generate_datajs(env, name, models, taskcats):
    template = env.get_template('data.js')
    filename = name
    with open('_site/' + filename, 'w') as fo:
        print(template.render(models=models, taskcats=taskcats), file=fo)
    return filename

if __name__ == '__main__':
    langs = ['ja', 'en']
    md = (
        MarkdownIt('commonmark', {'breaks':True,'html':True})
    )

    for lang in langs:
        # Load data.
        models = load_yaml('_data/model.yml', lang)
        taskcats = load_yaml('_data/task.yml', lang)
        modelcats = load_yaml('_data/category.yml', lang)
        about = load_yaml('_data/about.yml', lang)
        ui = load_yaml('_data/ui.yml', lang)

        # Render
        about['issues']['content'] = md.render(about['issues']['content'])

        # Convert the model object from list to dict.
        models = {m['id']: m for m in models}

        # Convert the task specifications from list to dict.
        for c in taskcats.values():
            c['tasks'] = {task['name']: task for task in c['tasks']}

        # Get ranking data.
        rdata_ja_avg = get_ranking_data(models, 'ja_basic', 'Ja Avg')
        rdata_jamtb_avg = get_ranking_data(models, 'ja_mtb', 'JMT Avg')
        rdata_en_avg = get_ranking_data(models, 'en_basic', 'En Avg')

        # Generate data for visualization.
        for name, model in models.items():
            # Generate URI.
            model['uri'] = model['id'].replace('/', '_')

            # Find category.
            model['category'] = []
            for c in modelcats:
                size = float(model['params'])
                if size == 0:
                    size = 99
                if c['min'] <= size < c['max']:
                    for t in c['type']:
                        if (t == 'base' and not model['base_model']) or (t == 'chat' and model['base_model']):
                            model['category'].append(c['name'])

            # Generate ranking data.
            model['ranking'] = {
                'Ja Avg': count_rank_of_model(rdata_ja_avg, model),
                'En Avg': count_rank_of_model(rdata_en_avg, model),
            }
            if model['base_model']:
                model['ranking']['JMT Avg'] = count_rank_of_model(rdata_jamtb_avg, model)

            # Generate radar data.
            model['radar'] = dict(
                ja_basic=get_radar_data(model, taskcats, 'ja_basic'),
                en_basic=get_radar_data(model, taskcats, 'en_basic'),
            )
            if model['base_model']:
                model['radar']['ja_mtb'] = get_radar_data(model, taskcats, 'ja_mtb')

        env = Environment(loader=FileSystemLoader('./_template'))

        # Generate HTMLs for models.
        datajs = generate_datajs(env, f'data_model_{lang}.js', models, taskcats)
        template = env.get_template('model.html')
        for name, model in models.items():
            filename = f'{model["uri"]}'
            print(filename)

            description = f'{model["name"]} の性能を棒グラフやレーダーチャートでチェック' if lang == 'ja' else f'Check the performance of {model["name"]} with bar and radar charts'
            with open(f'_site/{filename}.{lang}.html', 'w') as fo:
                print(template.render(
                    filename=filename,
                    datajs=datajs,
                    title=model['name'],
                    description=description,
                    models=models,
                    model_id = name,
                    taskcats=taskcats,
                    modelcats=modelcats,
                    lang=lang,
                    ui=ui,
                    ),
                    file=fo
                    )

        template = env.get_template('category.html')
        for modelcat in modelcats:
            _models = apply_category(models, modelcat['name'])
            datajs = generate_datajs(env, f'data_{modelcat["name"]}_{lang}.js', _models, taskcats)
            filename = f'{modelcat["name"]}'
            print(filename)
            with open(f'_site/{filename}.{lang}.html', 'w') as fo:
                print(template.render(
                    filename=filename,
                    datajs=datajs,
                    title=modelcat['title'],
                    description=modelcat['description'],
                    models=_models,
                    taskcats=taskcats,
                    modelcats=modelcats,
                    modelcat=modelcat,
                    lang=lang,
                    ui=ui,
                    ),
                    file=fo
                    )

        template = env.get_template('about.html')
        filename = f'about'
        print(filename)
        with open(f'_site/{filename}.{lang}.html', 'w') as fo:
            print(template.render(
                filename=filename,
                about=about,
                title=ui['about'],
                description=about['description'],
                models=models,
                taskcats=taskcats,
                modelcats=modelcats,
                lang=lang,
                ui=ui,
                ),
                file=fo
                )

    os.system('rsync -av --delete dist _site/')
    os.system('rsync -av --delete static _site/')
    os.system('rsync -av --delete index.html _site/')
    os.system('rsync -av --delete bar.js _site/')
