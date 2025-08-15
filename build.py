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

def apply_wildcard(obj, taskspec):
    if isinstance(obj, list):
        return [apply_wildcard(item, taskspec) for item in obj]
    elif isinstance(obj, dict):
        if 'columns' in obj:
            C = []
            for category, name in obj['columns']:
                if name == '*':
                    for t in taskspec[category]['tasks']:
                        if not t.get('collective', False):
                            C.append([category, t['name']])
                else:
                    C.append([category, name])
            obj['columns'] = C
            return obj
        else:
            return {key: apply_wildcard(value, taskspec) for key, value in obj.items()}
    else:
        return obj

def add_taskdict(taskspec):
    for name, value in taskspec.items():
        value['taskdict'] = {task['name']: task for task in value['tasks']}

def load_yaml(filename, lang=''):
    with open(filename) as fi:
        obj = yaml.safe_load(fi)
        if lang:
            obj = apply_language(obj, lang)
        return obj

def generate(env, src, dst, args):
    print(dst)
    template = env.get_template(src)
    _dst = f'_site/{dst}'
    kwargs = dict(args.items())
    kwargs['filename'] = dst
    with open(_dst, 'w') as fo:
        print(template.render(**kwargs), file=fo)
    return _dst

if __name__ == '__main__':
    langs = ['ja', 'en']
    md = (
        MarkdownIt('commonmark', {'breaks':True, 'html':True})
    )
    env = Environment(loader=FileSystemLoader('./_template'))

    # Convert model.yml to model.json
    models = load_yaml('_data/model.yml')

    for lang in langs:
        taskspec_pre = load_yaml('_data/task_pre.yml', lang)
        add_taskdict(taskspec_pre)
        taskspec_post = load_yaml('_data/task_post.yml', lang)
        add_taskdict(taskspec_post)

        ui = load_yaml('_data/ui.yml', lang)
        ui = apply_wildcard(ui, taskspec_pre | taskspec_post)

        ##########
        # For pre-trained models.
        ##########
        pre_models = {m['id']: m for m in models if not m['is_post']}

        # Javascript Library.
        jspath = f'swallow_leaderboard_pre_{lang}.js'
        generate(env, 'swallow_leaderboard.js', jspath, dict(models=pre_models, tasks=taskspec_pre, lang=lang))
        
        # Top page.
        args = dict(
            models=pre_models,
            taskspec=taskspec_pre,
            ui=ui,
            jspath=jspath,
            lang=lang,
            is_post=False,
            select='__ALL__',
        )
        generate(env, 'page-bar.html', f'bar-pre.{lang}.html', args)
        generate(env, 'page-scatter.html', f'scatter-pre.{lang}.html', args)
        args['select'] = ''
        generate(env, 'page-radar.html', f'radar-pre.{lang}.html', args)
        for name, model in pre_models.items():
            uri = model['id'].replace('/', '_')
            args['select'] = model['id']
            generate(env, 'page-radar.html', f'{uri}.{lang}.html', args)

        ##########
        # For post-trained models.
        ##########
        post_models = {m['id']: m for m in models if m['is_post']}

        # Javascript Library.
        jspath = f'swallow_leaderboard_post_{lang}.js'
        generate(env, 'swallow_leaderboard.js', jspath, dict(models=post_models, tasks=taskspec_post, lang=lang))

        # Top page.
        args = dict(
            models=post_models,
            taskspec=taskspec_post,
            ui=ui,
            jspath=jspath,
            lang=lang,
            is_post=True,
            select='__ALL__',
        )

        generate(env, 'page-bar.html', f'bar-post.{lang}.html', args)
        generate(env, 'page-scatter.html', f'scatter-post.{lang}.html', args)
        args['select'] = ''
        generate(env, 'page-radar.html', f'radar-post.{lang}.html', args)
        for name, model in post_models.items():
            uri = model['id'].replace('/', '_')
            args['select'] = model['id']
            generate(env, 'page-radar.html', f'{uri}.{lang}.html', args)
