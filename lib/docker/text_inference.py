import warnings
warnings.filterwarnings("ignore")

import accelerate

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig  
from dotenv import load_dotenv
from memory import ConversationHistory, PGClient
import os
import random as r
from trl import setup_chat_format

load_dotenv()

model_name = "/app/qwen/"
quantization_config = BitsAndBytesConfig(load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type= "nf4"
)

quantized_model = AutoModelForCausalLM.from_pretrained(model_name, device_map="cuda:0", torch_dtype=torch.bfloat16,quantization_config=quantization_config)
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.chat_template = None
quantized_model, tokenizer = setup_chat_format(model=quantized_model, tokenizer=tokenizer)



pg_db = os.getenv("PG_DB")
pg_user = os.getenv("PG_USER")
pg_psw = os.getenv("PG_PASSWORD")

pg_conn_str = f"postgresql://{pg_user}:{pg_psw}@localhost:5432/{pg_db}"
pg_client = PGClient(pg_conn_str)

usr_id = r.randint(1,10000)
convo_hist = ConversationHistory(pg_client, usr_id)
convo_hist.add_message(role="system", content="You are a web searching assistant: your task is to create a human-readable content based on a JSON representation of the keywords of several websites related to the search that the user performed and on the context that you are provided with")

def pipe(prompt: str, temperature: float, top_p: float, max_new_tokens: int, repetition_penalty: float):
    tokenized_chat = tokenizer.apply_chat_template(prompt, tokenize=True, add_generation_prompt=True, return_tensors="pt")
    outputs = quantized_model.generate(tokenized_chat, max_new_tokens=max_new_tokens, temperature=temperature, top_p=top_p, repetition_penalty=repetition_penalty) 
    results = tokenizer.decode(outputs[0])
    return results

def text_inference(message):
    convo_hist.add_message(role="user", content=message)
    prompt = convo_hist.get_conversation_history()
    res = pipe(
        prompt,
        temperature=0.1,
        top_p=1,
        max_new_tokens=512,
        repetition_penalty=1.2
    )
    ret = res.split("<|im_start|>assistant\n")[1]
    convo_hist.add_message(role="assistant", content=ret)
    return ret
