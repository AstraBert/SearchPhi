<h1 align="center">PrAIvateSearch</h1>
<h2 align="center">Own your AI, search the web with it🌐😎</h2>

<div align="center">
   <div>
        <img src="./imgs/PrAIvateSearch_logo.png" alt="Logo" align="center">
   </div>
</div>


## About PrAIvateSearch

PrAIvateSearch is a Gradio application that aims to implement similar features to SearchGPT, but in an open-source, local and private way. 

## Flowchart

<div align="center">
    <img src="./imgs/PrAIvateSearch_Flowchart.png" alt="Logo" align="center">
    <p><i>Flowchart for PrAIvateSearch</i></p>
</div>

The process of creating and the functioning of PrAIvateSearch is explained in this [blog post on HuggingFace](https://huggingface.co/blog/as-cle-bert/build-an-ai-powered-search-engine-from-scratch).

## Installation and usage


1. Clone the repository:

```bash
git clone https://github.com/AstraBert/PrAIvateSearch.git
cd PrAIvateSearch
```

2. Move `.env.example` to `.env`...

```bash
mv .env.example .env
```

...and specify PostgreSQL related variables:

```bash
# .env file
PG_DB="postgres"
PG_USER="pgql_usr"
PG_PASSWORD="pgql_psw"
```


3. Install necessary dependencies:
  - Linux:
```bash
python3 -m venv /path/to/SearchPhi
source /path/to/SearchPhi/bin/activate
python3 -m pip install -r requirements.txt
```
  - Windows:
```bash
python3 -m venv c:\path\to\SearchPhi
c:\path\to\SearchPhi\Scripts\activate  # For Command Prompt
# or
c:\path\to\SearchPhi\Scripts\Activate.ps1  # For PowerShell
# or
source c:\path\to\SearchPhi\Scripts\activate  # For Git

python3 -m pip install -r requirements.txt
```

4. Start third-party services:

```bash
docker compose up -d
```

5. Run the application:

```bash
python3 scripts/app.py
```

Once the models will be downloaded and loaded on your hardware, you'll see the application on `http://localhost:7860`.

**PROs**: You can customize the application code (change the model, change CPU/GPU settings, change generation kwargs, modify the app interface...)

**CONs**: Longer and more complex installation process

### Usage note

> ⚠️ _The Gradio application was successfully developed and tested on a Windows 10.0.22631 machine, with 32GB RAM, 16 core CPU and Nvidia GEFORCE RTX4050 GPU (6GB, cuda version 12.3), python version 3.11.9_

Although being at a good stage of development, the application is a `beta` and might still contain bugs and have OS/hardware/python version incompatibilities.

## Demo

Here's a video demo of what it can do:

![Video demo for SearechPhi](./imgs/demo.gif)

## Contributions

Contributions are more than welcome! See [contribution guidelines](./CONTRIBUTING.md) for more information :)

## Funding

If you found this project useful, please consider to [fund it](https://github.com/sponsors/AstraBert) and make it grow: let's support open-source together!😊

## License and rights of usage

This project is provided under [MIT license](./LICENSE): it will always be open-source and free to use.

If you use this project, please cite the author: [Astra Clelia Bertelli](https://astrabert.vercel.app)


