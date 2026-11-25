import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
import radar

class EditorialTopicGateTests(unittest.TestCase):
    def test_unrelated_gold_price_trend_is_rejected(self):
        self.assertFalse(radar._ok("why is gold price dropping"))
        self.assertFalse(radar._fits("gold prices are falling"))


    def test_finance_blocklist_is_channel_independent(self):
        self.assertFalse(radar._ok("why gold price dropped yesterday"))

    def test_unrelated_market_news_is_rejected(self):
        self.assertFalse(radar._ok("stock market prices are falling"))
        self.assertFalse(radar._fits("crypto market news today"))

    def test_channel_relevant_topic_is_accepted(self):
        if radar.KIDS:
            self.assertTrue(radar._ok("why do plants need sunlight"))
            self.assertTrue(radar._fits("how do plants grow from seeds"))
        else:
            self.assertTrue(radar._ok("how does ChatGPT use context windows"))
            self.assertTrue(radar._fits("how does ChatGPT use context windows"))

    def test_finance_terms_cannot_be_rescued_by_ai_brand_name(self):
        self.assertFalse(radar._ok("NVIDIA stock price is dropping"))
        self.assertFalse(radar._fits("OpenAI shares and market price"))

if __name__ == "__main__":
    unittest.main()
