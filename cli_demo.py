import os
import torch
import platform
import subprocess
from colorama import Fore, Style
from tempfile import NamedTemporaryFile
import json
import torch
import streamlit as st
import argparse
import requests
import socket
from transformers import AutoTokenizer, LlamaTokenizer, MarianMTModel, MarianTokenizer

st.set_page_config(page_title="LLM-CHAT-DEMO")
st.title("LLM-CHAT-DEMO")

tokenizer=LlamaTokenizer.from_pretrained("decapoda-research/llama-7b-hf", padding_side="left")
max_context_len=256

def get_streaming_response(response):
    for chunk in response.iter_lines():
        if chunk == b"\n":
            continue
        if chunk:
            payload = chunk.decode('utf-8')
            if payload.startswith("data:"):
                data = json.loads(payload.lstrip("data:").rstrip("/n"))
                output = data.pop('token', '')['text']
                yield output

def get_prompt(messages):
    q_list=[]
    a_list=[]
    for i in range(len(messages)-1, -1, -1):
        if messages[i].get('role') == "user":
            q = messages[i].get('content')
            q_list.append(q)
        else:
            a = messages[i].get('content')
            a_list.append(a)
    
    curr_question = q_list[0]
    q_list = q_list[1:]
    sum_len = 0
    q_res_list = []
    a_res_list = []
    for q,a in zip(q_list, a_list):
        messages_tokens = tokenizer(q + "<QA_SEP>" + a, return_tensors="pt")
        num_input_tokens = messages_tokens["input_ids"].shape[1]
        sum_len += int(num_input_tokens)
        global max_context_len
        if sum_len < max_context_len:
            q_res_list.append(q)
            a_res_list.append(a)
        else:
            remain_len = int(max_context_len - sum_len + num_input_tokens)
            messages_tok_cut = messages_tokens["input_ids"][:, : remain_len]
            messages_cut = tokenizer.decode(messages_tok_cut, skip_special_tokens=True)
            split_tokens = messages_cut.split("<QA_SEP>")
            if len(split_tokens) == 2:
                q = split_tokens[0]
                a = split_tokens[1]
                q_res_list.append(q)
                a_res_list.append(a)
                break
    assert(len(q_res_list) == len(a_res_list))
    prompt = ""
    for i in range(len(q_res_list) - 1, -1, -1):
        prompt += "user: " + q_res_list[i] + " assitant:" + a_res_list[i] + " </s> "
    prompt += "user: " + curr_question + " assitant:"
    return prompt


def generate(messages):
    input_text = get_prompt(messages)
    url = "http://127.0.0.1:5000/generate_stream"
    req = json.dumps({
	"traceid": 1234567,
	"clientip": socket.gethostname(),
	"inputs": input_text,
	"parameters": {
	    'top_k': 40,
	    'top_p': 0.7,
	    'temperature': 0.7,
	    'do_sample': True,
	    'best_of': 1,
	    'seed': 42, 
	    'repetition_penalty': 1.0,
	    'max_new_tokens': 32,
	    'details': False,
	}
    })
    try:
        print(req)
        headers = {"Content-Type": "application/json"}
        resp = requests.post(url=url, data=req, verify=False, headers=headers, stream=True)
        if resp.status_code != 200:
            print("error")
        for output in get_streaming_response(resp):
            yield output
    except  Exception as e:
        print(f"call error! {e}")

def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
    print(Fore.YELLOW + Style.BRIGHT + "欢迎使用LLM-CHAT-DEMO大模型，输入进行对话，vim 多行输入，clear 清空历史，CTRL+C 中断生成，stream 开关流式生成，exit 结束。")
    return []


def vim_input():
    with NamedTemporaryFile() as tempfile:
        tempfile.close()
        subprocess.call(['vim', '+star', tempfile.name])
        text = open(tempfile.name).read()
    return text


def main(stream=True):
    messages = clear_screen()
    while True:
        prompt = input(Fore.GREEN + Style.BRIGHT + "\n用户：" + Style.NORMAL)
        if prompt.strip() == "exit":
            break
        if prompt.strip() == "clear":
            messages = clear_screen()
            continue
        if prompt.strip() == 'vim':
            prompt = vim_input()
            print(prompt)
        print(Fore.CYAN + Style.BRIGHT + "\nBaichuan：" + Style.NORMAL, end='')
        if prompt.strip() == "stream":
            stream = not stream
            print(Fore.YELLOW + "({}流式生成)\n".format("开启" if stream else "关闭"), end='')
            continue
        messages.append({"role": "user", "content": prompt})
        result = ""
        if stream:
            try:
                for response in generate(messages):
                    result += response
                    print(response, end='', flush=True)
                    if torch.backends.mps.is_available():
                        torch.mps.empty_cache()
            except KeyboardInterrupt:
                pass
            print()
        messages.append({"role": "assistant", "content": result})
    print(Style.RESET_ALL)


if __name__ == "__main__":
    main()
