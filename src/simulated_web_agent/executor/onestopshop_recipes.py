nav = {
    "selector": "nav",
    "name": "nav",
    "children": [
        {
            "selector": "ul",
            "action": "strip_add_children",
            "direct_child": True,
            "children": [
                {
                    "selector": "li",
                    "direct_child": True,
                    "add_text": True,
                    "text_selector": "a",
                    "clickable": True,
                    "name": "from_text",
                    "children": [
                        {
                            "selector": "ul",
                            "direct_child": True,
                            "children": [
                                {
                                    "selector": "li",
                                    "add_text": True,
                                    "direct_child": True,
                                    "text_selector": "a",
                                    "clickable": True,
                                    "name": "from_text",
                                    "children": [
                                        {
                                            "selector": "ul",
                                            "direct_child": True,
                                            "children": [
                                                {
                                                    "selector": "li",
                                                    "add_text": True,
                                                    "direct_child": True,
                                                    "text_selector": "a",
                                                    "clickable": True,
                                                    "name": "from_text",
                                                }
                                            ],
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ],
        }
    ],
}

search_bar = {
    "selector": ".header.content",
    "name": "header",
    "children": [
        {
            "selector": "#search_mini_form",
            "name": "search_box",
            "children": [
                {
                    "selector": "input#search",
                    "name": "search_input",
                },
                {
                    "selector": "button.action.search",
                    "name": "search_button",
                    "add_text": True,
                    "clickable": True,
                },
            ],
        },
        # {
        #     "selector": "div.minicart-wrapper",
        #     "name": "minicart",
        #     "children": [
        #         {
        #             "selector": "a.action.showcart",
        #             "add_text": True,
        #             "text_js": "return 'Go to cart'",
        #             "name": "view_cart",
        #             "clickable": True,
        #             "children": [
        #                 {
        #                     "selector": "span.counter-label",
        #                     "add_text": True,
        #                 }
        #             ],
        #         }
        #     ],
        # },
    ],
}

recipes = [
    {
        "match": "#maincontent > div.columns > div > div:nth-child(3) > div > div.block-title > strong",
        "match_text": "Product Showcases",
        "selector": "html",
        "children": [
            {
                "selector": "head",
                "name": "",
                "children": [
                    {
                        "selector": "title",
                        "add_text": True,
                    }
                ],
            },
            {
                "selector": "body",
                "children": [
                    # nav,
                    search_bar,
                    {
                        "selector": "#maincontent > div.columns > div > div:nth-child(3)",
                        "add_text": True,
                        "text_selector": "div > div.block-title > strong",
                        "name": "product_showcases",
                        "children": [
                            {
                                "selector": "div.product-item-info",
                                "class": "product-item-info",
                                "name": "from_text",
                                "text_selector": "div.product-item-details strong.product-item-name",
                                "insert_split_marker": True,
                                "insert_split_marker_every": 4,
                                "children": [
                                    {
                                        "selector": "img",
                                    },
                                    {
                                        "selector": "div.product-item-details",
                                        "children": [
                                            {
                                                "selector": "div.rating-summary > div > span > span",
                                                "add_text": True,
                                                "text_format": "Rating: {}",
                                            },
                                            {
                                                "selector": "div.reviews-actions a",
                                                "add_text": True,
                                                "name": "rating",
                                                # "clickable": True,
                                                # "name": "view_reviews",
                                            },
                                            {
                                                "selector": ".product-item-name a",
                                                "add_text": True,
                                                "clickable": True,
                                                "name": "view_product",
                                            },
                                            {
                                                "selector": ".price-box",
                                                "add_text": True,
                                            },
                                            # {
                                            #     "selector": ".actions-primary",
                                            #     "add_text": True,
                                            #     "clickable": True,
                                            #     "name": "add_to_cart",
                                            #     "tag_name": "button",
                                            #     "click_selector": "button",
                                            # },
                                        ],
                                    },
                                ],
                            }
                        ],
                    },
                ],
            },
        ],
    },
    {
        "match": "#maincontent > div.page-title-wrapper > h1 > span",
        "match_text": "Search results",
        "selector": "html",
        "children": [
            {
                "selector": "head",
                "name": "",
                "children": [
                    {
                        "selector": "title",
                        "add_text": True,
                    }
                ],
            },
            {
                "selector": "body",
                "children": [
                    # nav,
                    search_bar,
                    {
                        "selector": "#maincontent",
                        "add_text": True,
                        "text_selector": "div.page-title-wrapper > h1",
                        "children": [
                            {
                                "selector": "div.filter",
                                "name": "filter",
                                "insert_split_marker": True,
                                "insert_split_marker_every": 1,
                                "children": [
                                    {
                                        "selector": ".filter-title",
                                        "add_text": True,
                                    },
                                    {
                                        "selector": "dl.filter-options",
                                        "add_text": True,
                                        "text_selector": "dt.filter-options-title",
                                        "children": [
                                            {
                                                "selector": "ol",
                                                "children": [
                                                    {
                                                        "selector": "li",
                                                        "children": [
                                                            {
                                                                "selector": "a",
                                                                "add_text": True,
                                                                "clickable": True,
                                                                "name": "from_text",
                                                            }
                                                        ],
                                                    }
                                                ],
                                            }
                                        ],
                                    },
                                ],
                            },
                            {
                                "selector": "div.search.results div.toolbar",
                                "name": "sorter",
                                "children": [
                                    {"selector": "#toolbar-amount", "add_text": True},
                                    {
                                        "selector": "select#sorter",
                                        "name": "sorter.select",
                                    },
                                    {
                                        "selector": "a.action.sorter-action",
                                        "add_text": True,
                                        "clickable": True,
                                        "name": "from_text",
                                        "keep_attr": ["class", "data-role"],
                                    },
                                ],
                            },
                            {
                                "selector": "div.search.results dl.block",
                                "add_text": True,
                                "text_selector": "dt.title",
                                "name": "related",
                                "children": [
                                    {
                                        "selector": "dd.item a",
                                        "add_text": True,
                                        "clickable": True,
                                        "name": "from_text",
                                    }
                                ],
                            },
                            {
                                "selector": "ol.product-items",
                                "name": "search_results",
                                "children": [
                                    {
                                        "selector": "div.product-item-info",
                                        "class": "product-item-info",
                                        "name": "from_text",
                                        "text_selector": "div.product-item-details strong.product-item-name a",
                                        "insert_split_marker": True,
                                        "insert_split_marker_every": 4,
                                        "children": [
                                            {
                                                "selector": "img",
                                            },
                                            {
                                                "selector": "div.product-item-details",
                                                "children": [
                                                    {
                                                        "selector": "div.rating-summary > div > span > span",
                                                        "add_text": True,
                                                        "text_format": "Rating: {}",
                                                    },
                                                    {
                                                        "selector": "div.product-reviews-summary > div.review-actions > a",
                                                        "add_text": True,
                                                        "name": "reviews",
                                                        # "clickable": True,
                                                        # "name": "view_reviews",
                                                    },
                                                    {
                                                        "selector": ".product-item-name a",
                                                        "add_text": True,
                                                        "clickable": True,
                                                        "name": "view_product",
                                                    },
                                                    {
                                                        "selector": ".price-box",
                                                        "add_text": True,
                                                    },
                                                    # {
                                                    #     "selector": ".actions-primary form",
                                                    #     "add_text": True,
                                                    #     "clickable": True,
                                                    #     "name": "add_to_cart",
                                                    #     "tag_name": "button",
                                                    #     "click_selector": "button",
                                                    # },
                                                ],
                                            },
                                        ],
                                    },
                                ],
                            },
                            {
                                "selector": "div.toolbar-products div.pages",
                                "add_text": True,
                                "text_selector": "strong",
                                "name": "pager",
                                "children": [
                                    {
                                        "selector": "ul",
                                        "children": [
                                            {
                                                "selector": "li",
                                                "keep_attr": ["class"],
                                                "add_text": True,
                                                "children": [
                                                    {
                                                        "selector": "strong.page",
                                                        "add_text": True,
                                                    },
                                                    {
                                                        "selector": "a",
                                                        "add_text": True,
                                                        "clickable": True,
                                                        "name": "from_text",
                                                    },
                                                ],
                                            }
                                        ],
                                    }
                                ],
                            },
                        ],
                    },
                ],
            },
        ],
    },
    {
        "match": "#maincontent > div.columns > div > div.product-info-main > div.product-info-price > div.product-info-stock-sku > div.stock.available > span",
        "match_text": "IN STOCK",
        "selector": "html",
        "terminate": """
return document.querySelector("span.counter-label").textContent.trim() != ""
""",
        "terminate_callback": """
cart = document.querySelector("#minicart-content-wrapper")
product = cart.querySelector("div.product-item-details")

option_list = product.querySelector("dl.product.options.list")
if (!option_list) {
    options = []
    options_str = ""
} else {
    values = [...option_list.querySelectorAll("dd.values")].map(a => a.textContent.trim())
    labels = [...option_list.querySelectorAll("dt.label")].map(a => a.textContent.trim())
    options = labels.map((l, i) => [l, values[i]])
    options_str = ""
    for (i of options) {options_str += `${i[0]}: ${i[1]}; `}
}

h1 = document.createElement("h1");
document.documentElement.remove();
div = document.createElement("div");
div.style.display="flex";
div.style.justifyContent="center";
div.style.alignItems="center";
div.style.width="100%"; div.style.height="100%";
document.appendChild(div);
div.style.alignContent="center";
h1.textContent=`You purchased ${product.querySelector(".product-item-name").textContent.trim()}, with options ${options_str}`
div.appendChild(h1)
return {
    "product_name": product.querySelector(".product-item-name").textContent.trim(),
    "options": options,
}
""",
        "children": [
            {
                "selector": "head",
                "name": "",
                "children": [
                    {
                        "selector": "title",
                        "add_text": True,
                    }
                ],
            },
            {
                "selector": "body",
                "children": [
                    # nav,
                    search_bar,
                    {
                        "selector": "#maincontent",
                        "children": [
                            {
                                "selector": "h1.page-title",
                                "add_text": True,
                            },
                            {
                                "selector": "div.fotorama__stage__shaft.fotorama__grab",
                                "class": "product media gallery",
                                "children": [
                                    {
                                        "selector": "div > img:nth-child(1)",
                                        "direct_child": True,
                                    }
                                ],
                            },
                            {
                                "selector": "div.product-reviews-summary",
                                "class": "product-reviews-summary",
                                "children": [
                                    {
                                        "selector": "div.rating-summary > div > span > span",
                                        "add_text": True,
                                        "text_format": "Rating: {}",
                                    },
                                    {
                                        "selector": "div.reviews-actions > a.view",
                                        "add_text": True,
                                        "clickable": True,
                                        "name": "view_reviews",
                                    },
                                ],
                            },
                            {
                                "selector": "div.price-box",
                                "add_text": True,
                            },
                            {
                                "selector": "div.product-add-form > form",
                                "class": "product-add-form",
                                "name": "product_form",
                                "insert_split_marker": True,
                                "insert_split_marker_every": 1000,
                                "children": [
                                    {
                                        "selector": "div.field.required",
                                        "name": "options",
                                        "children": [
                                            {
                                                "selector": "label",
                                                "direct_child": True,
                                                "add_text": True,
                                            },
                                            {
                                                "selector": "div.control > div.options-list",
                                                "children": [
                                                    {
                                                        "selector": "input",
                                                        "add_text": True,
                                                        "clickable": True,
                                                        "name": "from_text",
                                                        "text_js": "return arguments[0].nextElementSibling.innerText",
                                                        "override_attr": {
                                                            "value": "return arguments[0].nextElementSibling.innerText",
                                                        },
                                                    },
                                                ],
                                            },
                                            {
                                                "selector": "div.control > div.mage-error",
                                                "keep_attr": ["class"],
                                                "override_attr": {
                                                    "class": "return 'error'",
                                                    "style": "return 'color: red'",
                                                },
                                                "add_text": True,
                                            },
                                        ],
                                    },
                                    {
                                        "selector": "div.box-tocart",
                                        "children": [
                                            {
                                                "selector": "div.field",
                                                "children": [
                                                    {
                                                        "selector": "label",
                                                        "add_text": True,
                                                        "keep_attr": [
                                                            "for",
                                                        ],
                                                    },
                                                    {
                                                        "selector": "div.control > input",
                                                        "name": "quantity",
                                                    },
                                                ],
                                            },
                                            {
                                                "selector": "div.actions > button[type='submit']",
                                                "add_text": True,
                                                "clickable": True,
                                                "name": "add_to_cart",
                                            },
                                        ],
                                    },
                                ],
                            },
                            {
                                "selector": "div.product.info.detailed",
                                "class": "product info detailed",
                                "name": "product_info",
                                "insert_split_marker": True,
                                "insert_split_marker_every": 1000,
                                "children": [
                                    {
                                        "selector": "div.data.item.title",
                                        "add_text": True,
                                        "class": "data item title tab-title",
                                        "name": "from_text",
                                        "clickable": True,
                                    },
                                    {
                                        "selector": "#description[aria-hidden='false']",
                                        "keep_attr": ["class", "aria-hidden"],
                                        "children": [
                                            {
                                                "selector": "div.celwidget",
                                                "add_text": True,
                                            },
                                            {
                                                "selector": "#productDescription-3_feature_div",
                                                "children": [
                                                    {
                                                        "selector": "h2",
                                                        "direct_child": True,
                                                        "add_text": True,
                                                    },
                                                    {
                                                        "selector": "#shortDescription",
                                                        "add_text": True,
                                                    },
                                                    {
                                                        "selector": "#productDetails_detailBullets_sections1",
                                                        "children": [
                                                            {
                                                                "selector": "tbody",
                                                                "children": [
                                                                    {
                                                                        "selector": "tr",
                                                                        "children": [
                                                                            {
                                                                                "selector": "th",
                                                                                "add_text": True,
                                                                            },
                                                                            {
                                                                                "selector": "td",
                                                                                "add_text": True,
                                                                            },
                                                                        ],
                                                                    }
                                                                ],
                                                            }
                                                        ],
                                                    },
                                                ],
                                            },
                                        ],
                                    },
                                    {
                                        "selector": "#reviews[aria-hidden='false']",
                                        "keep_attr": ["class", "aria-hidden"],
                                        "name": "reviews",
                                        "children": [
                                            {
                                                "selector": "#product-review-container",
                                                "keep_attr": ["class", "id"],
                                                "empty_message": "No reviews",
                                                "children": [
                                                    {
                                                        "selector": "div.block-title",
                                                        "add_text": True,
                                                    },
                                                    {
                                                        "selector": "div.block-content > ol",
                                                        "children": [
                                                            {
                                                                "selector": "li",
                                                                "children": [
                                                                    {
                                                                        "selector": "div.review-title",
                                                                        "keep_attr": [
                                                                            "class",
                                                                        ],
                                                                        "add_text": True,
                                                                    },
                                                                    {
                                                                        "selector": "div.review-ratings div.rating-result > span > span",
                                                                        "add_text": True,
                                                                        "text_format": "Rating: {}",
                                                                    },
                                                                    {
                                                                        "selector": "div.review-content-container",
                                                                        "add_text": True,
                                                                    },
                                                                    {
                                                                        "selector": "review-details > p",
                                                                        "add_text": True,
                                                                    },
                                                                ],
                                                            }
                                                        ],
                                                    },
                                                    {
                                                        "selector": "div.review-toolbar:last-child div.pager div.pages",
                                                        "add_text": True,
                                                        "text_selector": "strong.label",
                                                        "name": "pager",
                                                        "children": [
                                                            {
                                                                "selector": "ul",
                                                                "children": [
                                                                    {
                                                                        "selector": "li",
                                                                        "keep_attr": [
                                                                            "class"
                                                                        ],
                                                                        "add_text": True,
                                                                        "children": [
                                                                            {
                                                                                "selector": "strong.page",
                                                                                "add_text": True,
                                                                            },
                                                                            {
                                                                                "selector": "a",
                                                                                "add_text": True,
                                                                                "clickable": True,
                                                                                "name": "from_text",
                                                                            },
                                                                        ],
                                                                    }
                                                                ],
                                                            }
                                                        ],
                                                    },
                                                ],
                                            }
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
        ],
    },
    # {
    #     "match": "#maincontent > div.page-title-wrapper > h1 > span",
    #     "match_text": "Shopping Cart",
    #     "terminate": "return true",
    #     "selector": "html",
    #     "children": [
    #         {
    #             "selector": "head",
    #             "name": "",
    #             "children": [
    #                 {
    #                     "selector": "title",
    #                     "add_text": True,
    #                 }
    #             ],
    #         },
    #         {
    #             "selector": "body",
    #             "children": [
    #                 # nav,
    #                 search_bar,
    #                 {
    #                     "selector": "#maincontent > div.columns > div > div:nth-child(3)",
    #                     "add_text": True,
    #                     "text_selector": "div > div.block-title > strong",
    #                     "name": "product_showcases",
    #                     "children": [
    #                         {
    #                             "selector": "div.product-item-info",
    #                             "class": "product-item-info",
    #                             "name": "from_text",
    #                             "text_selector": "div.product-item-details strong.product-item-name",
    #                             "children": [
    #                                 {
    #                                     "selector": "img",
    #                                 },
    #                                 {
    #                                     "selector": "div.product-item-details",
    #                                     "children": [
    #                                         {
    #                                             "selector": "div.rating-summary > div > span > span",
    #                                             "add_text": True,
    #                                             "text_format": "Rating: {}",
    #                                         },
    #                                         {
    #                                             "selector": "div.reviews-actions a",
    #                                             "add_text": True,
    #                                             "name": "rating",
    #                                             # "clickable": True,
    #                                             # "name": "view_reviews",
    #                                         },
    #                                         {
    #                                             "selector": ".product-item-name a",
    #                                             "add_text": True,
    #                                             "clickable": True,
    #                                             "name": "view_product",
    #                                         },
    #                                         {
    #                                             "selector": ".price-box",
    #                                             "add_text": True,
    #                                         },
    #                                         {
    #                                             "selector": ".actions-primary",
    #                                             "add_text": True,
    #                                             "clickable": True,
    #                                             "name": "add_to_cart",
    #                                             "tag_name": "button",
    #                                             "click_selector": "button",
    #                                         },
    #                                     ],
    #                                 },
    #                             ],
    #                         }
    #                     ],
    #                 },
    #             ],
    #         },
    #     ],
    # },
]
