import asyncio
import json
import logging
import os
import random
import re
import time
import urllib.parse
import traceback
from threading import Thread
from typing import Any, Union

import dominate
import dominate.tags
import dominate.util
import gymnasium as gym
import numpy
from bs4 import BeautifulSoup
from gymnasium import spaces
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

from .recipes import recipes

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
    ):
        self.element = element
        self.driver = driver
        self.headless = headless

    def __enter__(self):
        if self.headless:
            return self
        self.driver.execute_script(
            'arguments[0].scrollIntoView({ behavior: "smooth", block: "center", inline: "center" });',
            self.element,
        )
        self.driver.execute_script(
            "arguments[0].style.outline='3px solid #79ccd7'", self.element
        )
        self.driver.execute_script(
            "arguments[0].style.outline_offset='3px'", self.element
        )
        time.sleep(2)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        if self.headless:
            return
        try:
            self.driver.execute_script("arguments[0].style.outline=''", self.element)
            self.driver.execute_script(
                "arguments[0].style.outline_offset=''", self.element
            )
        except StaleElementReferenceException:
            pass

    def sleep(self):
        if self.headless:
            return
        time.sleep(max(0.1 + numpy.random.normal(0, 0.05), 0))


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
        elif type(child1) == str:
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
        if type(diffs[0][0]) == str:
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

    def __init__(self, url: str, headless: bool):
        options = Options()
        options.add_argument("start-maximized")
        if headless:
            options.add_argument("--headless")
        options.add_argument("--remote-debugging-port=9222")
        driver = webdriver.Chrome(options=options)
        self.driver = driver
        self.driver.get(url)
        self.clickables = {}
        self.inputs = {}
        self.last_url = url
        self.headless = headless
        self.window_height = self.driver.execute_script("return window.innerHeight")
        self.last_recipe_index = -1
        self.last_page = dominate.tags.html()

    def set_attribute(self, element: Element, attribute: str, value: str):
        self.driver.execute_script(
            "arguments[0].setAttribute(arguments[1], arguments[2]);",
            element,
            attribute,
            value,
        )

    def register_clickable(self, element: Element, name: str):
        self.clickables[name] = element
        self.set_attribute(element, "data-clickable-id", name)

    def register_input(self, element: Element, name: str):
        self.inputs[name] = element
        self.set_attribute(element, "data-input-id", name)

    def get_text(self, element: Element) -> str:
        elementText = element.get_attribute("textContent")
        if not elementText:
            elementText = element.get_attribute("innerText")
        elementText = re.sub(r"\s+", " ", elementText)  # type: ignore
        return elementText or ""

    def process(self, element: Element, recipe: dict, parent_name: str = ""):
        # if random.random() < 0.04:
        #     # element.scrollIntoView()
        #     self.driver.execute_script(
        #         'arguments[0].scrollIntoView({ behavior: "smooth" });', element
        #     )
        if not self.headless:
            boundingRect = self.driver.execute_script(
                "return arguments[0].getBoundingClientRect()", element
            )
            if boundingRect["top"] - self.window_height // 2 > 400:
                self.driver.execute_script(
                    "window.scrollBy({top: 400, behavior: 'smooth'});"
                )
                time.sleep(0.5)
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
            self.register_clickable(click_element, node["name"])
        for key in ["alt", "src", "href", "title", "type", "value"]:
            value = element.get_dom_attribute(key)
            if value:
                node[key] = value
        if tag_name == "input":
            input_type = element.get_attribute("type")
            if input_type == "radio":
                if element.get_attribute("checked"):
                    if "class" not in node:
                        node["selected"] = "true"
                    else:
                        node["selected"] = "false"
                assert "clickable" in recipe and recipe["clickable"]
            elif input_type == "text":
                node["value"] = element.get_attribute("value")
                self.register_input(element, node["name"])
            elif input_type == "number":
                node["value"] = element.get_attribute("value")
                self.register_input(element, node["name"])
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
                    for child_element in elements:
                        node.add(self.process(child_element, child, parent_name))
        # if is empty, add empty message
        if "empty_message" in recipe and recipe["empty_message"]:
            if len(node.children) == 0:
                node.add(recipe["empty_message"])
        return node

    def type(self, name, text):
        if name not in self.inputs:
            logger.error(f"INVALID ACTION: {name}")
            raise InvalidAction(f"INVALID ACTION: input {name} not found")
        with ElementHighlight(self.inputs[name], self.driver, self.headless) as h:
            for character in text:
                self.inputs[name].send_keys(character)
                h.sleep()

    def type_and_submit(self, name, text):
        if name not in self.inputs:
            logger.error(f"INVALID ACTION: {name}")
            raise InvalidAction(f"INVALID ACTION: input {name} not found")
        with ElementHighlight(self.inputs[name], self.driver, self.headless) as h:
            for character in text:
                self.inputs[name].send_keys(character)
                h.sleep()
            self.inputs[name].submit()

    def clear(self, name):
        if name not in self.inputs:
            logger.error(f"INVALID ACTION: {name}")
            raise InvalidAction(f"INVALID ACTION: input {name} not found")
        with ElementHighlight(self.inputs[name], self.driver, self.headless) as h:
            # self.inputs[name].clear()
            # send end key
            self.inputs[name].send_keys("\ue010")
            # send backspace key
            while self.inputs[name].get_attribute("value"):
                self.inputs[name].send_keys("\ue003")
                h.sleep()

    def click(self, name):
        if name not in self.clickables:
            logger.error(f"INVALID ACTION: {name} is not clickable")
            raise InvalidAction(f"INVALID ACTION: {name} is not clickable")
        if name in self.selects:
            select = self.selects[name]
            select = Select(select)
            option = self.clickables[name]
            with ElementHighlight(self.selects[name], self.driver, self.headless):
                select.select_by_value(option.get_attribute("value"))
        else:
            with ElementHighlight(self.clickables[name], self.driver, self.headless):
                self.clickables[name].click()
        time.sleep(1)

    def back(self):
        self.driver.back()

    def observe(self, skip_wait: bool = False):
        self.clickables = {}
        self.inputs = {}
        # wait for the page to load
        if not skip_wait:
            wait = WebDriverWait(self.driver, 10)
            wait.until(
                lambda driver: driver.execute_script("return document.readyState")
                == "complete"
            )
            # await asyncio.sleep(1)
            logger.info("OBSERVING")
            time.sleep(1)

        url = urllib.parse.urlparse(self.driver.current_url)
        path = url.path
        recipe = None
        recipe_index = -1
        for i, r in enumerate(recipes):
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, r["match"])
                if (
                    element
                    and r["match_text"].lower() in self.get_text(element).lower()
                ):
                    recipe = r
                    recipe_index = i
                    break
                else:
                    logger.info(
                        f"NO MATCH FOR recipe i, {r['match']}, got {self.get_text(element)}"
                    )
            except NoSuchElementException:
                logger.info(f"NO SUCH ELEMENT FOR recipe i, {r['match']}")
                pass
        else:
            logging.error(f"NO RECIPE FOUND FOR {path}")
            raise Exception(f"NO RECIPE FOUND FOR {path}")
        if "terminate" in recipe and self.driver.execute_script(recipe["terminate"]):
            if "terminate_callback" in recipe:
                self.driver.execute_script(recipe["terminate_callback"])
                input("Press Enter to continue...")
            return {
                "page": "TERMINATE",
                "diff_selector": "",
                "url": self.driver.current_url,
                "clickables": [],
                "inputs": [],
                "ended": True,
            }
        new_root = self.process(
            self.driver.find_element(By.CSS_SELECTOR, recipe["selector"]), recipe
        )
        self.driver.execute_script("window.scrollBy({top: -800, behavior: 'smooth'});")
        if recipe_index == self.last_recipe_index:
            # get diff
            diff = tree_diff(self.last_root, new_root)
            self.last_root = new_root
            self.last_recipe_index = recipe_index
            if diff is not None:
                selector_1 = node_to_selector(diff[0])
                selector_2 = node_to_selector(diff[1])
                # assert selector_1 == selector_2
                return {
                    "page": diff[1],
                    "diff_selector": selector_2,
                    "url": self.driver.current_url,
                    "clickables": list(self.clickables.keys()),
                    "inputs": list(self.inputs.keys()),
                    "ended": False,
                }
        self.last_root = new_root
        self.last_recipe_index = recipe_index
        return {
            "page": new_root,
            "diff_selector": "",
            "url": self.driver.current_url,
            "clickables": list(self.clickables.keys()),
            "inputs": list(self.inputs.keys()),
            "ended": False,
        }


class SeleniumEnv(gym.Env):
    browser: Browser

    def __init__(self, start_url, pretty=False, headless=True, no_animate=None):
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
        self.pretty = pretty
        self.ended = False
        self.headless = headless
        self.no_animate = self.headless if no_animate is None else no_animate

    def reset(self, seed=None):
        super().reset(seed=seed)
        self.browser = Browser(self.start_url, self.headless)
        self.ended = False
        if not self.headless:
            input("Press Enter to continue...")
        self.browser.headless = True
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
            self.browser.headless = False
            # self.browser.observe()  # re-run to make
            # re-run in new thread
            # asyncio.create_task(self.browser.observe())
            thread = Thread(target=self.browser.observe, args=(False,))
            thread.start()
        return (
            {
                "url": obs["url"],
                "page": obs["page"].render(pretty=self.pretty),
                "clickables": obs["clickables"],
                "inputs": obs["inputs"],
                "error_message": "",
                "diff_selector": obs["diff_selector"],
            },
            {},
        )

    def step(self, actions):
        for action in json.loads(actions):
            print(action)
            error_message = ""
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

            self.browser.headless = True
            # obs = self.browser.observe()
            obs = self.browser.observe()
            logger.info(f"get obs")
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
        if not self.headless and not self.no_animate:
            self.browser.headless = False
            # self.browser.observe()  # re-run to make
            # re-run in new thread
            # asyncio.create_task(self.browser.observe())
            thread = Thread(target=self.browser.observe, args=(False,))
            thread.start()
        if type(obs["page"]) == str:
            print(obs["page"])
        return (
            {
                "url": obs["url"],
                "page": obs["page"].render(pretty=self.pretty),
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
