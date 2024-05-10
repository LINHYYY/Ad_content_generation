from fastapi import FastAPI, Request
from transformers import AutoTokenizer, AutoModel
import uvicorn, json, datetime
import torch, os
from transformers import AutoConfig

DEVICE = "cuda"
DEVICE_ID = "0"
CUDA_DEVICE = f"{DEVICE}:{DEVICE_ID}" if DEVICE_ID else DEVICE


def torch_gc(): # clear tensor caching
    if torch.cuda.is_available():
        with torch.cuda.device(CUDA_DEVICE):
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()


app = FastAPI()


@app.post("/")
async def create_item(request: Request): # Handle POST requests and create functions with asynchronous APIs
    global model, tokenizer
    json_post_raw = await request.json()
    json_post = json.dumps(json_post_raw)
    json_post_list = json.loads(json_post)
    prompt = json_post_list.get('prompt')
    history = json_post_list.get('history')
    max_length = json_post_list.get('max_length')
    top_p = json_post_list.get('top_p')
    temperature = json_post_list.get('temperature')
    response, history = model.chat(tokenizer,
                                   prompt,
                                   history=history,
                                   max_length=max_length if max_length else 2048,
                                   top_p=top_p if top_p else 0.7,
                                   temperature=temperature if temperature else 0.95)
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    answer = {
        "response": response,
        "history": history,
        "status": 200,
        "time": time
    }
    log = "[" + time + "] " + '", prompt:"' + prompt + '", response:"' + repr(response) + '"'
    print(log)
    torch_gc()
    return answer

'''
if __name__ == '__main__':
    uvicorn.run('api:app', host='0.0.0.0', port=8000, workers=1)

history = []
tokenizer = AutoTokenizer.from_pretrained("model", trust_remote_code=True)
model = AutoModel.from_pretrained("model", trust_remote_code=True).quantize(4).half().cuda()
model.eval()
'''
# 24.4.22 linghy Fine-tuning deployment successful
if __name__ == '__main__':
    uvicorn.run('api:app', host='0.0.0.0', port=8000, workers=1)

history = []
tokenizer = AutoTokenizer.from_pretrained("model", trust_remote_code=True)
config = AutoConfig.from_pretrained("model", trust_remote_code=True, pre_seq_len = 128)
 # pre_seq_len needs to be consistent with the actual value of train

model = AutoModel.from_pretrained("model", config=config, trust_remote_code=True).quantize(4).half().cuda()
prefix_state_dict = torch.load(os.path.join("output\lr-le-2\checkpoint-3000", "pytorch_model.bin")) # Fine-tuning the model's intervention
new_prefix_state_dict = {}
for k, v in prefix_state_dict.items():
    new_prefix_state_dict[k[len("transformer.prefix_encoder."):]] = v
model.transformer.prefix_encoder.load_state_dict(new_prefix_state_dict)

model = model.eval()

