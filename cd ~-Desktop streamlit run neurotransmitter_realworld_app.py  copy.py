import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import time
from PIL import Image
import base64
import io

# Set page configuration
st.set_page_config(
    page_title="Neurotransmitter Explorer",
    page_icon="🧠",
    layout="wide"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    .profile-img {
        border-radius: 50%;
        width: 100px;
        height: 100px;
        object-fit: cover;
        border: 3px solid #4CAF50;
        margin: 0 auto;
        display: block;
    }
    .header {
        text-align: center;
        color: #2196F3;
        padding: 10px;
    }
    .disorder-card {
        background-color: #f0f8ff;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin: 10px 0;
    }
    .progress-container {
        background-color: #e0e0e0;
        border-radius: 10px;
        margin: 10px 0;
    }
    .progress-bar {
        height: 20px;
        border-radius: 10px;
        transition: width 0.5s ease-in-out;
    }
    .positive { background-color: #4CAF50; }
    .negative { background-color: #F44336; }
    .neutral { background-color: #FFC107; }
    .severe-negative { background-color: #D32F2F; }
    .severe-positive { background-color: #388E3C; }
</style>
""", unsafe_allow_html=True)

# Real-world neurotransmitter directionality data for psychological disorders
data = {
    "Major Depression": {
        "Dopamine": "↓", "Serotonin": "↓", "Norepinephrine": "↓", "Acetylcholine": "→",
        "GABA": "↓", "Glutamate": "↑", "Glycine": "→", "Substance P": "↑", "Endorphins": "↓", "CGRP": "→"
    },
    "Bipolar Disorder (Mania)": {
        "Dopamine": "↑", "Serotonin": "↓", "Norepinephrine": "↑", "Acetylcholine": "→",
        "GABA": "↓", "Glutamate": "↑", "Glycine": "→", "Substance P": "→", "Endorphins": "→", "CGRP": "→"
    },
    "Bipolar Disorder (Depression)": {
        "Dopamine": "↓", "Serotonin": "↓", "Norepinephrine": "↓", "Acetylcholine": "→",
        "GABA": "↓", "Glutamate": "→", "Glycine": "→", "Substance P": "→", "Endorphins": "↓", "CGRP": "→"
    },
    "Schizophrenia": {
        "Dopamine": "↑", "Serotonin": "→", "Norepinephrine": "→", "Acetylcholine": "→",
        "GABA": "↓", "Glutamate": "↑", "Glycine": "→", "Substance P": "→", "Endorphins": "→", "CGRP": "→"
    },
    "Anxiety Disorders": {
        "Dopamine": "→", "Serotonin": "↓", "Norepinephrine": "↑", "Acetylcholine": "→",
        "GABA": "↓", "Glutamate": "↑", "Glycine": "→", "Substance P": "↑", "Endorphins": "↓", "CGRP": "↑"
    },
    "ADHD": {
        "Dopamine": "↓", "Serotonin": "↓", "Norepinephrine": "↓", "Acetylcholine": "→",
        "GABA": "→", "Glutamate": "→", "Glycine": "→", "Substance P": "→", "Endorphins": "→", "CGRP": "→"
    },
    "Parkinson's Disease": {
        "Dopamine": "↓↓", "Serotonin": "→", "Norepinephrine": "↓", "Acetylcholine": "↑",
        "GABA": "→", "Glutamate": "→", "Glycine": "→", "Substance P": "↓", "Endorphins": "↓", "CGRP": "→"
    },
    "Alzheimer's Disease": {
        "Dopamine": "→", "Serotonin": "→", "Norepinephrine": "→", "Acetylcholine": "↓",
        "GABA": "→", "Glutamate": "↑", "Glycine": "→", "Substance P": "↓", "Endorphins": "↓", "CGRP": "→"
    },
    "Autism Spectrum": {
        "Dopamine": "→", "Serotonin": "↑", "Norepinephrine": "→", "Acetylcholine": "→",
        "GABA": "↓", "Glutamate": "↑", "Glycine": "→", "Substance P": "→", "Endorphins": "→", "CGRP": "→"
    },
    "Seizure Disorders": {
        "Dopamine": "→", "Serotonin": "→", "Norepinephrine": "→", "Acetylcholine": "→",
        "GABA": "↓", "Glutamate": "↑", "Glycine": "→", "Substance P": "→", "Endorphins": "→", "CGRP": "→"
    },
    "Huntington Disease": {
        "Dopamine": "↓", "Serotonin": "→", "Norepinephrine": "→", "Acetylcholine": "→",
        "GABA": "↓", "Glutamate": "↑", "Glycine": "→", "Substance P": "→", "Endorphins": "→", "CGRP": "→"
    }
}

# Convert data to DataFrame
df = pd.DataFrame(data).T
df.index.name = 'Disorder'

# Function to map directionality to numerical values
def map_directionality(val):
    if val == "↑":
        return 1
    elif val == "↓":
        return -1
    elif val == "→":
        return 0
    elif val == "↓↓":
        return -2
    elif val == "↑↑":
        return 2
    else:
        return 0

# Create numerical DataFrame
df_numeric = df.map(map_directionality)

# Function to create progress bar visualization
def create_progress_bar(value, label):
    # Normalize value to 0-100 scale for display
    normalized = abs(value) * 25  # Scale -2 to 2 -> 0 to 100
    percentage = min(normalized, 100)
    
    # Determine color class
    if value > 1:
        color_class = "severe-positive"
    elif value > 0:
        color_class = "positive"
    elif value < -1:
        color_class = "severe-negative"
    elif value < 0:
        color_class = "negative"
    else:
        color_class = "neutral"
    
    # Create progress bar HTML
    progress_html = f"""
    <div class="progress-container">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span>{label}</span>
            <span>{'↑↑' if value > 1 else '↑' if value > 0 else '↓↓' if value < -1 else '↓' if value < 0 else '→'}</span>
        </div>
        <div style="background-color: #e0e0e0; border-radius: 10px; height: 20px;">
            <div class="progress-bar {color_class}" style="width: {percentage}%; height: 20px; border-radius: 10px;"></div>
        </div>
    </div>
    """
    return progress_html

# Function to convert image to base64 for embedding
def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        # Return a default base64 encoded image if file not found
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="

# Main app
st.markdown("<h1 class='header'>🧠 Neurotransmitter Explorer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Interactive visualization of neurotransmitter levels in psychological disorders</p>", unsafe_allow_html=True)

# Profile section
col1, col2, col3 = st.columns([1,2,1])
with col2:
    # Add your photo here - replace 'profile.jpg' with your actual image path
    try:
        # Try to load user's profile image
        profile_img = Image.open('profile.jpg')
        st.image(profile_img, caption="Neuroscience Researcher", width=100, clamp=True)
    except:
        # Default profile placeholder
        st.markdown(f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAYAAACtWK6eAAAABmJLR0QA/wD/AP+gvaeTAAABZklEQVR4nO3dMU4DMRBG4Z8jEi1wCg6D6DgG0XIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6DgG0nIMpOMYdJyD6......" width="100">
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-weight: bold;'>Your Name</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.9em; color: #666;'>Neuroscience Researcher</p>", unsafe_allow_html=True)

# Disorder selection
st.sidebar.header("🔍 Disorder Selection")
selected_disorder = st.sidebar.selectbox(
    "Select a Disorder:",
    options=list(df.index),
    index=0
)

# Animation speed control
animation_speed = st.sidebar.slider("Animation Speed (ms)", 100, 1000, 300)

# Information about selected disorder
st.sidebar.markdown("---")
st.sidebar.subheader("ℹ️ Disorder Information")
disorder_info = {
    "Major Depression": "Characterized by persistent sadness, loss of interest, and cognitive impairments.",
    "Bipolar Disorder (Mania)": "Periods of elevated mood, increased energy, and impulsive behavior.",
    "Bipolar Disorder (Depression)": "Depressive episodes alternating with manic periods.",
    "Schizophrenia": "A mental disorder characterized by disruptions in thought processes and perceptions.",
    "Anxiety Disorders": "Excessive fear or anxiety that interferes with daily activities.",
    "ADHD": "Persistent pattern of inattention and/or hyperactivity-impulsivity.",
    "Parkinson's Disease": "Progressive nervous system disorder affecting movement.",
    "Alzheimer's Disease": "Progressive brain disorder that affects memory and thinking skills.",
    "Autism Spectrum": "Developmental disorder affecting communication and behavior.",
    "Seizure Disorders": "Conditions characterized by recurrent seizures.",
    "Huntington Disease": "Inherited disease causing progressive breakdown of nerve cells."
}
st.sidebar.info(disorder_info.get(selected_disorder, "No information available."))

# Main content area
st.markdown(f"<div class='disorder-card'><h2 style='margin: 0;'>{selected_disorder}</h2></div>", unsafe_allow_html=True)

# Get data for selected disorder
disorder_data = df.loc[selected_disorder]
disorder_numeric = df_numeric.loc[selected_disorder]

# Create columns for metrics
cols = st.columns(2)

# Display key metrics
with cols[0]:
    st.markdown("<div class='metric-card'><h3>Neurotransmitter Levels</h3></div>", unsafe_allow_html=True)
    
    # Create progress bars with animation effect
    for neurotransmitter, value in disorder_numeric.items():
        # Simulate loading animation
        progress_bar = st.empty()
        for i in range(0, int(abs(value) * 25) + 1, 5):
            progress_html = f"""
            <div class="progress-container">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span>{neurotransmitter}</span>
                    <span>{'↑↑' if value > 1 else '↑' if value > 0 else '↓↓' if value < -1 else '↓' if value < 0 else '→'}</span>
                </div>
                <div style="background-color: #e0e0e0; border-radius: 10px; height: 20px;">
                    <div class="progress-bar {'severe-positive' if value > 1 else 'positive' if value > 0 else 'severe-negative' if value < -1 else 'negative' if value < 0 else 'neutral'}" 
                         style="width: {i}%; height: 20px; border-radius: 10px;"></div>
                </div>
            </div>
            """
            progress_bar.markdown(progress_html, unsafe_allow_html=True)
            time.sleep(animation_speed/1000)
        
        # Final display
        final_html = create_progress_bar(value, neurotransmitter)
        progress_bar.markdown(final_html, unsafe_allow_html=True)

with cols[1]:
    st.markdown("<div class='metric-card'><h3>Level Summary</h3></div>", unsafe_allow_html=True)
    
    # Calculate summary statistics
    increased = sum(1 for v in disorder_numeric if v > 0)
    decreased = sum(1 for v in disorder_numeric if v < 0)
    neutral = sum(1 for v in disorder_numeric if v == 0)
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Increased", increased, "levels")
    col2.metric("Decreased", decreased, "levels")
    col3.metric("Neutral", neutral, "levels")
    
    # Visualization
    st.markdown("### Level Distribution")
    fig, ax = plt.subplots(figsize=(8, 6))
    levels = ['↑↑', '↑', '→', '↓', '↓↓']
    counts = [
        sum(1 for v in disorder_numeric if v == 2),
        sum(1 for v in disorder_numeric if v == 1),
        sum(1 for v in disorder_numeric if v == 0),
        sum(1 for v in disorder_numeric if v == -1),
        sum(1 for v in disorder_numeric if v == -2)
    ]
    
    colors = ['#388E3C', '#4CAF50', '#FFC107', '#F44336', '#D32F2F']
    bars = ax.bar(levels, counts, color=colors)
    ax.set_xlabel('Directionality')
    ax.set_ylabel('Count')
    ax.set_title('Neurotransmitter Level Distribution')
    
    # Add value labels on bars
    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                str(count), ha='center', va='bottom')
    
    st.pyplot(fig)

# Detailed data table
st.markdown("---")
st.subheader("📋 Detailed Data")
st.dataframe(df.loc[[selected_disorder]].style.map(
    lambda x: "background-color: #FFEBEE" if x in ["↓", "↓↓"] else 
             ("background-color: #E8F5E9" if x in ["↑", "↑↑"] else 
             "background-color: #FFFDE7")
))

# Legend
st.markdown("---")
st.markdown("### 📖 Legend")
legend_cols = st.columns(5)
legend_cols[0].markdown("**↑↑** - Severely Increased")
legend_cols[1].markdown("**↑** - Increased")
legend_cols[2].markdown("**→** - Neutral/Variable")
legend_cols[3].markdown("**↓** - Decreased")
legend_cols[4].markdown("**↓↓** - Severely Decreased")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #999; font-size: 0.8em;'>Neurotransmitter Explorer v1.0 | Data based on peer-reviewed research</p>", unsafe_allow_html=True)