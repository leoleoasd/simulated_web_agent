import json
import logging
import os
import random
import re
import time
import urllib

import dominate
import dominate.tags
import gymnasium as gym
import numpy
from bs4 import BeautifulSoup
from gymnasium import spaces
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
                                        StaleElementReferenceException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement as Element
from tqdm.auto import tqdm

from .recipes import recipes

logger = logging.getLogger(__name__)


class InvalidAction(Exception):
    pass


class ElementHighlight:
    def __init__(self, element, driver, headless, sleep=0.5):
        self.element = element
        self.driver = driver
        self.headless = headless

    def __enter__(self):
        if self.headless:
            return
        self.driver.execute_script('arguments[0].scrollIntoView({ behavior: "smooth", block: "center", inline: "center" });', self.element)
        self.driver.execute_script(
            "arguments[0].style.outline='3px solid #79ccd7'", self.element
        )
        self.driver.execute_script(
            "arguments[0].style.outline_offset='3px'", self.element
        )
        time.sleep(2)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.headless:
            return
        try:
            self.driver.execute_script("arguments[0].style.outline=''", self.element)
            self.driver.execute_script(
                "arguments[0].style.outline_offset=''", self.element
            )
        except StaleElementReferenceException:
            pass


class Browser:
    clickables = {}
    inputs = {}

    def __init__(self, url, headless=True):
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

    def set_attribute(self, element: Element, attribute, value):
        self.driver.execute_script(
            "arguments[0].setAttribute(arguments[1], arguments[2]);",
            element,
            attribute,
            value,
        )

    def slow_type(self, element: Element, text: str, delay: float = 0.1):
        if self.headless:
            element.send_keys(text)
        else:
            """Send a text to an element one character at a time with a delay."""
            for character in text:
                element.send_keys(character)
                time.sleep(max(delay + numpy.random.normal(0, 0.05), 0))

    def register_clickable(self, element: Element, name: str):
        self.clickables[name] = element
        self.set_attribute(element, "data-clickable-id", name)

    def register_input(self, element: Element, name: str):
        self.inputs[name] = element
        self.set_attribute(element, "data-input-id", name)

    def get_text(self, element):
        elementText = element.text  # sometime NOT work
        if not elementText:
            elementText = element.get_attribute("innerText")
        if not elementText:
            elementText = element.get_attribute("textContent")
        return element.get_attribute("innerText")

    def process(self, element: Element, recipe, parent_name=""):
        if random.random() < 0.04:
            # element.scrollIntoView()
            self.driver.execute_script(
                'arguments[0].scrollIntoView({ behavior: "smooth" });', element
            )
        elementText = ""
        if "text_selector" in recipe:
            text_element = element.find_element(
                By.CSS_SELECTOR, recipe["text_selector"]
            )
            elementText = self.get_text(text_element)
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
        for key in ["class", "id"]:
            if key in recipe and recipe[key]:
                node[key] = recipe[key]
        if "override_attr" in recipe:
            for key in recipe["override_attr"]:
                node[key] = self.driver.execute_script(
                    recipe["override_attr"][key], element
                )
        if tag_name == "input":
            input_type = element.get_attribute("type")
            if input_type == "radio":
                if element.get_attribute("checked"):
                    if "class" not in node:
                        node["class"] = "selected"
                    else:
                        node["class"] += " selected"
                assert "clickable" in recipe and recipe["clickable"]
            elif input_type == "text": # TODO: handle number
                node["value"] = element.get_attribute("value")
                self.register_input(element, node["name"])
        if "keep_attr" in recipe:
            for key in recipe["keep_attr"]:
                value = element.get_attribute(key)
                if value:
                    node[key] = value
        if "children" in recipe and recipe["children"]:
            with node:
                for child in recipe["children"]:
                    if "direct_child" in child and child["direct_child"]:
                        selector = ":scope > " + child["selector"]
                    else:
                        selector = child["selector"]
                    elements = element.find_elements(By.CSS_SELECTOR, selector)
                    for child_element in elements:
                        self.process(child_element, child, parent_name)
        return node

    def type(self, name, text):
        if name not in self.inputs:
            logger.error(f"INVALID ACTION: {name}")
            raise InvalidAction(f"INVALID ACTION: input {name} not found")
        with ElementHighlight(self.inputs[name], self.driver, self.headless):
            self.slow_type(self.inputs[name], text)

    def click(self, name):
        if name not in self.clickables:
            logger.error(f"INVALID ACTION: {name}")
            raise InvalidAction(f"INVALID ACTION: clickable {name} not found")
        with ElementHighlight(self.clickables[name], self.driver, self.headless):
            self.clickables[name].click()

    def back(self):
        self.driver.back()

    def observe(self):
        if self.driver.current_url != self.last_url:
            self.last_url = self.driver.current_url
            self.clickables = {}
            self.inputs = {}
        url = urllib.parse.urlparse(self.driver.current_url)
        path = url.path
        print(path)
        recipe = None
        for i, r in enumerate(recipes):
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, r["match"])
                if element and r["match_text"] in self.get_text(element):
                    recipe = r
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
        root = self.process(
            self.driver.find_element(By.CSS_SELECTOR, recipe["selector"]), recipe
        )
        return {
            "page": root,
            "url": self.driver.current_url,
            "clickables": list(self.clickables.keys()),
            "inputs": list(self.inputs.keys()),
            "ended": False,
        }


class SeleniumEnv(gym.Env):
    browser: Browser = None

    def __init__(self, start_url, pretty=False, headless=True):
        self.observation_space = spaces.Dict(
            {
                "url": spaces.Text(10000),
                "page": spaces.Text(10000),
                "clickables": spaces.Sequence(spaces.Text(10000)),
                "inputs": spaces.Sequence(spaces.Text(10000)),
            }
        )
        self.action_space = spaces.Text(10000)
        self.start_url = start_url
        self.pretty = pretty
        self.ended = False
        self.headless = headless

    def reset(self, seed=None):
        super().reset(seed=seed)
        self.browser = Browser(self.start_url, self.headless)
        self.ended = False
        obs = self.browser.observe()
        return (
            {
                "url": obs["url"],
                "page": obs["page"].render(pretty=self.pretty),
                "clickables": obs["clickables"],
                "inputs": obs["inputs"],
            },
            {},
        )

    def step(self, action):
        action = json.loads(action)
        if action["type"] == "type":
            self.browser.type(action["name"], action["text"])
        elif action["type"] == "click":
            self.browser.click(action["name"])
        elif action["type"] == "back":
            self.browser.back()
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
        obs = self.browser.observe()
        if obs["ended"]:
            self.ended = True
        return (
            {
                "url": obs["url"],
                "page": obs["page"].render(pretty=self.pretty),
                "clickables": obs["clickables"],
                "inputs": obs["inputs"],
            },
            0,
            self.ended,
            self.ended,
            {},
        )


gym.register(
    id="SeleniumEnv-v0",
    entry_point="simulated_web_agent.executor.env:SeleniumEnv",
)
