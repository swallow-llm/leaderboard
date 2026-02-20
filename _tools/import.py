import csv
import oyaml as yaml
import re
import operator
import sys

includes_pre = set([
    'Qwen/Qwen2.5-0.5B',
    'Qwen/Qwen2.5-1.5B',
    'Qwen/Qwen2.5-3B',
    'Qwen/Qwen2.5-7B',
    'Qwen/Qwen2.5-14B',
    'Qwen/Qwen2.5-32B',
    'Qwen/Qwen2.5-72B',
    'Qwen/Qwen3-0.6B-Base',
    'Qwen/Qwen3-1.7B-Base',
    'Qwen/Qwen3-4B-Base',
    'Qwen/Qwen3-8B-Base',
    'Qwen/Qwen3-14B-Base',
    'Qwen/Qwen3-30B-A3B-Base',
    'SakanaAI/TinySwallow-1.5B',
    'sbintuitions/sarashina2.2-0.5b',
    'sbintuitions/sarashina2.2-1b',
    'sbintuitions/sarashina2.2-3b',
    'sbintuitions/sarashina2-7b',
    'sbintuitions/sarashina2-13b',
    'sbintuitions/sarashina2-70b',
    'google/gemma-2-2b',
    'tokyotech-llm/Gemma-2-Llama-Swallow-2b-pt-v0.1',
    'google/gemma-2-9b',
    'tokyotech-llm/Gemma-2-Llama-Swallow-9b-pt-v0.1',
    'google/gemma-2-27b',
    'tokyotech-llm/Gemma-2-Llama-Swallow-27b-pt-v0.1',
    'google/gemma-3-1b-pt',
    'google/gemma-3-4b-pt',
    'google/gemma-3-12b-pt',
    'google/gemma-3-27b-pt',
    'llm-jp/llm-jp-3-1.8b',
    'llm-jp/llm-jp-3-3.7b',
    'llm-jp/llm-jp-3-7.2b',
    'llm-jp/llm-jp-3-13b',
    'meta-llama/Llama-3.2-1B',
    'meta-llama/Llama-3.2-3B',
    'meta-llama/Meta-Llama-3.1-8B',
    'tokyotech-llm/Llama-3.3-Swallow-8B-v0.5',
    'meta-llama/Meta-Llama-3.1-70B',
    'tokyotech-llm/Llama-3.3-Swallow-70B-v0.4',
    'meta-llama/Llama-4-Scout-17B-16E',
    'pfnet/plamo-2-1b',
    'pfnet/plamo-2-8b',
    'tiiuae/Falcon3-1B-Base',
    'tiiuae/Falcon3-3B-Base',
    'tiiuae/Falcon3-7B-Base',
    'tiiuae/Falcon3-10B-Base',
    'pfnet/plamo-3-nict-2b-base',
    'pfnet/plamo-3-nict-8b-base',
    'pfnet/plamo-3-nict-31b-base',
])

excludes_post = set([
    # Base models
    
    # Post-trained models
    'sbintuitions/sarashina2.2-0.5b-instruct-v0.1',
    'sbintuitions/sarashina2.2-1b-instruct-v0.1',
    'XiaomiMiMo/MiMo-7B-RL',
    'nvidia/NVIDIA-Nemotron-Nano-9B-v2',
    'nvidia/NVIDIA-Nemotron-Nano-12B-v2',
    'Qwen/Qwen3-8B-Base',
    'Qwen/Qwen3-30B-A3B-Base',
])

renames = {
    'tokyotech-llm/Llama3-8b-exp6-LR2.5E-5-MINLR2.5E-6-WD0.1-iter0012500': 'tokyotech-llm/Llama-3-Swallow-8B-v0.1',
    'tokyotech-llm/Llama-3.1-8B-LR2.5e-5-MINLR2.5E-6-WD0.1-iter0027500': 'tokyotech-llm/Llama-3.1-Swallow-8B-v0.1',
    'tokyotech-llm/Llama-3.1-Swallow-8B-v0.2-from-base-LR2.5e-5-MINLR2.5E-6-WD0.1-iter0030000': 'tokyotech-llm/Llama-3.1-Swallow-8B-v0.2',
    'tokyotech-llm/Llama-3-70b-exp6-LR1.0e-5-MINLR1.0E-6-WD0.1-iter0012500': 'tokyotech-llm/Llama-3-Swallow-70B-v0.1',
    'tokyotech-llm/Llama-3.1-70b-LR1.0E-5-MINLR1.0E-6-WD0.1-iter0025000': 'tokyotech-llm/Llama-3.1-Swallow-70B-v0.1',
    'tokyotech-llm/Llama-3.3-70B-v0.1-exp1-LR1.25E-5-iter0037500': 'tokyotech-llm/Llama-3.3-Swallow-70B-v0.4',
    'tokyotech-llm/Llama-3.1-8B-Swallow-v0.5-LR2.5e-5-WD0.1-iter0025000': 'tokyotech-llm/Llama-3.3-Swallow-8B-v0.5',
    'tokyotech-llm/Llama3-8b-exp6-LR2.5E-5-MINLR2.5E-6-WD0.1-iter0012500_chatvec0.5-inst-v1-NEFTune-lr2e-6-GB256': 'tokyotech-llm/Llama-3-Swallow-8B-Instruct-v0.1',
    'tokyotech-llm/Llama-3.1-8B-Instruct-exp2-12-2-LR_2.5e-5_MINLR_2.5e-6_WD_0.1_GC_1-iter_0005490': 'tokyotech-llm/Llama-3.1-Swallow-8B-Instruct-v0.1',
    'tokyotech-llm/Llama-3.1-8B-Instruct-exp3-1-LR_2.5e-5_MINLR_2.5e-6_WD_0.1_GC_1-iter_0005490': 'tokyotech-llm/Llama-3.1-Swallow-8B-Instruct-v0.2',
    'tokyotech-llm/Llama-3-70b-exp6-LR1e-5-MINLR1E-6-WD01-iter0012500_chatvec05-inst-lr1e-6-GB256': 'tokyotech-llm/Llama-3-Swallow-70B-Instruct-v0.1',
    'tokyotech-llm/Llama-3.1-70B-Instruct-exp2-LR_1.75e-5_MINLR_1.75e-6_WD_0.1_GC_1-iter_0005490': 'tokyotech-llm/Llama-3.1-Swallow-70B-Instruct-v0.1',
    'tokyotech-llm/Llama-3.3-Swallow-70B-Instruct-v0.1-stage2-iter_0002500': 'tokyotech-llm/Llama-3.3-Swallow-70B-Instruct-v0.4',
    'tokyotech-llm/llama-3.1-swallow-v0.5-exp3_LR_2.5e-5_MINLR_2.5e-6_WD_0.1_42': 'tokyotech-llm/Llama-3.1-Swallow-8B-Instruct-v0.5',
    'tokyotech-llm/gemma2_2b_exp2-checkpoint-50000-fp32': 'tokyotech-llm/Gemma-2-Llama-Swallow-2b-pt-v0.1',
    'tokyotech-llm/gemma2_9b_exp6-checkpoint-50000': 'tokyotech-llm/Gemma-2-Llama-Swallow-9b-pt-v0.1',
    'tokyotech-llm/gemma2_27b_exp6-checkpoint-50000': 'tokyotech-llm/Gemma-2-Llama-Swallow-27b-pt-v0.1',
    'tokyotech-llm/gemma2_2b_sft_exp3-checkpoint-1495': 'tokyotech-llm/Gemma-2-Llama-Swallow-2b-it-v0.1',
    'tokyotech-llm/gemma2_9b_sft_exp11-checkpoint-1495': 'tokyotech-llm/Gemma-2-Llama-Swallow-9b-it-v0.1',
    'tokyotech-llm/gemma2_27b_sft_exp12-checkpoint-1495': 'tokyotech-llm/Gemma-2-Llama-Swallow-27b-it-v0.1',
    'tokyotech-llm/Qwen-3-Swallow-8B-v0.2-Base-LR1.5E-5-iter0025000': 'tokyotech-llm/Qwen-3-Swallow-8B-CPT-v0.2',
    'tokyotech-llm/Qwen3-Swallow-8B-Instruct-v0.2-exp3-LR1.5E-5-iter0033000': 'tokyotech-llm/Qwen-3-Swallow-8B-SFT-v0.2',
    'tokyotech-llm/Qwen3-Swallow-8B-RL-v0.2_iter_0000800': 'tokyotech-llm/Qwen-3-Swallow-8B-RL-v0.2',
    'tokyotech-llm/Qwen3-Swallow-30B-A3B-v0.2-LR2.5E-5-iter0025000': 'tokyotech-llm/Qwen-3-Swallow-30B-A3B-CPT-v0.2',
    'tokyotech-llm/Qwen3-Swallow-30B-A3B-Instruct-v0.2-exp2-LR1.5E-5-iter0017374': 'tokyotech-llm/Qwen-3-Swallow-30B-A3B-SFT-v0.2',
    'tokyotech-llm/Qwen3-Swallow-30B-A3B-exp2-RL-v0.2_iter_0000800': 'tokyotech-llm/Qwen-3-Swallow-30B-A3B-RL-v0.2',
    'tokyotech-llm/Qwen3-Swallow-32B-v0.2-LR1.0E-5-iter0025000': 'tokyotech-llm/Qwen-3-Swallow-32B-CPT-v0.2',
    'tokyotech-llm/Qwen3-Swallow-32B-Instruct-v0.2-exp2-LR1.0E-5-iter0017374': 'tokyotech-llm/Qwen-3-Swallow-32B-SFT-v0.2',
    'tokyotech-llm/Qwen3-Swallow-32B-exp2-RL-v0.2_iter_0000600': 'tokyotech-llm/Qwen-3-Swallow-32B-RL-v0.2',
    'tokyotech-llm/GPT-OSS-Swallow-20B-v0.1-Instruct-exp1-LR-1.0E-5-iter0017373': 'tokyotech-llm/GPT-OSS-Swallow-20B-SFT-v0.1',
    'tokyotech-llm/GPT-OSS-Swallow-20B-v0.1-Instruct-exp1-RL_iter_0000800': 'tokyotech-llm/GPT-OSS-Swallow-20B-RL-v0.1',
    'tokyotech-llm/GPT-OSS-Swallow-120B-v0.1-Instruct-exp1-LR-1.0E-5-iter0017373': 'tokyotech-llm/GPT-OSS-Swallow-120B-SFT-v0.1',
    'tokyotech-llm/GPT-OSS-Swallow-120B-v0.1-Instruct-exp1-RL_iter_0000652': 'tokyotech-llm/GPT-OSS-Swallow-120B-RL-v0.1',
}

def read_float(x):
    if x is None:
        return 0
    if isinstance(x, str) and x == '#N/A':
        return -0.001
    try:
        if x.find('.') != -1:
            v = float(x)
            return v if 0 <= v else -0.001
        else:
            return int(x)
    except:
        return 0

def read_model_id(x):
    return renames.get(x, x)

def read_base(x):
    return x.replace('非公開', '(private)')

def read_reasoning(x):
    return x.replace('非対応', 'N/A')

def get_sortkey(model):
    name = model['name']
    name = re.sub(r'\d+x\d+[bB]', '', name)
    name = re.sub(r'[\d.]+[bB]', '', name)
    name = name.replace('-', ' ')
    name = name.lower()
    for s in ('base', 'instruct', 'inst', 'chat', ' it'):
        name = name.replace(s, '')
    name = re.sub(r'[ ]+', ' ', name)
    return name.strip()

def get_url(inst):
    if inst['id'].startswith('gpt-') or inst['id'].startswith('o3-'):
        return 'https://platform.openai.com/docs/models'
    elif inst['id'].startswith('deepinfra'):
        return inst['id'].replace('deepinfra', 'https://deepinfra.com/')
    else:
        return 'https://huggingface.co/' + inst['id']

def read_data(fi, F, T, is_post=False, includes=None, excludes=None, num_skips=2):
    # Open the CSV file.
    reader = csv.reader(fi)
    
    # Skip two lines and obtain column names.
    columns = next(reader)
    for i in range(num_skips):
        next(reader)

    # Index for associating CSV columns to fields, which is a tuple of:
    #   category:   category name for a result; None otherwise (basic fields).
    #   field:      field name.
    #   i:          column index of the CSV rows.
    #   func:       function to parse the cell value.
    I = []

    # Basic fields

    # Build the index for extracting basic fields.
    for f in F:
        for i in range(len(columns)):
            if f[1] == columns[i]:
                I.append((None, f[0], i, f[2]))

    # 
    I.append((None, 'sortkey', -1, ''))

    # Update the index to parse results.
    for c, config in T.items():
        for task in config['tasks']:
            for i in range(len(columns)):
                if task['field'] == columns[i]:
                    I.append((c, task['name'], i, read_float))

    # Read the data from the CSV file.
    data = []
    for row in reader:
        if not row[0]:
            break

        inst = {}
        results = {}
        for c, f, i, func in I:
            # Reserve the position of 'id' field.
            if f == 'model_id':
                inst['id'] = ''
            if c is not None:
                results.setdefault(c, {})
                results[c][f] = func(row[i]) if i != -1 else func
            else:
                inst[f] = func(row[i]) if i != -1 else func
        inst['id'] = inst['model_id']
        inst['is_post'] = is_post
        inst['sortkey'] = get_sortkey(inst)
        inst['url'] = get_url(inst)
        inst['results'] = results
        if inst['active_params'] == 0:
            inst['active_params'] = inst['params']

        # Skip models that are registered in the exclude list.
        if excludes is not None and inst['id'] in excludes:
            continue
        # Skip models that are not registered in the include list.
        if includes is not None and inst['id'] not in includes:
            continue

        data.append(inst)

    return data

if __name__ == '__main__':
    data = []

    # Read evaluation results of pre-trained models.
    with open('../_data/task_pre.yml') as fi:
        T = yaml.safe_load(fi)
        F = [
            ('model_id', 'id', read_model_id),
            ('name', 'name', str),
            ('date', 'date', str),
            ('params', 'params', read_float),
            ('active_params', 'active_params', read_float),
            ('family', 'family', str),
            ('base', 'base', read_base),
        ]
        with open('Swallow実験結果 - (Llama-3.x,Gemma-2,3)-Swallow-base-v0.x.csv') as fi:
            data += read_data(fi, F, T, False, includes_pre, num_skips=2)

    # Read evaluation results of post-trained models.
    with open('../_data/task_post.yml') as fi:
        T = yaml.safe_load(fi)
        F = [
            ('model_id', 'id', read_model_id),
            ('name', 'name', str),
            ('date', 'date', str),
            ('params', 'params', read_float),
            ('active_params', 'active_params', read_float),
            ('family', 'family', str),
            ('pre_training', 'base', read_base),
            ('reasoning', 'reasoning mode', read_reasoning),
        ]
        with open('Swallow実験結果 - (Qwen3,GPT-OSS)-Swallow-Instruct.csv') as fi:
            data += read_data(fi, F, T, True, None, excludes_post, num_skips=4)

    # Sort models.
    data.sort(key=operator.itemgetter('sortkey', 'params'))

    print('# Evaluation results in Swallow LLM Leaderboard')
    print('# Copyright (c) 2025 Swallow LLM team')
    print('# This file is distributed under Creative Commons Attribution 4.0 (CC-BY 4.0) License')
    print('')
    print(yaml.dump(data, allow_unicode=True), end='')
