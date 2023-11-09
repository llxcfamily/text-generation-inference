How to build service with text-generation-inference
Step1: git clone
    https://github.com/llxcfamily/text-generation-inference.git
Step2: 下载或copy模型到/models/xxx 目录

Step3: 构建docker镜像，并启动docker
'bash build_tgi_docker.sh'
`bash run_tgi_docker.sh`
cd /workspace/

Step4: 加载模型，启动服务
`bash start_server.sh `

Step5: 请求服务
python server_request.py
