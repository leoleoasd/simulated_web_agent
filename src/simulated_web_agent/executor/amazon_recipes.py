nav = {
    "selector": "#nav-search-bar-form",
    "children": [
        {
            "selector": "input#twotabsearchtextbox",
            "name": "search_input",
        },
        {
            "selector": "#nav-search-submit-button",
            "clickable": True,
            "name": "search_button",
        },
    ],
}
refinement_option = [
    {
        "selector": "span.a-size-base.a-color-base.puis-bold-weight-text",
        "add_text": True,
        "class": "refinement-title",
    },
    {
        "selector": "span.a-declarative > span > li",
        "add_text": True,
        "name": "from_text",
        "clickable": True,
        "children": [{"selector": "input[type='checkbox']"}],
    },
]
recipes = [
    {
        "match": "/",
        "match_method": "url",
        "selector": "html",
        "children": [
            {"selector": "head", "children": [{"selector": "title", "add_text": True}]},
            {
                "selector": "body",
                "children": [nav],
            },
        ],
    },
    {
        "match": "/s",
        "match_method": "url",
        "selector": "html",
        "children": [
            {"selector": "head", "children": [{"selector": "title", "add_text": True}]},
            {
                "selector": "body",
                "children": [
                    nav,
                    {
                        "selector": "div.s-main-slot.s-result-list.s-search-results",
                        "name": "search_results",
                        "children": [
                            {
                                "insert_split_marker": True,
                                "insert_split_marker_every": 4,
                                "selector": 'div[data-component-type="s-search-result"]',
                                "text_selector": "span.a-size-base-plus.a-color-base.a-text-normal",
                                "name": "from_text",
                                "children": [
                                    {
                                        "selector": "div[data-cy='title-recipe'] a",
                                        "add_text": True,
                                        "class": "product-name",
                                        "clickable": True,
                                        "name": "view_product",
                                    },
                                    {
                                        "selector": "div[data-cy='reviews-block']",
                                        "class": "product-review",
                                        "children": [
                                            {
                                                # .a-icon-alt
                                                "selector": "span.a-icon-alt",
                                                "add_text": True,
                                                "class": "product-rating",
                                            },
                                            # document.querySelector('[data-component-type="s-search-result"]').querySelector(".a-size-base.s-underline-text")
                                            {
                                                "selector": "span.a-size-base.s-underline-text",
                                                "add_text": True,
                                                "text_format": "{} reviews",
                                                "class": "product-rating-count",
                                            },
                                        ],
                                    },
                                    {
                                        # offscreen
                                        "selector": "div[data-cy='price-recipe']",
                                        "class": "product-price",
                                        "children": [
                                            {
                                                "selector": "a.a-link-normal > span.a-price > span.a-offscreen",
                                                "add_text": True,
                                            },
                                        ],
                                    },
                                    {
                                        "selector": "div[data-cy='delivery-recipe']",
                                        "add_text": True,
                                        "class": "product-delivery",
                                    },
                                ],
                            }
                        ],
                    },
                    {
                        "selector": "#s-refinements",
                        "name": "refinements",
                        "children": [
                            {
                                "selector": "#primeRefinements",
                                "name": "prime_refinements",
                                "children": refinement_option,
                            },
                            {
                                "selector": "#deliveryRefinements",
                                "name": "delivery_refinements",
                                "children": refinement_option,
                            },
                            {
                                "selector": "#deliveryRelatedProgramsRefinements",
                                "name": "delivery_programs_refinements",
                                "children": refinement_option,
                            },
                            {
                                "selector": "#climatePledgeFriendlyRefinements",
                                "name": "climate_pledge_friendly_refinements",
                                "children": refinement_option,
                            },
                            {
                                "selector": "#departments",
                                "name": "departments",
                                "children": [
                                    {
                                        "selector": "li a",
                                        "add_text": True,
                                        "name": "from_text",
                                        "clickable": True,
                                    }
                                ],
                            },
                            {
                                "selector": "#reviewsRefinements",
                                "name": "reviews_refinements",
                                "children": [
                                    {
                                        "selector": "li a",
                                        "add_text": True,
                                        "name": "from_text",
                                        "clickable": True,
                                    }
                                ],
                            },
                            # brandsRefinements
                            {
                                "selector": "#brandsRefinements",
                                "name": "brands_refinements",
                                "children": refinement_option,
                            },
                        ],
                    },
                    {
                        "selector": "span.s-pagination-strip",
                        "children": [
                            {
                                "selector": ".s-pagination-item",
                                "add_text": True,
                                "name": "from_text",
                                "clickable": True,
                            }
                        ],
                    },
                ],
            },
        ],
    },
    {
        "match": "#add-to-cart-button",
        "match_text": "",
        "terminate": "return true",
        "terminate_callback": "return true",
        "selector": "html",
    },
]
