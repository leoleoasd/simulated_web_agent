import json
import logging
import os
import random
import re
from collections import defaultdict
from decimal import Decimal
from os.path import join

import gymnasium as gym
from gymnasium import spaces
from pyserini.search.lucene import LuceneSearcher
from tqdm.auto import tqdm

logger = logging.getLogger(__name__)


BASE_DIR = "/home/leo/code/webshop"
DEBUG_PROD_SIZE = 1000  # set to `None` to disable

DEFAULT_ATTR_PATH = join(BASE_DIR, "data/items_ins_v2_1000.json")
DEFAULT_FILE_PATH = join(BASE_DIR, "data/items_shuffle_1000.json")
DEFAULT_REVIEW_PATH = join(BASE_DIR, "data/reviews.json")

FEAT_CONV = join(BASE_DIR, "data/feat_conv.pt")
FEAT_IDS = join(BASE_DIR, "data/feat_ids.pt")

HUMAN_ATTR_PATH = join(BASE_DIR, "data/items_human_ins.json")
HUMAN_ATTR_PATH = join(BASE_DIR, "data/items_human_ins.json")

SEARCH_RETURN_N = 50


def get_top_n_product_from_keywords(
    keywords,
    search_engine,
    all_products,
    product_item_dict,
    attribute_to_asins=None,
):
    if keywords[0] == "<r>":
        top_n_products = random.sample(all_products, k=SEARCH_RETURN_N)
    elif keywords[0] == "<a>":
        attribute = " ".join(keywords[1:]).strip()
        asins = attribute_to_asins[attribute]
        top_n_products = [p for p in all_products if p["asin"] in asins]
    elif keywords[0] == "<c>":
        category = keywords[1].strip()
        top_n_products = [p for p in all_products if p["category"] == category]
    elif keywords[0] == "<q>":
        query = " ".join(keywords[1:]).strip()
        top_n_products = [p for p in all_products if p["query"] == query]
    else:
        keywords = " ".join(keywords)
        hits = search_engine.search(keywords, k=SEARCH_RETURN_N)
        docs = [search_engine.doc(hit.docid) for hit in hits]
        top_n_asins = [json.loads(doc.raw())["id"] for doc in docs]
        top_n_products = [
            product_item_dict[asin] for asin in top_n_asins if asin in product_item_dict
        ]
    return top_n_products


def generate_product_prices(all_products):
    product_prices = dict()
    for product in all_products:
        asin = product["asin"]
        pricing = product["pricing"]
        if not pricing:
            price = 100.0
        elif len(pricing) == 1:
            price = pricing[0]
        else:
            price = random.uniform(*pricing[:2])
        product_prices[asin] = price
    return product_prices


def init_search_engine(num_products=None):
    if num_products == 100:
        indexes = "indexes_100"
    elif num_products == 1000:
        indexes = "indexes_1k"
    elif num_products == 100000:
        indexes = "indexes_100k"
    elif num_products is None:
        indexes = "indexes"
    else:
        raise NotImplementedError(
            f"num_products being {num_products} is not supported yet."
        )
    search_engine = LuceneSearcher(os.path.join(BASE_DIR, f"search_engine/{indexes}"))
    return search_engine


def clean_product_keys(products):
    for product in products:
        product.pop("product_information", None)
        product.pop("brand", None)
        product.pop("brand_url", None)
        product.pop("list_price", None)
        product.pop("availability_quantity", None)
        product.pop("availability_status", None)
        product.pop("total_reviews", None)
        product.pop("total_answered_questions", None)
        product.pop("seller_id", None)
        product.pop("seller_name", None)
        product.pop("fulfilled_by_amazon", None)
        product.pop("fast_track_message", None)
        product.pop("aplus_present", None)
        product.pop("small_description_old", None)
    print("Keys cleaned.")
    return products


def load_products(filepath, num_products=None, human_goals=True):
    # TODO: move to preprocessing step -> enforce single source of truth
    with open(filepath) as f:
        products = json.load(f)
    print("Products loaded.")
    products = clean_product_keys(products)

    # with open(DEFAULT_REVIEW_PATH) as f:
    #     reviews = json.load(f)
    all_reviews = dict()
    all_ratings = dict()
    # for r in reviews:
    #     all_reviews[r['asin']] = r['reviews']
    #     all_ratings[r['asin']] = r['average_rating']

    if human_goals:
        with open(HUMAN_ATTR_PATH) as f:
            human_attributes = json.load(f)
    with open(DEFAULT_ATTR_PATH) as f:
        attributes = json.load(f)
    with open(HUMAN_ATTR_PATH) as f:
        human_attributes = json.load(f)
    print("Attributes loaded.")

    asins = set()
    all_products = []
    attribute_to_asins = defaultdict(set)
    if num_products is not None:
        # using item_shuffle.json, we assume products already shuffled
        products = products[:num_products]
    for i, p in tqdm(enumerate(products), total=len(products)):
        asin = p["asin"]
        if asin == "nan" or len(asin) > 10:
            continue

        if asin in asins:
            continue
        else:
            asins.add(asin)

        products[i]["category"] = p["category"]
        products[i]["query"] = p["query"]
        products[i]["product_category"] = p["product_category"]

        products[i]["Title"] = p["name"]
        products[i]["Description"] = p["full_description"]
        products[i]["Reviews"] = all_reviews.get(asin, [])
        products[i]["Rating"] = all_ratings.get(asin, "N.A.")
        for r in products[i]["Reviews"]:
            if "score" not in r:
                r["score"] = r.pop("stars")
            if "review" not in r:
                r["body"] = ""
            else:
                r["body"] = r.pop("review")
        products[i]["BulletPoints"] = (
            p["small_description"]
            if isinstance(p["small_description"], list)
            else [p["small_description"]]
        )

        pricing = p.get("pricing")
        if pricing is None or not pricing:
            pricing = [100.0]
            price_tag = "$100.0"
        else:
            pricing = [
                float(Decimal(re.sub(r"[^\d.]", "", price)))
                for price in pricing.split("$")[1:]
            ]
            if len(pricing) == 1:
                price_tag = f"${pricing[0]}"
            else:
                price_tag = f"${pricing[0]} to ${pricing[1]}"
                pricing = pricing[:2]
        products[i]["pricing"] = pricing
        products[i]["Price"] = price_tag

        options = dict()
        customization_options = p["customization_options"]
        option_to_image = dict()
        if customization_options:
            for option_name, option_contents in customization_options.items():
                if option_contents is None:
                    continue
                option_name = option_name.lower()

                option_values = []
                for option_content in option_contents:
                    option_value = (
                        option_content["value"].strip().replace("/", " | ").lower()
                    )
                    option_image = option_content.get("image", None)

                    option_values.append(option_value)
                    option_to_image[option_value] = option_image
                options[option_name] = option_values
        products[i]["options"] = options
        products[i]["option_to_image"] = option_to_image

        # without color, size, price, availability
        # if asin in attributes and 'attributes' in attributes[asin]:
        #     products[i]['Attributes'] = attributes[asin]['attributes']
        # else:
        #     products[i]['Attributes'] = ['DUMMY_ATTR']
        # products[i]['instruction_text'] = \
        #     attributes[asin].get('instruction', None)
        # products[i]['instruction_attributes'] = \
        #     attributes[asin].get('instruction_attributes', None)

        # without color, size, price, availability
        if asin in attributes and "attributes" in attributes[asin]:
            products[i]["Attributes"] = attributes[asin]["attributes"]
        else:
            products[i]["Attributes"] = ["DUMMY_ATTR"]

        if human_goals:
            if asin in human_attributes:
                products[i]["instructions"] = human_attributes[asin]
        else:
            products[i]["instruction_text"] = attributes[asin].get("instruction", None)

            products[i]["instruction_attributes"] = attributes[asin].get(
                "instruction_attributes", None
            )

        products[i]["MainImage"] = p["images"][0]
        products[i]["query"] = p["query"].lower().strip()

        all_products.append(products[i])

    for p in all_products:
        for a in p["Attributes"]:
            attribute_to_asins[a].add(p["asin"])

    product_item_dict = {p["asin"]: p for p in all_products}
    product_prices = generate_product_prices(all_products)
    return all_products, product_item_dict, product_prices, attribute_to_asins


class Webshop:
    def __init__(self, purchase_callback):
        self.products = []
        self.page_name = "home"
        self.page_params = {}
        self.clickables = {}
        self.inputs = {}
        self.page = ""
        self.page_stack = []
        self.page_inited = False
        self.render()

        self.all_products, self.product_item_dict, self.product_prices, _ = (
            load_products(
                filepath=DEFAULT_FILE_PATH, num_products=None, human_goals=True
            )
        )
        self.search_engine = init_search_engine(num_products=1000)
        self.purchase_callback = purchase_callback

    def type(self, name, text):
        if name in self.inputs:
            self.inputs[name] = text
            self.render()
        else:
            logger.error(f"INVALID ACTION: Input field {name} not found")

    def click(self, name):
        if name in self.clickables:
            self.clickables[name]()
            self.render()
        else:
            logger.error(f"INVALID ACTION: Clickable {name} not found")

    def render(self):
        if self.page_name == "home":
            if not self.page_inited:
                self.render_homepage(init=True)
                self.page_inited = True
            self.render_homepage()
        elif self.page_name == "search":
            if not self.page_inited:
                self.render_search(init=True)
                self.page_inited = True
            self.render_search()
        elif self.page_name == "product":
            if not self.page_inited:
                self.render_product(init=True)
                self.page_inited = True
            self.render_product()
        from urllib.parse import quote_plus, urlencode

        self.url = f"http://127.0.0.1/{self.page_name}?{urlencode(self.page_params, quote_via=quote_plus)}"

    def push_stack(self):
        self.page_stack.append(
            {
                "page_name": self.page_name,
                "page_params": self.page_params,
            }
        )

    def pop_stack(self):
        if len(self.page_stack) > 0:
            self.page_name = self.page_stack[-1]["page_name"]
            self.page_params = self.page_stack[-1]["page_params"]
            self.page_stack.pop()
        else:
            self.page_name = "home"
            self.page_params = {}
        self.page_inited = False
        self.render()

    def go(self, page_name, page_params):
        self.push_stack()
        self.page_name = page_name
        self.page_params = page_params
        self.page_inited = False

    def render_homepage(self, init=False):
        if init:
            self.clickables = {
                "search": lambda: self.go(
                    "search", {"search_term": self.inputs["search"]}
                )
            }
            self.inputs = {"search": ""}
            self.page_params = {}
        self.page = f"""
<input type="text" name="search" placeholder="Search" value="{self.inputs['search']}">
<button type="submit" name="search">Search</button>
"""

    def render_search(self, init=False):
        if init:
            self.page_params = {
                "search_term": self.page_params["search_term"],
                "page": 0
                if "page" not in self.page_params
                else self.page_params["page"],
            }
            self.inputs = {
                "searchbox.search": self.page_params["search_term"],
            }
        top_n_products = get_top_n_product_from_keywords(
            self.page_params["search_term"].split(),
            self.search_engine,
            self.all_products,
            self.product_item_dict,
        )
        products = top_n_products[
            self.page_params["page"] * 10 : (self.page_params["page"] + 1) * 10
        ]
        # print products asinx
        print("search result", [p["asin"] for p in products])
        n_pages = len(top_n_products) // 10

        products_html = [
            f"""
            <div class="product" name="{p['asin']}">
                <img src="{p['MainImage']}" alt="{p['Title']}">
                <div class="product-info">
                    <h3>{p['Title']}</h3>
                    <p>{p['Description']}</p>
                    <p>{p['Price']}</p>
                    <button type="submit" name="searchresult.{p['asin']}.view">View</button>
                </div>
            </div>
            """
            for p in products
        ]
        pagination_html = [
            f"""
            <button type="submit" name="pagination.{i+1}">{i+1}</button>
            """
            for i in range(n_pages)
        ]
        pagination_html = (
            [
                """
            <button type="submit" name="pagination.back">Back</button>
            """
                if self.page_params["page"] > 0
                else ""
            ]
            + pagination_html
            + [
                """
            <button type="submit" name="pagination.next">Next</button>
            """
                if self.page_params["page"] < n_pages - 1
                else ""
            ]
        )

        self.page = f"""
<div name="searchbox">
<input type="text" name="searchbox.search" placeholder="Search" value="{self.inputs['searchbox.search']}">
<button type="submit" name="search">Search</button>
</div>
<div name="searchresult">
{''.join(products_html)}
</div>
<div name="pagination">
viewing page {self.page_params['page']+1} of {n_pages}
{''.join(pagination_html)}
</div>
"""
        # self.clickables = {"searchbox.search": lambda: self.go("search", {"search_term": self.inputs["search"]})}
        self.clickables = {
            "searchbox.search": lambda: self.go(
                "search", {"search_term": self.inputs["search"]}
            ),
            **{
                f"searchresult.{p['asin']}.view": lambda asin=p["asin"]: self.go(
                    "product", {"asin": asin}
                )
                for p in products
            },
            "pagination.back": lambda: self.go(
                "search",
                {
                    "search_term": self.page_params["search_term"],
                    "page": self.page_params["page"] - 1,
                },
            ),
            "pagination.next": lambda: self.go(
                "search",
                {
                    "search_term": self.page_params["search_term"],
                    "page": self.page_params["page"] + 1,
                },
            ),
            **{
                f"pagination.{i}": lambda: self.go(
                    "search",
                    {"search_term": self.page_params["search_term"], "page": i - 1},
                )
                for i in range(1, n_pages + 1)
            },
        }

    def render_product(self, init=False):
        if init:
            product = self.product_item_dict[self.page_params["asin"]]
            self.page_params = {
                "asin": self.page_params["asin"],
                "options": {
                    option_name: product["options"][option_name][0]
                    for option_name in product["options"]
                },
            }
            self.inputs = {}
        product = self.product_item_dict[self.page_params["asin"]]
        options_html = [
            f"""
            <div class="option" name="{option_name}">
                <h4>{option_name}</h4>
                <ul>
                    {''.join([f'<button name="options.{option_name}.{option_value}">{option_value} {"(selected)" if self.page_params["options"][option_name] == option_value else ""}</button>' for option_value in option_values])}
                </ul>
            </div>
            """
            for option_name, option_values in product["options"].items()
        ]
        self.page = f"""
<div name="product">
    <img src="{product['MainImage']}" alt="{product['Title']}">
    <div>
        <h3>{product['Title']}</h3>
        <p>{product['Price']}</p>
        <p>{product['Description']}</p>
        <p>{product['BulletPoints']}</p>
        <button type="submit" name="product.purchase">Add to Cart</button>
    </div>
</div>
<div class="options">
{''.join(options_html)}
</div>
"""

        def select_option(option_name, option_value):
            self.page_params["options"][option_name] = option_value

        self.clickables = {
            "product.purchase": lambda: self.purchase_callback(
                product, self.page_params["options"]
            ),
            **{
                f"options.{option_name}.{option_value}": lambda option_name=option_name,
                option_value=option_value: select_option(option_name, option_value)
                for option_name, option_values in product["options"].items()
                for option_value in option_values
            },
        }


# Define the environment class
class WebshopEnv(gym.Env):
    def __init__(self):
        self.observation_space = spaces.Dict(
            {
                "url": spaces.Text(10000),
                "page": spaces.Text(10000),
                "clickables": spaces.Sequence(spaces.Text(10000)),
            }
        )
        self.action_space = spaces.Text(10000)

    def reset(self, seed=None):
        super().reset(seed=seed)
        self.ended = False
        self.product_selected = None
        self.product_options = None

        def purchase_callback(product, options):
            self.product_selected = product
            self.product_options = options
            self.ended = True

        self.webshop = Webshop(purchase_callback)
        return {
            "url": self.webshop.url,
            "page": self.webshop.page,
            "clickables": list(self.webshop.clickables.keys()),
        }, {}

    def step(self, action):
        action = json.loads(action)
        if action["type"] == "type":
            self.webshop.type(action["name"], action["text"])
        elif action["type"] == "click":
            self.webshop.click(action["name"])
        elif action["type"] == "back":
            self.webshop.pop_stack()
        elif action["type"] == "terminate":
            self.ended = True
        else:
            logger.error(f"INVALID ACTION: {action}")
            return (
                {
                    "url": self.webshop.url,
                    "page": self.webshop.page,
                    "clickables": list(self.webshop.clickables.keys()),
                },
                0,
                True,
                True,
                {},
            )
        return (
            {
                "url": self.webshop.url,
                "page": self.webshop.page,
                "clickables": list(self.webshop.clickables.keys()),
            },
            0,
            self.ended,
            self.ended,
            {},
        )


gym.register(
    id="Webshop-v0",
    entry_point="simulated_web_agent.webshop.env:WebshopEnv",
)
