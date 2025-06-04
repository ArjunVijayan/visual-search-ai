# 🧠 Visual Search System using Multimodal LLMs

## 📌 Overview

This project implements an intelligent image search system that leverages **multimodal Large Language Models (LLMs)** to analyze images, generate high-quality captions, index them in a **vector database**, and enable natural language queries that return relevant images **with reasoning**.

---

## 🔍 Features

- **Multimodal Image Understanding** using vision-capable LLMs (e.g., OpenAI GPT-4V, CLIP)
- **Image Captioning**: Automatically generate meaningful, descriptive captions
- **Image-to-Caption Mapping**: Associate captions with image paths
- **Vector Indexing**: Store and search image descriptions using vector embeddings
- **Natural Language Querying**: Users can search with flexible prompts
- **Explainable Search**: Returns relevant image(s) with a brief reason why it matched

---

## ⚙️ Architecture

```text
          +---------------+            +------------------+
          |   Image Dir   |---> Loop ->|  Multimodal LLM  |---+
          +---------------+            +------------------+   |
                                                        |     v
                                                +---------------+
                                                |  Caption Text |
                                                +-------+-------+
                                                        |
                                       +----------------v----------------+
                                       | Map Caption <-> Image Path      |
                                       +----------------+----------------+
                                                        |
                                       +----------------v----------------+
                                       |         Vector Embedding
                                       +----------------+----------------+
                                                        |
                                       +----------------v----------------+
                                       |         Vector Database
                                       +----------------+----------------+
                                                        |
                                       +----------------v----------------+
                                       | Natural Language Query Processor|
                                       +----------------+----------------+
                                                        |
                                       +----------------v----------------+
                                       |   Retrieve Matches + Reasoning  |
                                       +---------------------------------+
