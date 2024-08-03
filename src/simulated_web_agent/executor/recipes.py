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
                    {
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
                            }
                        ],
                    },
                    {
                        "selector": "#maincontent > div.columns > div > div:nth-child(3)",
                        "add_text": True,
                        "text_selector": "div > div.block-title > strong",
                        "children": [
                            {
                                "selector": "div.product-item-info",
                                "class": "product-item-info",
                                "name": "from_text",
                                "text_selector": "div.product-item-details strong.product-item-name",
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
                                                "clickable": True,
                                                "name": "view_reviews",
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
                                            {
                                                "selector": ".actions-primary",
                                                "add_text": True,
                                                "clickable": True,
                                                "name": "add_to_cart",
                                                "tag_name": "button",
                                                "click_selector": "button",
                                            },
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
                    {
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
                            }
                        ],
                    },
                    {
                        "selector": "#maincontent",
                        "add_text": True,
                        "text_selector": "div.page-title-wrapper > h1",
                        "children": [
                            {
                                "selector": "div.filter",
                                "name": "filter",
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
                                                        "clickable": True,
                                                        "name": "view_reviews",
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
                                                    {
                                                        "selector": ".actions-primary form",
                                                        "add_text": True,
                                                        "clickable": True,
                                                        "name": "add_to_cart",
                                                        "tag_name": "button",
                                                        "click_selector": "button",
                                                    },
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
        ],
    },
    {
        "match": "#maincontent > div.columns > div > div.product-info-main > div.product-info-price > div.product-info-stock-sku > div.stock.available > span",
        "match_text": "IN STOCK",
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
                    {
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
                            }
                        ],
                    },
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
                                        "name": "reviews",
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
                                        ],
                                    },
                                    {
                                        "selector": "div.product-options-bottom",
                                        "children": [
                                            {
                                                "selector": "div.field",
                                                "children": [
                                                    {
                                                        "selector": "label",
                                                    },
                                                    {
                                                        "selector": "div.control > input",
                                                        "name": "quantity",
                                                    },
                                                ],
                                            },
                                            {
                                                "selector": "div.actions > submit",
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
                                "children": [
                                    {
                                        "selector": "div.data.item.title",
                                        "add_text": True,
                                        "keep_attr": ["class"],
                                        "name": "from_text",
                                        "clickable": True,
                                    },
                                    {
                                        "selector": "div.data.item.content[aria-hidden='false']",
                                        "keep_attr": ["class", "aria-hidden"],
                                        "children": [
                                            {
                                                "selector": "div.celwidget:nth-child(3)",
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
                                ],
                            },
                        ],
                    },
                ],
            },
        ],
    },
]
