from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    pipeline,
    Pipeline,
)
import torch
from typing import Any, cast


class SentimentAnalyzer:
    def __init__(self):
        self.model_name = "ProsusAI/finbert"

        # CPU OPTIMIZATION: Use all available cores
        torch.set_num_threads(torch.get_num_threads())

        print(f"[*] Loading FinBERT on CPU...")
        self.tokenizer = BertTokenizer.from_pretrained(self.model_name)
        self.model = BertForSequenceClassification.from_pretrained(self.model_name)

        # Explicitly set device to -1 for CPU
        self.nlp = cast(
            Pipeline,
            pipeline(
                task="sentiment-analysis",  # type: ignore
                model=self.model,
                tokenizer=self.tokenizer,
                device=-1,  # -1 explicitly forces CPU
            ),
        )
        self.model.eval()

    def analyze_headlines(self, headlines):
        if not headlines:
            return []

        # Use 'inference_mode' to save memory and CPU cycles
        with torch.inference_mode():
            results = self.nlp(headlines)

        processed_results = []
        score_map = {"positive": 1, "neutral": 0, "negative": -1}

        # Track only high-confidence non-neutral scores for the 'Vibe'
        active_scores = []

        for i, res in enumerate(results):
            label = res["label"].lower()
            confidence = res["score"]

            # 1. Apply the Confidence Filter (The Guard)
            # If the model is guessing, we treat it as Neutral (0)
            if confidence > 0.70:
                score_value = score_map.get(label, 0)
            else:
                score_value = 0

            # 2. Add to active_scores ONLY if it's a strong Pos/Neg signal
            # This stops the 'Dave Ramsey' fluff from diluting your average
            if score_value != 0:
                active_scores.append(score_value)

            # 3. Append to results (FIXED: now uses the 'score_value' variable)
            processed_results.append(
                {
                    "headline": headlines[i],
                    "sentiment": label,
                    "confidence": round(confidence, 4),
                    "score_value": score_value,  # Uses your filtered logic now!
                }
            )

        # Calculate a 'Signal Strength' average
        # If active_scores is [ -1 ], the vibe is -1.0 (Strong Alert)
        # instead of -0.12 (Diluted Noise)
        self.final_vibe = (
            sum(active_scores) / len(active_scores) if active_scores else 0
        )

        return processed_results
