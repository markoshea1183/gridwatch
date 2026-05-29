import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


def line_chart(df: pd.DataFrame, x: str, y: str, title: str, xlabel: str, ylabel: str):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df[x], df[y], linewidth=1.5)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)


def scatter_chart(df: pd.DataFrame, x: str, y: str, title: str, xlabel: str, ylabel: str):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df[x], df[y], alpha=0.2, s=10)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)


def histogram(df: pd.DataFrame, col: str, title: str, xlabel: str, bins: int = 100):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(df[col].dropna(), bins=bins, edgecolor="none")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Frequency")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)


def stacked_area(df: pd.DataFrame, title: str, xlabel: str, ylabel: str):
    """df index = time axis, columns = categories to stack."""
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.stackplot(df.index, df.T.values, labels=df.columns, alpha=0.85)
    ax.legend(loc="upper left", fontsize=8)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)
