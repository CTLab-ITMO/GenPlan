FROM python:3.11

RUN apt-get update && apt-get install --no-install-recommends -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

WORKDIR /GenPlan

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "-u", "-W", "ignore", "pipeline.py"]
