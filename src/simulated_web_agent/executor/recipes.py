recipes = [
    {
        "match": "^/?$",
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
                    # {
                    #     "selector": "nav",
                    #     "name": "nav",
                    #     "children": [
                    #         {
                    #             "selector": "ul",
                    #             "action": "strip_add_children",
                    #             "direct_child": True,
                    #             "children": [
                    #                 {
                    #                     "selector": "li",
                    #                     "direct_child": True,
                    #                     "add_text": True,
                    #                     "text_selector": "a",
                    #                     "clickable": True,
                    #                     "name": "from_text",
                    #                     "children": [
                    #                         {
                    #                             "selector": "ul",
                    #                             "direct_child": True,
                    #                             "children": [
                    #                                 {
                    #                                     "selector": "li",
                    #                                     "add_text": True,
                    #                                     "direct_child": True,
                    #                                     "text_selector": "a",
                    #                                     "clickable": True,
                    #                                     "name": "from_text",
                    #                                     "children": [
                    #                                         {
                    #                                             "selector": "ul",
                    #                                             "direct_child": True,
                    #                                             "children": [
                    #                                                 {
                    #                                                     "selector": "li",
                    #                                                     "add_text": True,
                    #                                                     "direct_child": True,
                    #                                                     "text_selector": "a",
                    #                                                     "clickable": True,
                    #                                                     "name": "from_text",
                    #                                                 }
                    #                                             ],
                    #                                         }
                    #                                     ],
                    #                                 }
                    #                             ],
                    #                         }
                    #                     ],
                    #                 }
                    #             ],
                    #         }
                    #     ],
                    # },
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
        "match": "^/catalogsearch/result/.*$",
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
                    # {
                    #     "selector": "nav",
                    #     "name": "nav",
                    #     "children": [
                    #         {
                    #             "selector": "ul",
                    #             "action": "strip_add_children",
                    #             "direct_child": True,
                    #             "children": [
                    #                 {
                    #                     "selector": "li",
                    #                     "direct_child": True,
                    #                     "add_text": True,
                    #                     "text_selector": "a",
                    #                     "clickable": True,
                    #                     "name": "from_text",
                    #                     "children": [
                    #                         {
                    #                             "selector": "ul",
                    #                             "direct_child": True,
                    #                             "children": [
                    #                                 {
                    #                                     "selector": "li",
                    #                                     "add_text": True,
                    #                                     "direct_child": True,
                    #                                     "text_selector": "a",
                    #                                     "clickable": True,
                    #                                     "name": "from_text",
                    #                                     "children": [
                    #                                         {
                    #                                             "selector": "ul",
                    #                                             "direct_child": True,
                    #                                             "children": [
                    #                                                 {
                    #                                                     "selector": "li",
                    #                                                     "add_text": True,
                    #                                                     "direct_child": True,
                    #                                                     "text_selector": "a",
                    #                                                     "clickable": True,
                    #                                                     "name": "from_text",
                    #                                                 }
                    #                                             ],
                    #                                         }
                    #                                     ],
                    #                                 }
                    #                             ],
                    #                         }
                    #                     ],
                    #                 }
                    #             ],
                    #         }
                    #     ],
                    # },
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
                                                        "name": "rating",
                                                        "clickable": True,
                                                        "text_format": "Rating: {}",
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
]
