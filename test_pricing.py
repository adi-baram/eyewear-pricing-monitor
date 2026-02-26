"""Unit tests for the Eyewear Pricing Monitor."""

import unittest

from scraper import extract_search_queries, parse_search_results
from matcher import normalize_upc, extract_model_number, match_product
from pricing import suggest_price


class TestSearchQueryExtraction(unittest.TestCase):
    def test_standard_model(self):
        queries = extract_search_queries("Burberry BE2108 Black")
        self.assertEqual(queries[0], "Burberry BE2108 eyeglasses")
        self.assertIn("Burberry 2108 eyeglasses", queries)

    def test_two_word_brand(self):
        queries = extract_search_queries("Armani Exchange AX3016 Black")
        self.assertEqual(queries[0], "Armani Exchange AX3016 eyeglasses")
        self.assertIn("Armani Exchange 3016 eyeglasses", queries)

    def test_model_with_slash_generates_base_model(self):
        queries = extract_search_queries("Adidas AOM001O/N Blue/Black")
        self.assertEqual(queries[0], "Adidas AOM001O/N eyeglasses")
        self.assertIn("Adidas AOM001O eyeglasses", queries)

    def test_multi_color_product(self):
        queries = extract_search_queries("Coach HC6065 Tortoise, Brown")
        self.assertEqual(queries[0], "Coach HC6065 eyeglasses")
        self.assertIn("Coach 6065 eyeglasses", queries)

    def test_sunglasses_detection(self):
        queries = extract_search_queries("Kate Spade Avaline2/S Gold")
        self.assertEqual(queries[0], "Kate Spade Avaline2/S sunglasses")
        self.assertIn("Kate Spade Avaline2 sunglasses", queries)

    def test_tory_burch_stripped_prefix(self):
        queries = extract_search_queries("Tory Burch TY2129U Brown, Tortoise")
        self.assertEqual(queries[0], "Tory Burch TY2129U eyeglasses")
        self.assertIn("Tory Burch 2129U eyeglasses", queries)

    def test_miu_miu_stripped_prefix(self):
        queries = extract_search_queries("Miu Miu MU01YV Bronze, Tortoise")
        self.assertEqual(queries[0], "Miu Miu MU01YV eyeglasses")
        self.assertIn("Miu Miu 01YV eyeglasses", queries)

    def test_alphabetical_model_name(self):
        queries = extract_search_queries("Kate Spade Luella Pink, Clear")
        self.assertIn("Kate Spade Luella eyeglasses", queries)

    def test_alphabetical_model_renne(self):
        queries = extract_search_queries("Kate Spade Renne Beige, Clear")
        self.assertIn("Kate Spade Renne eyeglasses", queries)

    def test_alphabetical_model_emilyn(self):
        queries = extract_search_queries("Kate Spade Emilyn Tortoise, Pink")
        self.assertIn("Kate Spade Emilyn eyeglasses", queries)


class TestParseSearchResults(unittest.TestCase):
    def test_parses_valid_json(self):
        html = '''
        <script>
        searchResult.push({"title": "Test Product", "price": 10000, "variants": []});
        searchResult.push({"title": "Another", "price": 20000, "variants": []});
        </script>
        '''
        results = parse_search_results(html)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["title"], "Test Product")
        self.assertEqual(results[1]["price"], 20000)

    def test_ignores_invalid_json(self):
        html = 'searchResult.push({bad json here});'
        results = parse_search_results(html)
        self.assertEqual(len(results), 0)

    def test_empty_html(self):
        self.assertEqual(parse_search_results(""), [])


class TestUPCNormalization(unittest.TestCase):
    def test_strips_leading_zeros(self):
        self.assertEqual(normalize_upc("0713132395233"), "713132395233")

    def test_no_leading_zeros(self):
        self.assertEqual(normalize_upc("713132395233"), "713132395233")

    def test_strips_whitespace(self):
        self.assertEqual(normalize_upc(" 713132395233 "), "713132395233")


class TestModelExtraction(unittest.TestCase):
    def test_burberry(self):
        self.assertEqual(extract_model_number("Burberry BE2108 Black"), "BE2108")

    def test_michael_kors(self):
        self.assertEqual(extract_model_number("Michael Kors MK3056 Naxos"), "MK3056")

    def test_coach(self):
        self.assertEqual(extract_model_number("Coach HC6065 Tortoise"), "HC6065")

    def test_versace(self):
        self.assertEqual(extract_model_number("Versace VE3340U Clear"), "VE3340U")

    def test_no_model(self):
        self.assertIsNone(extract_model_number("Just a name"))


class TestProductMatching(unittest.TestCase):
    SAMPLE_RESULTS = [{
        "title": "Burberry BE2108 Eyeglasses",
        "price": 15100,
        "url": "/products/burberry-be2108",
        "variants": [
            {"barcode": "0713132395233", "price": 15100},
            {"barcode": "0713132395240", "price": 15100},
        ],
    }]

    def test_upc_match(self):
        our = {"upc": "713132395233", "item_name": "Burberry BE2108 Black"}
        m = match_product(our, self.SAMPLE_RESULTS)
        self.assertIsNotNone(m)
        self.assertEqual(m["match_type"], "upc")
        self.assertEqual(m["competitor_price"], 151.00)

    def test_upc_match_with_leading_zero(self):
        our = {"upc": "0713132395233", "item_name": "Burberry BE2108 Black"}
        m = match_product(our, self.SAMPLE_RESULTS)
        self.assertIsNotNone(m)
        self.assertEqual(m["match_type"], "upc")

    def test_name_fallback(self):
        our = {"upc": "9999999999999", "item_name": "Burberry BE2108 Black"}
        m = match_product(our, self.SAMPLE_RESULTS)
        self.assertIsNotNone(m)
        self.assertEqual(m["match_type"], "name")

    def test_no_match(self):
        our = {"upc": "0000000000000", "item_name": "Unknown XY1234 Blue"}
        m = match_product(our, self.SAMPLE_RESULTS)
        self.assertIsNone(m)


class TestPricingAlgorithm(unittest.TestCase):
    def test_undercut_competitor(self):
        r = suggest_price(our_price=304, our_discount_price=274, competitor_price=200)
        self.assertEqual(r["suggested_price"], 194.0)  # 200 * 0.97
        self.assertLess(r["change_amount"], 0)

    def test_already_cheaper(self):
        r = suggest_price(our_price=304, our_discount_price=150, competitor_price=200)
        self.assertEqual(r["suggested_price"], 150.0)
        self.assertEqual(r["change_amount"], 0)

    def test_floor_cap(self):
        r = suggest_price(our_price=300, our_discount_price=270, competitor_price=50)
        self.assertEqual(r["suggested_price"], 60.0)  # floor = 300 * 0.20

    def test_equal_prices(self):
        r = suggest_price(our_price=200, our_discount_price=180, competitor_price=180)
        self.assertEqual(r["suggested_price"], 180.0)
        self.assertEqual(r["change_amount"], 0)

    def test_competitor_slightly_cheaper(self):
        r = suggest_price(our_price=200, our_discount_price=160, competitor_price=155)
        expected = round(155 * 0.97, 2)  # 150.35
        self.assertEqual(r["suggested_price"], expected)

    def test_returns_reasoning(self):
        r = suggest_price(our_price=100, our_discount_price=90, competitor_price=80)
        self.assertIn("reasoning", r)
        self.assertTrue(len(r["reasoning"]) > 0)


if __name__ == "__main__":
    unittest.main()
