# 🤖 Simple AI Agent Generator

A web-based tool to create custom AI agents without writing code. Generate fully functional AI-powered applications with a beautiful web interface in minutes.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [What It Can Do](#-what-it-can-do)
- [What It Cannot Do](#-what-it-cannot-do)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [Supported LLM Providers](#-supported-llm-providers)
- [Available Tools](#-available-tools)
- [Output Formats](#-output-formats)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Examples](#-examples)
- [Troubleshooting](#-troubleshooting)
- [Limitations](#-limitations)
- [License](#license)

---

## Overview

**Simple AI Agent Generator** is a no-code platform that allows you to create custom AI agents through a step-by-step wizard interface. Each generated agent comes with:

- A standalone **web application** (Flask-based UI)
- A **command-line interface** (CLI)
- **Configuration files** for easy customization
- **Pre-built tool integrations** (web scraping, RSS feeds, etc.)

Perfect for creating content summarizers, flashcard generators, email writers, Q&A bots, and more!

---

## Features

| Feature | Description |
|---------|-------------|
| 🎨 **Visual Wizard** | 6-step guided interface to configure your agent |
| 🤖 **Multi-Provider LLM Support** | Google Gemini, Groq, and OpenAI models |
| 🛠️ **Built-in Tools** | Web scraper, RSS reader, text cleaner, file reader |
| 📤 **Multiple Output Formats** | Plain text, JSON, CSV, Markdown, HTML |
| 🌐 **Auto-Generated Web UI** | Each agent gets a beautiful, responsive web interface |
| 💻 **CLI Support** | Command-line interface for terminal users |
| 📝 **Template Library** | Quick-start templates for common use cases |
| ⚙️ **Fully Configurable** | Adjust temperature, max tokens, system prompts |
| 📁 **Clean Code Output** | Well-structured, readable Python code |

---

## ✅ What It Can Do

### Agent Types You Can Create

| Agent Type | Example Use Case |
|------------|------------------|
| **Content Summarizer** | Summarize articles, documents, or web pages |
| **Flashcard Generator** | Create Q&A pairs from study material |
| **Email Writer** | Generate professional emails from bullet points |
| **Q&A Bot** | Answer questions based on provided context |
| **Content Transformer** | Convert content between formats |
| **Text Analyzer** | Analyze sentiment, extract keywords |
| **RSS Digest Creator** | Summarize RSS feed articles |
| **Web Content Processor** | Scrape and process web pages |

### Capabilities

- ✅ Generate standalone Python applications
- ✅ Create web interfaces automatically
- ✅ Support multiple LLM providers
- ✅ Preprocess input with built-in tools
- ✅ Handle multiple input fields
- ✅ Format output in various styles
- ✅ Run agents locally without deployment
- ✅ Customize system prompts and personas
- ✅ Adjust model parameters (temperature, tokens)

---

## ❌ What It Cannot Do

| Limitation | Description |
|------------|-------------|
| **No Multi-Turn Conversations** | Agents are single-request/response, no chat memory |
| **No Agent Chaining** | Cannot connect multiple agents in a pipeline |
| **No Authentication** | Generated apps have no user login system |
| **No Database Storage** | No persistent storage for conversations |
| **No Deployment Tools** | No built-in cloud deployment (local only) |
| **No Fine-Tuning** | Uses pre-trained models only |
| **No Image/Audio Processing** | Text-only input and output |
| **No Real-Time Streaming** | Responses are returned all at once |
| **No Custom Tool Creation** | Limited to 5 pre-built tools |
| **No API Rate Limiting** | No built-in protection against API limits |

---

## Requirements

- **Python 3.8+**
- **pip** (Python package manager)
- **API Key** from at least one provider:
  - Google AI Studio (Gemini) - [Get Key](https://makersuite.google.com/app/apikey)
  - Groq - [Get Key](https://console.groq.com/keys)
  - OpenAI - [Get Key](https://platform.openai.com/api-keys)

---

## Installation

### 1. Clone or Download

```bash
# Create project directory
mkdir ai-agent-generator
cd ai-agent-generator

