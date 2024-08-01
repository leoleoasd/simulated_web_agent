homepage = {
    "selector": "html",
    "clickable": False,
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
                #     'selector': 'nav',
                #     'name': 'nav',
                #     'children': [
                #         {
                #             'selector': 'ul',
                #             'action': 'strip_add_children',
                #             'direct_child': True,
                #             'children': [
                #                 {
                #                     'selector': 'li',
                #                     'direct_child': True,
                #                     'add_text': True,
                #                     'text_selector': 'a',
                #                     'clickable': True,
                #                     'children': [
                #                         {
                #                             'selector': 'ul',
                #                             'direct_child': True,
                #                             'children': [
                #                                 {
                #                                     'selector': 'li',
                #                                     'add_text': True,
                #                                     'direct_child': True,
                #                                     'text_selector': 'a',
                #                                     'clickable': True,
                #                                     'children': [
                #                                         {
                #                                             'selector': 'ul',
                #                                             'direct_child': True,
                #                                             'children': [
                #                                                 {
                #                                                     'selector': 'li',
                #                                                     'add_text': True,
                #                                                     'direct_child': True,
                #                                                     'text_selector': 'a',
                #                                                     'clickable': True,
                #                                                 }
                #                                             ]
                #                                         }
                #                                     ]
                #                                 }
                #                             ]
                #                         }
                #                     ]
                #                 }
                #             ]
                #         }
                #     ]
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
                                            "name": "rating",
                                            "clickable": True,
                                            "text_format": "Rating: {}",
                                            "name": "view_reviews",
                                        },
                                        {
                                            "selector": ".product-item-name",
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
                                            "name": "add_to_card",
                                            "tag_name": "button",
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
}
