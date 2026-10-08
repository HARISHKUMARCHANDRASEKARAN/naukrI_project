from transformers import pipeline 
import gradio as gr

model = pipeline("sentiment-analysis")


def predict(text):
    result = model(text)
    return result[0]["label"]


app = gr.Interface(
    fn=predict,
    inputs="text",
    outputs="text",
    title="Sentiment Analyzer"
)

app.launch()