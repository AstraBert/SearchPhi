# Troubleshooting

## `pip` dependencies not installed

You could run into an issue which is similar to [this one](https://github.com/AstraBert/PrAIvateSearch/issues/13): it will seem that the pip dependencies were not installed. Make sure to:

1. Install the latest version of `conda`:

```bash
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
# make sure to run `source ~/.bashrc` if your Linux distro requires it!
```

2. Remove the `praivatesearch` environment and re-build it following the suggested installation:

```bash
conda env remove -n praivatesearch
conda env create -f conda_environment.yaml
```

3. Activate the conda environment and make sure that the activation is smooth:

```bash
conda activate praivatesearch
```

You should now be all set and ready to launch the application!🎉