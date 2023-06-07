FROM python:3.8
        EXPOSE 8501
        WORKDIR /st_agraph.py
        COPY requirements.txt ./requirements.txt
        RUN pip3 install -r requirements.txt
        COPY . .
        CMD streamlit run st_agraph.py
        