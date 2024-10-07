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
        "selector": "ul:nth-of-type(1) > span.a-declarative > span > li",
        "add_text": True,
        "name": "from_text",
        "clickable": True,
        "click_selector": "a",
        "direct_child": True,
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
                        "selector": "#s-refinements",
                        "name": "refinements",
                        "children": [
                            {
                                "selector": "div.a-section.a-spacing-none:not(:has(#n-title)):has(span.a-size-base.a-color-base.puis-bold-weight-text):has(ul span.a-declarative > span > li):not(#reviewsRefinements):not(#departments):not(#priceRefinements):not(#filters)",
                                "name": "from_text",
                                "text_selector": "span.a-size-base.a-color-base.puis-bold-weight-text",
                                "children": refinement_option,
                            },
                            # {
                            #     "selector": "#primeRefinements",
                            #     "name": "prime_refinements",
                            #     "children": refinement_option,
                            # },
                            # {
                            #     "selector": "#deliveryRefinements",
                            #     "name": "delivery_refinements",
                            #     "children": refinement_option,
                            # },
                            # {
                            #     "selector": "#deliveryRelatedProgramsRefinements",
                            #     "name": "delivery_programs_refinements",
                            #     "children": refinement_option,
                            # },
                            # {
                            #     "selector": "#climatePledgeFriendlyRefinements",
                            #     "name": "climate_pledge_friendly_refinements",
                            #     "children": refinement_option,
                            # },
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
                            # # brandsRefinements
                            # {
                            #     "selector": "#brandsRefinements",
                            #     "name": "brands_refinements",
                            #     "children": refinement_option,
                            # },
                        ],
                    },
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
                                "class": "search-result",
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
                        "selector": "span.s-pagination-strip",
                        "name": "pagination",
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
        "match": "#productTitle",
        "match_text": "",
        "selector": "html",
        "children": [
            {"selector": "head", "children": [{"selector": "title", "add_text": True}]},
            {
                "selector": "body",
                "children": [
                    nav,
                    {
                        "selector": "#centerCol",
                        "class": "product-card",
                        "children": [
                            {
                                "selector": "#title",
                                "add_text": True,
                                "keep_attr": ["id"],
                            },
                            {
                                "selector": "#averageCustomerReviews",
                                "class": "review",
                                "children": [
                                    {
                                        "selector": "span.a-icon-alt",
                                        "add_text": True,
                                    },
                                    {
                                        "selector": "#acrCustomerReviewText",
                                        "add_text": True,
                                    },
                                ],
                            },
                            {
                                "selector": "#apex_desktop_newAccordionRow #corePriceDisplay_desktop_feature_div span.a-price.aok-align-center.reinventPricePriceToPayMargin.priceToPay",
                                "add_text": True,
                                "text_format": "Price: {}",
                                "class": "product-price",
                            },
                            {
                                "selector": "#twister",
                                "class": "product-options",
                                "children": [
                                    {
                                        "selector": "div.a-row:has(label.a-form-label):has(span.selection)",
                                        "children": [
                                            {
                                                "selector": "label.a-form-label",
                                                "add_text": True,
                                            },
                                            {
                                                "selector": "span.selection",
                                                "add_text": True,
                                            },
                                        ],
                                    }
                                ],
                            },
                        ],
                    },
                    # addToCart
                    {
                        "selector": "#addToCart:has(#buy-now-button)",
                        "name": "add_to_cart",
                        "children": [
                            {
                                # productFactsDesktopExpander
                                "selector": "#productFactsDesktopExpander",
                                "add_text": True,
                                "class": "product-facts",
                            },
                            # mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE
                            {
                                "selector": "div.mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE",
                                "add_text": True,
                                "class": "product-delivery",
                            },
                            # buy-now-button
                            {
                                "selector": "#buy-now-button",
                                "add_text": True,
                                "clickable": True,
                                "name": "buy_now",
                                "class": "product-buy-now",
                                "before_hook": """
const title = document.querySelector("#title").innerText
const price = document.querySelector("span.a-price.aok-align-center.reinventPricePriceToPayMargin.priceToPay").innerText
const options = Array.from(document.querySelectorAll("#twister div.a-row:has(label.a-form-label):has(span.selection)")).map(a => ({label: a.querySelector("label.a-form-label").innerText, value: a.querySelector("span.selection").innerText}))
const options_dict = {}
for (const option of options) {
    options_dict[option["label"].replace(": ", "")] = option["value"]
}
const asin = document.querySelector("input#ASIN").value
console.log({title, price, options: options_dict, asin})
return {title, price, options: options_dict, asin}
""",
                            },
                        ],
                    },
                ],
            },
        ],
    },
    {
        "match": "/ap/signin",
        "match_method": "url",
        "terminate": "return true",
        "terminate_callback": "return arguments[0]",
        "selector": "html",
    },
]
