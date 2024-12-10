import warnings
warnings.filterwarnings("ignore")

import gradio as gr
from text_inference import text_inference
from image_gen import caption_image
from PIL import Image
from websearching import web_search, date_for_debug

def reply(text_input, image_input=None, max_results=5, enable_rag=False, debug = True):
    if debug:
        print(f"[{date_for_debug()}] Started query processing...")
    if image_input is None:
        prompt, qdrant_success = web_search(text_input, max_results, enable_rag, debug)
        if debug:
            print(qdrant_success)
        results = text_inference(prompt, debug)
        results = results.replace("<|im_end|>","")
        if debug:
            print(f"[{date_for_debug()}] Finished query processing!")
        return results
    else:
        if text_input:
            img = Image.fromarray(image_input)
            caption = caption_image(img)
            full_query = caption +"\n\n"+text_input
            prompt, qdrant_success = web_search(full_query, max_results, enable_rag)
            if debug:
                print(qdrant_success)
            results = text_inference(prompt, debug)
            results = results.replace("<|im_end|>","")
            if debug:
                print(f"[{date_for_debug()}] Finished query processing!")
            return results
        else:
            img = Image.fromarray(image_input)
            caption = caption_image(img)
            prompt, qdrant_success = web_search(caption, max_results, enable_rag)
            if debug:
                print(qdrant_success)
            results = text_inference(prompt, debug)
            results = results.replace("<|im_end|>","")
            if debug:
                print(f"[{date_for_debug()}] Finished query processing!")
            return results
        

iface = gr.Interface(fn=reply, inputs=[gr.Textbox(value="",label="Search Query"), gr.Image(value=None, label="Image Search Query"), gr.Slider(1,10,value=5,label="Maximum Number of Search Results", step=1), gr.Checkbox(value=False, label="Enable RAG"), gr.Checkbox(value=True, label="Debug")], outputs=[gr.Markdown(value="Your output will be generated here", label="Search Results")], title="PrAIvateSearch")

iface.launch(server_name="0.0.0.0", server_port=7860)