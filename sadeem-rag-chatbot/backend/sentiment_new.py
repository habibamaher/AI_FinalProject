class SentimentAnalyzer:
    def __init__(self):
        self.positive_words = {
            'good', 'great', 'excellent', 'amazing', 'love', 'thank', 'thanks', 'thank you',
            'happy', 'perfect', 'wonderful', 'fantastic', 'awesome', 'best', 'brilliant',
            'helpful', 'useful', 'satisfied', 'pleased', 'glad', 'appreciate', 'outstanding',
            'superb', 'impressed', 'delighted', 'nice', 'fantastic'
        }
        
        self.negative_words = {
            'bad', 'terrible', 'awful', 'hate', 'poor', 'angry', 'upset',
            'broken', 'waste', 'disappointed', 'frustrating', 'useless', 'horrible', 'worst',
            'complain', 'complaint', 'wrong', 'annoyed', 'disgusted', 'sad', 'unhappy',
            'fail', 'failure', 'dislike'
        }
        
        self.has_bert = False
        logger.info("✓ Sentiment analyzer initialized (lexicon-only, accurate mode)")
    
    def analyze(self, text: str) -> str:
        """Analyze sentiment: positive, negative, or neutral"""
        text_lower = text.lower().strip()
        
        positive_count = 0
        negative_count = 0
        
        # Count positive words
        for word in self.positive_words:
            if ' ' + word + ' ' in ' ' + text_lower + ' ':
                positive_count += text_lower.count(word)
        
        # Count negative words
        for word in self.negative_words:
            if ' ' + word + ' ' in ' ' + text_lower + ' ':
                negative_count += text_lower.count(word)
        
        # Determine sentiment
        if positive_count > 0 and positive_count > negative_count:
            sentiment = 'positive'
        elif negative_count > 0 and negative_count > positive_count:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        logger.info(f"Sentiment: pos={positive_count}, neg={negative_count} -> {sentiment}")
        return sentiment
