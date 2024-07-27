## Imports
from llama_cpp import Llama
import re

## Instantiate model from downloaded file
llm = Llama(
    model_path="model/Phi-3-mini-4k-instruct-q4.gguf",
    n_ctx=4096,  # Context length to use
    n_threads=14,            # Number of CPU threads to use
    n_gpu_layers=3        # Number of model layers to offload to GPU
)

## Generation kwargs
generation_kwargs = {
    "max_tokens":1024,
    "stop":["<|end|>"],
    "echo":False, # Echo the prompt in the output
    "top_k":1 # This is essentially greedy decoding, since the model will always return the highest-probability token. Set this value > 1 for sampling decoding
}

def run_inference_lcpp(jsonstr, user_search):
    prompt = f"""Instructions for the assistant: Starting from the URLs and the keywords deriving from Google search results and provided to you in JSON format, generate a meaningful summary of the search results that satisfies the user's query.
    URLs and keywords in JSON format: {jsonstr}.
    User's query to satisfy: {user_search}"""
    res = llm(prompt, **generation_kwargs)
    response = res["choices"][0]["text"]
    jsondict = eval(jsonstr)
    addon = "Reference websites:\n- "+ '\n- '.join(list(jsondict.keys()))
    input_string = response.replace("<|assistant|>", "") + "\n\n" + addon
    frag_res = re.findall(r'\w+|\s+|[^\w\s]', input_string)
    for word in frag_res:
        yield word

if __name__ == "__main__":
    prompt = """Context: A vector database, vector store or vector search engine is a database that can store vectors (fixed-length lists of numbers) along with other data items. Vector databases typically implement one or more Approximate Nearest Neighbor (ANN) algorithms,[1][2] so that one can search the database with a query vector to retrieve the closest matching database records.

    Vectors are mathematical representations of data in a high-dimensional space. In this space, each dimension corresponds to a feature of the data, with the number of dimensions ranging from a few hundred to tens of thousands, depending on the complexity of the data being represented. A vector's position in this space represents its characteristics. Words, phrases, or entire documents, as well as images, audio, and other types of data, can all be vectorized; Prompt: Describe what is a vector database"""
    res = llm(prompt, **generation_kwargs) # Res is a dictionary

    ## Unpack and the generated text from the LLM response dictionary and print it
    print(res["choices"][0]["text"])
    # res is short for result