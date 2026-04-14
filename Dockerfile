FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1

WORKDIR /app

# System packages commonly needed by ML/NLP libraries.
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	git \
	curl \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

# Install PyTorch CPU wheels first from the official index.
RUN python -m pip install --upgrade pip setuptools wheel && \
	pip install --index-url https://download.pytorch.org/whl/cpu \
	torch==2.3.0 torchvision==0.18.0 torchaudio==2.3.0

# Install the rest of the NLP stack.
RUN pip install -r /app/requirements.txt

# Install PyTorch Geometric and CPU extension wheels.
RUN pip install \
	pyg_lib \
	torch_scatter \
	torch_sparse \
	torch_cluster \
	torch_spline_conv \
	-f https://data.pyg.org/whl/torch-2.3.0+cpu.html && \
	pip install torch-geometric==2.5.3

EXPOSE 8000 8888

CMD ["sleep", "infinity"]
