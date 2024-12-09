import gradio as gr
from text_inference import text_inference
from image_gen import caption_image
from PIL import Image
from websearching import web_search

def reply(text_input, image_input=None, max_results=5, enable_rag=False):
    if image_input is None:
        prompt, qdrant_success = web_search(text_input, max_results, enable_rag)
        print(qdrant_success)
        results = text_inference(prompt)
        return results
    else:
        if text_input:
            img = Image.fromarray(image_input)
            caption = caption_image(img)
            print(caption)
            print(type(caption))
            full_query = caption +"\n\n"+text_input
            prompt, qdrant_success = web_search(full_query, max_results, enable_rag)
            print(qdrant_success)
            results = text_inference(prompt)
            return results
        else:
            img = Image.fromarray(image_input)
            caption = caption_image(img)
            print(caption)
            print(type(caption))
            prompt, qdrant_success = web_search(caption, max_results, enable_rag)
            print(qdrant_success)
            results = text_inference(prompt)
            return results
        

iface = gr.Interface(fn=reply, inputs=[gr.Textbox(value="",label="Search Query"), gr.Image(value=None, label="Image Search Query"), gr.Slider(1,10,value=5,label="Maximum Number of Search Results"), gr.Checkbox(value=False, label="Enable RAG")], outputs=[gr.Markdown(value="Your output will be generated here", label="Search Results")], title="PrAIvateSearch")

iface.launch(server_name="0.0.0.0", server_port=7860)