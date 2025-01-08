import warnings
warnings.filterwarnings("ignore")
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig  
from dotenv import load_dotenv
from chatHistoryUtils import ConversationHistory
from trl import setup_chat_format

load_dotenv()

model_name = "Qwen/Qwen2.5-1.5B-Instruct"
quantization_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True, bnb_4bit_quant_type= "nf4")

device = "cuda" if torch.cuda.is_available() else "cpu"
quantized_model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.bfloat16, quantization_config=quantization_config).to(device)
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.chat_template = None
quantized_model, tokenizer = setup_chat_format(model=quantized_model, tokenizer=tokenizer)


def pipe(prompt: dict, temperature: float, top_p: float, max_new_tokens: int, repetition_penalty: float):
    tokenized_chat = tokenizer.apply_chat_template(prompt, tokenize=True, add_generation_prompt=True, return_tensors="pt").to(device)
    outputs = quantized_model.generate(tokenized_chat, max_new_tokens=max_new_tokens, temperature=temperature, top_p=top_p, repetition_penalty=repetition_penalty).to(device)
    results = tokenizer.decode(outputs[0])
    return results

def text_inference(convo_hist: ConversationHistory):
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
