import asyncio
import json
import logging
import os
import platform
import random
import re
import time
import traceback
import urllib.parse
from threading import Thread
from typing import Any, Callable, Optional, Union

import dominate
import dominate.tags
import dominate.util
import gymnasium as gym
import numpy
from bs4 import BeautifulSoup
from gymnasium import spaces
from IPython import embed
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement as Element
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from tqdm.auto import tqdm

# run_path
from ..agent import context

# from .recipes import recipes

run_animate = """
// js
// while not to end, scroll down
// save a settimeout to document for future cancel
scrollDown = () => {
    window.scrollBy({top: 400, behavior: 'smooth'});
    if ((window.innerHeight + Math.round(window.scrollY)) < document.body.offsetHeight) {
        document.scrollDownTimeout = setTimeout(scrollDown, 1000);
    } else {
        // scroll back
        window.scrollBy({top: -800, behavior: 'smooth'});
    }
}
scrollDown();
"""

stop_animate = """
// js
// clear the scrollDownTimeout
if (document.scrollDownTimeout) {
    clearTimeout(document.scrollDownTimeout);
}
"""

process_js_code = """
function processElement(element, recipe, parentName = "", nthChild = 0) {
    // Create a new element using the DOM API
    let tagName = recipe.tag_name || element.tagName.toLowerCase();
    // Handle underscored tags
    if (tagName.endsWith("_")) {
        tagName = tagName.slice(0, -1);
    }
    const newElement = document.createElement(tagName);

    // Extract text content based on the recipe
    let elementText = "";
    if (recipe.text_selector) {
        const textElement = element.querySelector(recipe.text_selector);
        if (textElement) {
            elementText = textElement.innerText || textElement.textContent || "";
        }
    } else if (recipe.text_js) {
        elementText = eval(recipe.text_js);
    } else if (recipe.add_text) {
        elementText = element.innerText || element.textContent || "";
    }
    elementText = elementText.replace(/\s+/g, " ").trim();
    if (recipe.text_format && elementText) {
        elementText = recipe.text_format.replace("{}", elementText);
    }

    if (elementText && recipe.add_text) {
        newElement.textContent = elementText;
    }

    // Build the node attributes
    let elementName = "";
    if (recipe.name) {
        if (recipe.name === "from_text") {
            elementName = parentName ? parentName + "." : "";
            elementName += elementText.toLowerCase().replace(/[^\w]+/g, "_");
        } else if (recipe.name === "from_nth_child") {
            elementName = parentName ? parentName + "." : "";
            elementName += nthChild.toString();
        } else {
            elementName = parentName ? parentName + "." : "";
            elementName += recipe.name;
        }
        newElement.setAttribute("name", elementName);
        parentName = elementName;
    }

    // Handle clickables and inputs
    if (recipe.clickable) {
        if (!recipe.name) {
            throw new Error("clickable element must have a name");
        }
        // handle click_selector
        if (recipe.click_selector) {
            click_element = element.querySelector(recipe.click_selector);
        } else {
            click_element = element;
        }
        if (click_element) {
            click_element.setAttribute("data-clickable-id", elementName);
        } else {
            console.log('click-element not found', element, recipe);
        }
        if (!window.clickable_recipes) {
            window.clickable_recipes = {};
        }
        window.clickable_recipes[elementName] = recipe;
    }
    if (tagName === "input") {
        const inputType = element.getAttribute("type");
        if (["text", "number"].includes(inputType)) {
            newElement.setAttribute("value", element.value);
            element.setAttribute("data-input-id", elementName);
        } else if (inputType === "checkbox") {
            newElement.setAttribute("checked", element.checked.toString());
        } else if (inputType === "radio") {
            newElement.setAttribute("checked", element.checked.toString());
            element.setAttribute("data-clickable-id", elementName);
        }
        if (!window.input_recipes) {
            window.input_recipes = {};
        }
        window.input_recipes[elementName] = recipe;
    }
    // **Handle select elements**
    if (tagName === "select") {
        // Tag the select element with data-select-id
        element.setAttribute("data-select-id", elementName);

        const options = element.querySelectorAll('option');
        options.forEach((option) => {
            const optionValue = option.getAttribute('value') || option.textContent.trim();
            const optionName = elementName + "." + optionValue;
            const newOption = document.createElement('option');
            newOption.textContent = option.textContent;
            newOption.setAttribute('value', optionValue);
            newOption.setAttribute('name', optionName);
            newOption.setAttribute('selected', option.selected.toString());
            option.setAttribute('data-clickable-id', optionName); // Tag actual DOM option element
            newElement.appendChild(newOption);
        });
    }
    // Copy specified attributes
    const attrsToCopy = ["alt", "title", "type", "value", "role", "aria-label", "aria-hidden", "aria-selected"];
    attrsToCopy.forEach((attr) => {
        const value = element.getAttribute(attr);
        if (value) {
            newElement.setAttribute(attr, value);
        }
    });
    if (recipe.keep_attr) {
        for (const key in recipe.keep_attr) {
            const value = element.getAttribute(key);
            if (value) {
                newElement.setAttribute(key, value);
            }
        }
    }
    if (recipe['class']) {
        newElement.setAttribute('class', recipe['class']);
    }
    if (recipe['id']) {
        newElement.setAttribute('id', recipe['id']);
    }

    // Override attributes if specified
    if (recipe.override_attr) {
        for (const key in recipe.override_attr) {
            newElement.setAttribute(key, eval(recipe.override_attr[key]));
        }
    }

    // Process children
    if (recipe.children && recipe.children.length > 0) {
        for (const childRecipe of recipe.children) {
            const selector = childRecipe.direct_child ? `:scope > ${childRecipe.selector}` : childRecipe.selector;
            const childElements = element.querySelectorAll(selector);
            childElements.forEach((childElement, index) => {
                const childNode = processElement(childElement, childRecipe, parentName, index);
                newElement.appendChild(childNode);
                if (childRecipe.insert_split_marker) {
                    const every = childRecipe.insert_split_marker_every || 1;
                    if (index % every == 0) {
                        const splitMarker = document.createElement('split-marker');
                        newElement.appendChild(splitMarker);
                        // console.log("inserting split marker 1");
                    }
                }
                if (childRecipe.insert_split_marker) {
                    // console.log("inserting split marker 2");
                    const splitMarker = document.createElement('split-marker');
                    newElement.appendChild(splitMarker);
                } else {
                    console.log("no split marker");
                }
            });
        }
    }

    // Handle empty messages
    if (recipe.empty_message && newElement.children.length === 0) {
        const emptyTextNode = document.createTextNode(recipe.empty_message);
        newElement.appendChild(emptyTextNode);
    }

    return newElement;
}
"""

logger = logging.getLogger(__name__)


class InvalidAction(Exception):
    pass


class ElementHighlight:
    def __init__(
        self,
        element: Element,
        driver: webdriver.Chrome,
        headless: bool,
        sleep: float = 0.5,
        before_hook: Optional[str] = None,
        after_hook: Optional[str] = None,
    ):
        print("init")
        self.element = element
        self.driver = driver
        self.headless = headless
        self.before_hook = before_hook
        self.after_hook = after_hook

    def __enter__(self):
        if self.headless:
            return self
        self.driver.execute_script(
            """
console.log(arguments[0]);
requestAnimationFrame(() => {
    arguments[0].scrollIntoView({ behavior: "smooth", block: "center", inline: "center" });
});
""",
            self.element,
        )
        self.driver.execute_script(
            """
var cumulativeOffset = function(element) {
    var top = 0, left = 0;
    var rect = element.getBoundingClientRect();
    do {
        top += element.offsetTop  || 0;
        left += element.offsetLeft || 0;
        element = element.offsetParent;
    } while(element);

    return {
        top: top,
        left: left,
        width: rect.width,
        height: rect.height,
    };
};
console.log(cumulativeOffset(arguments[0]));
// rect = arguments[0].getBoundingClientRect();
rect = cumulativeOffset(arguments[0]);
div = document.createElement('div');
div.style.position = 'absolute';
div.style.top = rect.top + 'px';
div.style.left = rect.left + 'px';
div.style.width = rect.width + 'px';
div.style.height = rect.height + 'px';
div.style.outline = '3px solid #79ccd7';
div.style.zIndex = '10000';
div.style.pointerEvents = 'none';
document.body.appendChild(div);
document.highlightedElement = div;

""",
            self.element,
        )
        logger.info("highlight end")
        time.sleep(1.5)
        logger.info("sleep end")
        if self.before_hook:
            print("before_hook")
            result = self.driver.execute_script(
                self.before_hook, self.element, context.browser_context.get()
            )
            print("before_hook result", result)
            if result is not None:
                context.browser_context.set(result)
        # self.driver.execute_script(
        #     "arguments[0].style.outline='3px solid #79ccd7'", self.element
        # )
        # self.driver.execute_script(
        #     "arguments[0].style.outline_offset='3px'", self.element
        # )
        # get bounding rect
        # draw a rectangle
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        if self.headless:
            return
        try:
            # self.driver.execute_script("arguments[0].style.outline=''", self.element)
            # self.driver.execute_script(
            #     "arguments[0].style.outline_offset=''", self.element
            # )
            self.driver.execute_script(
                "document.highlightedElement && document.highlightedElement.remove()"
            )
            if self.after_hook:
                result = self.driver.execute_script(
                    self.after_hook, self.element, context.browser_context.get()
                )
                if result is not None:
                    context.browser_context.set(result)
        except StaleElementReferenceException:
            pass

    def pause(self, a: webdriver.ActionChains) -> webdriver.ActionChains:
        return a.pause(max(0.2 + numpy.random.normal(0, 0.05), 0))

    def sleep(self):
        if self.headless:
            return
        time.sleep(max(0.2 + numpy.random.normal(0, 0.05), 0))


# we assume there are only 'root' node for the diff
# so for any node from root to diff root, there should only be one different child
def tree_diff(tree1: dominate.tags.html_tag, tree2: dominate.tags.html_tag):
    diffs: list[
        tuple[Union[dominate.tags.html_tag, str], Union[dominate.tags.html_tag, str]]
    ] = []
    if len(tree1.children) != len(tree2.children):
        return tree1, tree2
    if len(tree1.children) == 0:
        return tree1, tree2
    child_count = 0
    for child1, child2 in zip(tree1.children, tree2.children):
        if child1 == "" and child2 == "":
            continue
        child_count += 1
        if type(child1) != type(child2):
            diffs.append((child1, child2))
        if isinstance(child1, str) and isinstance(child2, str):
            if child1 != child2:
                diffs.append((child1, child2))
        else:
            if child1.render(pretty=False) != child2.render(pretty=False):
                diffs.append((child1, child2))
    if child_count == 0:
        return tree1, tree2

    if len(diffs) == 0:
        return None
    if len(diffs) > 1:
        return tree1, tree2
    else:
        # if type(diffs[0][0]) == str:
        if isinstance(diffs[0][0], str) and isinstance(diffs[0][1], str):
            return tree1, tree2
        return tree_diff(*diffs[0])  # type: ignore


def node_to_selector(node: dominate.tags.html_tag):
    selector = getattr(node, "tag_name", type(node).__name__)
    if selector[-1] == "_":
        selector = selector[:-1]
    if "id" in node.attributes:
        selector += f"#{node['id']}"
    if "class" in node.attributes:
        for _cls in node["class"].split(" "):
            selector += f".{_cls}"
    if "name" in node.attributes:
        selector += f"[name='{node['name']}']"
    if node.parent is None:
        return selector
    return node_to_selector(node.parent) + " > " + selector


class Browser:
    clickables = {}
    inputs = {}
    selects = {}

    def __init__(
        self,
        url: str,
        headless: bool,
        recipes: list[dict],
        end_callback: Optional[Callable] = None,
    ):
        options = Options()
        options.add_argument("start-maximized")
        if headless:
            options.add_argument("--headless")
        # options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--unsafely-disable-devtools-self-xss-warnings")
        options.add_argument("--auto-open-devtools-for-tabs")
        options.add_argument("--window-position=-1000,-1440")
        options.add_argument("--window-size=2560,1440")

        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)
        self.driver = driver
        self.driver.get(url)
        self.clickables = {}
        self.clickable_recipes = {}
        self.inputs = {}
        self.inputs_recipes = {}
        self.last_url = url
        self.headless = headless
        self.window_height = self.driver.execute_script("return window.innerHeight")
        self.last_recipe_index = -1
        self.last_page = dominate.tags.html()
        self.recipes = recipes
        self.end_callback = end_callback

    def set_attribute(self, element: Element, attribute: str, value: str):
        self.driver.execute_script(
            "arguments[0].setAttribute(arguments[1], arguments[2]);",
            element,
            attribute,
            value,
        )

    def register_clickable(self, element: Element, name: str, recipe: dict):
        self.clickables[name] = element
        self.clickable_recipes[name] = recipe
        self.set_attribute(element, "data-clickable-id", name)

    def register_input(self, element: Element, name: str, recipe: dict):
        self.inputs[name] = element
        self.inputs_recipes[name] = recipe
        self.set_attribute(element, "data-input-id", name)

    def get_text(self, element: Element) -> str:
        elementText = element.get_attribute("textContent")
        if not elementText:
            elementText = element.get_attribute("innerText")
        elementText = re.sub(r"\s+", " ", elementText)  # type: ignore
        return elementText or ""

    def process(
        self, element: Element, recipe: dict, parent_name: str = "", nth_child: int = 0
    ):
        # if random.random() < 0.04:
        #     # element.scrollIntoView()
        #     self.driver.execute_script(
        #         'arguments[0].scrollIntoView({ behavior: "smooth" });', element
        #     )
        # if not self.headless:
        #     boundingRect = self.driver.execute_script(
        #         "return arguments[0].getBoundingClientRect()", element
        #     )
        #     if boundingRect["top"] - self.window_height // 2 > 400:
        #         self.driver.execute_script(
        #             "window.scrollBy({top: 400, behavior: 'smooth'});"
        #         )
        #         time.sleep(0.5)
        elementText = ""
        if "text_selector" in recipe:
            try:
                text_element = element.find_element(
                    By.CSS_SELECTOR, recipe["text_selector"]
                )
                elementText = self.get_text(text_element)
            except NoSuchElementException:
                elementText = ""
        elif "text_js" in recipe:
            elementText = self.driver.execute_script(recipe["text_js"], element)
        else:
            elementText = self.get_text(element)
        if "text_format" in recipe and recipe["text_format"]:
            elementText = recipe["text_format"].format(elementText)

        tag_name = element.tag_name
        if "tag_name" in recipe:
            tag_name = recipe["tag_name"]
        if tag_name in dominate.tags.underscored_classes:
            node = getattr(dominate.tags, tag_name + "_")(
                elementText if "add_text" in recipe and recipe["add_text"] else ""
            )
        else:
            node = getattr(dominate.tags, tag_name)(
                elementText if "add_text" in recipe and recipe["add_text"] else ""
            )

        if "name" in recipe and recipe["name"]:
            if recipe["name"] == "from_text":
                element_name = elementText.lower()
                for special_char in " \n":
                    element_name = element_name.replace(special_char, "_")
                for special_char in "[]{}()<>.:;|!@#$%^&*+-=,?/\\\"'":
                    element_name = element_name.replace(special_char, "")
                node["name"] = (parent_name + "." if parent_name else "") + element_name
            elif recipe["name"] == "from_nth_child":
                node["name"] = (parent_name + "." if parent_name else "") + str(
                    nth_child
                )
            else:
                node["name"] = (parent_name + "." if parent_name else "") + recipe[
                    "name"
                ]
            parent_name = node["name"]
        if "clickable" in recipe and recipe["clickable"]:
            if "name" not in recipe:
                raise Exception("clickable element must have a name")
            click_element = element
            if "click_selector" in recipe:
                click_element = element.find_element(
                    By.CSS_SELECTOR, recipe["click_selector"]
                )
            self.register_clickable(click_element, node["name"], recipe)
        for key in [
            "alt",
            "src",
            "href",
            "title",
            "type",
            "value",
            "role",
            "aria-label",
            "aria-hidden",
            "aria-selected",
        ]:
            value = element.get_dom_attribute(key)
            if value:
                node[key] = value
        if tag_name == "input":
            input_type = element.get_attribute("type")
            if input_type == "radio":
                if element.get_attribute("checked"):
                    if "class" not in node:
                        node["aria-selected"] = "true"
                    else:
                        node["aria-selected"] = "false"
                assert "clickable" in recipe and recipe["clickable"]
            elif input_type == "text":
                node["value"] = element.get_attribute("value")
                self.register_input(element, node["name"], recipe)
            elif input_type == "number":
                node["value"] = element.get_attribute("value")
                self.register_input(element, node["name"], recipe)
            elif input_type == "checkbox":
                if element.get_attribute("checked"):
                    node["checked"] = "true"
                else:
                    node["checked"] = "false"
        if tag_name == "select":
            select = Select(element)
            for option in select.options:
                option_name = node["name"] + "." + option.get_attribute("value")
                if option.is_selected():
                    node.add(
                        dominate.tags.option(
                            option.text,
                            value=option.get_attribute("value"),
                            selected="true",
                            name=option_name,
                        )
                    )
                else:
                    node.add(
                        dominate.tags.option(
                            option.text,
                            value=option.get_attribute("value"),
                            name=option_name,
                            selected="false",
                        )
                    )
                self.selects[option_name] = element
                self.clickables[option_name] = option
        if "keep_attr" in recipe:
            for key in recipe["keep_attr"]:
                value = element.get_attribute(key)
                if value:
                    node[key] = value
        for key in ["class", "id"]:
            if key in recipe and recipe[key]:
                node[key] = recipe[key]
        if "override_attr" in recipe:
            for key in recipe["override_attr"]:
                node[key] = self.driver.execute_script(
                    recipe["override_attr"][key], element
                )
        if "children" in recipe and recipe["children"]:
            for child in recipe["children"]:
                if "direct_child" in child and child["direct_child"]:
                    selector = ":scope > " + child["selector"]
                else:
                    selector = child["selector"]
                elements = element.find_elements(By.CSS_SELECTOR, selector)
                if child.get("insert_split_marker", False):
                    last_split_marker_index = 0
                    split_marker_every = child.get("insert_split_marker_every", 1)
                    node.add(dominate.util.raw("<split-marker/>"))
                    for i, child_element in enumerate(elements):
                        if i - last_split_marker_index >= split_marker_every:
                            node.add(dominate.util.raw("<split-marker/>"))
                            last_split_marker_index = i
                        node.add(self.process(child_element, child, parent_name))
                    node.add(dominate.util.raw("<split-marker/>"))
                else:
                    for i, child_element in enumerate(elements):
                        node.add(self.process(child_element, child, parent_name, i))
        # if is empty, add empty message
        if "empty_message" in recipe and recipe["empty_message"]:
            if len(node.children) == 0 or (
                len(node.children[0]) == 1 and node.children[0] == ""
            ):
                node.add(recipe["empty_message"])
        return node

    def type(self, name, text):
        print("typing", name, text)
        if name not in self.inputs:
            logger.error(f"INVALID ACTION: {name}")
            raise InvalidAction(f"INVALID ACTION: input {name} not found")
        with ElementHighlight(
            self.inputs[name],
            self.driver,
            self.headless,
            before_hook=self.inputs_recipes[name].get("before_hook", None),
            after_hook=self.inputs_recipes[name].get("after_hook", None),
        ) as h:
            action = webdriver.ActionChains(self.driver)
            action = action.click(self.inputs[name]).pause(0.5)
            for character in text:
                action = action.send_keys(character)
                action = h.pause(action)
            action = action.pause(0.5)
            action = action.send_keys(webdriver.Keys.ENTER)  # TODO
            action.perform()
        time.sleep(1)

    def type_and_submit(self, name, text):
        self.clear(name)
        if name not in self.inputs:
            logger.error(f"INVALID ACTION: {name}")
            raise InvalidAction(f"INVALID ACTION: input {name} not found")
        with ElementHighlight(
            self.inputs[name],
            self.driver,
            self.headless,
            before_hook=self.inputs_recipes[name].get("before_hook", None),
            after_hook=self.inputs_recipes[name].get("after_hook", None),
        ) as h:
            action = webdriver.ActionChains(self.driver)
            action = action.click(self.inputs[name]).pause(0.5)
            for character in text:
                action = action.send_keys(character)
                action = h.pause(action)
            action = action.pause(0.5)
            action = action.send_keys(webdriver.Keys.ENTER)
            action.perform()
        time.sleep(1)

    def clear(self, name):
        if name not in self.inputs:
            logger.error(f"INVALID ACTION: {name}")
            raise InvalidAction(f"INVALID ACTION: input {name} not found")
        with ElementHighlight(
            self.inputs[name],
            self.driver,
            self.headless,
            before_hook=self.inputs_recipes[name].get("before_hook", None),
            after_hook=self.inputs_recipes[name].get("after_hook", None),
        ) as h:
            # self.inputs[name].clear()
            # send end key
            # self.inputs[name].send_keys("\ue010")
            # # send backspace key
            # while self.inputs[name].get_attribute("value"):
            #     self.inputs[name].send_keys("\ue003")
            #     h.sleep()

            if platform.system() == "Darwin":  # macOS
                self.inputs[name].send_keys(webdriver.Keys.COMMAND, "a")
            else:
                self.inputs[name].send_keys(webdriver.Keys.CONTROL, "a")
            time.sleep(1)

    def click(self, name):
        if name not in self.clickables:
            logger.error(f"INVALID ACTION: {name} does not exist")
            raise InvalidAction(f"INVALID ACTION: {name} does not exist")

        element = self.clickables[name]

        # Check if the element is an option within a select element
        if element.tag_name.lower() == "option":
            # Retrieve the parent select element
            select_name = ".".join(
                name.split(".")[:-1]
            )  # Remove the option value from the name
            if select_name in self.selects:
                select_element = self.selects[select_name]
                option_value = name.split(".")[-1]
                with ElementHighlight(
                    select_element,
                    self.driver,
                    self.headless,
                    before_hook=self.clickable_recipes[name].get("before_hook", None),
                    after_hook=self.clickable_recipes[name].get("after_hook", None),
                ):
                    # Use Selenium's Select class to select the option
                    select_obj = Select(select_element)
                    select_obj.select_by_value(option_value)
                time.sleep(1)
            else:
                logger.error(
                    f"Select element {select_name} not found for option {name}"
                )
                raise InvalidAction(f"Select element {select_name} not found")
        else:
            with ElementHighlight(
                element,
                self.driver,
                self.headless,
                before_hook=self.clickable_recipes[name].get("before_hook", None),
                after_hook=self.clickable_recipes[name].get("after_hook", None),
            ):
                element.click()
            time.sleep(1)

    def back(self):
        self.driver.back()

    def observe(self, skip_wait: bool = False):
        self.clickables = {}
        self.inputs = {}

        if not skip_wait:
            wait = WebDriverWait(self.driver, 10)
            wait.until(
                lambda driver: driver.execute_script("return document.readyState")
                == "complete"
            )
            logger.info("OBSERVING")
            time.sleep(1)

        url = urllib.parse.urlparse(self.driver.current_url)
        path = url.path
        recipe = None
        for i, r in enumerate(self.recipes):
            match_method = r.get("match_method", "text")
            if match_method == "text":
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, r["match"])
                    if element and r["match_text"].lower() in element.text.lower():
                        recipe = r
                        break
                except NoSuchElementException:
                    pass
            elif match_method == "url":
                if r["match"] == path:
                    recipe = r
                    break
        else:
            logging.error(f"NO RECIPE FOUND FOR {path}")
            raise Exception(f"NO RECIPE FOUND FOR {path}")
        if "terminate" in recipe and self.driver.execute_script(
            recipe["terminate"], context.browser_context.get()
        ):
            if "terminate_callback" in recipe:
                result = self.driver.execute_script(
                    recipe["terminate_callback"], context.browser_context.get()
                )
                if self.end_callback:
                    self.end_callback(result)
                elif not self.headless:
                    input("Press Enter to continue...")
                if context.run_path.get():
                    (context.run_path.get() / "result.json").write_text(
                        json.dumps(result)
                    )
            return {
                "page": "TERMINATE",
                "diff_selector": "",
                "url": self.driver.current_url,
                "clickables": [],
                "inputs": [],
                "ended": True,
            }
        # Serialize the recipe to JSON
        recipe_json = json.dumps(recipe)

        # JavaScript code as a string
        js_code = f"""
            {process_js_code}
            const rootElement = document.querySelector('{recipe['selector']}');
            const recipeObj = {recipe_json};
            const newRoot = processElement(rootElement, recipeObj);
            return newRoot.outerHTML;
        """

        # Execute the script and get the result
        html_string = self.driver.execute_script(js_code)

        # Parse the HTML string if needed
        # For example, you can use BeautifulSoup or any other parser

        # Collect elements with data attributes
        self.collect_clickables_and_inputs()

        return {
            "page": html_string,
            "diff_selector": "",
            "url": self.driver.current_url,
            "clickables": list(self.clickables.keys()),
            "inputs": list(self.inputs.keys()),
            "ended": False,
        }

    def collect_clickables_and_inputs(self):
        # Clear existing mappings
        self.clickables = {}
        self.inputs = {}
        self.selects = {}

        # Find elements with data-clickable-id
        clickable_elements = self.driver.find_elements(
            By.CSS_SELECTOR, "[data-clickable-id]"
        )
        for element in clickable_elements:
            clickable_id = element.get_attribute("data-clickable-id")
            self.clickables[clickable_id] = element

        # Find elements with data-input-id
        input_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-input-id]")
        for element in input_elements:
            input_id = element.get_attribute("data-input-id")
            self.inputs[input_id] = element

        # Find select elements
        select_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-select-id]")
        for element in select_elements:
            select_id = element.get_attribute("data-select-id")
            self.selects[select_id] = element
        self.inputs_recipes = self.driver.execute_script("return window.input_recipes;")
        self.clickable_recipes = self.driver.execute_script(
            "return window.clickable_recipes;"
        )


class SeleniumEnv(gym.Env):
    browser: Browser

    def __init__(
        self,
        start_url,
        recipes,
        pretty=False,
        headless=True,
        no_animate=None,
        start_callback=None,
        end_callback=None,
    ):
        self.observation_space = spaces.Dict(
            {
                "url": spaces.Text(10000),
                "page": spaces.Text(10000),
                "clickables": spaces.Sequence(spaces.Text(10000)),
                "inputs": spaces.Sequence(spaces.Text(10000)),
                "error_message": spaces.Text(10000),
                "diff_selector": spaces.Text(10000),
            }
        )
        self.action_space = spaces.Text(10000)
        self.start_url = start_url
        self.recipes = recipes
        self.pretty = pretty
        self.ended = False
        self.headless = headless
        self.no_animate = self.headless if no_animate is None else no_animate
        self.start_callback = start_callback
        self.end_callback = end_callback

    def reset(self, seed=None):
        super().reset(seed=seed)
        self.browser = Browser(
            self.start_url, self.headless, self.recipes, self.end_callback
        )
        self.ended = False

        if self.start_callback:
            self.start_callback(self.browser)
        elif not self.headless:
            input("Press Enter to continue...")
        obs = self.browser.observe()
        if obs["ended"]:
            self.ended = True
            return (
                {
                    "url": obs["url"],
                    "page": obs["page"],
                    "clickables": obs["clickables"],
                    "inputs": obs["inputs"],
                    "error_message": "",
                    "diff_selector": obs["diff_selector"],
                },
                {},
            )
        if not self.headless:
            # self.browser.observe()  # re-run to make
            # re-run in new thread
            # asyncio.create_task(self.browser.observe())
            # thread = Thread(target=self.browser.observe, args=(False,))
            # thread.start()

            thread = Thread(
                target=self.browser.driver.execute_script, args=(run_animate,)
            )
            thread.start()
        return (
            {
                "url": obs["url"],
                "page": obs["page"],
                "clickables": obs["clickables"],
                "inputs": obs["inputs"],
                "error_message": "",
                "diff_selector": obs["diff_selector"],
            },
            {},
        )

    def step(self, actions):
        self.browser.driver.execute_script(stop_animate)
        obs = None
        error_message = ""
        for action in json.loads(actions):
            print(action)
            try:
                if action["type"] == "type":
                    self.browser.type(action["name"], action["text"])
                elif action["type"] == "type_and_submit":
                    self.browser.type_and_submit(action["name"], action["text"])
                elif action["type"] == "clear":
                    self.browser.clear(action["name"])
                elif action["type"] == "click":
                    self.browser.click(action["name"])
                elif action["type"] == "back":
                    self.browser.back()
                elif action["type"] == "terminate":
                    self.ended = True
                else:
                    logger.error(f"INVALID ACTION: {action}")
                    error_message = (
                        f"INVALID ACTION: {action} is not in the action space"
                    )
            except InvalidAction as e:
                error_message = str(e)
                break
            except Exception as e:
                logger.error(f"ERROR: {e}")
                print(traceback.format_exc())
                error_message = str(e)
                break

            time.sleep(1)
            # obs = self.browser.observe()
            obs = self.browser.observe()
            logger.info("get obs")
            if obs["ended"]:
                self.ended = True
                return (
                    {
                        "url": obs["url"],
                        "page": obs["page"],
                        "clickables": obs["clickables"],
                        "inputs": obs["inputs"],
                        "error_message": "",
                        "diff_selector": obs["diff_selector"],
                    },
                    0,
                    self.ended,
                    self.ended,
                    {},
                )
            # self.browser.headless = self.headless
        if obs is None:
            obs = self.browser.observe()
        # self.browser.headless = self.headless
        if not self.headless and not self.no_animate:
            # self.browser.observe()  # re-run to make
            # re-run in new thread
            # asyncio.create_task(self.browser.observe())
            thread = Thread(
                target=self.browser.driver.execute_script, args=(run_animate,)
            )
            thread.start()
        return (
            {
                "url": obs["url"],
                "page": obs["page"],
                "clickables": obs["clickables"],
                "inputs": obs["inputs"],
                "error_message": error_message,
                "diff_selector": obs["diff_selector"],
            },
            0,
            self.ended,
            self.ended,
            {},
        )

    def close(self):
        self.browser.driver.quit()
        return super().close()


gym.register(
    id="SeleniumEnv-v0",
    entry_point="simulated_web_agent.executor.env:SeleniumEnv",
)
