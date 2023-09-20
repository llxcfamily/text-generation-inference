import argparse
import json
import requests
import socket

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    group = parser.add_argument_group(title="launch config")
    group.add_argument("--host", type=str, default="127.0.0.1", help="host address")
    group.add_argument("--port", type=int, default="5000", help="port number")
    group.add_argument("--input_file", type=str, default="./test.txt", help="test file")
    group.add_argument("--output_file", type=str, default="./test_out.txt", help="test file")
    return parser.parse_args()

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

def generate(url: str, input_file: str, output_file: str) -> None:
    url = url + "/generate_stream"
    with open(input_file, 'r') as f, open(output_file, 'w') as fw: 
        for input_text in f:
            if input_text.startswith("|||"):
                continue
            req = json.dumps({
                "traceid": 1234567,
                "clientip": socket.gethostname(),
                "inputs": input_text.strip("\n"),
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
                print(req)
                headers = {"Content-Type": "application/json"}
                resp = requests.post(url=url, data=req, verify=False, headers=headers, stream=True)
                if resp.status_code != 200:
                    print("error")
                for output in get_streaming_response(resp):
                    print(output , end='', flush=True)
            except  Exception as e:
                print(f"call error! {e}")


def main():
    args = get_args()
    url = "http://{}:{}".format(args.host, args.port)
    generate(url, args.input_file, args.output_file)


if __name__ == "__main__":
    main()
