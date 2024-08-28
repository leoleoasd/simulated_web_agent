recipes = [
    {
        "match": "#yDmH0d > c-wiz.zQTmif.SSPGKf > div > div:nth-child(2) > c-wiz > div.cKvRXe > c-wiz > div.f8Ucw > div > div.Eo39gc",
        "match_text": "Flights",
        "selector": "html",
        "children": [
            {"selector": "head", "children": [{"selector": "title", "add_text": True}]},
            {
                "selector": "body",
                "children": [
                    {
                        "selector": "div.SS6Dqf.POQx1c",
                        "children": [
                            {"selector": "h1", "add_text": True},
                            {
                                "selector": "div.TQYpgc.gInvKb > div > div",
                                "name": "trip_type",
                                "children": [
                                    {
                                        "selector": "div:nth-child(1)",
                                        "add_text": True,
                                        "text_format": "Current trip type: {}",
                                    },
                                    {
                                        "selector": "ul",
                                        "children": [
                                            {
                                                "selector": "li:not(:last-child)",
                                                "add_text": True,
                                                "clickable": True,
                                                "name": "from_text",
                                                "before_hook": "document.querySelector('div.VfPpkd-O1htCb.VfPpkd-O1htCb-OWXEXe-MFS4be.VfPpkd-O1htCb-OWXEXe-SfQLQb-M1Soyc-Bz112c.VfPpkd-O1htCb-OWXEXe-di8rgd-V67aGc.hqBSCb.RnXJS.PnyZyf.JDygMb.PtTbbc > div').click()",
                                            }
                                        ],
                                    },
                                ],
                            },
                            # todo: add fare type
                            {
                                "selector": "div.JQrP8b.PLrkBc > div > div > div",
                                "name": "fare_type",
                                "children": [
                                    {
                                        "selector": "div:nth-child(1)",
                                        "add_text": True,
                                        "text_format": "Current fare type: {}",
                                    }
                                ],
                            },
                            {
                                "selector": "#i23",
                                "name": "city_picker",
                                "children": [
                                    {
                                        "selector": "input[aria-label='Where from?'][aria-expanded='false']",
                                        "name": "from_city",
                                    },
                                    {
                                        "selector": "input[placeholder='Where to?'][aria-expanded='false']",
                                        "name": "to_city",
                                    },
                                ],
                            },
                            {
                                "selector": "div.bgJkKe.K0Tsu div.cQnuXe.k0gFV",
                                "name": "date_picker",
                                "children": [
                                    {
                                        "selector": "input[aria-label='Departure']",
                                        "name": "departure_date",
                                        "after_hook": "setTimeout(() => {document.body.click(); console.log('clicked')}, 200)",
                                    },
                                    {
                                        "selector": "input[aria-label='Return']",
                                        "name": "return_date",
                                        "after_hook": "setTimeout(() => {document.body.click(); console.log('clicked')}, 200)",
                                    },
                                ],
                            },
                            {
                                "selector": "button.VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-k8QpJ.VfPpkd-LgbsSe-OWXEXe-Bz112c-M1Soyc.nCP5yc.AjY5Oe.LQeN7.TUT4y.zlyfOd",
                                "name": "search_button",
                                "clickable": True,
                                "add_text": True,
                                "override_attr": {
                                    "disabled": "return arguments[0].innerText !== 'Search'"
                                },
                            },
                        ],
                    }
                ],
            },
        ],
    },
    {
        "match": "#yDmH0d > c-wiz.zQTmif.SSPGKf > div > div:nth-child(2) > c-wiz > div.cKvRXe > c-wiz > div.PSZ8D.EA71Tc > div.FXkZv > div:nth-child(4) > h3",
        # "match": "#yDmH0d > c-wiz.zQTmif.SSPGKf > div > div:nth-child(2) > c-wiz > div.cKvRXe > c-wiz > div.PSZ8D.EA71Tc > div.FXkZv > div:nth-child(5) > h3",
        "match_text": "Best departing options",
        "selector": "html",
        "children": [
            {"selector": "head", "children": [{"selector": "title", "add_text": True}]},
            {
                "selector": "body",
                "children": [
                    {
                        "selector": "div[jsname='IWWDBc']",
                        "children": [
                            {"selector": "h3", "add_text": True, "direct_child": True},
                            {
                                "selector": "ul.Rk10dc",
                                "name": "best_departure_options",
                                "children": [
                                    {
                                        "selector": "li:not([data-ved])",
                                        "add_text": True,
                                        "clickable": True,
                                        "name": "from_nth_child",
                                    }
                                ],
                            },
                        ],
                    },
                    {
                        "selector": "div[jsname='YdtKid']",
                        "children": [
                            {"selector": "h3", "add_text": True, "direct_child": True},
                            {
                                "selector": "ul.Rk10dc",
                                "name": "other_departure_options",
                                "children": [
                                    {
                                        "selector": "li:not([data-ved])",
                                        "add_text": True,
                                        "clickable": True,
                                        "name": "from_nth_child",
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
        "match": "#yDmH0d > c-wiz.zQTmif.SSPGKf > div > div:nth-child(2) > c-wiz > div.cKvRXe > c-wiz > div.PSZ8D.EA71Tc > div.FXkZv > div:nth-child(4) > h3",
        "match_text": "Returning flights",
        "selector": "html",
        "children": [
            {"selector": "head", "children": [{"selector": "title", "add_text": True}]},
            {
                "selector": "body",
                "children": [
                    {"selector": "h3", "add_text": True, "direct_child": True},
                    {
                        "selector": "ul.Rk10dc",
                        "name": "returning_options",
                        "children": [
                            {
                                "selector": "li:not([data-ved])",
                                "add_text": True,
                                "clickable": True,
                                "name": "from_nth_child",
                            }
                        ],
                    },
                ],
            },
        ],
    },
    {
        "match": "#yDmH0d > c-wiz.zQTmif.SSPGKf > div > div:nth-child(2) > c-wiz > div.cKvRXe > c-wiz > div > div.SDUAh.Xag90b.jtr7Nd > div.OLfz3c > div:nth-child(4) > div > div.pkMWGc > h2",
        "match_text": "Selected flights",
        "terminate": "return true;",
        "terminate_callback": """
departure_time = document.querySelector("#yDmH0d > c-wiz.zQTmif.SSPGKf > div > div:nth-child(2) > c-wiz > div.cKvRXe > c-wiz > div > div.SDUAh.Xag90b.jtr7Nd > div.OLfz3c > div:nth-child(4) > div > div:nth-child(2) > div.rVD9dd > div > div > div > div:nth-child(1) > div.mz0jqb > div > div.KC3CM.zeBrcf > div > div.OgQvJf.nKlB3b > div > div.Ir0Voe > div.zxVSec.YMlIz.tPgKwe.ogfYpf > span").innerText

return_time = document.querySelector("#yDmH0d > c-wiz.zQTmif.SSPGKf > div > div:nth-child(2) > c-wiz > div.cKvRXe > c-wiz > div > div.SDUAh.Xag90b.jtr7Nd > div.OLfz3c > div:nth-child(4) > div > div:nth-child(2) > div.rVD9dd > div > div > div > div:nth-child(2) > div.mz0jqb > div > div.KC3CM.zeBrcf > div > div.OgQvJf.nKlB3b > div > div.Ir0Voe > div.zxVSec.YMlIz.tPgKwe.ogfYpf > span").innerText

departure_airline = document.querySelector("#yDmH0d > c-wiz.zQTmif.SSPGKf > div > div:nth-child(2) > c-wiz > div.cKvRXe > c-wiz > div > div.SDUAh.Xag90b.jtr7Nd > div.OLfz3c > div:nth-child(4) > div > div:nth-child(2) > div.rVD9dd > div > div > div > div:nth-child(1) > div.mz0jqb > div > div.KC3CM.zeBrcf > div > div.OgQvJf.nKlB3b > div > div.Ir0Voe > div.sSHqwe.tPgKwe.ogfYpf > span").innerText

return_airline = document.querySelector("#yDmH0d > c-wiz.zQTmif.SSPGKf > div > div:nth-child(2) > c-wiz > div.cKvRXe > c-wiz > div > div.SDUAh.Xag90b.jtr7Nd > div.OLfz3c > div:nth-child(4) > div > div:nth-child(2) > div.rVD9dd > div > div > div > div:nth-child(2) > div.mz0jqb > div > div.KC3CM.zeBrcf > div > div.OgQvJf.nKlB3b > div > div.Ir0Voe > div.sSHqwe.tPgKwe.ogfYpf > span").innerText
text_to_show = `You booked ${departure_airline} at ${departure_time} and ${return_airline} at ${return_time}`

h1 = document.createElement("h1");
document.documentElement.remove();
div = document.createElement("div");
div.style.display="flex";
div.style.justifyContent="center";
div.style.alignItems="center";
div.style.width="100%"; div.style.height="100%";
document.appendChild(div);
div.style.alignContent="center";
h1.textContent=text_to_show;
div.appendChild(h1)
""",
    },
]
