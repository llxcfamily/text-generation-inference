import json
import torch
import streamlit as st
import argparse
import requests
import socket

st.set_page_config(page_title="Baichuan-13B-Chat")
st.title("Baichuan-13B-Chat")

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

def generate(message):
    url = "http://127.0.0.1:5000/generate_stream"
    req = json.dumps({
	"traceid": 1234567,
	"clientip": socket.gethostname(),
	"inputs": message.strip("\n"),
	"parameters": {
	    'top_k': 40,
	    'top_p': 0.7,
	    'temperature': 0.7,
	    'do_sample': True,
	    'best_of': 1,
	    'seed': 42, 
	    'repetition_penalty': 1.0,
	    'max_new_tokens': 512,
	    'details': False,
	}
    })
    try:
        headers = {"Content-Type": "application/json"}
        resp = requests.post(url=url, data=req, verify=False, headers=headers, stream=True)
        if resp.status_code != 200:
            print("error")
        for output in get_streaming_response(resp):
            return output
    except  Exception as e:
        print(f"call error! {e}")


def clear_chat_history():
    del st.session_state.messages


def init_chat_history():
    with st.chat_message("assistant", avatar='🤖'):
        st.markdown("您好，我是百川大模型，很高兴为您服务🥰")

    if "messages" in st.session_state:
        for message in st.session_state.messages:
            avatar = '🧑‍💻' if message["role"] == "user" else '🤖'
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])
    else:
        st.session_state.messages = []

    return st.session_state.messages


def main():
    messages = init_chat_history()
    
    if prompt := st.chat_input("Shift + Enter 换行, Enter 发送"):
        with st.chat_message("user", avatar='🧑‍💻'):
            st.markdown(prompt)
        messages.append({"role": "user", "content": prompt})
        print(f"[user] {prompt}", flush=True)
        with st.chat_message("assistant", avatar='🤖'):
            placeholder = st.empty()
            for response in generate(messages):
                placeholder.markdown(response)
                if torch.backends.mps.is_available():
                    torch.mps.empty_cache()
        messages.append({"role": "assistant", "content": response})
        print(json.dumps(messages, ensure_ascii=False), flush=True)

        st.button("清空对话", on_click=clear_chat_history)


if __name__ == "__main__":
    main()
